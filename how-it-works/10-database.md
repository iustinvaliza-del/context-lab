# The database and the search

This folder has a small database in `database/`. It does two things: it lets the tool search the person's own files before it answers, and it keeps lists the person wants kept (one general list to start). The person never has to open it.

## What it is

- A database is one file that holds lists. Each list (a "table") is like one sheet in a spreadsheet: each row is one entry, each column one detail of it.
- Theirs is `database/data.db`. It is on this computer only: no account, no internet, and it is kept out of git. It is made with SQLite, which comes with Python, so setup installed nothing new for it.
- `database/SHAPE.md` says in plain words what lists it holds and what each column means. Open it to see the current shape.
- `database/schema.sql` is the same shape written for the database itself. `database/db.py` is the script the tool runs.

## How the search works

1. The search reads the files in `library/`, `sources/` and `Deliverables/`, and their Agent Memory folder: markdown, text, CSV, PDF, Word and PowerPoint files.
2. It cuts each file into short passages of a few paragraphs and keeps a list of which words are in which passage. That list is what makes a search take a fraction of a second.
3. When they ask about their own material, the tool searches with a few key words, reads the best passages and answers, naming the file (and the page) each fact came from. The search-my-files skill has the steps.
4. It ignores capitals and accents: "economica" finds "económica".
5. It only finds words that are in the file. "sales" does not find "revenue", so the tool tries two or three wordings before it says nothing matched.
6. When files change, `uv run database/db.py index` reads only the new and changed ones. Setup ran it once; the tool runs it again before a search when files have changed.

## The shape is theirs to choose

- The starting shape is one general list called `items` (anything: ideas, contacts, readings, deadlines) plus the search part. It is only a start.
- It can hold any lists they want, for example people they meet, deals, cases or readings, each with the details they choose.
- It can be shown any way they like: a list in the chat, a note in their Agent Memory folder that they read in Obsidian, a spreadsheet that opens in Excel, or a simple page in `Deliverables/<date>/`.
- To change it, they ask in their own words, for example "keep a list of the people I meet: name, company, where we met". The shape-database skill has the steps: the tool asks up to five short questions, shows the plan, changes nothing until they say yes, then updates `SHAPE.md`.
- The tool offers this once and may remind them once later. If they never want it, nothing changes.

## Is it safe?

- Before each change of shape, the tool saves a copy of the database in `database/backups/`.
- It never deletes a list or entries without asking first.
- If the database file is lost, the search can be built again from their files; their own lists come back from the copy in `database/backups/`.

## Questions they may ask

- "Where is my database?" `database/data.db` in this folder; `SHAPE.md` next to it says what is inside.
- "Why did you say which file that came from?" Because the answer came from their files, and naming the file lets them check it.
- "Why didn't it find X?" The search looks for the words themselves. Try another word, or check that the file is in one of the folders it reads (`uv run database/db.py stats` lists them).
- "Can it search another folder?" Yes: `uv run database/db.py index --path "<folder>"`.
- "Can it understand meaning, not only words?" Not yet. That would need a small AI model on the laptop; for now the tool tries several wordings instead.

How to say it: "I searched your files for 'working capital', read the two best passages, and the numbers come from your Brisa Bikes pre-notes."
