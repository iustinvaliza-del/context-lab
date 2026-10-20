# Sets up the workshop folder on Windows: installs git and Obsidian if they are missing,
# adds this folder to Obsidian as a vault, and opens it. Safe to run more than once.
# Nothing here needs the person to click: both install for this user only, with no admin prompt.
# Run it from the workshop folder:
#   powershell -NoProfile -ExecutionPolicy Bypass -File setup\windows.ps1
param(
  [string]$ConfigPath = "",  # for testing: write the vault list here instead of Obsidian's own file
  [switch]$NoLaunch,         # for testing: don't open Obsidian at the end
  [switch]$ResolveOnly       # for testing: print the installer address and stop
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12

$Vault = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path.TrimEnd('\')

function Say([string]$Text) { Write-Host "[setup] $Text" }

function Find-Obsidian {
  $candidates = @(
    (Join-Path $env:LOCALAPPDATA 'Programs\Obsidian\Obsidian.exe'),
    (Join-Path $env:LOCALAPPDATA 'Obsidian\Obsidian.exe'),
    (Join-Path $env:ProgramFiles 'Obsidian\Obsidian.exe')
  )
  foreach ($c in $candidates) { if (Test-Path $c) { return $c } }
  $keys = @(
    'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*',
    'HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*',
    'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*'
  )
  foreach ($k in $keys) {
    $hit = Get-ItemProperty $k -ErrorAction SilentlyContinue |
      Where-Object { $_.DisplayName -like 'Obsidian*' } | Select-Object -First 1
    if (-not $hit) { continue }
    if ($hit.DisplayIcon) {
      $exe = ($hit.DisplayIcon -split ',')[0].Trim('"')
      if (Test-Path $exe) { return $exe }
    }
    if ($hit.InstallLocation) {
      $exe = Join-Path $hit.InstallLocation 'Obsidian.exe'
      if (Test-Path $exe) { return $exe }
    }
  }
  return $null
}

# The download page links the current installer; the latest-release redirect is the backup.
function Get-InstallerUrl {
  try {
    $page = (Invoke-WebRequest -Uri 'https://obsidian.md/download' -UseBasicParsing).Content
    $m = [regex]::Match($page, 'https://github\.com/obsidianmd/obsidian-releases/releases/download/v[0-9.]+/Obsidian-[0-9.]+\.exe')
    if ($m.Success) { return $m.Value }
  } catch { }
  $req = [Net.HttpWebRequest]::Create('https://github.com/obsidianmd/obsidian-releases/releases/latest')
  $req.AllowAutoRedirect = $false
  $req.Method = 'HEAD'
  $resp = $req.GetResponse()
  $loc = $resp.Headers['Location']
  $resp.Close()
  if ($loc -match '/tag/v([0-9.]+)$') {
    $v = $Matches[1]
    return "https://github.com/obsidianmd/obsidian-releases/releases/download/v$v/Obsidian-$v.exe"
  }
  throw 'could not find the address of the Obsidian installer'
}

function Find-Git {
  $cmd = Get-Command git -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Source }
  $candidates = @(
    (Join-Path $env:LOCALAPPDATA 'Programs\Git\cmd\git.exe'),
    (Join-Path $env:ProgramFiles 'Git\cmd\git.exe')
  )
  foreach ($c in $candidates) { if (Test-Path $c) { return $c } }
  return $null
}

# Git for Windows, for this user only (no admin prompt): winget first, then the installer
# from the latest GitHub release.
function Install-Git {
  if (Get-Command winget -ErrorAction SilentlyContinue) {
    Say 'Installing git with winget.'
    & winget install --id Git.Git --exact --source winget --scope user --silent --accept-package-agreements --accept-source-agreements --disable-interactivity | Out-Host
    $exe = Find-Git
    if ($exe) { return $exe }
    Say 'winget did not finish the install, so downloading the git installer directly.'
  }
  $rel = Invoke-RestMethod -Uri 'https://api.github.com/repos/git-for-windows/git/releases/latest' -UseBasicParsing
  $pattern = if ($env:PROCESSOR_ARCHITECTURE -eq 'ARM64') { '^Git-[0-9.]+(\.windows\.[0-9]+)?-arm64\.exe$' } else { '^Git-[0-9.]+(\.windows\.[0-9]+)?-64-bit\.exe$' }
  $asset = $rel.assets | Where-Object { $_.name -match $pattern } | Select-Object -First 1
  if (-not $asset) { throw 'could not find the git installer in the latest release' }
  $file = Join-Path $env:TEMP $asset.name
  Say "Downloading $($asset.browser_download_url)."
  Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $file -UseBasicParsing
  Say 'Running the git installer.'
  Start-Process -FilePath $file -ArgumentList '/VERYSILENT', '/NORESTART', '/SUPPRESSMSGBOXES', '/CURRENTUSER' -Wait
  Remove-Item $file -ErrorAction SilentlyContinue
  $exe = Find-Git
  if (-not $exe) { throw 'the git installer ran, but git.exe cannot be found afterwards' }
  return $exe
}

function Install-Obsidian {
  if (Get-Command winget -ErrorAction SilentlyContinue) {
    Say 'Installing Obsidian with winget. This is a large download and can take a few minutes.'
    & winget install --id Obsidian.Obsidian --exact --source winget --silent --accept-package-agreements --accept-source-agreements --disable-interactivity | Out-Host
    $exe = Find-Obsidian
    if ($exe) { return $exe }
    Say 'winget did not finish the install, so downloading the installer directly.'
  }
  $url = Get-InstallerUrl
  $file = Join-Path $env:TEMP ([IO.Path]::GetFileName($url))
  Say "Downloading $url. This can take a few minutes."
  Invoke-WebRequest -Uri $url -OutFile $file -UseBasicParsing
  Say 'Running the Obsidian installer.'
  Start-Process -FilePath $file -ArgumentList '/S' -Wait
  Remove-Item $file -ErrorAction SilentlyContinue
  $exe = Find-Obsidian
  if (-not $exe) { throw 'the installer ran, but Obsidian.exe cannot be found afterwards' }
  return $exe
}

# Obsidian keeps its list of vaults in obsidian.json. Add this folder, mark it as the
# one to open, and keep every other vault in the list.
function Register-Vault([string]$Cfg) {
  $dir = Split-Path $Cfg -Parent
  if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
  $data = $null
  if (Test-Path $Cfg) {
    try { $data = Get-Content $Cfg -Raw -Encoding UTF8 | ConvertFrom-Json }
    catch {
      Copy-Item $Cfg "$Cfg.bak" -Force
      Say "Obsidian's vault list could not be read, so a copy was saved as obsidian.json.bak and a new list started."
      $data = $null
    }
  }
  if (-not $data) { $data = New-Object psobject }
  if (-not ($data.PSObject.Properties.Name -contains 'vaults') -or -not $data.vaults) {
    $data | Add-Member -NotePropertyName vaults -NotePropertyValue (New-Object psobject) -Force
  }
  $id = $null
  foreach ($p in @($data.vaults.PSObject.Properties)) {
    if ($p.Value.path -and ($p.Value.path.TrimEnd('\') -ieq $Vault)) { $id = $p.Name }
    if ($p.Value.PSObject.Properties.Name -contains 'open') { $p.Value.PSObject.Properties.Remove('open') }
  }
  if (-not $id) {
    $id = -join (1..16 | ForEach-Object { '{0:x}' -f (Get-Random -Maximum 16) })
    $entry = New-Object psobject
    $entry | Add-Member -NotePropertyName path -NotePropertyValue $Vault
    $entry | Add-Member -NotePropertyName ts -NotePropertyValue ([DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds())
    $data.vaults | Add-Member -NotePropertyName $id -NotePropertyValue $entry
  }
  $data.vaults.$id | Add-Member -NotePropertyName open -NotePropertyValue $true -Force
  $json = $data | ConvertTo-Json -Depth 20 -Compress
  [IO.File]::WriteAllText($Cfg, $json, (New-Object Text.UTF8Encoding $false))
}

try {
  Say "Setting up $Vault"
  $realConfig = -not $ConfigPath
  if ($realConfig) { $ConfigPath = Join-Path $env:APPDATA 'obsidian\obsidian.json' }

  if ($ResolveOnly) { Get-InstallerUrl; exit 0 }

  $git = Find-Git
  if ($git) { Say "Git is already installed: $git" }
  else { $git = Install-Git; Say "Git is installed: $git. A new terminal finds it as git; this one needs the full path." }

  # Obsidian reads its vault list only when it starts, so close it; it saves notes as you type.
  if ($realConfig -and (Get-Process -Name Obsidian -ErrorAction SilentlyContinue)) {
    Say 'Closing Obsidian so it picks up this folder when it opens again.'
    Get-Process -Name Obsidian -ErrorAction SilentlyContinue | ForEach-Object { [void]$_.CloseMainWindow() }
    Start-Sleep -Seconds 3
    Get-Process -Name Obsidian -ErrorAction SilentlyContinue | Stop-Process -Force
  }

  # The vault goes in first, so an installer that opens Obsidian right away opens this folder.
  Register-Vault $ConfigPath
  Say "Added this folder to Obsidian's vault list."

  $exe = Find-Obsidian
  if ($exe) { Say "Obsidian is already installed: $exe" }
  else { $exe = Install-Obsidian; Say "Obsidian is installed: $exe" }

  if (-not $NoLaunch) {
    Start-Sleep -Seconds 1
    if (-not (Get-Process -Name Obsidian -ErrorAction SilentlyContinue)) { Start-Process -FilePath $exe }
    Say 'Obsidian is opening on this folder.'
  }
  Say 'Done. Git and Obsidian are ready, and Obsidian is open on this folder.'
  exit 0
}
catch {
  Say "Failed: $($_.Exception.Message)"
  Say 'You can still install Obsidian from obsidian.md, then choose Open folder as vault and pick this folder.'
  exit 1
}
