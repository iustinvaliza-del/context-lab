# Sets up the workshop folder on Windows: installs git, uv (which brings Python), Obsidian and
# MarkText if they are missing, gets the case pipeline's packages ready, makes an Agent Memory
# folder on the Desktop with the note-taking rules in it, adds it to Obsidian as a vault, and opens it.
# It also writes that folder's path into the AGENTS.md template, lets Claude Code read and
# write there, and builds the search over the person's files in database\. Safe to run more than once.
# Nothing here needs the person to click: everything installs for this user only, with no admin prompt.
# Run it from the workshop folder:
#   powershell -NoProfile -ExecutionPolicy Bypass -File setup\windows.ps1
param(
  [string]$ConfigPath = "",  # for testing: write the vault list here instead of Obsidian's own file
  [string]$MemoryPath = "",  # for testing: make the Agent Memory folder here instead of on the Desktop
  [switch]$NoLaunch,         # for testing: don't open Obsidian at the end
  [switch]$SkipPipeline,     # for testing: don't download the pipeline's packages
  [switch]$ResolveOnly,      # for testing: print the installer address and stop
  [switch]$SkipMarkText,     # for testing: don't install MarkText
  [switch]$SkipDatabase      # for testing: don't build the search in database\
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12

$Here = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path.TrimEnd('\')
# The vault is the Agent Memory folder on the Desktop, outside the workshop folder, so every
# project can read the same notes. GetFolderPath finds the Desktop even when OneDrive moved it.
if ($MemoryPath) { $Vault = $MemoryPath.TrimEnd('\') }
else { $Vault = Join-Path ([Environment]::GetFolderPath('Desktop')) 'Agent Memory' }
$Placeholder = '<full path of my Agent Memory folder>'
# The note-taking rules that every new or existing Agent Memory folder gets a copy of.
$Rules = Join-Path $Here 'setup\vault\How to keep notes.md'
# The MarkText version this setup was tested with, used when the newest one cannot be found.
$MarkTextTested = '0.23.0'

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

function Find-Uv {
  $cmd = Get-Command uv -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Source }
  $c = Join-Path $env:USERPROFILE '.local\bin\uv.exe'
  if (Test-Path $c) { return $c }
  return $null
}

# uv runs the case pipeline's Python scripts and installs Python and their packages itself,
# for this user only. Its own installer first, then winget.
function Install-Uv {
  Say 'Installing uv, which runs the case pipeline and brings its own Python.'
  try { Invoke-RestMethod -Uri 'https://astral.sh/uv/install.ps1' -UseBasicParsing | Invoke-Expression } catch { Say "The uv installer stopped: $($_.Exception.Message)" }
  $exe = Find-Uv
  if ($exe) { return $exe }
  if (Get-Command winget -ErrorAction SilentlyContinue) {
    & winget install --id astral-sh.uv --exact --source winget --scope user --silent --accept-package-agreements --accept-source-agreements --disable-interactivity | Out-Host
    $exe = Find-Uv
    if (-not $exe) {
      $hit = Get-ChildItem (Join-Path $env:LOCALAPPDATA 'Microsoft\WinGet\Packages') -Recurse -Filter uv.exe -ErrorAction SilentlyContinue | Select-Object -First 1
      if ($hit) { $exe = $hit.FullName }
    }
    if ($exe) { return $exe }
  }
  throw 'uv could not be installed'
}

# The first run of each script downloads Python and its packages; doing it now means the case
# pipeline starts at once in the workshop. A failure here is not fatal: the first real run retries.
function Prepare-Pipeline([string]$Uv) {
  $dir = Join-Path $Here 'pipeline'
  if (-not (Test-Path $dir)) { return }
  Say 'Getting the case pipeline ready (Python and its packages). This can take a few minutes.'
  & $Uv run (Join-Path $dir 'blackboard.py') check | Out-Host
  if ($LASTEXITCODE -ne 0) { Say 'The browser check did not pass; the first Blackboard run will try again.' }
  & $Uv run (Join-Path $dir 'read_case.py') --help *> $null
  & $Uv run (Join-Path $dir 'check_workbook.py') *> $null
  Say 'The case pipeline is ready.'
}

# The database in database\ keeps a search over the person's files and notes. It runs after
# the Agent Memory steps, so the search includes that folder. Building it now means the first
# search answers at once. A failure here is not fatal: the tool builds it before the first search.
function Prepare-Database([string]$Uv) {
  $dbScript = Join-Path $Here 'database\db.py'
  if (-not (Test-Path -LiteralPath $dbScript)) { return }
  Say 'Building the search over your files and notes (IESE, sources, outputs, Agent Memory).'
  try {
    & $Uv run $dbScript index | Out-Host
    if ($LASTEXITCODE -eq 0) { Say 'The search is ready.' }
    else { Say 'The search could not be built now. Setup carries on; the tool builds it before the first search.' }
  } catch {
    Say "The search could not be built now ($($_.Exception.Message)). Setup carries on; the tool builds it before the first search."
  }
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

# MarkText opens a markdown file as a formatted page that can be edited like a document.
function Find-MarkText {
  $candidates = @(
    (Join-Path $env:LOCALAPPDATA 'Programs\marktext\marktext.exe'),
    (Join-Path $env:LOCALAPPDATA 'Programs\MarkText\MarkText.exe')
  )
  if ($env:ProgramFiles) { $candidates += (Join-Path $env:ProgramFiles 'marktext\marktext.exe') }
  foreach ($c in $candidates) { if (Test-Path -LiteralPath $c) { return $c } }
  $keys = @(
    'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*',
    'HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*',
    'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*'
  )
  foreach ($k in $keys) {
    $hit = Get-ItemProperty $k -ErrorAction SilentlyContinue |
      Where-Object { $_.DisplayName -like 'marktext*' } | Select-Object -First 1
    if (-not $hit) { continue }
    if ($hit.DisplayIcon) {
      $exe = ($hit.DisplayIcon -split ',')[0].Trim('"')
      if (Test-Path -LiteralPath $exe) { return $exe }
    }
    if ($hit.InstallLocation) {
      $exe = Join-Path $hit.InstallLocation 'marktext.exe'
      if (Test-Path -LiteralPath $exe) { return $exe }
    }
  }
  return $null
}

# The newest MarkText release, from GitHub's latest-release address (it never points at a
# test release); the tested version is the backup.
function Get-MarkTextVersion {
  try {
    $req = [Net.HttpWebRequest]::Create('https://github.com/marktext/marktext/releases/latest')
    $req.AllowAutoRedirect = $false
    $req.Method = 'HEAD'
    $resp = $req.GetResponse()
    $loc = $resp.Headers['Location']
    $resp.Close()
    if ($loc -match '/tag/v([0-9.]+)$') { return $Matches[1] }
  } catch { }
  return $MarkTextTested
}

# MarkText's own installer, run silently for this user only (no admin prompt). Throws on any
# failure; the caller only warns.
function Install-MarkText {
  $arch = 'x64'
  if ($env:PROCESSOR_ARCHITECTURE -eq 'ARM64' -or $env:PROCESSOR_ARCHITEW6432 -eq 'ARM64') { $arch = 'arm64' }
  $versions = @(Get-MarkTextVersion)
  if ($versions[0] -ne $MarkTextTested) { $versions += $MarkTextTested }
  $file = $null
  foreach ($v in $versions) {
    $url = "https://github.com/marktext/marktext/releases/download/v$v/marktext-win-$arch-$v-setup.exe"
    $file = Join-Path $env:TEMP "marktext-win-$arch-$v-setup.exe"
    Say "Downloading MarkText from $url."
    try { Invoke-WebRequest -Uri $url -OutFile $file -UseBasicParsing; break }
    catch {
      Remove-Item -LiteralPath $file -ErrorAction SilentlyContinue
      $file = $null
      Say "That download did not work: $($_.Exception.Message)"
    }
  }
  if (-not $file) { throw 'the MarkText download did not work' }
  Say 'Running the MarkText installer.'
  try { Start-Process -FilePath $file -ArgumentList '/S', '/currentuser' -Wait }
  finally { Remove-Item -LiteralPath $file -ErrorAction SilentlyContinue }
  $exe = Find-MarkText
  if (-not $exe) { throw 'the installer ran, but MarkText cannot be found afterwards' }
  return $exe
}

# Obsidian keeps its list of vaults in obsidian.json. Add Agent Memory, mark it as the
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

# A new Agent Memory folder gets a Daily folder, Obsidian settings and one note that says
# what it is for. A folder that already exists is used as it is.
function New-MemoryVault {
  if (Test-Path $Vault) { Say "Using the Agent Memory folder that is already there: $Vault"; return }
  New-Item -ItemType Directory -Path (Join-Path $Vault 'Daily') -Force | Out-Null
  New-Item -ItemType Directory -Path (Join-Path $Vault '.obsidian') -Force | Out-Null
  $utf8 = New-Object Text.UTF8Encoding $false
  [IO.File]::WriteAllText((Join-Path $Vault '.obsidian\app.json'), '{"alwaysUpdateLinks":true}', $utf8)
  [IO.File]::WriteAllText((Join-Path $Vault '.obsidian\daily-notes.json'), '{"folder":"Daily","format":"YYYY-MM-DD"}', $utf8)
  $note = "# Agent Memory`n`nThis folder is your AI tool's memory. It stays nearly empty until round 3 of the workshop, when AGENTS.md tells the tool to keep notes here.`n`n- [[How to keep notes]] holds the rules the tool follows when it reads and writes notes here. The tool reads it at the start of every session. Change a rule there and the tool follows the new one.`n- One note per lesson, named YYYY-MM-DD-short-title.md, saved when you correct it or settle something.`n- Daily/ holds one note per day, with a line for each task it finished.`n`nIt sits on your Desktop, outside any one project, so every project you point at it reads the same notes. You can read, search and edit them here; the tool reads your edits too.`n"
  [IO.File]::WriteAllText((Join-Path $Vault 'Start here.md'), $note, $utf8)
  Say "Made the Agent Memory folder: $Vault"
}

# The rules note goes into a new folder, and into an existing one that does not have it yet.
# A rules note that is already there is never replaced: the person may have changed it.
function Add-NoteRules {
  if (-not (Test-Path -LiteralPath $Rules)) { return }
  $dest = Join-Path $Vault 'How to keep notes.md'
  if (Test-Path -LiteralPath $dest) { return }
  Copy-Item -LiteralPath $Rules -Destination $dest
  Say 'Added the note-taking rules to the Agent Memory folder: How to keep notes.md'
}

# The AGENTS.md template that round 3 fills in names the folder by its full path.
function Set-TemplatePath {
  $tpl = Join-Path $Here 'extras\AGENTS.starter.md'
  if (-not (Test-Path $tpl)) { return }
  $text = [IO.File]::ReadAllText($tpl)
  if ($text.Contains($Placeholder)) {
    [IO.File]::WriteAllText($tpl, $text.Replace($Placeholder, $Vault), (New-Object Text.UTF8Encoding $false))
    Say 'Wrote the Agent Memory path into extras\AGENTS.starter.md.'
  }
}

# Claude Code asks before it reads or writes outside the folder it runs in. Adding the
# Agent Memory folder to this folder's own Claude Code settings saves those questions.
function Grant-ClaudeAccess {
  $file = Join-Path $Here '.claude\settings.local.json'
  $data = $null
  if (Test-Path $file) {
    try { $data = Get-Content $file -Raw -Encoding UTF8 | ConvertFrom-Json } catch { Say 'Claude Code settings in this folder could not be read, so they were left alone.'; return }
  }
  if (-not $data) { $data = New-Object psobject }
  if (-not ($data.PSObject.Properties.Name -contains 'permissions') -or -not $data.permissions) {
    $data | Add-Member -NotePropertyName permissions -NotePropertyValue (New-Object psobject) -Force
  }
  $dirs = @()
  if ($data.permissions.PSObject.Properties.Name -contains 'additionalDirectories') { $dirs = @($data.permissions.additionalDirectories) }
  if ($dirs -contains $Vault) { return }
  $data.permissions | Add-Member -NotePropertyName additionalDirectories -NotePropertyValue (@($dirs) + $Vault) -Force
  New-Item -ItemType Directory -Path (Split-Path $file -Parent) -Force | Out-Null
  [IO.File]::WriteAllText($file, ($data | ConvertTo-Json -Depth 20), (New-Object Text.UTF8Encoding $false))
  Say 'Claude Code in this folder can now read and write the Agent Memory folder.'
}

try {
  Say "Setting up $Here"
  $realConfig = -not $ConfigPath
  if ($realConfig) { $ConfigPath = Join-Path $env:APPDATA 'obsidian\obsidian.json' }

  if ($ResolveOnly) { Get-InstallerUrl; exit 0 }

  $git = Find-Git
  if ($git) { Say "Git is already installed: $git" }
  else { $git = Install-Git; Say "Git is installed: $git. A new terminal finds it as git; this one needs the full path." }

  New-MemoryVault
  Add-NoteRules
  Set-TemplatePath
  Grant-ClaudeAccess

  $uv = Find-Uv
  if ($uv) { Say "uv is already installed: $uv" }
  else { $uv = Install-Uv; Say "uv is installed: $uv. A new terminal finds it as uv; this one needs the full path." }
  if (-not $SkipPipeline) { Prepare-Pipeline $uv }
  if (-not $SkipDatabase) { Prepare-Database $uv }

  # Obsidian reads its vault list only when it starts, so close it; it saves notes as you type.
  if ($realConfig -and (Get-Process -Name Obsidian -ErrorAction SilentlyContinue)) {
    Say 'Closing Obsidian so it picks up the Agent Memory folder when it opens again.'
    Get-Process -Name Obsidian -ErrorAction SilentlyContinue | ForEach-Object { [void]$_.CloseMainWindow() }
    Start-Sleep -Seconds 3
    Get-Process -Name Obsidian -ErrorAction SilentlyContinue | Stop-Process -Force
  }

  # The vault goes in first, so an installer that opens Obsidian right away opens Agent Memory.
  Register-Vault $ConfigPath
  Say "Added the Agent Memory folder to Obsidian's vault list."

  $exe = Find-Obsidian
  if ($exe) { Say "Obsidian is already installed: $exe" }
  else { $exe = Install-Obsidian; Say "Obsidian is installed: $exe" }

  # MarkText is for reading and editing markdown files. Setup carries on without it.
  $markText = $null
  if (-not $SkipMarkText) {
    $markText = Find-MarkText
    if ($markText) { Say "MarkText is already installed: $markText" }
    else {
      try { $markText = Install-MarkText; Say "MarkText is installed: $markText" }
      catch { Say "MarkText could not be installed ($($_.Exception.Message)). Setup carries on without it; running this script again tries once more." }
    }
  }

  if (-not $NoLaunch) {
    Start-Sleep -Seconds 1
    if (-not (Get-Process -Name Obsidian -ErrorAction SilentlyContinue)) { Start-Process -FilePath $exe }
    Say 'Obsidian is opening on the Agent Memory folder.'
  }
  Say "Done. Git, uv and Obsidian are ready, and Obsidian is open on $Vault."
  exit 0
}
catch {
  Say "Failed: $($_.Exception.Message)"
  Say 'You can still install Obsidian from obsidian.md, then choose Open folder as vault and pick the Agent Memory folder on your Desktop.'
  exit 1
}
