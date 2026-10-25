# Obsidian and MarkText

Obsidian is a free app for reading and searching a folder of markdown files, called a vault. It shows links between notes and renders the marks (headings, bullets, bold). Setup installed it, made a folder called Agent Memory on their Desktop, and opened that folder in it as the vault.

- Agent Memory holds `Start here.md` (what the folder is for), `How to keep notes.md` (the rules the tool follows for its notes, see `05-memory.md`), the notes themselves (one note per lesson, topic notes) and a `Daily/` folder with one note per day. Until round 3 adds the Memory section to `AGENTS.md`, only the first two are there.
- It sits outside this workshop folder, so every project can read and add to the same notes. That is the difference from a project in Chat or Cowork, which remembers only what is inside it.
- Obsidian reads the files where they are. Nothing is copied or uploaded.
- Edits made in Obsidian are ordinary file edits, so the tool reads them in the next session.
- This workshop folder (AGENTS.md, skills, outputs) is not in the vault; open its files in MarkText.

## MarkText

MarkText is a free app that opens one markdown file at a time as a formatted page the person can edit like a document. Setup installed it. When they want to read or edit a file (`AGENTS.md`, a skill, the notes in `outputs/`), open it in MarkText: on a Mac `open -a MarkText "<file>"`, on Windows `%LOCALAPPDATA%\Programs\marktext\marktext.exe` with the file's full path. Use Obsidian for the Agent Memory folder and MarkText for single files anywhere else.

## If it is not open, or not installed

Run the setup script for their computer from this folder. It installs git, Obsidian and MarkText if missing, makes Agent Memory if it is not there yet, puts `How to keep notes.md` in it if that note is missing (it never replaces one that is there), adds it as a vault and opens it, and it closes Obsidian first if it is already open:

- Windows: `powershell -NoProfile -ExecutionPolicy Bypass -File setup\windows.ps1`
- Mac: `bash setup/mac.sh`

If the script fails, fix the cause and run it again. Do not ask them to install anything by hand.

How to say it: "Obsidian shows your Agent Memory folder. I write the notes there, and you read, search and fix them. Any project can use the same notes."
