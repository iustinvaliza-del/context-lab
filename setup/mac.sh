#!/usr/bin/env bash
# Sets up the workshop folder on a Mac: installs git, uv (which brings Python), Obsidian and
# MarkText if they are missing, gets the case pipeline's packages ready, makes an Agent Memory
# folder on the Desktop with the note-taking rules in it, adds it to Obsidian as a vault, and opens it.
# It also writes that folder's path into the AGENTS.md template, lets Claude Code read and
# write there, and builds the search over the person's files in database/. Safe to run more than once.
# Run it from the workshop folder:  bash setup/mac.sh
# For testing: CL_CONFIG=<file> writes the vault list there instead of Obsidian's
# own file, CL_MEMORY=<folder> makes the Agent Memory folder there instead of on the
# Desktop, CL_NO_LAUNCH=1 skips opening Obsidian, CL_RESOLVE_ONLY=1 prints the
# installer address and stops, CL_SKIP_PIPELINE=1 skips downloading the pipeline's packages,
# CL_SKIP_DATABASE=1 skips building the search in database/.
set -euo pipefail

say() { printf '[setup] %s\n' "$*"; }
fail() {
  say "Failed: $*"
  say "You can still install Obsidian from obsidian.md, then choose Open folder as vault and pick the Agent Memory folder on your Desktop."
  exit 1
}

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
# The vault is the Agent Memory folder on the Desktop, outside the workshop folder, so every
# project can read the same notes.
VAULT="${CL_MEMORY:-$HOME/Desktop/Agent Memory}"
VAULT="${VAULT%/}"
PLACEHOLDER='<full path of my Agent Memory folder>'
# The note-taking rules that every new or existing Agent Memory folder gets a copy of.
RULES="$HERE/setup/vault/How to keep notes.md"
# The MarkText version this setup was tested with, used when the newest one cannot be found.
MARKTEXT_TESTED=0.23.0
CONFIG="${CL_CONFIG:-}"
REAL_CONFIG=1
if [[ -n "$CONFIG" ]]; then REAL_CONFIG=0; else CONFIG="$HOME/Library/Application Support/obsidian/obsidian.json"; fi

find_uv() {
  if command -v uv >/dev/null 2>&1; then command -v uv; return 0; fi
  if [[ -x "$HOME/.local/bin/uv" ]]; then printf '%s\n' "$HOME/.local/bin/uv"; return 0; fi
  return 1
}

# uv runs the case pipeline's Python scripts and installs Python and their packages itself,
# for this user only.
install_uv() {
  say "Installing uv, which runs the case pipeline and brings its own Python."
  curl -LsSf https://astral.sh/uv/install.sh | sh || say "The uv installer stopped."
  find_uv >/dev/null || fail "uv could not be installed."
}

# The first run of each script downloads Python and its packages; doing it now means the case
# pipeline starts at once in the workshop. A failure here is not fatal: the first real run retries.
prepare_pipeline() {
  local uv="$1" dir="$HERE/pipeline"
  [[ -d "$dir" ]] || return 0
  say "Getting the case pipeline ready (Python and its packages). This can take a few minutes."
  "$uv" run "$dir/blackboard.py" check || say "The browser check did not pass; the first Blackboard run will try again."
  "$uv" run "$dir/read_case.py" --help >/dev/null 2>&1 || true
  "$uv" run "$dir/check_workbook.py" >/dev/null 2>&1 || true
  say "The case pipeline is ready."
}

# The database in database/ keeps a search over the person's files and notes. It runs after
# the Agent Memory steps, so the search includes that folder. Building it now means the first
# search answers at once. A failure here is not fatal: the tool builds it before the first search.
prepare_database() {
  local uv="$1" script="$HERE/database/db.py"
  [[ -f "$script" ]] || return 0
  say "Building the search over your files and notes (IESE, sources, outputs, Agent Memory)."
  if "$uv" run "$script" index; then
    say "The search is ready."
  else
    say "The search could not be built now. Setup carries on; the tool builds it before the first search."
  fi
}

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

# MarkText opens a markdown file as a formatted page that can be edited like a document.
find_marktext() {
  local app
  for app in "/Applications/MarkText.app" "$HOME/Applications/MarkText.app"; do
    if [[ -d "$app" ]]; then printf '%s\n' "$app"; return 0; fi
  done
  return 1
}

# The newest MarkText release, from GitHub's latest-release address (it never points at a
# test release); the tested version is the backup.
marktext_version() {
  local ver
  ver="$(curl -fsSLI -o /dev/null -w '%{url_effective}' https://github.com/marktext/marktext/releases/latest 2>/dev/null \
    | sed -n 's#.*/tag/v\([0-9.]*\)$#\1#p' || true)"
  printf '%s\n' "${ver:-$MARKTEXT_TESTED}"
}

