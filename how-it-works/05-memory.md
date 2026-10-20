# Memory: how the tool remembers between sessions

The model remembers nothing from one session to the next. Everything it "remembers" is written in files in this folder.

## What is where

- `AGENTS.md`: what every session needs (who they are, their rules).
- `memory/`: one short note per lesson, named `YYYY-MM-DD-short-title.md`. A lesson is a correction or something settled, for example "headings in my notes follow the case questions".
- `memory/Daily/`: one note per day, with one line for each task finished: what was done and what is still open.

## How it works

1. Before a task, the tool reads the notes in `memory/` that relate to it.
2. When the person corrects it or they settle something, it saves the lesson as a note, without being asked.
3. When it finishes a task, it adds a line to today's daily note.
4. It keeps the notes tidy: it updates an old note instead of writing a repeat, merges notes that say the same thing and links related notes with `[[note name]]`.

The **Memory** section that round 2 adds to `AGENTS.md` is what tells it to do all this. Remove the section and it stops.

## Fix the file, not the chat

A correction typed in the chat lasts until the session ends. A correction written into `AGENTS.md`, the skill or a memory note lasts for every session after. That is round 4.

How to say it: "I don't remember yesterday. I read `memory/` before the task, and your correction from last time is a note there. Want to see it?"
