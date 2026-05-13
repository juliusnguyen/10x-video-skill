Start a new feature or video production.
Usage: `/feature NAME` or `/feature` (will prompt for name).

**Steps to execute:**

1. Determine the name from arguments, or ask the user if none given.

2. Determine the type and prefix:
   - If it looks like a video (e.g., "AI-NEWS", "TECH-TIPS") or if the user is in "video mode":
     - Scan `production_videos/` for existing `NNNNN-*` folders.
     - Determine next `N`. Prefix: `videoN`. Padded prefix: `NNNNN` (5 digits).
     - Construction slug: `NNNNN-NAME` (uppercase, hyphens).
     - Parent Folder: `production_videos/`.
     - Branch prefix: `production/`.
   - Otherwise (general feature):
     - Scan `changes/` for `NNN`.
     - Prefix: `NNN` (e.g., `001`).
     - Branch prefix: `changes/`.
     - Folder: `changes/`.

3. Create the video directory: `production_videos/NNNNN-NAME/`.
   - Inside, create subdirectories: `output/`, `production_plans/`, `thumbnails/`, `voices/`.

4. Write the prompt/topic to `production_videos/NNNNN-NAME/production_plans/videoN.00-PROMPT.md`.

5. Initialize history: `production_videos/NNNNN-NAME/production_plans/videoN.01-HISTORY.md`.

6. For videos: Create a stub script file `production_videos/NNNNN-NAME/voices/videoN_NAME.txt`.

7. Create and switch to the branch: `git checkout -b BRANCH_PREFIXNNNNN-NAME`.

8. Report success and next steps.
