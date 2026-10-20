# Obsidian

Obsidian is a free app for reading and searching a folder of markdown files. It shows links between notes and renders the marks (headings, bullets, bold). Setup installed it and opened this folder in it.

- It reads the same files in this folder. Nothing is copied or uploaded.
- Folders whose names start with a dot (`.claude/`, `.agents/`) are hidden in Obsidian.
- Edits made in Obsidian are ordinary file edits, so the tool reads them in the next session.

## If it is not open, or not installed

Run the setup script for their computer from this folder. It installs git and Obsidian if missing, adds this folder as a vault and opens it, and it closes Obsidian first if it is already open:

- Windows: `powershell -NoProfile -ExecutionPolicy Bypass -File setup\windows.ps1`
- Mac: `bash setup/mac.sh`

If the script fails, fix the cause and run it again. Do not ask them to install anything by hand.

How to say it: "Obsidian is a reader for this folder. Your notes, outputs and AGENTS.md are all there."
