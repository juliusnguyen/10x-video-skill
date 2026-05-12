# 10x Video Skill 🎬

Premium AI explainer video pipeline: topic → script → TTS → HTML slides → render → thumbnail → YouTube.

## Quick Start

```bash
# 1. Clone
git clone https://github.com/sonicleez/10x-video-skill.git
cd 10x-video-skill

# 2. Install dependencies
npm install puppeteer chart.js
pip3 install -r requirements.txt

# 3. Set environment variables
export ITERA102_API_KEY="your_key_here"
export YOUTUBE_CLIENT_ID="your_client_id"
export YOUTUBE_CLIENT_SECRET="your_secret"
export YOUTUBE_REFRESH_TOKEN="your_token"

# 4. Create your video HTML, then:
ITERA102_API_KEY="$ITERA102_API_KEY" bash scripts/tts.sh 1 minimax
bash scripts/validate-html.sh video1_example
node scripts/render-safe.js 1
python3 scripts/upload_youtube.py 1
```

## Directory Structure

```
├── SKILL.md                    # Main reference (pipeline + checklist)
├── scripts/
│   ├── tts.sh                  # TTS generation (MiniMax + ElevenLabs)
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
3. **TTS** → `scripts/tts.sh` (MiniMax/ElevenLabs)
4. **Slides** → HTML (v5.1 design system, JS-driven animations)
5. **Validate** → `scripts/validate-html.sh`
6. **Render** → `scripts/render-safe.js` (Puppeteer → MP4)
7. **QC** → pixel analysis (mean > 18, max = 255, unique > 5000)
8. **Thumbnail + SEO** → SVG → PNG → JPEG
9. **Upload** → `scripts/upload_youtube.py`
10. **Cleanup** → `scripts/clean-assets.sh`

## API Keys Needed

| Key | Purpose | Get From |
|-----|---------|----------|
| `ITERA102_API_KEY` | TTS (MiniMax + ElevenLabs) | itera102.space |
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
