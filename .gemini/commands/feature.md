Start a new feature or video production.
Usage: `/feature NAME` or `/feature` (will prompt for name).

**Steps to execute:**

1. Determine the name from arguments, or ask the user if none given.

2. Determine the type and prefix:
   - If it looks like a video (e.g., "AI-NEWS", "TECH-TIPS") or if the user is in "video mode":
     - Scan `voices/` or `output/` or `production_plans/` for `videoN`.
     - Prefix: `videoN` (e.g., `video13`).
     - Branch prefix: `production/`.
     - Folder: `production_plans/`.
   - Otherwise (general feature):
     - Scan `changes/` for `NNN`.
     - Prefix: `NNN` (e.g., `001`).
     - Branch prefix: `changes/`.
     - Folder: `changes/`.

3. Construct slug: `PREFIX-NAME` (uppercase, hyphens).

4. Create the directory: `FOLDER/PREFIX-NAME/`.

5. Write the prompt/topic to `FOLDER/PREFIX-NAME/PREFIX.00-PROMPT.md`.

6. Initialize history: `FOLDER/PREFIX-NAME/PREFIX.01-HISTORY.md`.

7. For videos: Create a stub script file `voices/PREFIX_NAME.txt`.

8. Create and switch to the branch: `git checkout -b BRANCH_PREFIXPREFIX-NAME`.

9. Report success and next steps.
