# The shape of your database

This file says in plain words what your database holds. The database is one file, `database/data.db`, on this computer only: no account, no internet, and it is kept out of git.

A database holds lists. Each list (a "table") is like one sheet in a spreadsheet: each row is one entry, and each column is one detail of it.

This is only a starting shape. It can hold any lists you want (people you meet, cases, deals, readings, deadlines, anything) and show them any way you like. Ask the tool to change it whenever you want; it changes this file each time, so this file always says what is in there.

## Your lists

### `items`: one general list
Anything you want to keep track of, until you want a list of its own for it.
- `id`: a number the database gives each row
- `kind`: what sort of thing it is, for example idea, contact, reading or deadline
- `title`: its name, in a few words
- `details`: anything else about it
- `tags`: words to find it by, separated by commas
- `date`: a date that matters for it, written YYYY-MM-DD
- `source`: where it came from: a file, a link or a person
- `added`: when it was added, filled in by itself

## The search part

The search reads your files in `library/`, `sources/`, `Deliverables/` and your Agent Memory folder, and keeps what it read in these three lists. `uv run database/db.py index` fills them; nobody changes them by hand. If they are ever lost, `index` builds them again from your files.

### `documents`: one row per file the search has read
- `id`: a number for each file
- `path`: where the file is
- `title`: its first heading, or its name
- `kind`: markdown, text, table, pdf, word or slides
- `folder`: library, sources, Deliverables, Agent Memory, or another folder's name
- `modified` and `size`: when the file last changed and how big it is, to notice changes quickly
- `fingerprint`: a code computed from the file's contents, to tell whether it really changed
- `note`: why a file gave no text, when it gave none (for example a scanned PDF)
- `indexed_at`: when the search last read it

### `passages`: the files cut into short pieces of a few paragraphs
- `id`: a number for each passage
- `document_id`: which file it comes from
- `position`: 1 for the first passage of the file, 2 for the next, and so on
- `page`: the page of a PDF or the slide of a presentation
- `text`: the words of the passage

### `passages_search`: the word list that makes the search fast
- `text`: every word of every passage, without capitals or accents

## How you see it

Not chosen yet. For now the tool shows a list in the chat when you ask. It can also save it as a note in your Agent Memory folder (so you read it in Obsidian), as a spreadsheet file that opens in Excel, or as a simple page in `Deliverables/<date>/`.

## Asked so far

- Offer to shape this database: not made yet.
- Reminder: not made yet.
