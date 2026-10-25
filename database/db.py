# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "pypdf>=4.0",
# ]
# ///
"""Your database: one file on this computer with a search over your files and your own lists.

The database is database/data.db (SQLite, built into Python: no account, no internet). It holds
a word search over the files in IESE/, sources/, outputs/ and the Agent Memory folder, and the
lists the person keeps (one general list, `items`, to start). database/SHAPE.md says in plain
words what it holds; database/schema.sql is the same shape written for the database.

    uv run database/db.py init                    make the database (safe to run again)
    uv run database/db.py index                   read new and changed files into the search
    uv run database/db.py index --path "<folder>" also read another folder
    uv run database/db.py search "words"          find passages, best first, with the file each is in
    uv run database/db.py add items title="..." kind=idea      add a row to a list
    uv run database/db.py tables                  every list, its columns and how many rows
    uv run database/db.py show items              print a list (--csv FILE, --note FILE to save it)
    uv run database/db.py stats                   what the search holds and which folders it reads
    uv run database/db.py check                   check the database against schema.sql and SHAPE.md
    uv run database/db.py change "SQL"            change the shape (a copy goes to database/backups/ first)

The search finds passages that contain the words searched for, ignoring capitals and accents
("economica" finds "económica"). It does not know that two different words mean the same thing.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import logging
import os
import re
import sqlite3
import sys
import time
import unicodedata
import zipfile
from pathlib import Path
from xml.etree import ElementTree

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
DB_FILE = HERE / "data.db"
SCHEMA_FILE = HERE / "schema.sql"
SHAPE_FILE = HERE / "SHAPE.md"
BACKUPS = HERE / "backups"

# Folders inside this project that the search reads; the Agent Memory folder is added when its
# path is known (setup writes it into extras/AGENTS.starter.md, round 3 into AGENTS.md).
PROJECT_FOLDERS = ("IESE", "sources", "outputs")
KINDS = {
    ".md": "markdown",
    ".txt": "text",
    ".csv": "table",
    ".pdf": "pdf",
    ".docx": "word",
    ".pptx": "slides",
}
SKIP_FOLDERS = {"_pages", "__pycache__", "node_modules"}
SEARCH_TABLES = ("documents", "passages", "passages_search")
MAX_TEXT_BYTES = 5_000_000  # larger text files are skipped (a big data file is not worth searching)
MAX_OTHER_BYTES = 100_000_000
PASSAGE_CHARS = 900
PLACEHOLDER_START = "<"
# Meaning search (finding "revenue" from "sales") would go here later, as a second way to rank passages.


def say(text: str = "") -> None:
    print(text, flush=True)


def n_of(number: int, word: str) -> str:
    """'1 file', '2 files'."""
    return f"{number} {word}" if number == 1 else f"{number} {word}s"


def shown(path: Path) -> str:
    """How a file is named in the database and in answers: relative inside this project, full outside."""
    try:
        return path.resolve().relative_to(PROJECT).as_posix()
    except ValueError:
        return str(path)


def real_path(stored: str) -> Path:
    p = Path(stored)
    return p if p.is_absolute() else PROJECT / p


# ---------------------------------------------------------------- the database file


def connect() -> sqlite3.Connection:
    new = not DB_FILE.exists()
    con = sqlite3.connect(DB_FILE, timeout=30)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    if new:
        build_shape(con)
    return con


def build_shape(con: sqlite3.Connection) -> None:
    if not has_fts5():
        raise SystemExit("This Python's SQLite has no FTS5 (the word search). Run it with uv, which brings a Python that has it.")
    con.executescript(SCHEMA_FILE.read_text(encoding="utf-8"))
    con.commit()


def has_fts5() -> bool:
    try:
        probe = sqlite3.connect(":memory:")
        probe.execute("CREATE VIRTUAL TABLE t USING fts5(x, tokenize='unicode61 remove_diacritics 2')")
        probe.close()
        return True
    except sqlite3.OperationalError:
        return False


def table_names(con: sqlite3.Connection) -> list[str]:
    """Tables a person would recognise: no SQLite internals and no search-engine helper tables."""
    rows = con.execute("SELECT name, sql FROM sqlite_master WHERE type = 'table' ORDER BY name").fetchall()
    virtual = [r["name"] for r in rows if (r["sql"] or "").upper().startswith("CREATE VIRTUAL TABLE")]
    names = []
    for r in rows:
        name = r["name"]
        if name.startswith("sqlite_"):
            continue
        if any(name.startswith(v + "_") for v in virtual):
            continue
        names.append(name)
    return names


def own_tables(con: sqlite3.Connection) -> list[str]:
    return [t for t in table_names(con) if t not in SEARCH_TABLES]


def columns(con: sqlite3.Connection, table: str) -> list[str]:
    return [r[1] for r in con.execute(f'PRAGMA table_info("{table}")')]


def count(con: sqlite3.Connection, table: str) -> int:
    return con.execute(f'SELECT count(*) FROM "{table}"').fetchone()[0]


# ---------------------------------------------------------------- which folders the search reads


MEMORY_LINE = re.compile(r"Agent Memory folder:\s*(.+?)\s*$")


def find_memory() -> tuple[Path | None, str]:
    """The Agent Memory folder's path, from where setup and round 3 write it, and where it was found."""
    for name in ("AGENTS.md", "extras/AGENTS.starter.md"):
        try:
            text = (PROJECT / name).read_text(encoding="utf-8")
        except OSError:
            continue
        for line in text.splitlines():
            m = MEMORY_LINE.search(line)
            if not m:
                continue
            value = re.split(r"\.\s+It sits", m.group(1))[0].strip().strip("`\"'").rstrip(".")
            if value and not value.startswith(PLACEHOLDER_START):
                return Path(value).expanduser(), name
    try:
        data = json.loads((PROJECT / ".claude" / "settings.local.json").read_text(encoding="utf-8"))
        for d in data.get("permissions", {}).get("additionalDirectories", []):
            if isinstance(d, str) and Path(d).name == "Agent Memory":
                return Path(d), ".claude/settings.local.json"
    except (OSError, ValueError, AttributeError):
        pass
    return None, ""


