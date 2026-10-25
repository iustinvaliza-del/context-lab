# Memory: how the tool remembers between sessions

The model remembers nothing from one session to the next. Everything it "remembers" is written in files: `AGENTS.md` in this folder, and notes in the Agent Memory folder on their Desktop. Setup made Agent Memory, and its full path is in the Memory section of `AGENTS.md` (before round 3, in `extras/AGENTS.starter.md`).

## What is where

- `AGENTS.md`: what every session needs (who they are, their rules). Its Memory section says where Agent Memory is and tells the tool to read `How to keep notes.md` there at the start of every session.
- `How to keep notes.md` in Agent Memory: the rules for the notes. Setup put it there. It says what goes in, how notes are named and written, when to read them and how to keep them tidy.
- Lesson notes in Agent Memory: one short note per lesson, named `YYYY-MM-DD-short-title.md`. A lesson is a correction or something settled, for example "headings in my notes follow the case questions".
- Topic notes in Agent Memory: one note for a person, a course or a project that keeps coming up, named after it, for example `Corporate Finance.md`.
- Agent Memory's `Daily/` folder: one note per day, with one line for each task finished: what was done and what is still open.

Agent Memory sits outside this folder on purpose. A project only sees what is inside it; a folder outside every project can be read by all of them. Any other project whose `AGENTS.md` has the same Memory section reads and adds to the same notes.

## How it works

1. At the start of a session, the tool reads `How to keep notes.md`.
2. Before a task, it searches Agent Memory and reads the notes that relate to it.
3. When the person corrects it or they settle something, it saves the lesson as a note, without being asked: a title, a few lines, one fact per note, and a short "Why:" line.
4. When it finishes a task, it adds a line to today's daily note.
5. It keeps the notes tidy: it updates an old note instead of writing a repeat, merges notes that say the same thing, links related notes with `[[note name]]` and fixes links that point to no note.
6. It never deletes a note without asking and never saves a password or other secret.

The **Memory** section that round 3 adds to `AGENTS.md` is what sends the tool to these rules. Remove the section and it stops. To change how it keeps notes, change `How to keep notes.md`: the tool follows the note as it is.

## Fix the file, not the chat

A correction typed in the chat lasts until the session ends. A correction written into `AGENTS.md`, the skill or a memory note lasts for every session after. That is rounds 2 and 5.

How to say it: "I don't remember yesterday. I read your Agent Memory folder before the task, and your correction from last time is a note there. Want to see it in Obsidian?"
