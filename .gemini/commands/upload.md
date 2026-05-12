Upload the rendered video to YouTube with SEO metadata.

Run: `python3 scripts/upload_youtube.py <N>`

Optional flags:
- `--dry-run`: Test the upload without actually publishing.
- `--batch --gap 5`: Schedule multiple uploads with a 5-hour gap.

Ensure `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, and `YOUTUBE_REFRESH_TOKEN` are configured.
