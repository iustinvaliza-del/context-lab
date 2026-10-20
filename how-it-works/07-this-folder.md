# This folder and the five rounds

## What each folder is for

| Folder or file | What it holds |
|---|---|
| `AGENTS.md` | The instructions every session reads first |
| `sources/` | The case to prep (one PDF), or the files for another task. Kept out of git. |
| `outputs/` | The answers saved in each round: `cold.md`, `warm.md`, `final.md` |
| `memory/`, `memory/Daily/` | Lessons and the daily log, written by the tool |
| `.claude/skills/`, `.agents/skills/` | Skills for Claude Code and for Codex |
| `extras/` | The `AGENTS.md` template that round 2 fills in |
| `how-it-works/` | These notes, for answering the person's questions |
| `SETUP.md`, `setup/` | The setup the tool ran at the start: git and Obsidian |

## The five rounds

The goal: by the end, this folder preps the person's next case the way they want it, from one sentence. They ask the same sentence every round, "Prep the case in sources/ for class.", and each round adds one file, so any change in the answer comes from the files.

1. **Cold**: nothing added. The answer anyone would get. Saved to `outputs/cold.md`.
2. **Create**: the interview fills in `AGENTS.md`. Saved to `outputs/warm.md`.
3. **Manage**: the steps go into the `prep-case` skill; `AGENTS.md` stays short.
4. **Maintain**: one correction goes into a file, and the lesson lands in `memory/`. Saved to `outputs/final.md`.
5. **Understand**: they ask what you know about them and which file each piece came from.

Then they compare `cold.md` with `final.md`.

If they are behind, help them catch up one round at a time. If they want to use another weekly task instead of a case, the rounds work the same with their own sentence.
