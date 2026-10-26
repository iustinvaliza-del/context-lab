# Library

Your library: the material the tool reads before it answers, kept on this computer.

```
library/
  IESE/
    COURSES.md            every course you are enrolled in
    SCHEDULE.md           every class this year by date, from the my.iese.edu agenda
    PREP_LOG.md           one row per case prepped
    1st year/
      Corporate Finance/
        Syllabus.md       one row per session, with the prep questions
        Session 5_.../    Blackboard's files for the session, and the notes written next to the case
    2nd year/
    Other courses/        courses whose year Blackboard does not say
```

- `library/IESE/` is built by the case pipeline the first time you prep a case: it sets up the course you have next first, then downloads every other course in the background. Each later prep fetches that session's newest files first, because professors add material close to class.
- `library/IESE/SCHEDULE.md` is how the tool knows what "today" and "tomorrow" mean: it finds the date there and gets the course, the session number and the folder. It is rebuilt from my.iese.edu when it is more than a week old.
- Notes and workbooks for a case are written in that session's folder, next to the case.
- You can add your own areas next to `IESE/`, for example `library/recruiting/` or `library/reading/`. Ask the tool to file something there and it will.

`library/IESE/` stays out of git: the cases are copyrighted and the notes are yours.