def folders_to_read(extra: list[str] | None, quiet: bool = False) -> list[tuple[str, Path]]:
    roots = [(name, PROJECT / name) for name in PROJECT_FOLDERS if (PROJECT / name).is_dir()]
    memory, found_in = find_memory()
    if memory is None:
        if not quiet:
            say("Agent Memory folder: its path is not written in AGENTS.md or extras/AGENTS.starter.md yet "
                "(setup writes it there), so it was not searched.")
    elif not memory.is_dir():
        if not quiet:
            say(f"Agent Memory folder: {memory} (from {found_in}) does not exist, so it was not searched.")
    else:
        roots.append(("Agent Memory", memory))
        if not quiet:
            say(f"Agent Memory folder: {memory}")
    for p in extra or []:
        folder = Path(p).expanduser()
        if not folder.is_absolute():
            folder = Path.cwd() / folder
        if folder.is_dir():
            roots.append((folder.name, folder))
        else:
            say(f"Not a folder, so it was not read: {p}")
    return roots


def files_in(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if not d.startswith(".") and d not in SKIP_FOLDERS)
        here = Path(dirpath)
        for f in sorted(filenames):
            if f.startswith((".", "~$")):
                continue
            p = here / f
            if p.suffix.lower() in KINDS:
                yield p


# ---------------------------------------------------------------- reading files


