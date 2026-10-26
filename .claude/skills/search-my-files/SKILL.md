---
name: search-my-files
description: Search the person's own files and notes (their library of IESE courses, sources, Deliverables, the Agent Memory folder, their lists) before answering a question about them, then answer from what was found and name the file each fact came from. Use when they ask what they wrote, what a case, reading or note says, where something is, or anything about their own material.
---

# Search my files

The database in `database/` keeps a search over the person's files: `library/`, `sources/`, `Deliverables/` and their Agent Memory folder, plus their own lists (see `database/SHAPE.md`). It finds passages that contain the words you search for, ignoring capitals and accents ("economica" finds "económica"). It does not know that two different words mean the same thing: "sales" does not find "revenue". It reads markdown, text, CSV, PDF, Word (.docx) and PowerPoint (.pptx) files.

Every path below is relative to this project folder. If `uv` is not found, call it by its full path: `~/.local/bin/uv` on a Mac, on Windows `~/.local/bin/uv.exe` in Git Bash or `& "$env:USERPROFILE\.local\bin\uv.exe"` in PowerShell.

## When

- Before answering a question about their own files, notes or past work: "what did I write about pricing", "which case had the Spanish bank", "what do my notes say about WACC", "who did I meet at the career fair".
- Not for general questions that are not about their material, and not when they name one file: then read that file.

## Steps

1. **Bring the search up to date.** If files were added or changed since the last search (a Blackboard download, a new note, a file they dropped in `sources/`), or a search says it "has not read any files yet" or ends with "new, changed or gone since the last update", run `uv run database/db.py index` first. It reads only new and changed files. The first run after Blackboard downloads a whole course can take a few minutes: give it a long timeout.
2. **Search with two to four key words**, not a sentence: `uv run database/db.py search "pricing strategy"`.
   - Try two or three wordings before you give up: a synonym, the English and the Spanish word, a shorter form, a name or a number from the question.
   - `valu*` finds every word that starts with "valu": value, values, valuation.
   - A phrase in double quotes inside the words finds those words together: `uv run database/db.py search '"discounted cash flow"'`.
   - `--in "Corporate Finance"` keeps only files whose path contains that text; `--limit 20` shows more passages; `--full` prints each passage whole.
   - When no passage has all the words, it shows passages with some of them and says so.
3. **Read the best passages.** Each comes with its file and, for a PDF or a presentation, the page or slide. When a passage is not enough, open the file itself; for a PDF use `uv run pipeline/read_case.py "<file>"`.
4. **Answer from what you read**, naming the file (and the page) each fact came from, for example "(sources/dcf-note.md)" or "(Brisa_case.pdf, page 2)". Keep what the files say apart from what you add yourself.
5. **If nothing matches** after three wordings, say so plainly and say what you searched for. Never present something from your own knowledge as if it came from their files.

## Also

- Matches in their own lists (`items` and any list they added) show under "In your lists".
- Another folder, for example a reading folder elsewhere: `uv run database/db.py index --path "<folder>"` reads it into the search. Run it again with the same `--path` after that folder changes.
- `uv run database/db.py stats` says which folders the search reads, where the Agent Memory folder is, and which files gave no text (a scanned PDF has no text to search; read it with `read_case.py`, which saves page images).
- If the Agent Memory folder is not searched, its path is not yet written in `AGENTS.md` or `extras/AGENTS.starter.md`; setup writes it there.
- The database stays on this computer and out of git. If it is ever lost, `uv run database/db.py index` builds the search again from the files; their own lists come back only from a copy in `database/backups/`.
