# context-lab

The starter folder for "Context Matters", the IESE AI Club workshop. It is nearly empty on purpose. In the five rounds you write your own AGENTS.md and a skill into it, the tool starts keeping memory notes on its own in an Agent Memory folder on your Desktop, and by the end this folder knows how you prep a case. It works the same in Claude Code and in Codex.

Nothing you change in your copy goes back to this repository.

## Get started

You need Claude Code or Codex installed and signed in. Everything else (git, Obsidian, MarkText, and uv with Python for the case pipeline) the tool installs for you. The same steps, with copy buttons, are on the workshop's prompts page: https://claude.ai/artifact/JKZorWv9pp8gantQk7Lpre

**1. Make a folder and open it.** On your Desktop, make a new folder (call it anything), then open it in your tool:

| | Desktop app | Terminal |
|---|---|---|
| Claude Code | In the Claude desktop app, click the Code icon at the top left. Under the box where you type, click the folder name and choose your folder (a laptop icon means it runs on your computer) | Go into the folder and type `claude` |
| Codex | Open the Codex app on your folder and start a new chat | Go into the folder and type `codex` |

**2. Paste one line.**

> Set up this starter in this folder: github.com/iustinvaliza-del/context-lab

Allow what it asks. It copies this starter into the folder, installs git, Obsidian and MarkText if they are missing, makes an Agent Memory folder on your Desktop with the rules for taking notes in it, opens it in Obsidian, and tells you when it's done. You don't touch anything else.

**3. Start round 1.** Type `/clear` in Claude Code, or start a new chat in Codex, so round 1 starts fresh. The first time, the tool may ask whether you trust this folder, and it asks before it runs a command or writes a file. Allow it for this folder: that is how it writes your files.

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
4. **Run the setup.** Follow `SETUP.md` in that folder. It installs git, Obsidian and MarkText if they are still missing, makes the Agent Memory folder on their Desktop with the note-taking rules in it, opens Obsidian on it, and ends by telling them how to start round 1.

## What's in the folder

| Folder | What goes in it |
|---|---|
| `library/` | Your library. `library/IESE/` is made by the first pipeline run: your IESE courses from Blackboard, in a folder for each year (`1st year`, `2nd year`) with one folder per course inside it, each session's files, and the notes it writes. Kept out of git. |
| `pipeline/` | The case pipeline: the Blackboard downloader, the case reader, the Excel workbook builder and its Python check, and worked examples |
| `database/` | Your database: a search over your files and notes, and one general list to start. `SHAPE.md` says what it holds. The database file stays on your computer, out of git. |
| `.claude/skills/prep-case/`, `.agents/skills/prep-case/` | The prep-case skill: how the tool preps a case, step by step |
| `sources/` | Files for another weekly task, if you use the folder for one. The pipeline does not need it. |
| `Deliverables/` | Anything the tool makes for you to look at or keep, in a folder per day: `Deliverables/<date>/<name>/`. The copies you save in rounds 1 and 5 go in `Deliverables/<date>/workshop/`. Kept out of git, except its README. |
| `.claude/skills/search-my-files/`, `.claude/skills/shape-database/` (and the same in `.agents/skills/`) | Search your files before answering, naming the file each fact came from; and change the database's shape when you ask |
| `.claude/skills/summary/`, `.agents/skills/summary/` | Summary, then compact: type `/summary` (Claude Code) or ask for it (Codex) before the conversation passes half the window |
| `AGENTS.md` | The greeting, the Learning mode section and a short section on your database for now; you fill in the rest in round 3 |
| `how-it-works/` | Notes the tool reads when you ask how something works. You never need to open them. |
| `extras/` | The AGENTS.md template that round 3 fills in |
| `SETUP.md`, `setup/` | The setup your tool runs in step 2: git, Obsidian, MarkText and the Agent Memory folder with its note-taking rules, for Windows and Mac |

Your memory sits outside this folder, in **Agent Memory** on your Desktop, so every project can read it:

| Agent Memory folder | What goes in it |
|---|---|
| `How to keep notes.md` | The rules the tool follows for its notes: what goes in, how notes are named and written, and how they are kept tidy. Setup puts it there. Change a rule and the tool follows the new one. |
| the notes | Lessons the tool saves on its own from round 3, one note per lesson, kept tidy |
| `Daily/` | One note per day, a line for each task the tool finishes |

