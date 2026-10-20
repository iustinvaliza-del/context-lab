# Skills: steps for one task, read only when needed

A skill is a markdown file with the steps of one task, in order, and one line that says when to use it. It lives in its own folder:

- Claude Code: `.claude/skills/<name>/SKILL.md`
- Codex: `.agents/skills/<name>/SKILL.md`

Folders whose names start with a dot are hidden in most file browsers and in Obsidian. Open them from the editor or ask the tool to show the file.

## How the tool uses it

1. At the start of a session the tool sees only each skill's name and its "when to use" line.
2. When the request matches that line (for example "Prep the case in sources/ for class."), it reads the whole skill and follows the steps.
3. When the request does not match, the skill stays unread and takes no room.

That is the difference from `AGENTS.md`: `AGENTS.md` is read every time; a skill is read only for its task.

## In this workshop

Round 3 writes a skill called `prep-case` with the person's own steps for prepping a case. `/context` in Claude Code (or `/status` in Codex) shows it loaded after the sentence is asked.

How to say it: "Your steps for prepping a case are in `.claude/skills/prep-case/SKILL.md`. I read it because you asked me to prep a case. If you ask me something else, I don't read it."
