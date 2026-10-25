# AGENTS.md: the file every session reads first

`AGENTS.md`, in the top of this folder, holds the project's instructions. Every new session in this folder reads it before the person types anything.

- Claude Code and Codex both read `AGENTS.md`, so the one file works in both. It is the standard name; teach only this one.
- For the tool, not to bring up: Claude Code would read a `CLAUDE.md` instead if one existed (it reads `AGENTS.md` when there is none, from version 2.1.277). Do not create a `CLAUDE.md` here.

## "Radu says Hi"

The first line of `AGENTS.md` tells the tool to open every session with "Radu says Hi". It is there to show that the file is read every time: nobody typed the greeting, the file did. Deleting the line stops it.

## The MarkText line

The next line tells the tool to open a markdown file in MarkText when the person wants to read or edit one. Setup installed MarkText for that (see `08-obsidian.md`).

## What goes in it

After round 3 it holds four things, kept short (under about 40 lines):

1. Who the person is.
2. The task they do every week.
3. What a good answer looks like.
4. Their rules and constraints.

Plus three sections that stay: **Learning mode** (it points here and adds the "What just happened" line), **Your database** (search their files before answering, and the one offer to shape the database, see `10-database.md`) and **Memory** (it gives the path of the Agent Memory folder and tells the tool to read and follow `How to keep notes.md` there, see `05-memory.md`).

## Why short

Everything in `AGENTS.md` is read in every session, whether the task needs it or not. Steps for one task belong in a skill (`04-skills.md`), which is read only when that task comes up.

## Why it changes the answer

The model is the same for everyone. What changes its answer is what it knows about the person's situation when it starts. `AGENTS.md` is the cheapest way to give it that: write it once, and every session starts knowing it.

How to say it: "Before you typed anything, I read `AGENTS.md`. That is why I knew your course and how you like your notes. Change the file, and the next session changes with it."