AGENTS.md starts with one line that makes every session open with "Radu says Hi", and a Learning mode section: ask the tool how or why anything works and it explains it in plain steps, and every reply ends with one line on what it just did. Keep that section while you are learning. You fill in the rest in round 3. Claude Code and Codex both read AGENTS.md, so one file works in both.

## The five rounds

**The goal:** by the end, the case pipeline preps your next case the way you want it, from one sentence, and gets better every time you correct it.

**How:** pick the case for your next class and ask the same sentence in every round, with your own session number and course. Round 1 runs the pipeline as it comes; each round after that changes one file. Because the question never changes, any change in the answer comes from the files.

> Prep the case for session N of &lt;course&gt;.

Every prompt below is also on one page with copy buttons: https://claude.ai/artifact/JKZorWv9pp8gantQk7Lpre (the break slide shows its link and code).

| Round | Changes | You see |
|---|---|---|
| 1 Run | your courses | `library/IESE/` fills up and your first prep |
| 2 Correct | a rule in the prep-case skill | a correction that stays fixed |
| 3 Personalise | `AGENTS.md` | notes written the way you like them |
| 4 Ask | nothing; you read it all | every answer points at a file |
| 5 Compare | a note in Agent Memory | first prep against final prep |

Where a command differs, the Codex one follows in brackets.

### Round 1: Run

