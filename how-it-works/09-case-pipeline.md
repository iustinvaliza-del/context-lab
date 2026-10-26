# The case pipeline

The `prep-case` skill (in `.claude/skills/` and `.agents/skills/`) tells the tool how to prep an IESE case. It uses the scripts in `pipeline/`, which run with `uv`; uv installs Python and each script's packages the first time.

## What happens when they ask "prep the case for session 5 of Corporate Finance"

1. The first time only: the tool asks which course and session they have next. `pipeline/blackboard.py start --course "<course>"` opens a Blackboard window, and they sign in there. It lists all their courses in `library/IESE/COURSES.md` and sets up the course they have next first: its folder in `library/IESE/1st year/` or `library/IESE/2nd year/` and its syllabus. That session is fetched and prepped straight away, while `blackboard.py rest` downloads every other course in the background.
2. It offers to save their login. On yes, `blackboard.py save-login` opens a small window, and the email and password go into Windows Credential Manager or the Mac Keychain. You never see the password, and it is never in a file. `blackboard.py forget-login` removes it.
3. `blackboard.py session --course ... --session 5` downloads that session's files, every time, because professors add files close to class.
4. `read_case.py` prints the case text and its tables, and saves images of exhibit pages so numbers can be checked against the page.
5. The tool writes pre-notes, then case notes by question, with their positions left blank.
6. For cases with numbers: Python computes every number first; `workbook.py` builds an Excel file with yellow inputs, formulas and a Checks sheet; `check_workbook.py` recalculates it in Python and prints OK or FAIL for each row. A number is quoted only after "All checks OK".

## Questions they may ask

- "Where are my files?" In `library/IESE/<year>/<course>/`, inside Blackboard's own folders. Session N is the folder that starts "Session N_".
- "How does it know my year?" From Blackboard: the course name says the class ("MBA 2027" graduates in 2027), and the course's term or dates, or the day they were enrolled in it, say which academic year it ran in; the academic year starts in August. In 2026-27 the class of 2027 is in its 2nd year: its courses from 2025-26 go in `1st year` and this year's in `2nd year`. The class of 2028 is in `1st year`, and all its courses go there. `library/IESE/COURSES.md` marks the courses running this year as current, and the background download fetches those first. A course with no class in its name goes in `library/IESE/Other courses/`. If a course lands in the wrong year, say so and the tool moves its folder.
- "Is my password safe?" It is in the computer's own password store, the same place the browser keeps saved passwords. It is not in this folder, not in git and not in the chat.
- "Why did a window open again?" Blackboard's session expired and no login is saved, or Microsoft asked for a phone prompt.
- "Why Python and Excel both?" Python computes the numbers; the workbook lets them see and change the model in class. The check proves the two agree.
- "Does it work on a Mac?" Yes. Only setting up Excel's own Solver needs Windows with Excel.

How to say it: "I ran the Blackboard script for session 5, read the case, and checked every number in Python before putting it in the notes."
