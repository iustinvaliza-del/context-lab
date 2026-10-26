# This folder and the five rounds

## What each folder is for

| Folder or file | What it holds |
|---|---|
| `AGENTS.md` | The instructions every session reads first |
| `library/` | Their library. `library/IESE/` holds their IESE courses from Blackboard: a folder for each year (`1st year`, `2nd year`) with one folder per course inside it, each session's files, and the notes the pipeline writes. Kept out of git. |
| `pipeline/` | The case pipeline's scripts and worked examples; see `09-case-pipeline.md` |
| `database/` | Their database: a search over their files and notes, and their own lists. `SHAPE.md` says what it holds; see `10-database.md`. The database file is kept out of git. |
| `sources/` | Files for another weekly task, if they use the folder for one. The pipeline does not need it. Kept out of git. |
| `Deliverables/` | Anything made for them to look at or keep, one folder per day: `Deliverables/<date>/<name>/`. Rounds 1 and 5 save `first.md` and `final.md` in `Deliverables/<date>/workshop/`. See `Deliverables/README.md`. |
| `.claude/skills/`, `.agents/skills/` | Skills for Claude Code and for Codex |
| `extras/` | The `AGENTS.md` template that round 3 fills in |
| `how-it-works/` | These notes, for answering the person's questions |
| `SETUP.md`, `setup/` | The setup the tool ran at the start: git, Obsidian, MarkText and the Agent Memory folder. `setup/vault/How to keep notes.md` is the note-taking rules that setup copied into Agent Memory. |

The memory notes are not in this folder. They live in Agent Memory on the Desktop, so every project can read them; see `05-memory.md`.

## The five rounds

The goal: by the end, the case pipeline preps the person's next case the way they want it, from one sentence. They pick the case for their next class and ask the same sentence every round, "Prep the case for session N of <course>.", with their own number and course. Round 1 runs the pipeline as it comes; each round after that changes one file, so any change in the answer comes from the files.

1. **Run**: the first run signs in to Blackboard, builds `library/IESE/` and preps the case. They save the login when asked, save a copy of the notes to `Deliverables/<date>/workshop/first.md`, and `/context` (`/status`) shows the prep-case skill was read.
2. **Correct**: they tell the tool one thing to do differently, and the fix goes into the prep-case skill as a rule.
3. **Personalise**: the interview fills in `AGENTS.md` from the template, Memory section included, so the tool reads `How to keep notes.md` and saves lessons to Agent Memory from now on.
4. **Ask**: they ask what you know about them and which file each piece came from.
5. **Compare**: a fresh session, the same sentence, notes saved to `Deliverables/<date>/workshop/final.md`. A last correction lands as a note in Agent Memory.

Then they compare `first.md` with `final.md`.

If they are behind, help them catch up one round at a time. If Blackboard sign-in fails or they have no case this week, they can use a worked example in `pipeline/examples/` or put any case PDF in `sources/` and ask to prep that one; the rounds work the same.