Ask the sentence above, with the course and session of your next class. The first time, a Blackboard window opens: sign in with your IESE email and password, and approve the phone prompt if Microsoft asks. The pipeline sets up that course first in `library/IESE/1st year/` or `library/IESE/2nd year/`, fetches the session and preps it, and downloads all your other courses in the background (more in [The case pipeline](#the-case-pipeline) below). Say yes when it offers to save your login.

When the notes are done, ask it to save a copy to `Deliverables/<date>/workshop/first.md`. Type `/context` \[`/status`\]: it read the prep-case skill, because the task called for it.

The reply opens with "Radu says Hi". That comes from the one line in `AGENTS.md`, which the tool reads at the start of every session. Delete the line when you no longer want the greeting.

### Round 2: Correct

Read the pre-notes and the case notes. Tell the tool one thing you would do differently (shorter, another structure, more numbers), then ask:

> Change the prep-case skill so this does not happen again.

The skill is `.claude/skills/prep-case/SKILL.md` \[`.agents/skills/prep-case/SKILL.md`\]. Read the change: every prep follows it from now on, because the fix lives in a file, not in the chat.

### Round 3: Personalise

The skill holds the steps of the task. AGENTS.md holds who you are and how you like your work, for every session. Ask the tool to interview you:

> Interview me with up to eight questions: who I am, my courses, how I like my notes, what good looks like before class. Then fill in the template in extras/AGENTS.starter.md and add it to AGENTS.md, under 40 lines.

Read what it adds to AGENTS.md and fix anything wrong in the file itself. Leave the Memory section at the end as it is: it tells the tool to read `How to keep notes.md` in your Agent Memory folder at the start of every session. From now on the tool saves what it learns in that folder, adds a line to today's note in its `Daily/` folder when it finishes a task, and keeps the notes tidy, without being asked.

Stuck? Copy what is in `extras/AGENTS.starter.md` into `AGENTS.md`, below the line already there, and fill in the lines in angle brackets.

### Round 4: Ask

Ask: "What do you know about me and how you prep my cases, and which file did each piece come from?" Every answer should point at a file: AGENTS.md, the prep-case skill or a note. Correct anything wrong in the file, not in the chat.

### Round 5: Compare

1. Start fresh with `/clear` \[a new chat\], ask the same sentence, and save the notes to `Deliverables/<date>/workshop/final.md`. The files are already downloaded, so it goes straight to the prep.
2. Correct anything still off. Then look at Agent Memory in Obsidian: the lesson is already saved as a note, because the Memory section in AGENTS.md asks for that.

### Debrief

Open `Deliverables/<date>/workshop/first.md` and `Deliverables/<date>/workshop/final.md` side by side: the same sentence and the same model, with a corrected skill and your own AGENTS.md between them.

## The case pipeline

Ask: "Prep the case for session 5 of Corporate Finance" (any course and session). The `prep-case` skill does the rest:

1. **The first time**, it asks which course and session you have next, if you did not say. A Blackboard window opens: sign in with your IESE email and password and approve the phone prompt if Microsoft asks. The pipeline lists every course you are enrolled in, sets up the one you have next first (its folder in `library/IESE/1st year/` or `library/IESE/2nd year/`, or `library/IESE/Other courses/` when Blackboard does not say the year, and its syllabus), fetches that session and preps it. Meanwhile it downloads all your other courses in the background.
2. **It asks whether to save your login.** Say yes and a small window asks for your IESE email and password; they go into Windows Credential Manager or the Mac Keychain, never into a file or the chat. From then on it signs in by itself. Say no and the window opens again whenever Blackboard's session has expired. To remove them: `uv run pipeline/blackboard.py forget-login`.
3. **Every prep** downloads the session's latest files first, then writes pre-notes (what the case is about, in plain words) and case notes by question, with your positions left blank. For cases with numbers it computes them in Python and builds an Excel workbook whose Checks sheet Python recalculates; a number is quoted only when every check reads OK.

On Windows with Excel, optimisation cases can also get Excel's own Solver set up in the workbook; on a Mac the numbers are checked in Python and Solver is left to you. Microsoft may still ask for a phone prompt now and then, even with a saved login.

## Your database and search

Setup also makes a small database in `database/`, on your computer only. When you ask about your own material ("what do my notes say about WACC?"), the tool searches your files in `library/`, `sources/`, `Deliverables/` and Agent Memory first, reads the best passages, and names the file each fact came from. The search finds the words you use, with or without accents; it does not know that two different words mean the same thing, so the tool tries a few wordings.

The database starts with one general list and can be any shape you want: lists of people you meet, deals, readings, anything, shown in the chat, as a note in Obsidian, as a spreadsheet or as a page. The tool mentions this once and asks whether you want to shape it. Say no and it drops it. `database/SHAPE.md` always says what is in it.

## Ask how it works

You don't need to read any of this README to use the folder. Ask the tool instead: "How does memory work here?", "Why did you read that file?", "What is a skill?". It answers from `how-it-works/`, in plain steps, using your own folder.

## Read it in Obsidian

Obsidian is a free app that shows a folder of notes you can read and search. Setup installs it, makes the Agent Memory folder on your Desktop and opens that folder in it, so it is ready when round 1 starts. Until round 3 sets up the notes it holds only `Start here.md` and `How to keep notes.md`, the rules the tool follows when it writes notes. Because the folder sits outside any one project, the next project you start can read the same notes: copy the Memory section of your AGENTS.md into that project's AGENTS.md. The tool writes the notes and keeps them tidy, following those rules: it updates old notes instead of adding repeats, merges notes that say the same thing and fixes links that point nowhere. Obsidian is where you read and search them. You can still edit any note, and the tool reads your edits too.

Without Obsidian, open the Agent Memory folder in MarkText or any other editor: the notes are plain files.

## Read and edit files in MarkText

MarkText is a free app that shows a markdown file as a formatted page you can edit like a document. Setup installs it. Ask the tool to open a file, for example "Open AGENTS.md", and it opens in MarkText. If MarkText did not install, setup still finishes, and running it again tries once more.

## After the workshop

Nothing to switch on. The Memory section that round 3 added to AGENTS.md keeps working in every session. Before your next class, ask the same sentence with the new session number: it downloads that session's latest files first. To use the folder for a second task, put its files in `sources/`, add a section for it to AGENTS.md and a skill for its steps, the same way as in rounds 2 and 3.

In a long session, type `/summary` in Claude Code, or ask Codex to "summarize and compact", before the conversation passes half the context window (`/context` \[`/status`\] shows how full it is). It writes what matters to today's note in Agent Memory's `Daily/` folder, then tells you to type `/compact`, so only the good context goes on.

## Keep it private

`.gitignore` keeps `library/IESE/`, your database and whatever you put in `sources/` out of git, and your Blackboard login is never in this folder. If you put this folder on GitHub later, make that repository private, and keep keys, passwords and logins out of every file.
