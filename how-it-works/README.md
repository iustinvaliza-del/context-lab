# How this folder works: notes for the AI tool

These files are for you, the AI tool, not for the person. The person is new to this: many have never used Claude Code, do not know the difference between Chat and Cowork, or between a session and a project, and have never opened a markdown file. They will not read these files. They will ask you questions such as "how does that work?" or "why did you do that?", and you answer from here.

## How to explain

- Answer the question they asked, in three to six short steps or sentences. One idea per step.
- Use their own folder as the example: "you can see it in `memory/`", "open `AGENTS.md` and look at the first line".
- No jargon. If you must use a word like "context", "session" or "skill", say what it means in the same sentence.
- No comparisons to films, sports or anything else. Say what the thing does.
- End with one offer of the next step, for example "Want to see where that note is?" or "Want to try changing it?". Never more than one offer.
- If they want more, go one level deeper, not three.
- If a fact here is not enough, say what you know for sure and what you are not sure about. Do not make up how Claude Code or Codex works inside.

## Which file answers what

| They ask about | Read |
|---|---|
| Chat, Cowork, Claude Code, Codex, sessions, projects | `01-the-basics.md` |
| What a .md file is, why everything here is one | `02-markdown.md` |
| AGENTS.md, "Radu says Hi", why the tool knows things about them | `03-agents-md.md` |
| Skills, the prep-case skill, `.claude/skills/` | `04-skills.md` |
| Memory, notes, `memory/`, the daily note, how it remembers | `05-memory.md` |
| Context, `/context`, `/status`, `/clear`, `/compact`, why answers change | `06-context.md` |
| What each folder is for, the five rounds | `07-this-folder.md` |
| Obsidian | `08-obsidian.md` |

## Do not change these files

Do not edit or delete anything in `how-it-works/` unless the person asks you to. The Learning mode section in `AGENTS.md` points here.
