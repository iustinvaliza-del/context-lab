-- The shape of the database, written for the database itself. SHAPE.md says the same in plain words.
-- A "table" is one list: each row is one entry, each column one detail of it.
-- `uv run database/db.py init` makes these tables when they are missing; it never removes anything.
-- When the shape changes, change it here too, so a new database starts in the same shape.

-- Your lists ---------------------------------------------------------------------------------

-- One general list for anything worth keeping: ideas, contacts, readings, deadlines.
CREATE TABLE IF NOT EXISTS items (
  id INTEGER PRIMARY KEY,                             -- a number for each row, given by the database
  kind TEXT,                                          -- what sort of thing: idea, contact, reading, deadline...
  title TEXT NOT NULL,                                -- its name, in a few words
  details TEXT,                                       -- anything else about it
  tags TEXT,                                          -- words to find it by, separated by commas
  date TEXT,                                          -- a date that matters for it, YYYY-MM-DD
  source TEXT,                                        -- where it came from: a file, a link, a person
  added TEXT DEFAULT (datetime('now', 'localtime'))   -- when it was added, filled in by itself
);

-- The search part: `index` fills these from your files; do not change them by hand ----------

-- One row per file the search has read.
CREATE TABLE IF NOT EXISTS documents (
  id INTEGER PRIMARY KEY,
  path TEXT NOT NULL UNIQUE,  -- where the file is: inside this folder, or the full path outside it
  title TEXT,                 -- the file's first heading, or its name
  kind TEXT,                  -- markdown, text, table, pdf, word or slides
  folder TEXT,                -- library, sources, Deliverables, Agent Memory, or another folder's name
  modified INTEGER,           -- when the file last changed, to notice changes quickly
  size INTEGER,               -- its size in bytes
  fingerprint TEXT,           -- a code computed from its contents, to tell if it really changed
  note TEXT,                  -- why it gave no text, when it gave none
  indexed_at TEXT             -- when the search last read it
);

-- The files cut into short passages (a few paragraphs each), so a search can point at the right part.
CREATE TABLE IF NOT EXISTS passages (
  id INTEGER PRIMARY KEY,
  document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  position INTEGER NOT NULL,  -- 1 for the first passage of the file, 2 for the next...
  page INTEGER,               -- the page of a PDF or the slide of a presentation
  text TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS passages_by_document ON passages(document_id);

-- The word list that makes the search fast (SQLite's FTS5). It ignores capitals and accents.
CREATE VIRTUAL TABLE IF NOT EXISTS passages_search USING fts5(
  text, content = 'passages', content_rowid = 'id', tokenize = 'unicode61 remove_diacritics 2'
);

-- These keep the word list in step with the passages.
CREATE TRIGGER IF NOT EXISTS passages_added AFTER INSERT ON passages BEGIN
  INSERT INTO passages_search(rowid, text) VALUES (new.id, new.text);
END;
CREATE TRIGGER IF NOT EXISTS passages_removed AFTER DELETE ON passages BEGIN
  INSERT INTO passages_search(passages_search, rowid, text) VALUES ('delete', old.id, old.text);
END;
CREATE TRIGGER IF NOT EXISTS passages_changed AFTER UPDATE ON passages BEGIN
  INSERT INTO passages_search(passages_search, rowid, text) VALUES ('delete', old.id, old.text);
  INSERT INTO passages_search(rowid, text) VALUES (new.id, new.text);
END;