def decode(data: bytes) -> str:
    for enc in ("utf-8-sig", "cp1252"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("latin-1")


def read_pdf(path: Path) -> tuple[list[tuple[int | None, str]], str]:
    logging.getLogger("pypdf").setLevel(logging.ERROR)
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception:  # noqa: BLE001 - any failure here means the file is locked
            return [], "locked with a password"
    pages = []
    for number, page in enumerate(reader.pages, 1):
        try:
            text = page.extract_text() or ""
        except Exception:  # noqa: BLE001 - one broken page should not stop the file
            text = ""
        pages.append((number, text))
    return pages, ""


def xml_paragraphs(data: bytes, paragraph_tag: str, text_tag: str) -> list[str]:
    root = ElementTree.fromstring(data)
    out = []
    for para in root.iter(paragraph_tag):
        words = "".join(t.text or "" for t in para.iter(text_tag)).strip()
        if words:
            out.append(words)
    return out


W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"


def read_docx(path: Path) -> list[tuple[int | None, str]]:
    with zipfile.ZipFile(path) as z:
        paras = xml_paragraphs(z.read("word/document.xml"), W + "p", W + "t")
    return [(None, "\n\n".join(paras))]


def read_pptx(path: Path) -> list[tuple[int | None, str]]:
    with zipfile.ZipFile(path) as z:
        slides = [n for n in z.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)]
        slides.sort(key=lambda n: int(re.findall(r"\d+", n)[-1]))
        return [(int(re.findall(r"\d+", n)[-1]), "\n\n".join(xml_paragraphs(z.read(n), A + "p", A + "t"))) for n in slides]


def read_file(path: Path, kind: str, size: int) -> tuple[list[tuple[int | None, str]], str]:
    """The file's text as (page or slide number, text) pieces, and a note when there is no text."""
    limit = MAX_TEXT_BYTES if kind in ("markdown", "text", "table") else MAX_OTHER_BYTES
    if size > limit:
        return [], f"too large to read ({size // 1_000_000} MB)"
    try:
        if kind == "pdf":
            pages, note = read_pdf(path)
        elif kind == "word":
            pages, note = read_docx(path), ""
        elif kind == "slides":
            pages, note = read_pptx(path), ""
        else:
            pages, note = [(None, decode(path.read_bytes()))], ""
    except Exception as e:  # noqa: BLE001 - a file that cannot be read is noted, not fatal
        return [], f"could not be read ({type(e).__name__})"
    if not note and not any(text.strip() for _, text in pages):
        note = "no text found (a scanned page or an image)" if kind == "pdf" else "empty"
    return pages, note


def split_text(text: str, limit: int = PASSAGE_CHARS) -> list[str]:
    """Cuts text into passages of up to about `limit` characters, at paragraph and sentence ends."""
    out: list[str] = []
    current = ""
    for para in re.split(r"\n\s*\n", text):
        para = re.sub(r"[ \t\r\f\v]+", " ", para).strip()
        if not para:
            continue
        while len(para) > limit:
            cut = para.rfind(". ", 0, limit)
            if cut < limit // 2:
                cut = para.rfind(" ", 0, limit)
            if cut < limit // 2:
                cut = limit - 1
            piece, para = para[: cut + 1].strip(), para[cut + 1 :].strip()
            if current:
                out.append(current)
                current = ""
            out.append(piece)
        if current and len(current) + len(para) + 2 > limit:
            out.append(current)
            current = para
        else:
            current = f"{current}\n\n{para}" if current else para
    if current:
        out.append(current)
    return out


def title_of(path: Path, pages: list[tuple[int | None, str]]) -> str:
    if path.suffix.lower() == ".md" and pages:
        for line in pages[0][1].splitlines()[:30]:
            if line.startswith("# "):
                return line[2:].strip()
    return path.stem


def fingerprint(path: Path) -> str:
    h = hashlib.sha1()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


# ---------------------------------------------------------------- commands


def cmd_init(_args) -> int:
    existed = DB_FILE.exists()
    con = connect()
    build_shape(con)
    say(f"The database is ready: {shown(DB_FILE)} ({'already there' if existed else 'new'}).")
    say("Lists in it: " + ", ".join(table_names(con)) + ". database/SHAPE.md says what each holds.")
    return 0