# Downloads MarkText with curl, not Homebrew: macOS then does not mark the file as downloaded,
# so MarkText opens without a warning even though it is not signed by Apple. It is copied under
# a .partial name and renamed only when the copy is complete, so a copy cut short never looks
# installed. Returns 1 on any failure; the caller only warns.
install_marktext() {
  local arch=x64 ver url tmp mnt dest src="" app
  if [[ "$(sysctl -n hw.optional.arm64 2>/dev/null || true)" == 1 ]]; then arch=arm64; fi
  ver="$(marktext_version)"
  tmp="$(mktemp -d)" || return 1
  url="https://github.com/marktext/marktext/releases/download/v$ver/marktext-mac-$arch-$ver.dmg"
  say "Downloading MarkText from $url."
  if ! curl -fL --progress-bar -o "$tmp/MarkText.dmg" "$url"; then
    if [[ "$ver" == "$MARKTEXT_TESTED" ]]; then rm -rf "$tmp"; return 1; fi
    url="https://github.com/marktext/marktext/releases/download/v$MARKTEXT_TESTED/marktext-mac-$arch-$MARKTEXT_TESTED.dmg"
    say "Trying MarkText $MARKTEXT_TESTED instead: $url."
    curl -fL --progress-bar -o "$tmp/MarkText.dmg" "$url" || { rm -rf "$tmp"; return 1; }
  fi
  mnt="$tmp/mnt"
  mkdir -p "$mnt" || { rm -rf "$tmp"; return 1; }
  hdiutil attach -nobrowse -quiet -mountpoint "$mnt" "$tmp/MarkText.dmg" || { rm -rf "$tmp"; return 1; }
  for app in "$mnt"/*.app; do
    if [[ -d "$app" ]]; then src="$app"; break; fi
  done
  dest="/Applications"
  if [[ ! -w "$dest" ]]; then dest="$HOME/Applications"; mkdir -p "$dest" || true; fi
  rm -rf "$dest/MarkText.app.partial"
  say "Copying MarkText to $dest."
  if [[ -z "$src" ]] || ! cp -R "$src" "$dest/MarkText.app.partial" || ! mv "$dest/MarkText.app.partial" "$dest/MarkText.app"; then
    rm -rf "$dest/MarkText.app.partial"
    hdiutil detach -quiet "$mnt" || true
    rm -rf "$tmp"
    return 1
  fi
  hdiutil detach -quiet "$mnt" || true
  rm -rf "$tmp"
  find_marktext >/dev/null
}

# A new Agent Memory folder gets a Daily folder, Obsidian settings and one note that says
# what it is for. A folder that already exists is used as it is.
new_memory_vault() {
  if [[ -e "$VAULT" ]]; then say "Using the Agent Memory folder that is already there: $VAULT"; return 0; fi
  mkdir -p "$VAULT/Daily" "$VAULT/.obsidian"
  printf '%s' '{"alwaysUpdateLinks":true}' > "$VAULT/.obsidian/app.json"
  printf '%s' '{"folder":"Daily","format":"YYYY-MM-DD"}' > "$VAULT/.obsidian/daily-notes.json"
  cat > "$VAULT/Start here.md" <<'NOTE'
# Agent Memory

This folder is your AI tool's memory. It stays nearly empty until round 3 of the workshop, when AGENTS.md tells the tool to keep notes here.

- [[How to keep notes]] holds the rules the tool follows when it reads and writes notes here. The tool reads it at the start of every session. Change a rule there and the tool follows the new one.
- One note per lesson, named YYYY-MM-DD-short-title.md, saved when you correct it or settle something.
- Daily/ holds one note per day, with a line for each task it finished.

It sits on your Desktop, outside any one project, so every project you point at it reads the same notes. You can read, search and edit them here; the tool reads your edits too.
NOTE
  say "Made the Agent Memory folder: $VAULT"
}

# The rules note goes into a new folder, and into an existing one that does not have it yet.
# A rules note that is already there is never replaced: the person may have changed it.
add_note_rules() {
  [[ -f "$RULES" ]] || return 0
  [[ -e "$VAULT/How to keep notes.md" ]] && return 0
  cp "$RULES" "$VAULT/How to keep notes.md"
  say "Added the note-taking rules to the Agent Memory folder: How to keep notes.md"
}

# The AGENTS.md template that round 3 fills in names the folder by its full path.
set_template_path() {
  local tpl="$HERE/extras/AGENTS.starter.md" text
  [[ -f "$tpl" ]] || return 0
  text="$(cat "$tpl"; printf x)"
  text="${text%x}"
  [[ "$text" == *"$PLACEHOLDER"* ]] || return 0
  # Split around the placeholder: macOS bash 3.2 keeps the quotes of a quoted ${x//a/"b"} replacement.
  local before="${text%%"$PLACEHOLDER"*}" after="${text#*"$PLACEHOLDER"}"
  printf '%s' "$before$VAULT$after" > "$tpl"
  say "Wrote the Agent Memory path into extras/AGENTS.starter.md."
}

# Claude Code asks before it reads or writes outside the folder it runs in. Adding the
# Agent Memory folder to this folder's own Claude Code settings saves those questions.
grant_claude_access() {
  local js out
  mkdir -p "$HERE/.claude"
  js="$(mktemp)"
  cat > "$js" <<'JXA'
ObjC.import('Foundation');
function run(argv) {
  var file = argv[0], dir = argv[1];
  var fm = $.NSFileManager.defaultManager;
  var data = {};
  if (fm.fileExistsAtPath(file)) {
    var raw = $.NSString.stringWithContentsOfFileEncodingError(file, $.NSUTF8StringEncoding, null);
    try { data = JSON.parse(ObjC.unwrap(raw)); } catch (e) { return 'unreadable'; }
  }
  if (!data || typeof data !== 'object' || Array.isArray(data)) return 'unreadable';
  if (!data.permissions || typeof data.permissions !== 'object') data.permissions = {};
  var dirs = Array.isArray(data.permissions.additionalDirectories) ? data.permissions.additionalDirectories : [];
  if (dirs.indexOf(dir) >= 0) return 'same';
  dirs.push(dir);
  data.permissions.additionalDirectories = dirs;
  var ok = $(JSON.stringify(data, null, 2)).writeToFileAtomicallyEncodingError(file, true, $.NSUTF8StringEncoding, null);
  if (!ok) throw new Error('could not write ' + file);
  return 'added';
}
JXA
  out="$(osascript -l JavaScript "$js" "$HERE/.claude/settings.local.json" "$VAULT")" || out="failed"
  rm -f "$js"
  case "$out" in
    added) say "Claude Code in this folder can now read and write the Agent Memory folder." ;;
    same) ;;
    *) say "Claude Code settings in this folder could not be read, so they were left alone." ;;
  esac
}

# Obsidian keeps its list of vaults in obsidian.json. Add Agent Memory, mark it as the
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

say "Setting up $HERE"

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

if UV="$(find_uv)"; then
  say "uv is already installed: $UV"
else
  install_uv
  UV="$(find_uv)"
  say "uv is installed: $UV. A new terminal finds it as uv; this one needs the full path."
fi
if [[ "${CL_SKIP_PIPELINE:-0}" != 1 ]]; then prepare_pipeline "$UV"; fi

new_memory_vault
add_note_rules
set_template_path
grant_claude_access
if [[ "${CL_SKIP_DATABASE:-0}" != 1 ]]; then prepare_database "$UV"; fi

# Obsidian reads its vault list only when it starts, so quit it; it saves notes as you type.
if [[ "$REAL_CONFIG" == 1 ]] && pgrep -x Obsidian >/dev/null; then
  say "Closing Obsidian so it picks up the Agent Memory folder when it opens again."
  osascript -e 'quit app "Obsidian"' >/dev/null 2>&1 || true
  for _ in 1 2 3 4 5 6; do pgrep -x Obsidian >/dev/null || break; sleep 1; done
  pkill -x Obsidian 2>/dev/null || true
fi

# The vault goes in first, so Obsidian opens Agent Memory the first time it starts.
register_vault || fail "could not add the Agent Memory folder to Obsidian's vault list."
say "Added the Agent Memory folder to Obsidian's vault list."

if APP="$(find_obsidian)"; then
  say "Obsidian is already installed: $APP"
else
  install_obsidian
  APP="$(find_obsidian)"
  say "Obsidian is installed: $APP"
fi

# MarkText is for reading and editing markdown files. Setup carries on without it.
if MD_APP="$(find_marktext)"; then
  say "MarkText is already installed: $MD_APP"
elif install_marktext && MD_APP="$(find_marktext)"; then
  say "MarkText is installed: $MD_APP"
else
  say "MarkText could not be installed. Setup carries on without it; running this script again tries once more."
fi

if [[ "${CL_NO_LAUNCH:-0}" != 1 ]]; then
  open "$APP"
  say "Obsidian is opening on the Agent Memory folder."
fi
say "Done. Obsidian is open on $VAULT."
