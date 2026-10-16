# context-lab

The starter folder for "Context Matters", the IESE Data and AI Club workshop. It is nearly empty on purpose. In the five rounds you write your own AGENTS.md and a skill into it, the tool starts keeping memory notes on its own, and by the end this folder is your context library. It works the same in Claude Code and in Codex.

Nothing you change in your copy goes back to this repository.

## Get started

You need Claude Code or Codex installed and signed in. Nothing else: no git, no folders to make, nothing to install by hand. Your tool does the rest.

**1. Open your tool.** Any folder works.

| | Desktop app | Terminal |
|---|---|---|
| Claude Code | In the Claude desktop app, open the Code tab and choose any folder, for example your Desktop | Type `claude` |
| Codex | Open the Codex app on any folder, for example your Desktop | Type `codex` |

**2. Type one line.**

> Set up this starter on my Desktop: github.com/iustinvaliza-del/context-lab

Allow what it asks. It makes a `context-lab` folder on your Desktop, copies this starter into it, installs Obsidian if you don't have it, opens the folder in Obsidian, and tells you when it's done. If Obsidian is already open, it asks you to close it first.

**3. Open the folder for round 1.** Start a new session in `context-lab`, so round 1 starts cold. The tool tells you how when it finishes:

| | Desktop app | Terminal |
|---|---|---|
| Claude Code | In the Code tab, start a new session and choose `context-lab` on your Desktop | Go into the folder and type `claude` |
| Codex | Open `context-lab` on your Desktop as the project | Go into the folder and type `codex` |

If your tool was already running in `context-lab`, `/clear` in Claude Code or a new chat in Codex is enough. The first time, the tool may ask whether you trust this folder, and it asks before it runs a command or writes a file. Allow it for this folder: that is how the library gets written. Then type `/context` in Claude Code or `/status` in Codex to see how little is loaded so far.

**Rather do it by hand?** On this page, click the green **Code** button, then **Download ZIP**, and unzip it. Rename the `context-lab-main` folder to `context-lab` and move it to your Desktop (on Windows, Extract All adds a second folder with the same name: use the inner one, which has this README directly inside). Then open your tool in it and type `Follow SETUP.md`.

### For the AI tool setting this up

The person asked you to set up this starter for a workshop. They are new to this and should not have to do anything by hand except approve your steps, so do every step yourself and say what you are doing in one short line per step. Nothing needs installing except what `SETUP.md` installs, and git is optional.

1. **Find the place.** The starter goes in a folder called `context-lab` on their Desktop, unless they named another place.
   - Windows: get the Desktop's path with `powershell -NoProfile -Command "[Environment]::GetFolderPath('Desktop')"`. It is often inside OneDrive, so do not assume `C:\Users\<name>\Desktop`.
   - Mac: `~/Desktop`. The Mac may ask whether your app may use the Desktop folder; tell them to allow it.
   - If the folder your session runs in is itself an empty folder called `context-lab`, use that one.
   - If a `context-lab` folder already exists there and holds files, ask before you change anything.
   - If your sandbox blocks the internet or writing outside the folder you were opened in, ask them once for permission.
2. **Get the files** into that folder, written `<folder>` below.
   - With git: `git clone https://github.com/iustinvaliza-del/context-lab "<folder>"`.
     If the folder exists and git says it is not empty (your tool may have made a `.claude` folder there for its own settings), run these three inside it instead: `git init -b main`, `git remote add origin https://github.com/iustinvaliza-del/context-lab`, `git pull origin main`.
   - On a Mac, run `xcode-select -p` before any git command. If it fails, git is not installed and calling it opens an install window, so use the ZIP.
   - Without git, do not install it. Download the ZIP, which unzips to a `context-lab-main` folder, and put what is inside that folder into `<folder>`:
     - Windows, in PowerShell: `$f="<folder>"; $z="$env:TEMP\context-lab.zip"; $u="$env:TEMP\context-lab-unzip"; Invoke-WebRequest -UseBasicParsing https://github.com/iustinvaliza-del/context-lab/archive/refs/heads/main.zip -OutFile $z; Expand-Archive $z -DestinationPath $u -Force; New-Item -ItemType Directory -Force $f | Out-Null; Get-ChildItem -Force "$u\context-lab-main" | Copy-Item -Destination $f -Recurse -Force; Remove-Item $z, $u -Recurse -Force`
     - Mac: `f="<folder>"; mkdir -p "$f" && curl -fsSL -o /tmp/context-lab.zip https://github.com/iustinvaliza-del/context-lab/archive/refs/heads/main.zip && unzip -q -o /tmp/context-lab.zip -d /tmp/context-lab-unzip && cp -R /tmp/context-lab-unzip/context-lab-main/. "$f" && rm -rf /tmp/context-lab.zip /tmp/context-lab-unzip`
