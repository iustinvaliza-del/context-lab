# context-lab

The starter folder for "Context Matters", the IESE Data and AI Club workshop. It is nearly empty on purpose. In the five rounds you write your own AGENTS.md and a skill into it, the tool starts keeping memory notes on its own, and by the end this folder knows how you prep a case. It works the same in Claude Code and in Codex.

Nothing you change in your copy goes back to this repository.

## Get started

You need Claude Code or Codex installed and signed in. Everything else (git, Obsidian) the tool installs for you. The same steps, with copy buttons, are on the workshop's prompts page: https://claude.ai/artifact/JKZorWv9pp8gantQk7Lpre

**1. Make a folder and open it.** On your Desktop, make a new folder (call it anything), then open it in your tool:

| | Desktop app | Terminal |
|---|---|---|
| Claude Code | In the Claude desktop app, click the Code tab. Set Environment to Local, click Select folder and choose your folder | Go into the folder and type `claude` |
| Codex | Open the Codex app on your folder and start a new chat | Go into the folder and type `codex` |

**2. Paste one line.**

> Set up this starter in this folder: github.com/iustinvaliza-del/context-lab

Allow what it asks. It copies this starter into the folder, installs git and Obsidian if they are missing, opens the folder in Obsidian, and tells you when it's done. You don't touch anything else.

**3. Start round 1.** Type `/clear` in Claude Code, or start a new chat in Codex, so round 1 starts cold. The first time, the tool may ask whether you trust this folder, and it asks before it runs a command or writes a file. Allow it for this folder: that is how it writes your files. Then type `/context` in Claude Code or `/status` in Codex to see what it read: almost nothing so far.

**Rather do it by hand?** On this page, click the green **Code** button, then **Download ZIP**, and unzip it. Move the `context-lab-main` folder to your Desktop (on Windows, Extract All adds a second folder with the same name: use the inner one, which has this README directly inside). Then open your tool in it and type `Follow SETUP.md`.

### For the AI tool setting this up

The person asked you to set up this starter for a workshop. They are new to this and must not have to do anything by hand except allow your steps, so do every step yourself, install what is missing, and say what you are doing in one short line per step.

1. **Find the place.** The starter goes in the folder this session runs in: the folder they made on their Desktop and opened, whatever they called it. Write it `<folder>` below.
   - If that folder holds files other than your tool's own settings folder (`.claude`, `.codex`), ask before you change anything.
   - If the session runs in their home folder, or anywhere that is clearly not a folder they just made, ask them which folder to use.
   - If your sandbox blocks the internet or installing programs, ask them once for permission.
2. **Make sure git is installed.** Run `git --version`; on a Mac run `xcode-select -p` instead, because calling git without it opens an install window.
   - Windows, if git is missing: `winget install --id Git.Git --exact --source winget --scope user --silent --accept-package-agreements --accept-source-agreements --disable-interactivity`. This shell will not find `git` until it restarts, so call it by its full path: `"$env:LOCALAPPDATA\Programs\Git\cmd\git.exe"` (or `C:\Program Files\Git\cmd\git.exe`). Without winget, use the ZIP below and let `SETUP.md` install git.
   - Mac, if git is missing: run `xcode-select --install` and tell them to click Install in the window Apple shows; it is the only click setup needs. Do not wait for it: use the ZIP below for now.
3. **Get the files** into `<folder>`.
   - With git: `git clone https://github.com/iustinvaliza-del/context-lab "<folder>"`.
     If git says the folder is not empty (your tool may have made a `.claude` folder there for its own settings), run these three inside it instead: `git init -b main`, `git remote add origin https://github.com/iustinvaliza-del/context-lab`, `git pull origin main`.
   - With the ZIP, which unzips to a `context-lab-main` folder; put what is inside that folder into `<folder>`:
     - Windows, in PowerShell: `$f="<folder>"; $z="$env:TEMP\context-lab.zip"; $u="$env:TEMP\context-lab-unzip"; Invoke-WebRequest -UseBasicParsing https://github.com/iustinvaliza-del/context-lab/archive/refs/heads/main.zip -OutFile $z; Expand-Archive $z -DestinationPath $u -Force; New-Item -ItemType Directory -Force $f | Out-Null; Get-ChildItem -Force "$u\context-lab-main" | Copy-Item -Destination $f -Recurse -Force; Remove-Item $z, $u -Recurse -Force`
     - Mac: `f="<folder>"; mkdir -p "$f" && curl -fsSL -o /tmp/context-lab.zip https://github.com/iustinvaliza-del/context-lab/archive/refs/heads/main.zip && unzip -q -o /tmp/context-lab.zip -d /tmp/context-lab-unzip && cp -R /tmp/context-lab-unzip/context-lab-main/. "$f" && rm -rf /tmp/context-lab.zip /tmp/context-lab-unzip`
4. **Run the setup.** Follow `SETUP.md` in that folder. It installs git and Obsidian if they are still missing, opens Obsidian on the folder, and ends by telling them how to start round 1.

## What's in the folder

| Folder | What goes in it |
|---|---|
| `sources/` | The case you prep (one PDF), or the files for your own task |
| `outputs/` | The answers you save in each round |
| `memory/` | Lessons the tool saves on its own from round 2, one note per lesson, kept tidy |
| `memory/Daily/` | One note per day, a line for each task the tool finishes |
| `.claude/skills/` | The prep-case skill you make in round 3, for Claude Code |
| `.agents/skills/` | The same skill, for Codex |
| `AGENTS.md` | The greeting and the Learning mode section for now; you fill in the rest from round 2 |
| `how-it-works/` | Notes the tool reads when you ask how something works. You never need to open them. |
| `extras/` | The AGENTS.md template that round 2 fills in |
| `SETUP.md`, `setup/` | The setup your tool runs in step 2: git and Obsidian for Windows and Mac |

