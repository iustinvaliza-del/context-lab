---
name: prep-case
description: Prep an IESE class session from Blackboard - fetch the session's files, read the case, write pre-notes and case notes with the person's positions left blank, and for cases with numbers a Python-checked Excel workbook. Use when the person asks to prep a case, a class or a session, or to set up their courses.
---

# Prep a case

Turns "prep the case for session 5 of Corporate Finance" (or "prep tomorrow's case", "set up my courses") into notes the person takes to class. Read the case yourself and write the notes yourself. Every path below is relative to this project folder.

The tools are in `pipeline/` and run with `uv run`, which installs what each script needs the first time. If `uv` is not found, call it by its full path: `~/.local/bin/uv` on a Mac, on Windows `~/.local/bin/uv.exe` in Git Bash or `& "$env:USERPROFILE\.local\bin\uv.exe"` in PowerShell.

| Tool | What it does |
|---|---|
| `pipeline/blackboard.py` | Signs in to Blackboard, builds `IESE/`, downloads files |
| `pipeline/read_case.py` | Prints a case PDF's text and tables, and saves page images of exhibits |
| `pipeline/workbook.py` | Builds the Excel workbook: Inputs, exhibit sheets, Checks |
| `pipeline/check_workbook.py` | Calculates the workbook in Python and prints the Checks rows |
| `pipeline/solver_runner.py` | Runs Excel's own Solver (Windows with Excel only, optional) |
| `pipeline/examples/` | One worked example per case type |

## Before anything: the first run

If `IESE/COURSES.md` does not exist, the person's courses are not set up yet. Do this first, then carry on with the prep:

1. Tell them: "A Blackboard window will open. Sign in with your IESE email and password, and approve the phone prompt if Microsoft asks."
2. Run `uv run pipeline/blackboard.py start` with the longest timeout the tool allows (10 minutes in Claude Code). It waits for the sign-in, finds every course they are enrolled in, makes a folder for each year under `IESE/` (`1st year`, `2nd year`, and `Other courses` when Blackboard does not say the year) with one folder per course inside it, copies Blackboard's folders inside each course, downloads each course's syllabus or outline, and writes `IESE/COURSES.md`.
3. Start `uv run pipeline/blackboard.py rest` in the background (the rest of the files, one at a time). Do not wait for it: the prep needs only the syllabus and the session's own files.
4. If the output says there is no saved login, ask once: "Save your IESE email and password for next time, so the pipeline signs in by itself? They go into this computer's password store, not into a file." On yes, run `uv run pipeline/blackboard.py save-login`: a small window asks for them. Never ask them to type the password in the chat, and never read it back. On no, carry on: each run that finds the Blackboard session expired opens the sign-in window again.

## Model and budget

- Use the strongest model the tool offers. If the session runs a small model, say so and ask whether to continue.
- You do not do arithmetic in your head. Python computes every number first, and the workbook must agree with Python before a number is quoted.
- Deliverable 1 (pre-notes and notes): about 12 tool calls. Deliverable 2 (the workbook, for cases with numbers): about 10 more. Batch independent calls. Over budget: deliver what exists, say what is left, and ask before continuing.

## Steps

1. **Target.** Find the course and the session number from what they said, `IESE/COURSES.md` and the course's `Syllabus.md`. If the course has no `Syllabus.md` yet, read its syllabus or outline file with `read_case.py` and write `IESE/<year>/<Course>/Syllabus.md`: one row per session with number, date, title, case or reading, and the prep questions word for word. For "today" or "tomorrow", run `date` and match the dates in `Syllabus.md`. Unsure which session: ask; never guess from the order of the syllabus.
2. **Fetch the session.** Always, even when the folder already has files, because professors add slides and readings close to class: `uv run pipeline/blackboard.py session --course "<course>" --session N` (10-minute timeout; a sign-in window may open). Lines with `+` are new files, `=` were already there. Name the new ones in your reply. If the run stops because the sign-in was not completed, prep from the files already on disk and say "Blackboard not checked" at the top of your reply. "No files in a Session N_ folder" can mean the syllabus and Blackboard number sessions differently: check `--session N+1` or `N-1` once and say what you found.
3. **Read.** `uv run pipeline/read_case.py "<case.pdf>" ["<reading.pdf>"] --out "<session folder>/_pages"`. It prints each page's text, each table as markdown, and saves images of the pages with tables or little text. Before using a number from an exhibit, open that page's image and check the number against it; when an exhibit got no image (its table was not found), check it against the page text and say so in the notes. Spreadsheets that come with the case: read them with Python (openpyxl or pandas).
4. **Pre-notes first.** Name every file after the case in capitals with underscores, for example `BRISA_BIKES`: that is `<CASE>` below. Write `<CASE>_PRE_NOTES.md` in the session folder (outline below) and show it before asking them anything about the case or writing the full notes. They may not have read the case: a question about an assumption means nothing without it.
5. **Classify** by the questions, not by the course name:
   - **Discussion**: judgement, people, strategy, ethics. No number is asked for.
   - **Quantitative**: the questions ask for numbers that are not an optimisation: valuation, NPV, payback, financial statements, costing, break-even, cash needs, a decision tree, capacity or a bottleneck.
   - **Data**: the case comes with a data file and asks what the data says: regression, forecast, A/B test, churn.
   - **Optimisation**: the case or syllabus says optimise, maximise or minimise subject to limits, or hands over a model to solve.
   The table at the end says what each first-year course usually asks for.
