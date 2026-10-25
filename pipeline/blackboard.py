# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "playwright>=1.45",
#   "keyring>=24",
# ]
# ///
"""Blackboard downloader for the case pipeline.

Signs in to IESE Blackboard (vc.iese.edu) in a browser that is already on the laptop (Edge or
Chrome), finds every course the person is enrolled in, builds a folder per course under
IESE/<year>/ in this project ("1st year", "2nd year"), and downloads the course materials
through Blackboard's REST API.

    uv run pipeline/blackboard.py start            first run: sign in, build every course folder,
                                                   download each course's syllabus and outline
    uv run pipeline/blackboard.py session --course "Corporate Finance" --session 5
                                                   download one session's folder (the case to prep)
    uv run pipeline/blackboard.py rest             download everything else, one file at a time
    uv run pipeline/blackboard.py list             print the courses and their folders
    uv run pipeline/blackboard.py save-login       ask for the IESE email and password in a small
                                                   window and keep them in the computer's password
                                                   store (Windows Credential Manager, Mac Keychain)
    uv run pipeline/blackboard.py forget-login     remove them again
    uv run pipeline/blackboard.py check            install what this script needs and find a browser

Files land in IESE/<year>/<course>/<Blackboard folders>/<file>, for example
IESE/1st year/Corporate Finance/Materials/Session 5_ Pacific Grove/Pacific_Grove.pdf. Blackboard's
own folder names are kept, so session N is always the folder that starts "Session N_".

The year comes from Blackboard: a term name that says "Year 1" or "Year 2", or else the class in
the course name ("MBA 2027 - ...", the year the class graduates) set against the academic year the
course runs in (from the term's name or start date, or else today's date; the academic year starts
in August). The class of 2027 is in its 2nd year in 2026-27. A course whose year cannot be told
goes in IESE/Other courses/. CASE_COURSES_DIR=<folder> puts the IESE folder somewhere else.

Signing in: without a saved login, a browser window opens and the person signs in there
(email, password and any phone prompt). With a saved login the run signs in by itself and
opens the window only when Microsoft asks for something it cannot answer, such as a code.
The password is never printed, logged or written to a file in this project.

The list of downloaded files is in pipeline/.state/, which git ignores. The browser profile that
keeps the Blackboard sign-in is outside the project, in the user's app data folder
(context-lab/browser), so a synced Desktop folder does not have to sync it.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
# The IESE folder: one folder per year inside, one folder per course inside each year.
IESE = Path(os.environ.get("CASE_COURSES_DIR") or PROJECT / "IESE")
OTHER_YEAR = "Other courses"
STATE = HERE / ".state"


def user_data_dir() -> Path:
    """The browser profile lives outside the project: Desktop folders are often synced by
    OneDrive or iCloud, and a browser profile is thousands of small files that change constantly."""
    if os.environ.get("PIPELINE_PROFILE"):
        return Path(os.environ["PIPELINE_PROFILE"])
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
    return base / "context-lab" / "browser"


PROFILE = user_data_dir()
MANIFEST = STATE / "manifest.json"
COURSE_LIST = STATE / "courses.json"

BB_BASE = (os.environ.get("BLACKBOARD_URL") or "https://vc.iese.edu").rstrip("/")
BB_API = f"{BB_BASE}/learn/api/public/v1"
BB_UI = f"{BB_BASE}/ultra/course"

KEYRING_SERVICE = "context-lab IESE Blackboard"
WINDOW_MINUTES = 9  # under the 10-minute limit Claude Code puts on one command
# Seconds between downloads in `rest`, so a room of laptops does not hit Blackboard at once.
PAUSE = float(os.environ.get("PIPELINE_PAUSE", "0.5"))

SYLLABUS_WORDS = re.compile(r"syllab|outline|programa|schedule|calendar|course guide", re.I)


def say(text: str = "") -> None:
    print(text, flush=True)


class NotSignedIn(Exception):
    pass


# ─── Saved login (the computer's password store) ────────────────────────────

def load_login() -> dict | None:
    """The saved email and password, or None. Environment variables win, for testing."""
    if os.environ.get("IESE_EMAIL") and os.environ.get("IESE_PASSWORD"):
        return {"email": os.environ["IESE_EMAIL"], "password": os.environ["IESE_PASSWORD"], "source": "environment"}
    try:
        import keyring
        email = keyring.get_password(KEYRING_SERVICE, "email")
        password = keyring.get_password(KEYRING_SERVICE, email) if email else None
    except Exception:
        return None
    if email and password:
        return {"email": email, "password": password, "source": "password store"}
    return None


def store_login(email: str, password: str) -> None:
    import keyring
    keyring.set_password(KEYRING_SERVICE, "email", email)
    keyring.set_password(KEYRING_SERVICE, email, password)


def forget_login() -> bool:
    import keyring
    email = keyring.get_password(KEYRING_SERVICE, "email")
    if not email:
        return False
    for key in (email, "email"):
        try:
            keyring.delete_password(KEYRING_SERVICE, key)
        except Exception:
            pass
    return True


def ask_login() -> tuple[str, str] | None:
    """Email and password from a small window, so the password never passes through the chat."""
    try:
        return _ask_tk()
    except Exception:
        pass
    if sys.platform == "win32":
        return _ask_windows()
    if sys.platform == "darwin":
        return _ask_mac()
    if sys.stdin.isatty():
        import getpass
        email = input("IESE email: ").strip()
        return (email, getpass.getpass("IESE password: ")) if email else None
    raise RuntimeError("no way to show a login window on this computer")


def _ask_tk() -> tuple[str, str] | None:
    import tkinter as tk
    result: dict = {}
    root = tk.Tk()
    root.title("Save your IESE login")
    root.attributes("-topmost", True)
    tk.Label(root, text="Saved in this computer's password store, for the case pipeline only.").grid(row=0, column=0, columnspan=2, padx=12, pady=(12, 8))
    tk.Label(root, text="IESE email").grid(row=1, column=0, sticky="e", padx=8)
    email = tk.Entry(root, width=34)
    email.grid(row=1, column=1, padx=8, pady=4)
    tk.Label(root, text="Password").grid(row=2, column=0, sticky="e", padx=8)
    password = tk.Entry(root, width=34, show="•")
    password.grid(row=2, column=1, padx=8, pady=4)

    def save(_event=None):
        result["email"], result["password"] = email.get().strip(), password.get()
        root.destroy()

    buttons = tk.Frame(root)
    buttons.grid(row=3, column=0, columnspan=2, pady=12)
    tk.Button(buttons, text="Save", width=10, command=save).pack(side="left", padx=6)
    tk.Button(buttons, text="Cancel", width=10, command=root.destroy).pack(side="left", padx=6)
    root.bind("<Return>", save)
    email.focus_force()
    root.mainloop()
    if result.get("email") and result.get("password"):
        return result["email"], result["password"]
    return None


def _ask_windows() -> tuple[str, str] | None:
    script = (
        "$c = Get-Credential -Message 'Your IESE email and password, saved in Windows Credential Manager for the case pipeline';"
        "if ($c) { @{email=$c.UserName; password=$c.GetNetworkCredential().Password} | ConvertTo-Json -Compress }"
    )
    out = subprocess.run(["powershell", "-NoProfile", "-Command", script], capture_output=True, text=True)
    if out.returncode != 0 or not out.stdout.strip():
        return None
    data = json.loads(out.stdout)
    return data["email"], data["password"]


def _ask_mac() -> tuple[str, str] | None:
    def dialog(prompt: str, hidden: bool) -> str | None:
        script = f'text returned of (display dialog "{prompt}" default answer ""{" with hidden answer" if hidden else ""} with title "Save your IESE login")'
        out = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
        return out.stdout.rstrip("\n") if out.returncode == 0 else None
    email = dialog("Your IESE email", False)
    password = dialog("Your IESE password (kept in the Mac Keychain)", True) if email else None
    return (email.strip(), password) if email and password else None


# ─── Browser ─────────────────────────────────────────────────────────────────

def launch(pw, headless: bool):
    """A browser with this project's own profile: Edge, then Chrome, then Playwright's Chromium."""
    PROFILE.mkdir(parents=True, exist_ok=True)
    opts = dict(user_data_dir=str(PROFILE), headless=headless, viewport={"width": 1280, "height": 900},
                args=["--no-sandbox"] if sys.platform.startswith("linux") else [])
    exe = os.environ.get("PIPELINE_BROWSER")
    if exe:
        return pw.chromium.launch_persistent_context(executable_path=exe, **opts)
    errors = []
    for channel in ("msedge", "chrome"):
        try:
            return pw.chromium.launch_persistent_context(channel=channel, **opts)
        except Exception as e:  # not installed
            _stop_if_profile_busy(e)
            errors.append(f"{channel}: {str(e).splitlines()[0]}")
    try:
        return pw.chromium.launch_persistent_context(**opts)
    except Exception as e:
        _stop_if_profile_busy(e)
        say("[blackboard] Neither Edge nor Chrome was found, so downloading a browser for this script (once).")
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        return pw.chromium.launch_persistent_context(**opts)


def _stop_if_profile_busy(error: Exception) -> None:
    """Another run of this script is signing in with the same browser profile: say so, never download a browser."""
    if re.search(r"ProcessSingleton|already in use", str(error)):
        say("[blackboard] Another download from this script is signing in right now. Wait a minute and run it again.")
        sys.exit(3)


def can_show_window() -> bool:
    return sys.platform in ("win32", "darwin") or bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


def logged_in(url: str) -> bool:
    return url.startswith(BB_BASE) and not re.search(r"login|saml", url, re.I)


def settle(page) -> None:
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except Exception:
        pass


# Microsoft's sign-in screens, as IESE shows them.
PASSWORD = 'input[name="passwd"]'
EMAIL = 'input[name="loginfmt"]'
SUBMIT = "#idSIButton9"
KMSI = "#KmsiCheckboxField"
ERRORS = ["#passwordError", "#usernameError"]
ANY_TILE = '#tilesHolder [data-test-id]:not([data-test-id$="-menu-dots"])'


def _visible(page, sel: str) -> bool:
    try:
        return page.locator(sel).first.is_visible()
    except Exception:
        return False


def _click(page, sel: str, timeout: int = 5000) -> bool:
    # Microsoft lays a progress cover over the page while it moves on by itself, which blocks
    # clicks for a moment: a click that fails reports False so the loop looks again.
    try:
        page.locator(sel).first.click(timeout=timeout)
        return True
    except Exception:
        return False


def sign_in_microsoft(page, login: dict, step_delay: float = 1.5, max_steps: int = 8, max_idle: int = 6) -> bool:
    """Walk Microsoft's screens with the saved login until the page is back on Blackboard.

    Returns False on a rejected password or a screen it does not know (a code prompt, for
    example), so the caller can open the sign-in window instead. The password is submitted at
    most once: sending a wrong one again could lock the account.
    """
    tile = f'#tilesHolder [data-test-id="{login["email"]}"]'
    password_sent = False
    idle = steps = 0
    while steps < max_steps:
        if page.url.startswith(BB_BASE):
            return True
        if any(_visible(page, sel) for sel in ERRORS):
            # A wrong saved password sent on every run could lock the account, so it is removed.
            if login.get("source") == "password store":
                forget_login()
                say("[blackboard] Microsoft did not accept the saved login, so it was removed. Sign in in the window; "
                    "to save the right one, run: uv run pipeline/blackboard.py save-login")
            else:
                say("[blackboard] Microsoft did not accept the saved login.")
            return False
        acted = False
        if _visible(page, PASSWORD):
            if not password_sent:
                page.locator(PASSWORD).first.fill(login["password"])
                acted = password_sent = _click(page, SUBMIT)
        elif _visible(page, KMSI):
            acted = _click(page, SUBMIT)
        elif _visible(page, tile):
            acted = _click(page, tile)
        elif _visible(page, ANY_TILE):
            acted = _click(page, ANY_TILE)
        elif _visible(page, EMAIL):
            page.locator(EMAIL).first.fill(login["email"])
            acted = _click(page, SUBMIT)
        if not acted:
            idle += 1
            if idle >= max_idle:
                return False
            time.sleep(step_delay)
            continue
        steps += 1
        idle = 0
        settle(page)
        time.sleep(step_delay)
    return page.url.startswith(BB_BASE)


def open_session(pw, allow_window: bool = True):
    """A signed-in browser context; main() keeps its cookies for the downloads and closes it."""
    context = launch(pw, headless=True)
    page = context.new_page()
    page.goto(BB_UI, wait_until="domcontentloaded", timeout=30000)
    settle(page)
    if not logged_in(page.url):
        login = load_login()
        if login:
            say(f"[blackboard] Signing in with the saved login ({login['source']}).")
            try:
                if sign_in_microsoft(page, login):
                    settle(page)
            except Exception as e:
                say(f"[blackboard] Signing in with the saved login stopped: {str(e).splitlines()[0]}")
    if logged_in(page.url):
        return keep_cookies(context)

    context.close()
    if not allow_window or not can_show_window():
        raise NotSignedIn("not signed in to Blackboard, and no sign-in window was allowed")
    # The profile allows one browser at a time, so the hidden one is closed first.
    context = launch(pw, headless=False)
    page = context.pages[0] if context.pages else context.new_page()
    page.goto(BB_UI, wait_until="domcontentloaded", timeout=30000)
    say(f"[blackboard] A Blackboard sign-in window is open. Sign in there with your IESE email and password, "
        f"and answer any phone prompt. Waiting up to {WINDOW_MINUTES} minutes.")
    try:
        page.wait_for_url(lambda u: logged_in(u), timeout=WINDOW_MINUTES * 60 * 1000)
    except Exception:
        context.close()
        raise NotSignedIn("the sign-in window was not completed")
    settle(page)
    say("[blackboard] Signed in.")
    return keep_cookies(context)


def keep_cookies(context):
    """Keep Blackboard's sign-in cookies after the browser closes, so the next run starts signed in.

    They are session cookies, which a browser drops when it closes. Blackboard still ends the
    session on its side after a while; then the saved login or the window signs in again.
    """
    host = urlparse(BB_BASE).hostname or ""
    later = int(time.time()) + 365 * 24 * 3600
    cookies = [c for c in context.cookies() if host in c.get("domain", "") or re.search(r"iese|blackboard|microsoftonline", c.get("domain", ""))]
    if cookies:
        context.add_cookies([{**c, "expires": later} for c in cookies])
    return context


# ─── API ─────────────────────────────────────────────────────────────────────

class Api:
    def __init__(self, request):
        self.request = request

    def get(self, path: str, params: dict | None = None):
        resp = self.request.get(BB_API + path, params=params or {}, headers={"Accept": "application/json"},
                                timeout=30000, max_redirects=5)
        try:
            if not resp.ok:
                raise ApiError(resp.status, path)
            return resp.json()
        finally:
            resp.dispose()

    def get_all(self, path: str) -> list:
        results, offset, limit = [], 0, 100
        while True:
            data = self.get(path, {"limit": limit, "offset": offset})
            items = data.get("results") or []
            results.extend(items)
            if not (data.get("paging") or {}).get("nextPage") or len(items) < limit:
                return results
            offset += limit

    def download(self, path: str, dest: Path) -> None:
        resp = self.request.get(BB_API + path, timeout=120000, max_redirects=5)
        try:
            if not resp.ok:
                raise ApiError(resp.status, path)
            dest.parent.mkdir(parents=True, exist_ok=True)
            tmp = dest.with_name(dest.name + ".part")
            tmp.write_bytes(resp.body())
            tmp.replace(dest)
        finally:
            resp.dispose()


class ApiError(Exception):
    def __init__(self, status: int, path: str):
        super().__init__(f"HTTP {status} {path}")
        self.status = status


# ─── Names and folders ───────────────────────────────────────────────────────

def sanitize(name: str | None) -> str:
    # Windows cannot open a folder whose name ends in a dot or a space, so those are cut.
    name = re.sub(r'[<>:"/\\|?*]', "_", name or "Untitled")
    name = re.sub(r"\s+", " ", name).strip()
    return re.sub(r"[. ]+$", "", name)[:100] or "Untitled"


def course_folder_name(blackboard_name: str) -> str:
    """'MBA 2027 - Corporate Finance - NRB' -> 'Corporate Finance'."""
    name = re.sub(r"^MBA \d{4} - ", "", blackboard_name)
    name = re.sub(r" - [A-Z0-9]{1,6}$", "", name)
    return sanitize(name)


YEAR_NAMES = {1: "1st year", 2: "2nd year"}


def _academic_year_end(term: str, term_start: str, today: datetime | None = None) -> int:
    """The calendar year an academic year ends in: 2027 for 2026-27. It starts in August."""
    m = re.search(r"\b(20\d\d)\s*[-/]\s*(?:20)?(\d\d)\b", term)
    if m and (int(m.group(2)) - int(m.group(1)[2:])) % 100 == 1:
        return int(m.group(1)) + 1
    m = re.match(r"(20\d\d)-(\d\d)", term_start)  # Blackboard dates look like 2026-08-24T22:00:00.000Z
    if m:
        year, month = int(m.group(1)), int(m.group(2))
    else:
        when = today or datetime.now()
        year, month = when.year, when.month
    return year + 1 if month >= 8 else year


def course_year(name: str, term: str = "", term_start: str = "", today: datetime | None = None) -> str:
    """'1st year', '2nd year' or 'Other courses', from what Blackboard says about the course."""
    m = re.search(r"\b(?:year\s*([12])|([12])(?:st|nd)\s+year|(first|second)\s+year)\b", term, re.I)
    if m:
        word = (m.group(3) or "").lower()
        return YEAR_NAMES[int(m.group(1) or m.group(2) or (1 if word == "first" else 2))]
    m = re.search(r"\bMBA\s*(20\d\d)\b", name, re.I) or re.search(r"\bMBA\s*(20\d\d)\b", term, re.I)
    if not m:
        return OTHER_YEAR
    # The class graduates in the summer its academic year ends: then it is in its 2nd year.
    year = 2 - (int(m.group(1)) - _academic_year_end(term, term_start, today))
    return YEAR_NAMES.get(year, OTHER_YEAR)


def course_dir(course: dict) -> Path:
    return IESE / course.get("year", OTHER_YEAR) / course["folder"]


def course_label(course: dict) -> str:
    return f"{course.get('year', OTHER_YEAR)} / {course['folder']}"


def session_number(title: str) -> int | None:
    m = re.match(r"Session\s*(\d+)(?!\d)", title, re.I)
    return int(m.group(1)) if m else None


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.{os.getpid()}.tmp")  # one per process: `rest` and `session` can run together
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


def discover_courses(api: Api) -> list[dict]:
    """Every enrolled course with its year and folder name, kept stable in .state/courses.json."""
    known = {c["id"]: c for c in load_json(COURSE_LIST, [])}
    for c in known.values():  # saved by an earlier version, before the year folders
        c.setdefault("year", course_year(c.get("name", ""), c.get("term", "")))
    me = api.get("/users/me")
    enrolments = api.get_all(f"/users/{me['id']}/courses")
    courses, used = [], {(c["year"], c["folder"]) for c in known.values()}
    terms: dict[str, dict] = {}
    for e in enrolments:
        cid = e.get("courseId")
        if not cid:
            continue
        if cid in known:
            courses.append(known[cid])
            continue
        try:
            data = api.get(f"/courses/{cid}")
        except ApiError:
            data = {}
        name = data.get("name") or data.get("courseId") or cid
        term: dict = {}
        if data.get("termId"):
            if data["termId"] not in terms:
                try:
                    terms[data["termId"]] = api.get(f"/terms/{data['termId']}")
                except ApiError:
                    terms[data["termId"]] = {}
            term = terms[data["termId"]]
        term_name = term.get("name") or ""
        term_start = ((term.get("availability") or {}).get("duration") or {}).get("start") or ""
        year = course_year(name, term_name, term_start)
        folder = course_folder_name(name)
        if (year, folder) in used:  # two courses with the same name: add Blackboard's course code
            folder = sanitize(f"{folder} ({data.get('courseId') or cid})")
        used.add((year, folder))
        course = {"id": cid, "name": name, "year": year, "folder": folder, "term": term_name}
        known[cid] = course
        courses.append(course)
    save_json(COURSE_LIST, list(known.values()))
    return courses


def walk(api: Api, course_id: str, parent: str | None = None, parts: tuple = ()):
    """Yield ('folder', parts) for each folder and ('file', parts, item) for each file item."""
    path = f"/courses/{course_id}/contents/{parent}/children" if parent else f"/courses/{course_id}/contents"
    try:
        items = api.get_all(path)
    except ApiError as e:
        if e.status not in (403, 404):
            say(f"  [warn] {path}: HTTP {e.status}")
        return
    for item in items:
        handler = (item.get("contentHandler") or {}).get("id", "")
        title = sanitize(item.get("title"))
        if handler == "resource/x-bb-file":
            yield ("file", parts, item)
        elif handler in ("resource/x-bb-folder", "resource/x-bb-document", "") or item.get("hasChildren"):
            yield ("folder", parts + (title,))
            yield from walk(api, course_id, item["id"], parts + (title,))


def in_session(parts: tuple, number: int | None = None) -> bool:
    return any(session_number(p) is not None and (number is None or session_number(p) == number) for p in parts)


# ─── Downloads ───────────────────────────────────────────────────────────────

class Downloader:
    def __init__(self, api: Api):
        self.api = api
        self.manifest = load_json(MANIFEST, {"files": {}, "lastRun": None})
        self.new = self.skipped = self.failed = 0

    def file_item(self, course: dict, parts: tuple, item: dict, pause: float = 0.0, quiet: bool = False) -> None:
        try:
            attachments = self.api.get_all(f"/courses/{course['id']}/contents/{item['id']}/attachments")
        except ApiError:
            return
        for att in attachments:
            key = f"{course['id']}/{item['id']}/{att['id']}"
            name = sanitize(att.get("fileName") or f"{item.get('title') or 'file'}.bin")
            dest = course_dir(course) / Path(*parts) / name
            shown = " / ".join((course_label(course),) + parts + (name,))
            if dest.exists():  # a file deleted or moved since is fetched again
                self.manifest["files"].setdefault(key, {"path": str(dest)})
                self.skipped += 1
                if not quiet:
                    say(f"  = {shown}")
                continue
            try:
                self.api.download(f"/courses/{course['id']}/contents/{item['id']}/attachments/{att['id']}/download", dest)
                self.manifest["files"][key] = {"path": str(dest), "at": datetime.now(timezone.utc).isoformat()}
                self.new += 1
                say(f"  + {shown}")
            except ApiError as e:
                self.failed += 1
                say(f"  ! {shown} (HTTP {e.status})")
            save_json(MANIFEST, self.manifest)
            if pause:
                time.sleep(pause)

    def finish(self) -> None:
        self.manifest["lastRun"] = datetime.now(timezone.utc).isoformat()
        save_json(MANIFEST, self.manifest)
        say(f"[blackboard] {self.new} new files, {self.skipped} already here, {self.failed} failed.")


def matching(courses: list[dict], text: str) -> list[dict]:
    text = text.lower()
    return [c for c in courses if text in c["folder"].lower() or text in c["name"].lower()
            or text in course_label(c).lower()]


def write_index(courses: list[dict], pending: dict[str, int]) -> None:
    lines = [
        "# My courses",
        "",
        "Built by `pipeline/blackboard.py` from Blackboard. One folder per year (`1st year`, `2nd year`), and in it one "
        "folder per course; inside each course, Blackboard's own folders, so session N is the folder that starts "
        "\"Session N_\". Each course's `Syllabus.md` is written the first time a case from that course is prepped.",
        "",
        "The year comes from the course's name on Blackboard (\"MBA 2027\" is the class that graduates in 2027) and its term.",
    ]
    if any(c.get("year", OTHER_YEAR) == OTHER_YEAR for c in courses):
        lines.append(f"For the courses in `{OTHER_YEAR}/`, Blackboard did not say which year they belong to.")
    lines += [
        "",
        "| Year folder | Course folder | Blackboard name | Term | Files not downloaded yet |",
        "|---|---|---|---|---|",
    ]
    order = {name: i for i, name in enumerate([*YEAR_NAMES.values(), OTHER_YEAR])}
    for c in sorted(courses, key=lambda c: (order.get(c.get("year", OTHER_YEAR), 9), c.get("term") or "", c["folder"])):
        lines.append(f"| {c.get('year', OTHER_YEAR)} | {c['folder']} | {c['name']} | {c.get('term') or ''} | {pending.get(c['id'], 0)} |")
    lines += ["", f"Updated {datetime.now():%Y-%m-%d %H:%M}. Run `uv run pipeline/blackboard.py rest` to download the rest."]
    IESE.mkdir(parents=True, exist_ok=True)
    (IESE / "COURSES.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


# ─── Commands ────────────────────────────────────────────────────────────────

def cmd_start(api: Api, args) -> None:
    courses = discover_courses(api)
    if args.course:
        courses = matching(courses, args.course)
    say(f"[blackboard] {len(courses)} courses. Building the folders and downloading each syllabus.")
    dl = Downloader(api)
    pending: dict[str, int] = {}
    for course in courses:
        root = course_dir(course)
        root.mkdir(parents=True, exist_ok=True)
        say(f"\n[course] {course_label(course)}")
        for entry in walk(api, course["id"]):
            if entry[0] == "folder":
                (root / Path(*entry[1])).mkdir(parents=True, exist_ok=True)
                continue
            _, parts, item = entry
            title = item.get("title") or ""
            if not in_session(parts) and (SYLLABUS_WORDS.search(title) or SYLLABUS_WORDS.search(" ".join(parts)) or not parts):
                dl.file_item(course, parts, item)
            else:
                pending[course["id"]] = pending.get(course["id"], 0) + 1
    dl.finish()
    write_index(courses if not args.course else discover_courses(api), pending)
    say(f"[blackboard] Course folders are in {IESE}, one folder per year. The list is {IESE / 'COURSES.md'}.")
    say(f"[blackboard] {sum(pending.values())} more files wait for `rest`.")
    if not load_login():
        say("[blackboard] No saved login yet. Ask the person whether to save their IESE email and password for "
            "next time; if yes, run: uv run pipeline/blackboard.py save-login")


def cmd_session(api: Api, args) -> None:
    courses = matching(discover_courses(api), args.course)
    if not courses:
        raise SystemExit(f'[blackboard] No course matches "{args.course}". See {IESE / "COURSES.md"} for the names.')
    dl = Downloader(api)
    for course in courses:
        say(f"\n[course] {course_label(course)}, session {args.session}")
        found = 0
        for entry in walk_session(api, course["id"], args.session):
            _, parts, item = entry
            found += 1
            dl.file_item(course, parts, item)
        if not found:
            say(f'  no files in a "Session {args.session}_" folder on Blackboard')
    dl.finish()


def walk_session(api: Api, course_id: str, number: int, parent: str | None = None, parts: tuple = ()):
    """Files inside the session's folder; other sessions' folders are never opened."""
    path = f"/courses/{course_id}/contents/{parent}/children" if parent else f"/courses/{course_id}/contents"
    try:
        items = api.get_all(path)
    except ApiError:
        return
    inside = in_session(parts, number)
    for item in items:
        handler = (item.get("contentHandler") or {}).get("id", "")
        title = sanitize(item.get("title"))
        if handler == "resource/x-bb-file":
            if inside:
                yield ("file", parts, item)
        elif handler in ("resource/x-bb-folder", "resource/x-bb-document", "") or item.get("hasChildren"):
            n = session_number(title)
            if not inside and n is not None and n != number:
                continue
            yield from walk_session(api, course_id, number, item["id"], parts + (title,))


def cmd_rest(api: Api, args) -> None:
    courses = discover_courses(api)
    if args.course:
        courses = matching(courses, args.course)
    dl = Downloader(api)
    for course in courses:
        say(f"\n[course] {course_label(course)}")
        for entry in walk(api, course["id"]):
            if entry[0] == "folder":
                (course_dir(course) / Path(*entry[1])).mkdir(parents=True, exist_ok=True)
            else:
                dl.file_item(course, entry[1], entry[2], pause=PAUSE, quiet=True)
    dl.finish()
    write_index(discover_courses(api), {})


def cmd_list(api: Api, args) -> None:
    for c in discover_courses(api):
        say(f"{course_label(c)}  <-  {c['name']}" + (f"  ({c['term']})" if c.get("term") else ""))


def cmd_save_login(args) -> int:
    if args.from_env:
        pair = (os.environ.get("IESE_EMAIL", ""), os.environ.get("IESE_PASSWORD", ""))
    else:
        say("[blackboard] A small window asks for your IESE email and password.")
        pair = ask_login()
    if not pair or not pair[0] or not pair[1]:
        say("[blackboard] Nothing saved.")
        return 1
    store_login(*pair)
    say(f"[blackboard] Saved the login for {pair[0]} in this computer's password store. "
        "Next runs sign in by themselves; Microsoft may still ask for a phone prompt now and then.")
    return 0


def cmd_check() -> int:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        context = launch(pw, headless=True)
        name = context.browser.browser_type.name if context.browser else "chromium"
        context.close()
    say(f"[blackboard] Ready: the script's packages are installed and a browser starts ({name}).")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Blackboard downloader for the case pipeline.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("start", "rest", "list"):
        p = sub.add_parser(name)
        p.add_argument("--course", default="", help="only courses whose name contains this")
        p.add_argument("--no-window", action="store_true", help="never open a sign-in window")
    p = sub.add_parser("session")
    p.add_argument("--course", required=True)
    p.add_argument("--session", type=int, required=True)
    p.add_argument("--no-window", action="store_true")
    p = sub.add_parser("save-login")
    p.add_argument("--from-env", action="store_true", help="for testing: take IESE_EMAIL and IESE_PASSWORD")
    sub.add_parser("forget-login")
    sub.add_parser("check")
    args = ap.parse_args(argv)

    if args.cmd == "save-login":
        return cmd_save_login(args)
    if args.cmd == "forget-login":
        say("[blackboard] Saved login removed." if forget_login() else "[blackboard] No saved login to remove.")
        return 0
    if args.cmd == "check":
        return cmd_check()

    from playwright.sync_api import sync_playwright
    say(f"[blackboard] Course folders: {IESE}")
    try:
        with sync_playwright() as pw:
            context = open_session(pw, allow_window=not args.no_window)
            # Close the browser once signed in, so a background `rest` never holds the browser profile
            # while `session` needs it; the downloads use the saved cookies instead.
            state = context.storage_state()
            context.close()
            request = pw.request.new_context(storage_state=state)
            try:
                {"start": cmd_start, "session": cmd_session, "rest": cmd_rest, "list": cmd_list}[args.cmd](Api(request), args)
            finally:
                request.dispose()
    except NotSignedIn as e:
        say(f"[blackboard] Stopped: {e}. Run it again and sign in in the window that opens.")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