AGENTS.md starts with one line that makes every session open with "Radu says Hi", and a Learning mode section: ask the tool how or why anything works and it explains it in plain steps, and every reply ends with one line on what it just did. Keep that section while you are learning. You fill in the rest in round 2. Codex reads AGENTS.md, and Claude Code reads it when the folder has no CLAUDE.md, so one file works in both.

## The five rounds

**The goal:** by the end, this folder preps your next case the way you want it, from one sentence, and gets better every time you correct it.

**How:** you ask the same sentence in every round, and each round adds one file. Because the question never changes, any change in the answer comes from the files.

> Prep the case in sources/ for class.

Every prompt below is also on one page with copy buttons: https://claude.ai/artifact/JKZorWv9pp8gantQk7Lpre (the break slide shows its link and code).

| Round | Adds | You see |
|---|---|---|
| 1 Cold | nothing yet | the answer anyone would get |
| 2 Create | `AGENTS.md` | the same question, a better answer |
| 3 Manage | a skill | it reads the skill only for this task |
| 4 Maintain | memory notes | a correction that stays fixed |
| 5 Understand | nothing; you read it all | every answer points at a file |

Put one case in `sources/`: any case from this term, as the PDF from Blackboard. Nothing confidential: no case supplements, other people's personal data or documents under NDA. Rather work on another weekly task, such as researching a company before a coffee chat? Put its files in `sources/`, use your own sentence, and follow the same rounds. Where a command differs, the Codex one follows in brackets.

### Round 1: Cold

Ask the sentence above and have the tool save the answer to `outputs/cold.md`. Type `/context` \[`/status`\] and note how little it read.

The reply opens with "Radu says Hi". That comes from the one line in `AGENTS.md`, which the tool reads at the start of every session. Delete the line when you no longer want the greeting.

### Round 2: Create

Ask the tool to interview you:

> Interview me with up to eight questions about how I prep a case: who I am, the course, what I need before class, what good looks like. Then fill in the template in extras/AGENTS.starter.md and add it to AGENTS.md, under 40 lines.

Read what it adds to AGENTS.md and fix anything wrong in the file itself. Leave the Memory section at the end as it is: from now on the tool saves what it learns in `memory/`, adds a line to today's note in `memory/Daily/` when it finishes a task, and keeps the notes tidy, without being asked. Then start fresh with `/clear` \[a new chat\], ask the same sentence, and save the answer to `outputs/warm.md`. Open `cold.md` and `warm.md` side by side: the only difference is one file.

Stuck? Copy what is in `extras/AGENTS.starter.md` into `AGENTS.md`, below the line already there, and fill in the lines in angle brackets.

### Round 3: Manage

AGENTS.md is read in every session, so it should hold only what every session needs. The steps of the task go in a skill, which is read only when the task calls for it. Ask:

> Write a skill called prep-case with the steps I want when I prep a case, in order, and one line on when to use it. Keep AGENTS.md to who I am and my rules.

The skill lands in `.claude/skills/prep-case/SKILL.md` \[`.agents/skills/prep-case/SKILL.md`\]. Start fresh, ask the same sentence, and type `/context` \[`/status`\]: it read the skill because the task called for it.

### Round 4: Maintain

1. Read the prep. Tell the tool one thing it got wrong, then ask: "Update AGENTS.md or the skill so this does not happen again." Read the change.
2. Open `memory/`: the lesson is already saved as a note, because the Memory section in AGENTS.md asks for that.
3. Start fresh with `/clear` \[a new chat\], ask the same sentence, and save the answer to `outputs/final.md`. The mistake is gone, because the fix lives in a file.

### Round 5: Understand

Ask: "What do you know about me and how I prep a case, and which file did each piece come from?" Every answer should point at a file. Correct anything wrong in the file, not in the chat. Then open `memory/`: every note the tool wrote is there, already tidy.

### Debrief

Open `outputs/cold.md` and `outputs/final.md` side by side: the same sentence and the same model, with three rounds of files between them.

## Ask how it works

You don't need to read any of this README to use the folder. Ask the tool instead: "How does memory work here?", "Why did you read that file?", "What is a skill?". It answers from `how-it-works/`, in plain steps, using your own folder.

## Read it in Obsidian

Obsidian is a free app that shows this folder as notes you can read and search. Setup installs it and opens this folder in it, so it is ready when round 1 starts. AGENTS.md, your outputs and the memory notes are all there. The tool writes the notes and keeps them tidy: it updates old notes instead of adding repeats, merges notes that say the same thing and fixes links that point nowhere. Obsidian is where you read and search them. You can still edit any note, and the tool reads your edits too.

Obsidian hides folders whose names start with a dot, so the skills don't show there: open `.claude/skills/` or `.agents/skills/` in any editor. Without Obsidian, open `memory/` in any editor: the notes are plain files.

## After the workshop

Nothing to switch on. The Memory section that round 2 added to AGENTS.md keeps working in every session. Before your next class, put the new case in `sources/` and ask the same sentence. To use the folder for a second task, add a section for it to AGENTS.md and a skill for its steps, the same way as in rounds 2 and 3.

## Keep it private

`.gitignore` keeps whatever you put in `sources/` out of git. If you put this folder on GitHub later, make that repository private, and keep keys, passwords and logins out of every file.
