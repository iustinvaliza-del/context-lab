# The basics: Chat, Cowork, Claude Code, sessions and projects

## Three ways to use Claude

The same model sits behind all three. What differs is what it can see and what it can do.

- **Chat** (claude.ai, the Claude app on a computer, phone or iPad): a conversation. It sees what you type and the files you attach. It answers one message at a time.
- **Cowork** (a tab in the Claude desktop app, also in the Claude iOS app on paid plans): you connect folders, and Claude does a longer task on those files, step by step. It can only read and write in the folders you connected.
- **Claude Code** (the Code tab in the Claude desktop app, or `claude` in a terminal): Claude works inside one folder on your computer. It reads the files there, writes new ones and runs commands, asking first according to the permission mode.
- **Codex** is OpenAI's tool that works the same way as Claude Code. This folder works in both.

This workshop uses Claude Code (or Codex) because the whole library is files in one folder, and Claude Code works directly on that folder.

## Session

A session is one conversation. In Claude Code, a session is tied to the folder it was opened in. When a new session starts, it remembers nothing from the last one. `/clear` in Claude Code (a new chat in Codex) starts a fresh session in the same folder; the old one is saved and `/resume` brings it back.

How to say it: "A session is one conversation. When you start a new one, I start from zero, except for what is written in the files in this folder."

## Project

A project is what every session shares.

- In Chat and Cowork, a Project is a space in the app with its own instructions and files (Chat calls them project instructions and project knowledge). Every chat in that Project sees them.
- In Claude Code, the project is the folder. This folder, the one they made for the workshop, is the project. Every session opened in it reads `AGENTS.md` first.

How to say it: "The session forgets, the project stays. Whatever should last goes into a file in this folder, not into the chat."

## Where things are in the desktop app

- The tabs Chat, Cowork and Code are at the top.
- In the Code tab, the folder (the project) is chosen with **Select folder**, with Environment set to **Local**.
- Next to the send button is the permission mode: how much Claude may do without asking.
- If the person's app shows different words, use the words on their screen.

## Only an iPad or a phone

Claude Code on a phone or iPad works only with cloud sessions linked to a GitHub repository, which is more than a beginner needs. The simple route: a Project in the Claude app, where the project instructions play the part of `AGENTS.md` and the project files play the part of `sources/`. The ideas are the same; the files just live in the app instead of a folder.
