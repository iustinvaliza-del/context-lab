# Set up this folder

These steps are for Claude Code or Codex. The person asked you to set up this folder for a workshop. They are new to this and must not have to do anything by hand except allow your steps, so do every step yourself and tell them what you are doing in plain words, one short line per step.

1. Find the folder that holds this file: that is the workshop folder. It is the folder they made and opened, whatever they called it. If it sits one folder down, for example in `context-lab-main` inside it, the inner folder is the one.
2. Run the setup script for their computer from the workshop folder. It installs git and Obsidian if they are missing, adds the folder to Obsidian as a vault and opens Obsidian on it. It can take a few minutes; tell them so.
   - Windows: `powershell -NoProfile -ExecutionPolicy Bypass -File setup\windows.ps1`
   - Mac: `bash setup/mac.sh`. If git was missing, a window from Apple asks to install the command line developer tools: tell them to click Install. It is the only click setup needs.
   If the script stops with an error, read its last lines, fix the cause and run it again. If Obsidian still will not install, download it from obsidian.md yourself, run the installer, and run the script again: it adds the folder and opens it.
3. Tell them three things: setup is done and Obsidian is open on their folder, they can ask you how anything in this folder works at any time, and round 1 starts fresh. If this session runs in the workshop folder, fresh means `/clear` in Claude Code or a new chat in Codex. If it runs somewhere else, give the folder's full path and say how to open it: in the Claude desktop app, start a new session in the Code tab and choose the folder; in the Codex app, open it as the project; in a terminal, go into it and type `claude` or `codex`.

Do not create CLAUDE.md, do not change AGENTS.md or how-it-works/, and do not change any other file. The person writes those during the workshop.
