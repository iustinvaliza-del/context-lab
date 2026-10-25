# Context: everything the model sees when it answers

Context is everything the model can see when it answers: its instructions (including `AGENTS.md`), the files it has read in this session, and the conversation so far. It has no other memory.

The space for all of this is called the context window. It is large but not endless. When it fills up, older parts of the conversation get summarized or dropped.

## Why the answer changes

The same model, asked the same sentence, gives a better answer when its context holds the person's situation: who they are, what good looks like, their steps and past corrections. That is why the workshop asks the same sentence in every round and only changes the files.

## Commands

| What | Claude Code | Codex |
|---|---|---|
| See what is loaded and how full the window is | `/context` | `/status` |
| Start fresh in the same folder | `/clear` | a new chat |
| Shrink a long conversation into a summary and keep going | `/compact` | `/compact` |

Use `/clear` between tasks so an old conversation does not mix into a new one. In one long task, run the `summary` skill (type `/summary` in Claude Code, or ask Codex to summarize and compact) before the window is half full: it writes what matters to today's note in Agent Memory's `Daily/` folder, then you type `/compact`. Past about half the window the model gets worse at using what it has, so compacting from a clean summary keeps only the good context.

How to say it: "Type `/context`. The list shows what I am looking at right now: my own instructions, your `AGENTS.md`, and this conversation. Nothing else."
