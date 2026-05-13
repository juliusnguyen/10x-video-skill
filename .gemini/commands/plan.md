Generate a plan for the current feature or video and save it to the corresponding directory.

**Steps to execute:**

1. Detect current context from branch name:
   - If `production/NNNNN-NAME`: 
     - Search `production_videos/` for the directory `NNNNN-NAME`.
     - Parse out `videoN` from the directory contents (scan for files matching `videoN.*` in `production_plans`).
   - If `changes/NNN-NAME`: Folder = `changes/`, Prefix = `NNN`, Name = `NAME`.

2. For videos:
   - Folder = `production_videos/NNNNN-NAME/production_plans/`.
   - Read `videoN.00-PROMPT.md` for context.
   - Determine the next MM number for plans: scan `videoN.MM-*.md`. Take highest MM + 1. Default MM = `02`.
   - Formulate the plan including 10x-video pipeline steps.
   - Write the plan to `videoN.MM-UPPERCASE-PLAN-TITLE.md`.
   - Append log entry to `videoN.01-HISTORY.md`.

3. Show the plan to the user.
