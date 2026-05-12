Generate a plan for the current feature or video and save it to the corresponding directory.

**Steps to execute:**

1. Detect current context from branch name:
   - If `production/videoN-NAME`: Folder = `production_plans/`, Prefix = `videoN`, Name = `NAME`.
   - If `changes/NNN-NAME`: Folder = `changes/`, Prefix = `NNN`, Name = `NAME`.
   - Otherwise: Ask for context.

2. Read `FOLDER/PREFIX-NAME/PREFIX.00-PROMPT.md` for context.

3. Determine the next MM number for plans: scan `FOLDER/PREFIX-NAME/PREFIX.MM-*.md`. Take highest MM + 1. Default MM = `02`.

4. Determine the plan name: provided after `/plan` or `INITIAL-PLAN`. Format: `PREFIX.MM-UPPERCASE-PLAN-TITLE.md`.

5. Formulate the plan:
   - If it's a video: Include 10x-video pipeline steps (script, tts, slides, validate, render, qc, thumb, seo, upload).
   - If it's a feature: Detail the technical implementation steps.

6. Write the plan to `FOLDER/PREFIX-NAME/PREFIX.MM-UPPERCASE-PLAN-TITLE.md`.

7. Append a log entry to `FOLDER/PREFIX-NAME/PREFIX.01-HISTORY.md`.

8. Show the plan to the user.
