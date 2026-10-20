# AGENTS.md: the file every session reads first

`AGENTS.md`, in the top of this folder, holds the project's instructions. Every new session in this folder reads it before the person types anything.

- Codex reads `AGENTS.md`.
- Claude Code reads `CLAUDE.md`, and reads `AGENTS.md` when the folder has no `CLAUDE.md` (Claude Code 2.1.277 or later). This folder has no `CLAUDE.md` on purpose, so the one file works in both. Do not create a `CLAUDE.md` here.

## "Radu says Hi"

The first line of `AGENTS.md` tells the tool to open every session with "Radu says Hi". It is there to show that the file is read every time: nobody typed the greeting, the file did. Deleting the line stops it.

## What goes in it

After round 2 it holds four things, kept short (under about 40 lines):

1. Who the person is.
2. The task they do every week.
3. What a good answer looks like.
4. Their rules and constraints.

Plus two sections that stay: **Learning mode** (it points here and adds the "What just happened" line) and **Memory** (it tells the tool to keep notes, see `05-memory.md`).

## Why short

Everything in `AGENTS.md` is read in every session, whether the task needs it or not. Steps for one task belong in a skill (`04-skills.md`), which is read only when that task comes up.

## Why it changes the answer

The model is the same for everyone. What changes its answer is what it knows about the person's situation when it starts. `AGENTS.md` is the cheapest way to give it that: write it once, and every session starts knowing it.

How to say it: "Before you typed anything, I read `AGENTS.md`. That is why I knew your course and how you like your notes. Change the file, and the next session changes with it."
