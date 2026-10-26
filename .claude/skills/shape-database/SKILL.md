---
name: shape-database
description: The optional conversation about how the person's database should be shaped and how they want to see it, and the safe way to change its shape. Use when they ask to change or add to their database, to keep a new kind of list, or to see a list another way, when they accept the offer from AGENTS.md, or when you make or record that offer.
---

# Shape the database

The database in `database/` starts with one general list (`items`) and the search part. That is only a starting shape: it can hold any lists the person wants and show them any way they like. They decide. This skill is for when they want to; never push it.

A few words to explain once when you use them: a "table" is one list, like one sheet in a spreadsheet; each row is one entry and each column one detail of it. SQL is the language you write the change in; they never need to read it.

Every path below is relative to this project folder. If `uv` is not found, call it by its full path (see the search-my-files skill).

## The offer, and the one reminder

`database/SHAPE.md` ends with "Asked so far". Read it before you offer anything.

- **Offer not made yet:** near the end of your reply, before the "What just happened" line, say in two plain sentences that the database is only a starting shape and can hold any lists they want and show them any way they like (a note in Obsidian, a spreadsheet, a page). Then ask once: "Want me to ask a few questions about how you'd like it shaped and how it should look?" Change the line to "Offer to shape this database: made on <date>; they said <yes, no, or nothing>."
- **They say no, or move on:** drop it. You may mention it once more, only when it would help, for example when they keep the same kind of list by hand, paste a table of contacts, or ask where to keep something. Record it on the "Reminder" line. After that, never bring it up again; they can still ask.
- **They say yes**, now or later: ask the questions below.

## The questions (only after a yes)

Ask one at a time, up to five, in plain words. Stop early when you have enough.

1. What do you want to keep track of? For example people you meet, cases, deals, readings, deadlines.
2. For each one, what do you want to write down? For example name, company, date, where it came from.
3. How will you look for things later? By person, by course, by date, by a word?
4. How do you want to see it? A list in the chat, a note in Obsidian, a spreadsheet that opens in Excel, or a simple page.
5. Is there anything that must stay out? For example grades or anything private about other people.

Then show the plan in plain words: each list, what each entry holds, and how they will see it. Change nothing until they say yes to the plan.

## Making the change (after a yes to the plan)

1. Run the change: `uv run database/db.py change "<SQL>"`. It saves a copy of the database in `database/backups/` first, and makes the whole change or none of it.
   - A new list: `CREATE TABLE people (id INTEGER PRIMARY KEY, name TEXT NOT NULL, company TEXT, where_met TEXT, added TEXT DEFAULT (datetime('now', 'localtime')))`. Short lowercase names with underscores.
   - A new detail on a list: `ALTER TABLE items ADD COLUMN course TEXT`.
   - Moving entries from `items` into a new list: `INSERT INTO people (name) SELECT title FROM items WHERE kind = 'contact'`. Leave them in `items` unless they ask to remove them.
2. Write the same shape into `database/schema.sql` (the CREATE TABLE, with its new columns), so a new database starts in this shape.
3. Update `database/SHAPE.md` in plain words: a heading `` ### `name`: what it is `` for each list, and one line per column with its name in backticks and what it holds. Write what they chose under "How you see it".
4. Run `uv run database/db.py check`. It must print "All checks passed"; if it names a problem, fix it and run it again.
5. Show them the result in the way they chose:
   - in the chat: `uv run database/db.py show <list>`;
   - a note in Obsidian: `uv run database/db.py show <list> --note "<Agent Memory folder>/Lists/<list>.md"`, and run it again after each change to the list;
   - a spreadsheet: `uv run database/db.py show <list> --csv Deliverables/<YYYY-MM-DD>/<list>/<list>.csv`;
   - a page: a simple HTML page next to that CSV, in the same `Deliverables/<YYYY-MM-DD>/<list>/` folder.
6. Tell them in one or two sentences what changed and that they can change it again any time.

Add entries with `uv run database/db.py add <list> column="value" ...`, for example `add people name="Ana García" company=CaixaBank`.

## Rules

- Change the shape only after they say yes. Never because it seems useful to you.
- Never delete a list, a column or entries without asking first and naming exactly what goes. `change` refuses DROP and DELETE unless you add `--allow-delete`; add it only after their yes.
- To undo a change, copy the newest file from `database/backups/` over `database/data.db`, after telling them what will be lost.
- Do not change the search part (`documents`, `passages`, `passages_search`): `index` fills it.
- Keep passwords, logins and other secrets out of the database.