def cmd_index(args) -> int:
    started = time.perf_counter()
    con = connect()
    roots = folders_to_read(args.path)
    known = {r["path"]: r for r in con.execute("SELECT id, path, size, modified, fingerprint FROM documents")}
    seen: set[str] = set()
    todo = []
    unchanged = 0
    for label, root in roots:
        for path in files_in(root):
            key = shown(path)
            if key in seen:
                continue
            seen.add(key)
            try:
                st = path.stat()
            except OSError:
                continue
            row = known.get(key)
            if row and row["size"] == st.st_size and row["modified"] == st.st_mtime_ns:
                unchanged += 1
                continue
            todo.append((label, path, key, st, row))

    if len(todo) > 50:
        say(f"Reading {len(todo)} new or changed files. Large PDFs take a moment each.")
    new = changed = passages = 0
    problems: list[str] = []
    now = time.strftime("%Y-%m-%dT%H:%M:%S")
    for n, (label, path, key, st, row) in enumerate(todo, 1):
        try:
            fp = fingerprint(path)
        except OSError:
            continue
        if row and row["fingerprint"] == fp:
            con.execute("UPDATE documents SET size = ?, modified = ? WHERE id = ?", (st.st_size, st.st_mtime_ns, row["id"]))
            unchanged += 1
            continue
        kind = KINDS[path.suffix.lower()]
        pages, note = read_file(path, kind, st.st_size)
        values = (key, title_of(path, pages), kind, label, st.st_mtime_ns, st.st_size, fp, note or None, now)
        if row:
            con.execute("DELETE FROM passages WHERE document_id = ?", (row["id"],))
            con.execute(
                "UPDATE documents SET path=?, title=?, kind=?, folder=?, modified=?, size=?, fingerprint=?, note=?, indexed_at=? WHERE id=?",
                (*values, row["id"]),
            )
            doc_id = row["id"]
            changed += 1
        else:
            cur = con.execute(
                "INSERT INTO documents (path, title, kind, folder, modified, size, fingerprint, note, indexed_at) VALUES (?,?,?,?,?,?,?,?,?)",
                values,
            )
            doc_id = cur.lastrowid
            new += 1
        rows = []
        for page, text in pages:
            for piece in split_text(text):
                rows.append((doc_id, len(rows) + 1, page, piece))
        con.executemany("INSERT INTO passages (document_id, position, page, text) VALUES (?,?,?,?)", rows)
        passages += len(rows)
        if note:
            problems.append(f"  {key}: {note}")
        if n % 100 == 0:
            con.commit()
            say(f"  {n} of {len(todo)} files read")

    removed = 0
    for key, row in known.items():
        if key not in seen and not real_path(key).exists():
            con.execute("DELETE FROM passages WHERE document_id = ?", (row["id"],))
            con.execute("DELETE FROM documents WHERE id = ?", (row["id"],))
            removed += 1
    con.commit()

    folders = ", ".join(label for label, _ in roots) or "none"
    say(f"Searched folders: {folders}.")
    say(f"Read {new} new and {n_of(changed, 'changed file')} ({n_of(passages, 'passage')}). "
        f"{unchanged} unchanged, not read again. {removed} removed because the file is gone. "
        f"Took {time.perf_counter() - started:.1f} s.")
    if problems:
        say("Files with no searchable text:")
        for line in problems[:10]:
            say(line)
        if len(problems) > 10:
            say(f"  and {len(problems) - 10} more (see: stats)")
    return 0


def files_out_of_date(con: sqlite3.Connection) -> int:
    """How many files are new, changed or gone since the last index, from their size and date only."""
    known = {r["path"]: (r["size"], r["modified"]) for r in con.execute("SELECT path, size, modified FROM documents")}
    seen = set()
    stale = 0
    for _, root in folders_to_read(None, quiet=True):
        for path in files_in(root):
            key = shown(path)
            seen.add(key)
            try:
                st = path.stat()
            except OSError:
                continue
            if known.get(key) != (st.st_size, st.st_mtime_ns):
                stale += 1
    stale += sum(1 for key in known if key not in seen and not real_path(key).exists())
    return stale


QUERY_PART = re.compile(r'"([^"]*)"|(\S+)')


def match_expression(words: str, any_word: bool) -> str:
    """Turns what was typed into an FTS5 search: every word must be there (or any, with --any).
    "a phrase" in double quotes stays a phrase, and word* matches every word that starts that way."""
    parts = []
    for phrase, word in QUERY_PART.findall(words):
        if phrase:
            tokens = re.findall(r"\w+", phrase)
            if tokens:
                parts.append('"' + " ".join(tokens) + '"')
            continue
        tokens = re.findall(r"\w+", word)
        for i, t in enumerate(tokens):
            star = "*" if word.endswith("*") and i == len(tokens) - 1 else ""
            parts.append(f'"{t}"{star}')
    return (" OR " if any_word else " ").join(parts)


