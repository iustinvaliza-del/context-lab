# Set up this folder

These steps are for Claude Code or Codex. The person asked you to set up this folder for a workshop. They are new to this, so tell them what you are doing in plain words, one short line per step.

1. Find the folder that holds this file: that is the starter folder. If you just downloaded it for them, it is the `context-lab` folder you made. If they unzipped it by hand and it sits one folder down, for example in `context-lab-main` inside a folder with the same name, the inner folder is the one.
2. Run the setup script for this computer, from inside the starter folder:
   - Windows: `powershell -NoProfile -ExecutionPolicy Bypass -File setup\windows.ps1`
   - Mac: `bash setup/mac.sh`

   The script installs Obsidian if it is missing, adds this folder to Obsidian as a vault, and opens it. It downloads Obsidian and writes Obsidian's own settings outside this folder, so it needs internet access. If your sandbox blocks that, ask them once for permission to run it outside the sandbox. The download can take a few minutes.
3. If it stops because Obsidian is open, ask them to close Obsidian, then run it again.
4. If it fails, explain the error in one sentence. Then tell them the folder works without Obsidian, and that they can install Obsidian later from obsidian.md and choose **Open folder as vault**.
5. When it finishes, tell them three things: setup is done, Obsidian is open on the starter folder, and round 1 starts in a fresh session in that folder. Give its full path and say how to open it: in the Claude desktop app, the Code tab, then choose the folder; in the Codex app, open it as the project; in a terminal, go into it and type `claude` or `codex`. If this session already runs in the starter folder, `/clear` in Claude Code or a new chat in Codex is enough.

Install nothing else: git is not needed. Do not create AGENTS.md or CLAUDE.md, and do not change any other file. The person writes those during the workshop.
