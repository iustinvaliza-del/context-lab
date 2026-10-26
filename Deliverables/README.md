# Deliverables

Anything the tool makes for you to look at or keep goes here: copies of notes you ask for, summaries across courses, pages, spreadsheets, exports. One folder per day, one folder per thing inside it:

```
Deliverables/
  2026-11-03/
    workshop/
      first.md
      final.md
    reading-list/
      reading-list.csv
```

- The date is the day it was made, written `YYYY-MM-DD`, so the folders sort in order.
- The name says what it is, in a few lowercase words joined by hyphens.
- Case notes and workbooks do not go here. They stay next to their case in `library/IESE/<year>/<course>/`, so everything for one class sits in one place.
- Scripts and code do not go here either: they belong in `pipeline/`.

## Tidying

When you ask the tool to tidy this folder, it moves day folders older than a month into `Deliverables/archive/` and lists them for you. It deletes nothing unless you say so. Put an empty file called `KEEP` in a folder to keep it out of the tidy.

Everything in this folder stays on your computer: `.gitignore` keeps it out of git, except this README.
