Ship the current feature or video: commit, update changelog, open PR, merge, and cleanup.

**Steps to execute:**

1. Detect current context from branch name (similar to `/plan`).

2. Run `/clean` (for videos).

3. **Update CHANGELOG.md**:
   - Summarize work from the history file.
   - Add a new section dated today.
   - Insert at the top.

4. **Commit everything**:
   ```
   git add .
   git commit -m "feat(PREFIX): NAME - complete"
   ```

5. **Create a PR** using `gh pr create`:
   - Title: `feat(PREFIX): NAME`
   - Body: Summary from history file.
   - Target: `main`

6. **Merge the PR**:
   ```
   gh pr merge --merge --delete-branch
   ```

7. **Return to main and pull**.

8. Report success.
