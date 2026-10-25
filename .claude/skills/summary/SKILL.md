---
name: summary
description: Write a short summary of this session to today's note in Agent Memory/Daily, then have the person compact. Use when they type /summary or say "summarize and compact", or when the conversation is near half the context window.
---

# Summary, then compact

A long conversation gets worse past about half the context window: the model is worse at using what it has, then it starts to forget the start. Run this before that point, so only the good context goes into the next part of the conversation.

## When

- The person types `/summary` or asks to summarize and compact.
- `/context` (Claude Code) or `/status` (Codex) shows the window about half full. Say so once and offer to run it.

## Steps

1. Write the summary to `Daily/<today's date, YYYY-MM-DD>.md` in the Agent Memory folder. Its full path is in the Memory section of `AGENTS.md`; before round 3 it is in `extras/AGENTS.starter.md`, and if neither has it, it is the Agent Memory folder on their Desktop. If the file exists, add a new section at the end; do not replace what is there. Plain words, short, under these headings:
   - **What we did**: three to five sentences.
   - **Decided**: each decision and why.
   - **Tried, did not work**: one line each, so it is not tried again.
   - **Files**: each file made or changed, and what it is now.
   - **Next**: the exact next step.
   Only what still matters. Leave out guesses, long quotes and anything already undone.
2. Show the person the summary in your reply.
3. Tell them to type the compact command; you cannot run it yourself:
   - Claude Code: `/compact Keep only what is in Agent Memory/Daily/<date>.md`
   - Codex: `/compact`
4. After the compaction, read that daily note back before you carry on.