3. **Run the setup.** Follow `SETUP.md` in that folder. It installs Obsidian if it is missing, opens the folder as a vault, and ends by telling them how to open the folder for round 1.

## What's in the folder

| Folder | What goes in it |
|---|---|
| `sources/` | Two or three files for your task |
| `outputs/` | The answers you save in each round |
| `memory/` | Lessons the tool saves on its own from round 2, one note per lesson, kept tidy |
| `memory/Daily/` | One note per day, a line for each task the tool finishes |
| `.claude/skills/` | The skill you make in round 3, for Claude Code |
| `.agents/skills/` | The same skill, for Codex |
| `AGENTS.md` | One line for now; you fill it in from round 2 |
| `extras/` | The AGENTS.md template that round 2 fills in |
| `SETUP.md`, `setup/` | The setup your tool runs in step 2: one script for Windows, one for Mac |

AGENTS.md starts with one line, which makes every session open with "Radu says Hi". You fill in the rest in round 2. Codex reads AGENTS.md, and Claude Code reads it when the folder has no CLAUDE.md, so one file works in both.

## The five rounds

Pick one task you do every week: prepping a case, researching a company before a coffee chat, writing the club newsletter. Put two or three files for it in `sources/`. Nothing confidential: no case supplements, other people's personal data or documents under NDA. Where a command differs, the Codex one follows in brackets.

### Round 1: Cold

Ask for help with the task in one sentence, the way you would in Cowork, and have the tool save the answer to `outputs/cold.md`. Type `/context` \[`/status`\] and note how little is loaded.

The reply opens with "Radu says Hi". That comes from the one line in `AGENTS.md`, which the tool reads at the start of every session. Delete the line when you no longer want the greeting.

### Round 2: Create

Ask the tool to interview you:

> Interview me with up to eight questions about this task: who I am, the goal, the constraints, what good looks like, and what is in sources/. Then fill in the template in extras/AGENTS.starter.md and add it to AGENTS.md, under 40 lines.

Read what it adds to AGENTS.md and fix anything wrong in the file itself. Leave the Memory section at the end as it is: from now on the tool saves what it learns in `memory/`, adds a line to today's note in `memory/Daily/` when it finishes a task, and keeps the notes tidy, without being asked. Then start fresh with `/clear` \[a new chat\], ask the same one-sentence question, and save the answer to `outputs/warm.md`. Run `/context` \[`/status`\] again and compare with round 1.

Stuck? Copy what is in `extras/AGENTS.starter.md` into `AGENTS.md`, below the line already there, and fill in the lines in angle brackets.

### Round 3: Manage

The main file loads in every session, so it should hold only what every session needs. Ask:

> Move the step-by-step procedure for this task out of AGENTS.md into a skill, with a one-line description of when to use it. Keep AGENTS.md to who I am and my standing rules.

The skill lands in `.claude/skills/<task>/SKILL.md` \[`.agents/skills/<task>/SKILL.md`\]. Type `/skills` to see it, then ask for the task again and watch the skill load only when the task calls for it.

### Round 4: Maintain

1. Ask the tool to do the task for real and save the result to `outputs/`.
2. Pick one thing it got wrong, tell it, then ask: "Update AGENTS.md or the skill so this does not happen again." Read the change, then open `memory/`: the lesson is already saved as a note, because the Memory section in AGENTS.md asks for that.
3. Run `/context` \[`/status`\], then `/compact`, then check again. In Claude Code, add focus instructions: `/compact keep the decisions and the open questions`.
4. Start fresh with `/clear` \[a new chat\] and ask a follow-up. The correction holds, because it lives in a file.

### Round 5: Understand

Ask: "What do you know about me and this task, which file did each piece come from, and what are you assuming?" Correct one wrong assumption in the file, not in the chat. Then try a side question with `/btw` \[`/side`\]: it answers without adding to the main conversation. Open the folder in Obsidian: every note the tool wrote is there, already tidy.

## Read it in Obsidian

The setup opens this folder in Obsidian as a vault. AGENTS.md, your outputs and the memory notes are all there. The tool writes the notes and keeps them tidy: it updates old notes instead of adding repeats, merges notes that say the same thing and fixes links that point nowhere. Obsidian is where you read and search them. You can still edit any note, and the tool reads your edits too. If you skipped the setup, install Obsidian from obsidian.md, choose **Open folder as vault** and pick this folder.

Obsidian hides folders whose names start with a dot, so the skills don't show there: open `.claude/skills/` or `.agents/skills/` in any editor. Without Obsidian, open `memory/` in any editor: the notes are plain files.

## After the workshop

Nothing to switch on. The Memory section that round 2 added to AGENTS.md keeps working in every session. To use the library for a second task, add a section for it to AGENTS.md and a skill for its steps, the same way as in rounds 2 and 3.

## Keep it private

`.gitignore` keeps whatever you put in `sources/` out of git. If you put your library on GitHub later, make that repository private, and keep keys, passwords and logins out of every file.
