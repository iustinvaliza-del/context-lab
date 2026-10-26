# Library

Your library: the material the tool reads before it answers, kept on this computer.

```
library/
  IESE/
    COURSES.md            every course you are enrolled in
    PREP_LOG.md           one row per case prepped
    1st year/
      Corporate Finance/
        Syllabus.md       one row per session, with the prep questions
        Session 5_.../    Blackboard's files for the session, and the notes written next to the case
    2nd year/
    Other courses/        courses whose year Blackboard does not say
```

- `library/IESE/` is built by the case pipeline the first time you prep a case: it sets up the course you have next first, then downloads every other course in the background. Each later prep fetches that session's newest files first, because professors add material close to class.
- Notes and workbooks for a case are written in that session's folder, next to the case.
- You can add your own areas next to `IESE/`, for example `library/recruiting/` or `library/reading/`. Ask the tool to file something there and it will.

`library/IESE/` stays out of git: the cases are copyrighted and the notes are yours.
