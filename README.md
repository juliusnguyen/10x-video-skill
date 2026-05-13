# 10x Video Skill 🎬

Premium AI explainer video pipeline: topic → script → TTS → HTML slides → render → thumbnail → YouTube.

## Quick Start

```bash
# 1. Clone
git clone https://github.com/juliusnguyen/10x-video-skill.git
cd 10x-video-skill

# 2. Install dependencies (Requires LLVM 20+ for local TTS)
npm install puppeteer chart.js
pip3 install -r requirements.txt

# 3. Set environment variables (Optional fallback for ITERA102)
export ITERA102_API_KEY="your_key_here"
```

## AI-Powered Workflow (Gemini CLI)

This project is designed to be used with the **Gemini CLI**. The following custom commands automate the entire pipeline:

- `/feature VIDEO-NAME`: Start a new video (creates branch, folder, and history).
- `/plan`: Generate a detailed production plan and research.
- `/video VIDEO-NAME`: **Autopilot mode**. Runs the entire pipeline (1-7) automatically.
- `/script <N> <topic>`: Research and write a Vietnamese script.
- `/tts <N>`: Generate high-quality VieNeu voiceover.
- `/slides <N>`: Create HTML slides using the v5.1 design system.
- `/validate <N>`: Validate HTML slides for syntax and runtime errors.
- `/render <N>`: Render slides to MP4 using Puppeteer.
- `/qc <N>`: Perform Pixel Quality Control.
- `/thumb <N>`: Generate a high-quality JPEG thumbnail.
- `/seo <N>`: Generate YouTube metadata (title, description, tags).
- `/upload <N>`: Upload to YouTube with smart scheduling.
- `/ship`: Finalize production: update changelog, commit, and merge.
- `/clean`: Purge temporary assets (frames, temp audio) to save disk space.

## Directory Structure

```
├── SKILL.md                    # Main reference (pipeline + checklist)
├── scripts/
│   ├── tts.sh                  # TTS generation (VieNeu + legacy)
│   ├── tts_vieneu.py           # VieNeu CLI wrapper
│   ├── render-safe.js          # Puppeteer frame capture → MP4
│   ├── validate-html.sh        # JS validation (run before render)
│   ├── clean-assets.sh         # Disk cleanup
│   └── upload_youtube.py        # YouTube upload with scheduler
├── references/
│   ├── design-system.md        # v5.1 design tokens, typography, rules
│   ├── slide-patterns.md       # HTML patterns + JS animation functions
│   └── pitfalls.md             # 30 production gotchas
└── templates/
    └── card-comparison-v5.1.html  # 6 slide patterns template
```

## Video Pipeline

1. **Research** → topic + key points
2. **Script** → `voices/videoN_name.txt` (Vietnamese, ≥60s)
3. **TTS** → `scripts/tts.sh` (VieNeu local high-quality)
4. **Slides** → HTML (v5.1 design system, JS-driven animations)
5. **Validate** → `scripts/validate-html.sh`
6. **Render** → `scripts/render-safe.js` (Puppeteer → MP4)
7. **QC** → pixel analysis (mean > 18, max = 255, unique > 5000)
8. **Thumbnail + SEO** → SVG → PNG → JPEG
9. **Upload** → `scripts/upload_youtube.py`
10. **Cleanup** → `scripts/clean-assets.sh`

## Prerequisites

- **Python 3.12+**
- **LLVM 20+** (Required to build `llvmlite` dependency for `vieneu`)
- **Node.js** (for Puppeteer rendering)
- **FFmpeg** (for video processing)

## API Keys (Optional fallback)

| Key | Purpose | Get From |
|-----|---------|----------|
| `ITERA102_API_KEY` | Legacy TTS (MiniMax + ElevenLabs) | itera102.space |
| `YOUTUBE_CLIENT_ID` | YouTube OAuth2 | Google Cloud Console |
| `YOUTUBE_CLIENT_SECRET` | YouTube OAuth2 | Google Cloud Console |
| `YOUTUBE_REFRESH_TOKEN` | YouTube OAuth2 | OAuth2 flow |

## Design System v5.1

- Dark theme: `#0a0a12` background + neon accents
- JS-driven animations ONLY (no CSS transitions — causes strobing in Puppeteer)
- Vietnamese diacritics mandatory
- SVG icons only (no emoji — VPS lacks emoji fonts)
- 12-15 slides per 60s, 3-6s per slide

See `references/design-system.md` for full tokens and `references/slide-patterns.md` for copy-paste patterns.

## License

MIT — Use freely, modify as needed.