def plain(text: str) -> str:
    """Lower case without accents, to match the person's own lists the way the search matches files."""
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c)).casefold()


def search_lists(con: sqlite3.Connection, words: str, limit: int) -> list[tuple[str, sqlite3.Row]]:
    wanted = [plain(w) for w in re.findall(r"\w+", words)]
    if not wanted:
        return []
    hits = []
    for table in own_tables(con):
        for row in con.execute(f'SELECT * FROM "{table}" LIMIT 20000'):
            text = plain(" ".join(str(v) for v in row if v is not None))
            if all(w in text for w in wanted):
                hits.append((table, row))
                if len(hits) >= limit:
                    return hits
    return hits


def cmd_search(args) -> int:
    started = time.perf_counter()
    words = " ".join(args.words).strip()
    if not words:
        say('Give some words to search for, for example: uv run database/db.py search "pricing strategy"')
        return 2
    con = connect()
    if count(con, "documents") == 0:
        say("The search has not read any files yet. Run: uv run database/db.py index")
    sql = (
        "SELECT d.path, d.title, p.page, p.text, "
        "snippet(passages_search, 0, '**', '**', ' ... ', 40) AS snip, bm25(passages_search) AS score "
        "FROM passages_search JOIN passages p ON p.id = passages_search.rowid "
        "JOIN documents d ON d.id = p.document_id WHERE passages_search MATCH ?"
    )
    params: list = []
    if args.inside:
        sql += " AND d.path LIKE ?"
        params.append(f"%{args.inside}%")
    sql += " ORDER BY score LIMIT ?"

    def run(any_word: bool):
        expr = match_expression(words, any_word)
        if not expr:
            return []
        try:
            return con.execute(sql, [expr, *params, args.limit * 4]).fetchall()
        except sqlite3.OperationalError as e:
            say(f"The search could not read those words ({e}). Use plain words, \"a phrase\" or word*.")
            return []

    rows = [] if args.any else run(False)
    some_words = False
    if not rows:
        rows = run(True)
        some_words = bool(rows) and not args.any

    per_file: dict[str, int] = {}
    results = []
    for r in rows:
        if per_file.get(r["path"], 0) >= 3:
            continue
        per_file[r["path"]] = per_file.get(r["path"], 0) + 1
        results.append(r)
        if len(results) >= args.limit:
            break

    if some_words:
        say("No passage has all of those words, so these have some of them:")
    for i, r in enumerate(results, 1):
        where = r["path"] + (f"  (page {r['page']})" if r["page"] else "")
        say(f"{i}. {where}")
        body = r["text"] if args.full else r["snip"]
        for line in body.splitlines():
            if line.strip():
                say(f"   {line.strip()}")
    lists = search_lists(con, words, 5)
    if lists:
        say("In your lists:")
        for table, row in lists:
            shown_row = ", ".join(f"{k}: {row[k]}" for k in row.keys() if row[k] not in (None, ""))  # noqa: SIM118 - a Row gives values when iterated
            say(f"  {table}: {shown_row[:300]}")
    if not results and not lists:
        say(f"Nothing matched: {words}")
        say("Try other words: a synonym, the Spanish or English word, a shorter word, or word* to match the start of a word.")
    elif not results:
        say(f"No passage in your files has those words; the matches above are from your lists ({time.perf_counter() - started:.2f} s).")
    else:
        say(f"Found {n_of(len(results), 'passage')} in {n_of(len(per_file), 'file')} ({time.perf_counter() - started:.2f} s).")
    if not args.no_freshness:
        stale = files_out_of_date(con)
        if stale:
            say(f"Note: {n_of(stale, 'file')} new, changed or gone since the last update of the search. "
                "Run: uv run database/db.py index, then search again.")
    return 0


