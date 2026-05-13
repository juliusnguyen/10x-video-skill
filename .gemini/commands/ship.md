Ship the current feature or video: commit, update changelog, open PR, merge, and cleanup.

**Steps to execute:**

1. Detect current context from branch name (same as `/plan`).

2. For videos:
   - Base Directory: `production_videos/NNNNN-NAME/`.
   - Run `/clean` to remove temporary frames inside the folder.
   - Update `CHANGELOG.md` using the history file in `production_plans/`.

3. **Commit everything**:
   ```
   git add .
   git commit -m "feat(NNNNN): NAME - complete"
   ```

4. **Create a PR** using `gh pr create`.

5. **Merge the PR** and delete the branch.

6. **Return to main and pull**.

7. Report success.
