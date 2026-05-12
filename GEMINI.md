# 10x Video Project Instructions

This project is a premium AI explainer video pipeline.

## Environment
- **Python:** 3.12 (in `.venv`)
- **Node.js:** Required for Puppeteer rendering.
- **Key API:** Local VieNeu TTS (preferred) or `ITERA102_API_KEY` for legacy fallback.

## Workflow
See `SKILL.md` for the full 10x Video Pipeline details.

## Commands
Custom commands are located in `.gemini/commands/`.

- `/feature VIDEO-NAME`: Start a new video (branch + folder + history + script stub).
- `/plan`: Generate a detailed production plan (saved to subfolder).
- `/script <N> <topic>`: Research and write a Vietnamese script.
- `/tts <N> [provider]`: Generate TTS voiceover (VieNeu, MiniMax, or ElevenLabs).
- `/slides <N>`: Create HTML slides using the v5.1 design system.
- `/validate videoN_name`: Validate HTML slides for syntax and runtime errors.
- `/render <N>`: Render video slides to MP4 using Puppeteer.
- `/qc <N>`: Perform Pixel Quality Control on the rendered video.
- `/thumb <N>`: Generate a high-quality JPEG thumbnail.
- `/seo <N>`: Generate YouTube metadata (title, description, tags).
- `/upload <N>`: Upload the video to YouTube (with scheduling).
- `/ship`: Finalize production: update changelog, commit, PR, and merge.
- `/clean`: Clean up temporary assets (frames, temp audio).