def cmd_add(args) -> int:
    con = connect()
    if args.table not in table_names(con):
        say(f"There is no list called {args.table}. Lists: {', '.join(own_tables(con))}")
        return 2
    if args.table in SEARCH_TABLES:
        say(f"{args.table} is part of the search and is filled by index, not by hand.")
        return 2
    cols = columns(con, args.table)
    values = {}
    for pair in args.values:
        if "=" not in pair:
            say(f"Write each value as column=value, for example title=\"Call Ana\". Not understood: {pair}")
            return 2
        key, value = pair.split("=", 1)
        key = key.strip()
        if key not in cols:
            say(f"{args.table} has no column {key}. Its columns: {', '.join(cols)}")
            return 2
        values[key] = value
    if not values:
        say(f"Nothing to add. Its columns: {', '.join(cols)}")
        return 2
    names = ", ".join(f'"{k}"' for k in values)
    marks = ", ".join("?" for _ in values)
    try:
        cur = con.execute(f'INSERT INTO "{args.table}" ({names}) VALUES ({marks})', list(values.values()))
    except sqlite3.DatabaseError as e:
        say(f"Not added: {e}")
        return 2
    con.commit()
    say(f"Added row {cur.lastrowid} to {args.table}.")
    return 0


def cmd_tables(_args) -> int:
    con = connect()
    for group, names in (("Your lists", own_tables(con)), ("The search part (filled by index)", list(SEARCH_TABLES))):
        say(f"{group}:")
        for t in names:
            if t in table_names(con):
                say(f"  {t} ({n_of(count(con, t), 'row')}): {', '.join(columns(con, t))}")
    return 0


def cell(value, width: int | None) -> str:
    text = "" if value is None else str(value)
    text = text.replace("\n", " ").replace("|", "/")
    if width and len(text) > width:
        text = text[: width - 3] + "..."
    return text


def markdown_table(head: list[str], rows: list, width: int | None) -> list[str]:
    lines = ["| " + " | ".join(head) + " |", "|" + "|".join("---" for _ in head) + "|"]
    for r in rows:
        lines.append("| " + " | ".join(cell(r[c], width) for c in head) + " |")
    return lines


def cmd_show(args) -> int:
    con = connect()
    if args.table not in table_names(con):
        say(f"There is no list called {args.table}. Lists: {', '.join(table_names(con))}")
        return 2
    head = columns(con, args.table)
    if args.table == "passages_search":
        head = ["text"]
    order = "" if args.table == "passages_search" else " ORDER BY rowid DESC"
    limit = "" if (args.csv or args.note) and not args.limit_given else f" LIMIT {int(args.limit)}"
    rows = con.execute(f'SELECT {", ".join(chr(34) + c + chr(34) for c in head)} FROM "{args.table}"{order}{limit}').fetchall()
    total = count(con, args.table)
    if args.csv:
        out = Path(args.csv) if Path(args.csv).is_absolute() else Path.cwd() / args.csv
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(head)
            w.writerows([[r[c] for c in head] for r in rows])
        say(f"Saved {n_of(len(rows), 'row')} of {args.table} to {out} (opens in Excel).")
    if args.note:
        out = Path(args.note) if Path(args.note).is_absolute() else Path.cwd() / args.note
        out.parent.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y-%m-%d %H:%M")
        intro = (f"Made from the database on {stamp}, {n_of(len(rows), 'row')}, newest first. "
                 "Ask the tool to show it again to bring it up to date.")
        text = [f"# {args.table}", "", intro, ""]
        text += markdown_table(head, rows, None)
        out.write_text("\n".join(text) + "\n", encoding="utf-8")
        say(f"Saved {n_of(len(rows), 'row')} of {args.table} as a note: {out}")
    if not args.csv and not args.note:
        say(f"{args.table}: {n_of(total, 'row')}, showing the newest {len(rows)}.")
        for line in markdown_table(head, rows, 60):
            say(line)
    return 0