6. **Discussion case.** Write `<CASE>_CASE_NOTES.md` (outline below), organised by the prep questions, with page references and the evidence on both sides of every judgement. Example: `pipeline/examples/discussion.md`.
7. **Quantitative or data case.**
   - a. Compute every number the questions ask for in Python first (a short script in the session's `_build/` folder). This is the independent check.
   - b. Deliverable 1: the notes, with those numbers marked "workbook check: pending".
   - c. Deliverable 2: `_build/build_<CASE>.py` builds `<CASE>_WORKBOOK.xlsx` with `pipeline/workbook.py`: inputs in yellow on Inputs with their sources, formulas everywhere else, and a Checks sheet that compares each key result's formula with its Python value. Compute the expected values in the build script itself (or import them from the Python script), never retype them rounded: the check allows only rounding to two decimals for numbers above 1 and to four for rates. Start the script with a `uv` header that lists `openpyxl` (and `numpy`, `pandas` or `scipy` if it uses them), put the project's `pipeline/` folder on `sys.path` (the example shows how), and run it with `uv run`.
   - d. Run `uv run pipeline/check_workbook.py "<workbook>"`. When it prints "All checks OK", change the notes to "workbook check: passed". A FAIL means the workbook or the Python is wrong: find which, fix it, run again.
   Examples: `pipeline/examples/quantitative.md`, `pipeline/examples/data.md`.
8. **Optimisation case.**
   - a. Solve it in Python first: scipy `linprog(method="highs")`, or `milp` for whole numbers. Get the plan, the objective, the shadow prices (`-res.ineqlin.marginals` for a maximisation written as `<=` rows) and every scenario the case asks about.
   - b. Notes organised by the case's questions, numbers marked "workbook check: pending".
   - c. The workbook lays the model out with formulas (SUMPRODUCT rows for the objective and each limit) at the Python optimum, with Checks rows for the objective and each limit's usage; `check_workbook.py` then proves the layout matches the Python solve. On Windows with Excel installed, `pipeline/solver_runner.py` can also set up and run Excel's own Solver in the file, so they can re-solve it in class; on a Mac, say that Solver setup is left to them.
   Example: `pipeline/examples/optimisation.md`.
9. **Deliver.** Point to the pre-notes, the notes and the workbook with their full paths. In a few lines: what the session teaches, the key facts or answers, every assumption you made (so they can correct it), and the positions they should bring. Never fill their positions in.
10. **Log.** Add a row to `IESE/PREP_LOG.md` (make it with a header if missing): date, course, session, case, type, what was delivered, and whether Blackboard was checked.

## Pre-notes outline: `<CASE>_PRE_NOTES.md`

One to two screens, plain words, no positions, no analysis.

- `# <Case> - pre-notes for Session N`, then course, date, and what there is to read.
- What the class is about, in two or three sentences.
- The story: who, where, when, what happened, five to ten lines with page references.
- The decision on the table and who makes it.
- The cast: each person or company and their role.
- The handful of numbers that matter, with page references.
- Terms a non-specialist would not know, one line each.
- The prep questions in plain words.
- What you will ask them during the prep (assumptions to confirm, positions to take), each with one line of context; "nothing" if there is nothing.

A session with no case (a lecture, a guest, an exercise): say what the session is, the background a newcomer needs, and how it connects to the sessions around it.

## Notes outline: `<CASE>_CASE_NOTES.md`

- `# <Case> - case notes for Session N`, then course, date, authors and length, and the readings.
- What the session teaches, first.
- The prep questions from `Syllabus.md`, numbered.
- The situation and the decision: a pointer to the pre-notes plus anything they leave out.
- Facts and numbers, each exhibit number checked against the page image; mark your own arithmetic as such.
- Material by question, with the evidence on both sides.
- The framework the course teaches, applied.
- The readings, summarised.
- Where the case is loose: inconsistencies, typos, numbers that do not add up.
- Your positions to bring to class: left blank for them.

## Rules

- Teach first: they should understand the case, not only have answers.
- Their positions are theirs. Never fill them in.
- Every assumption is visible, in the notes and on the workbook's Cover sheet.
- Numbers from the workbook only after `check_workbook.py` prints "All checks OK".
- Hand-ins: only they know which cases are graded hand-ins; never infer it.
- Case PDFs are copyrighted: paraphrase, with at most one short quote. `IESE/` stays out of git.

## What first-year IESE courses usually ask for

A guide from one student's first year (MBA 2027). The questions decide the type, not the course.

| Course | Usual type | Typical numbers |
|---|---|---|
| Analysis of Business Problems | Quantitative and discussion | Cash flow, financial statements, a business decision |
| Business Analytics | Data | Regression, classification, A/B tests on a data file |
| Business Ethics, Leadership, Communication | Discussion | None |
| Competitive Strategy, Global Economics | Discussion, some numbers | Industry economics, macro data |
| Corporate Finance | Quantitative | NPV, WACC, valuation, capital structure |
| Decision Analysis | Quantitative | Decision trees, expected value, value of information |
| Financial Accounting | Quantitative | Statements, ratios, journal entries |
| Managerial Accounting | Quantitative | Costing, contribution margin, budgets |
| Operational Finance | Quantitative | Working capital, cash budgets, financing needs |
| Operations Management | Quantitative, some optimisation | Process capacity, bottlenecks, queues, inventory |
| Operations Strategy | Discussion, some numbers | Capacity and network choices |
| Marketing Management, Marketing Planning | Discussion, some numbers | Break-even, customer lifetime value, market size |
| Fundamentals of Entrepreneurial Management | Discussion, some numbers | Unit economics, cap tables |
