# context-lab

The starter folder for "Context is the job", the IESE Data and AI Club workshop. It is nearly empty on purpose. In the five rounds you write your own AGENTS.md, a skill and memory notes into it, and by the end this folder is your context library. It works the same in Claude Code and in Codex.

Nothing you change in your copy goes back to this repository.

## Get started

You need Claude Code or Codex installed and signed in. Nothing else: your tool downloads this folder and installs the rest.

**1. Ask your tool to set it up.** Open Claude Code or Codex in your Documents folder and type:

> Set up this workshop starter: github.com/iustinvaliza-del/context-lab

Allow what it asks. It downloads this folder into Documents as `context-lab`, installs Obsidian if you don't have it, adds the folder to Obsidian as a vault and opens it, and tells you when it's done. If Obsidian is already open, it asks you to close it first.

**2. Open the folder for round 1.** Open the new `context-lab` folder in a fresh session, so round 1 starts cold:

| | Desktop app | Terminal |
|---|---|---|
| Claude Code | In the Claude desktop app, open the Code tab and choose `context-lab` | Go into the folder and type `claude` |
| Codex | In the Codex app, open `context-lab` as the project | Go into the folder and type `codex` |

The first time, the tool may ask whether you trust this folder, and it asks before it runs a command or writes a file. Allow it for this folder: that is how the library gets written.

Type `/context` in Claude Code or `/status` in Codex to see how little is loaded so far.

**Rather do it by hand?** On this page, click the green **Code** button, then **Download ZIP**, and unzip it. On Windows, Extract All puts the folder inside a second folder with the same name: use the inner one, which has this README directly inside. Open it in your tool as in step 2 and type `Follow SETUP.md`. Already use git? `git clone` the HTTPS address from the same button instead.

### For the AI tool setting this up

The person asked you to set up this starter. They are new to this, so say what you are doing in one short line per step.

1. Download this folder into the folder your session runs in, unless they named another place. Git is not needed:
   - Windows, in PowerShell: `Invoke-WebRequest -UseBasicParsing https://github.com/iustinvaliza-del/context-lab/archive/refs/heads/main.zip -OutFile context-lab.zip; Expand-Archive context-lab.zip -DestinationPath .; Rename-Item context-lab-main context-lab; Remove-Item context-lab.zip`
   - Mac: `curl -fsSL -o context-lab.zip https://github.com/iustinvaliza-del/context-lab/archive/refs/heads/main.zip && unzip -q context-lab.zip && mv context-lab-main context-lab && rm context-lab.zip`

   If git is installed, `git clone https://github.com/iustinvaliza-del/context-lab` does the same. If a `context-lab` folder is already there, ask them before you replace it. The download needs internet access; if your sandbox blocks it, ask them once for permission.
2. Follow `context-lab/SETUP.md`.

## What's in the folder

| Folder | What goes in it |
|---|---|
| `sources/` | Two or three files for your task |
| `outputs/` | The answers you save in each round |
| `memory/` | Lessons the tool saves when you correct it, one note per lesson |
| `memory/Daily/` | One note per day, once you switch on the extras |
| `.claude/skills/` | The skill you make in round 3, for Claude Code |
| `.agents/skills/` | The same skill, for Codex |
| `extras/` | A starter AGENTS.md and two skills for after the workshop |
| `SETUP.md`, `setup/` | The setup your tool runs in step 1: one script for Windows, one for Mac |

There is no AGENTS.md yet: you write it in round 2. Codex reads AGENTS.md, and Claude Code reads it when the folder has no CLAUDE.md, so one file works in both.

## The five rounds

Pick one task you do every week: prepping a case, researching a company before a coffee chat, writing the club newsletter. Put two or three files for it in `sources/`. Nothing confidential: no case supplements, other people's personal data or documents under NDA. Where a command differs, the Codex one follows in brackets.

### Round 1: Cold

Ask for help with the task in one sentence, the way you would in Cowork, and have the tool save the answer to `outputs/cold.md`. Type `/context` \[`/status`\] and note how little is loaded.

### Round 2: Create

Ask the tool to interview you:

> Interview me with up to eight questions about this task: who I am, the goal, the constraints, what good looks like, and what is in sources/. Then write an AGENTS.md for this folder, under 40 lines.

Read the AGENTS.md it writes and fix anything wrong in the file itself. Then start fresh with `/clear` \[a new chat\], ask the same one-sentence question, and save the answer to `outputs/warm.md`. Run `/context` \[`/status`\] again and compare with round 1.

Stuck? Copy `extras/AGENTS.starter.md` into this folder as `AGENTS.md` and fill in the lines in angle brackets.

### Round 3: Manage

The main file loads in every session, so it should hold only what every session needs. Ask:

> Move the step-by-step procedure for this task out of AGENTS.md into a skill, with a one-line description of when to use it. Keep AGENTS.md to who I am and my standing rules.

The skill lands in `.claude/skills/<task>/SKILL.md` \[`.agents/skills/<task>/SKILL.md`\]. Type `/skills` to see it, then ask for the task again and watch the skill load only when the task calls for it.

### Round 4: Maintain

1. Ask the tool to do the task for real and save the result to `outputs/`.
2. Pick one thing it got wrong, tell it, then ask: "Update AGENTS.md or the skill so this does not happen again, and save the lesson as a dated note in memory/." Read both changes.
3. Run `/context` \[`/status`\], then `/compact`, then check again. In Claude Code, add focus instructions: `/compact keep the decisions and the open questions`.
4. Start fresh with `/clear` \[a new chat\] and ask a follow-up. The correction holds, because it lives in a file.

### Round 5: Understand

Ask: "What do you know about me and this task, which file did each piece come from, and what are you assuming?" Correct one wrong assumption in the file, not in the chat. Then try a side question with `/btw` \[`/side`\]: it answers without adding to the main conversation.

## Read it in Obsidian

The setup opens this folder in Obsidian as a vault. AGENTS.md, your outputs and the memory notes are all there, and you can read or edit any of them. A note you write in Obsidian goes to `memory/`, where the tool reads it too. If you skipped the setup, install Obsidian from obsidian.md, choose **Open folder as vault** and pick this folder.

Obsidian hides folders whose names start with a dot, so the skills don't show there: open `.claude/skills/` or `.agents/skills/` in any editor. Without Obsidian, open `memory/` in any editor: the notes are plain files.

## After the workshop: switch on the extras

Open the tool in this folder and ask:

> Copy each skill folder in extras/skills/ into .claude/skills/ and into .agents/skills/. Then make sure my AGENTS.md has the Memory section from extras/AGENTS.starter.md, and add this line to it: "Read memory/Daily/ only when I ask about an earlier session."

That gives you:

- `save-lesson`: when you correct the tool, it fixes AGENTS.md or the skill, then saves the lesson as a dated note in `memory/`.
- `wrap-up`: say "wrap up" at the end of a session and it adds a short summary to today's note in `memory/Daily/`.
- The Memory section in AGENTS.md: every session starts by reading your lessons in `memory/`, and reads the daily notes only when you ask about an earlier session.

In the workshop demo, the daily note is written at the end of every session without asking, by a Claude Code hook. A hook runs a command on your computer every session, so this starter leaves it out. Once `wrap-up` is a habit, the hooks guide in the Claude Code docs shows how to add one.

## Keep it private

`.gitignore` keeps whatever you put in `sources/` out of git. If you put your library on GitHub later, make that repository private, and keep keys, passwords and logins out of every file.
