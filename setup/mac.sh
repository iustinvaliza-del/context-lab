#!/usr/bin/env bash
# Sets up the workshop folder on a Mac: installs git and Obsidian if they are missing,
# adds this folder to Obsidian as a vault, and opens it. Safe to run more than once.
# Run it from the workshop folder:  bash setup/mac.sh
# For testing: CL_CONFIG=<file> writes the vault list there instead of Obsidian's
# own file, CL_NO_LAUNCH=1 skips opening Obsidian, CL_RESOLVE_ONLY=1 prints the
# installer address and stops.
set -euo pipefail

say() { printf '[setup] %s\n' "$*"; }
fail() {
  say "Failed: $*"
  say "You can still install Obsidian from obsidian.md, then choose Open folder as vault and pick this folder."
  exit 1
}

VAULT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
CONFIG="${CL_CONFIG:-}"
REAL_CONFIG=1
if [[ -n "$CONFIG" ]]; then REAL_CONFIG=0; else CONFIG="$HOME/Library/Application Support/obsidian/obsidian.json"; fi

find_obsidian() {
  local app
  for app in "/Applications/Obsidian.app" "$HOME/Applications/Obsidian.app"; do
    if [[ -d "$app" ]]; then printf '%s\n' "$app"; return 0; fi
  done
  return 1
}

# The download page links the current installer; the latest-release redirect is the backup.
installer_url() {
  local url ver
  # A failed page fetch is expected on some networks; the redirect below is the backup.
  url="$(curl -fsSL https://obsidian.md/download 2>/dev/null \
    | grep -Eo 'https://github\.com/obsidianmd/obsidian-releases/releases/download/v[0-9.]+/Obsidian-[0-9.]+\.dmg' \
    | head -n 1 || true)"
  if [[ -n "$url" ]]; then printf '%s\n' "$url"; return 0; fi
  ver="$(curl -fsSLI -o /dev/null -w '%{url_effective}' https://github.com/obsidianmd/obsidian-releases/releases/latest \
    | sed -n 's#.*/tag/v\([0-9.]*\)$#\1#p' || true)"
  [[ -n "$ver" ]] || return 1
  printf 'https://github.com/obsidianmd/obsidian-releases/releases/download/v%s/Obsidian-%s.dmg\n' "$ver" "$ver"
}

install_obsidian() {
  if command -v brew >/dev/null 2>&1; then
    say "Installing Obsidian with Homebrew. This is a large download and can take a few minutes."
    if brew install --cask obsidian && find_obsidian >/dev/null; then return 0; fi
    say "Homebrew did not finish the install, so downloading Obsidian directly."
  fi
  local url tmp mnt dest
  url="$(installer_url)" || fail "could not find the address of the Obsidian download."
  tmp="$(mktemp -d)"
  mnt="$tmp/mnt"
  mkdir -p "$mnt"
  say "Downloading $url. This can take a few minutes."
  curl -fL --progress-bar -o "$tmp/Obsidian.dmg" "$url" || fail "the download did not finish."
  hdiutil attach -nobrowse -quiet -mountpoint "$mnt" "$tmp/Obsidian.dmg" || fail "could not open the downloaded file."
  dest="/Applications"
  if [[ ! -w "$dest" ]]; then dest="$HOME/Applications"; mkdir -p "$dest"; fi
  say "Copying Obsidian to $dest."
  if ! cp -R "$mnt/Obsidian.app" "$dest/"; then
    hdiutil detach -quiet "$mnt" || true
    fail "could not copy Obsidian to $dest."
  fi
  hdiutil detach -quiet "$mnt" || true
  rm -rf "$tmp"
  find_obsidian >/dev/null || fail "Obsidian was copied, but it cannot be found afterwards."
}

# Obsidian keeps its list of vaults in obsidian.json. Add this folder, mark it as the
# one to open, and keep every other vault in the list. macOS has no JSON tool built
# in, so this runs as JavaScript through osascript, which every Mac has.
register_vault() {
  local js
  mkdir -p "$(dirname "$CONFIG")"
  js="$(mktemp)"
  cat > "$js" <<'JXA'
ObjC.import('Foundation');
function run(argv) {
  var cfg = argv[0], vault = argv[1];
  var fm = $.NSFileManager.defaultManager;
  var data = {};
  if (fm.fileExistsAtPath(cfg)) {
    var raw = $.NSString.stringWithContentsOfFileEncodingError(cfg, $.NSUTF8StringEncoding, null);
    try { data = JSON.parse(ObjC.unwrap(raw)); }
    catch (e) { fm.removeItemAtPathError(cfg + '.bak', null); fm.copyItemAtPathToPathError(cfg, cfg + '.bak', null); data = {}; }
  }
  if (!data || typeof data !== 'object' || Array.isArray(data)) data = {};
  if (!data.vaults || typeof data.vaults !== 'object') data.vaults = {};
  var id = null;
  Object.keys(data.vaults).forEach(function (k) {
    var v = data.vaults[k];
    if (!v || typeof v !== 'object') return;
    if (typeof v.path === 'string' && v.path.replace(/\/+$/, '') === vault) id = k;
    delete v.open;
  });
  if (!id) {
    id = '';
    for (var i = 0; i < 16; i++) id += Math.floor(Math.random() * 16).toString(16);
    data.vaults[id] = { path: vault, ts: Date.now() };
  }
  data.vaults[id].open = true;
  var ok = $(JSON.stringify(data)).writeToFileAtomicallyEncodingError(cfg, true, $.NSUTF8StringEncoding, null);
  if (!ok) throw new Error('could not write ' + cfg);
  return id;
}
JXA
  osascript -l JavaScript "$js" "$CONFIG" "$VAULT" >/dev/null
  rm -f "$js"
}

say "Setting up $VAULT"

if [[ "${CL_RESOLVE_ONLY:-0}" == 1 ]]; then
  installer_url || fail "could not find the address of the Obsidian download."
  exit 0
fi

# Git comes with Apple's command line tools. macOS installs them only through its own window,
# which asks for one click on Install; the rest of the setup does not need git, so carry on.
if xcode-select -p >/dev/null 2>&1; then
  say "Git is already installed."
else
  xcode-select --install >/dev/null 2>&1 || true
  say "A window from Apple asks to install the command line developer tools, which include git. Click Install: it is the only click this setup needs."
fi

# Obsidian reads its vault list only when it starts, so quit it; it saves notes as you type.
if [[ "$REAL_CONFIG" == 1 ]] && pgrep -x Obsidian >/dev/null; then
  say "Closing Obsidian so it picks up this folder when it opens again."
  osascript -e 'quit app "Obsidian"' >/dev/null 2>&1 || true
  for _ in 1 2 3 4 5 6; do pgrep -x Obsidian >/dev/null || break; sleep 1; done
  pkill -x Obsidian 2>/dev/null || true
fi

# The vault goes in first, so Obsidian opens this folder the first time it starts.
register_vault || fail "could not add this folder to Obsidian's vault list."
say "Added this folder to Obsidian's vault list."

if APP="$(find_obsidian)"; then
  say "Obsidian is already installed: $APP"
else
  install_obsidian
  APP="$(find_obsidian)"
  say "Obsidian is installed: $APP"
fi

if [[ "${CL_NO_LAUNCH:-0}" != 1 ]]; then
  open "$APP"
  say "Obsidian is opening on this folder."
fi
say "Done. Obsidian is open on this folder."