def cmd_stats(_args) -> int:
    con = connect()
    memory, found_in = find_memory()
    docs = count(con, "documents")
    say(f"Database: {shown(DB_FILE)} ({DB_FILE.stat().st_size / 1_000_000:.1f} MB)")
    say(f"Files in the search: {docs}, cut into {count(con, 'passages')} passages.")
    for r in con.execute("SELECT folder, count(*) AS n FROM documents GROUP BY folder ORDER BY n DESC"):
        say(f"  {r['folder']}: {n_of(r['n'], 'file')}")
    kinds = con.execute("SELECT kind, count(*) AS n FROM documents GROUP BY kind ORDER BY n DESC").fetchall()
    if kinds:
        say("  by type: " + ", ".join(f"{r['kind']} {r['n']}" for r in kinds))
    last = con.execute("SELECT max(indexed_at) FROM documents").fetchone()[0]
    say(f"Last file read: {last or 'never'}")
    if memory:
        state = "found" if memory.is_dir() else "missing"
        say(f"Agent Memory folder: {memory} ({state}; path from {found_in})")
    else:
        say("Agent Memory folder: path not written in AGENTS.md or extras/AGENTS.starter.md yet, so it is not searched.")
    empty = con.execute("SELECT path, note FROM documents WHERE note IS NOT NULL ORDER BY path").fetchall()
    if empty:
        say(f"Files with no searchable text: {len(empty)}")
        for r in empty[:20]:
            say(f"  {r['path']}: {r['note']}")
    say("Your lists: " + (", ".join(f"{t} ({n_of(count(con, t), 'row')})" for t in own_tables(con)) or "none"))
    return 0


SHAPE_HEADING = re.compile(r"^#{2,4}\s+`([A-Za-z_][A-Za-z0-9_]*)`")


def shape_sections(text: str) -> dict[str, str]:
    """Each `table` heading in SHAPE.md and the text under it, up to the next heading."""
    sections: dict[str, str] = {}
    current = None
    for line in text.splitlines():
        m = SHAPE_HEADING.match(line)
        if m:
            current = m.group(1)
            sections[current] = ""
        elif line.startswith("#"):
            current = None
        elif current:
            sections[current] += line + "\n"
    return sections


def cmd_check(_args) -> int:
    problems = []
    if not has_fts5():
        problems.append("This Python's SQLite has no FTS5, so the search cannot work. Run the script with uv.")
    con = connect()
    if con.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
        problems.append("The database file is damaged. Copy the newest file from database/backups/ back, or delete data.db and run index again.")
    try:
        con.execute("INSERT INTO passages_search(passages_search) VALUES ('integrity-check')")
    except sqlite3.DatabaseError:
        problems.append("The search part is out of step. Fix: uv run database/db.py index --rebuild")

    planned = sqlite3.connect(":memory:")
    planned.row_factory = sqlite3.Row
    try:
        planned.executescript(SCHEMA_FILE.read_text(encoding="utf-8"))
    except sqlite3.DatabaseError as e:
        problems.append(f"database/schema.sql has a mistake: {e}")
    live = set(table_names(con))
    plan = set(table_names(planned))
    for t in sorted(plan - live):
        problems.append(f"schema.sql has a list {t} that the database does not have.")
    for t in sorted(live - plan):
        problems.append(f"The database has a list {t} that schema.sql does not have.")
    for t in sorted(plan & live):
        missing = [c for c in columns(planned, t) if c not in columns(con, t)]
        extra = [c for c in columns(con, t) if c not in columns(planned, t)]
        if missing:
            problems.append(f"{t}: schema.sql has columns the database does not: {', '.join(missing)}")
        if extra:
            problems.append(f"{t}: the database has columns schema.sql does not: {', '.join(extra)}")

    try:
        sections = shape_sections(SHAPE_FILE.read_text(encoding="utf-8"))
    except OSError:
        sections = {}
        problems.append("database/SHAPE.md is missing.")
    for t in sorted(live):
        if t not in sections:
            problems.append(f"SHAPE.md does not describe the list {t}.")
            continue
        undocumented = [c for c in columns(con, t) if f"`{c}`" not in sections[t]]
        if undocumented:
            problems.append(f"SHAPE.md does not describe these columns of {t}: {', '.join(undocumented)}")
    for t in sorted(set(sections) - live):
        problems.append(f"SHAPE.md describes a list {t} that the database does not have.")

    if problems:
        say("Problems found:")
        for p in problems:
            say(f"  - {p}")
        return 1
    say(f"All checks passed: {len(live)} lists, matching schema.sql and SHAPE.md, and the search is in step.")
    return 0


def cmd_rebuild_search(con: sqlite3.Connection) -> None:
    con.execute("DELETE FROM passages")
    con.execute("DELETE FROM documents")
    con.execute("INSERT INTO passages_search(passages_search) VALUES ('rebuild')")
    con.commit()


DELETING = re.compile(r"\b(DROP|DELETE|TRUNCATE)\b", re.IGNORECASE)


def cmd_change(args) -> int:
    if args.file:
        sql = Path(args.file).read_text(encoding="utf-8")
    else:
        sql = " ".join(args.sql).strip()
    if not sql:
        say('Give the change as SQL, for example: uv run database/db.py change "ALTER TABLE items ADD COLUMN course TEXT"')
        return 2
    if DELETING.search(sql) and not args.allow_delete:
        say("This change deletes a list, a column or rows, so it was not made. Ask the person first, "
            "naming exactly what goes; after their yes, run it again with --allow-delete.")
        return 3
    con = connect()
    BACKUPS.mkdir(exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    backup = BACKUPS / f"data-{stamp}.db"
    n = 1
    while backup.exists():
        n += 1
        backup = BACKUPS / f"data-{stamp}-{n}.db"
    copy = sqlite3.connect(backup)
    con.backup(copy)
    copy.close()
    try:
        con.executescript("BEGIN;\n" + sql + "\n;COMMIT;")
    except sqlite3.DatabaseError as e:
        if con.in_transaction:
            con.execute("ROLLBACK")
        say(f"The change was not made: {e}. The database is as it was.")
        return 2
    say(f"Changed. A copy from before the change is in {shown(backup)}.")
    say("If the shape changed, describe it in database/SHAPE.md and database/schema.sql, then run: uv run database/db.py check")
    return 0


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Your database: a search over your files and your own lists.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init", help="make the database (safe to run again)")
    p = sub.add_parser("index", help="read new and changed files into the search")
    p.add_argument("--path", action="append", help="also read this folder (can be given more than once)")
    p.add_argument("--rebuild", action="store_true", help="forget every file and read them all again")
    p = sub.add_parser("search", help="find passages that contain these words")
    p.add_argument("words", nargs="+")
    p.add_argument("--limit", type=int, default=8, help="how many passages to show (default 8)")
    p.add_argument("--in", dest="inside", default="", help="only files whose path contains this text")
    p.add_argument("--any", action="store_true", help="passages with any of the words, not all")
    p.add_argument("--full", action="store_true", help="print each passage in full")
    p.add_argument("--no-freshness", action="store_true", help="skip the check for files changed since the last index")
    p = sub.add_parser("add", help='add a row to a list: add items title="Call Ana" kind=contact')
    p.add_argument("table")
    p.add_argument("values", nargs="*")
    sub.add_parser("tables", help="every list, its columns and how many rows")
    p = sub.add_parser("show", help="print a list, or save it with --csv or --note")
    p.add_argument("table")
    p.add_argument("--limit", type=int, default=None, help="how many rows (default 20 on screen, all when saving)")
    p.add_argument("--csv", help="save it as a spreadsheet file (CSV) that opens in Excel")
    p.add_argument("--note", help="save it as a markdown note, for example in Agent Memory to read in Obsidian")
    sub.add_parser("stats", help="what the search holds and which folders it reads")
    sub.add_parser("check", help="check the database against schema.sql and SHAPE.md")
    p = sub.add_parser("change", help="change the shape with SQL; a copy goes to database/backups/ first")
    p.add_argument("sql", nargs="*")
    p.add_argument("--file", help="read the SQL from this file")
    p.add_argument("--allow-delete", action="store_true", help="only after the person said yes to deleting")
    args = ap.parse_args(argv)

    if args.cmd == "show":
        args.limit_given = args.limit is not None
        if args.limit is None:
            args.limit = 20
    if args.cmd == "index" and args.rebuild:
        cmd_rebuild_search(connect())
    commands = {
        "init": cmd_init, "index": cmd_index, "search": cmd_search, "add": cmd_add, "tables": cmd_tables,
        "show": cmd_show, "stats": cmd_stats, "check": cmd_check, "change": cmd_change,
    }
    return commands[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
