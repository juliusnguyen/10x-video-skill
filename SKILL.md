---
name: 10x-video
description: 10x Video — Premium AI explainer video pipeline. Vietnamese voiceover, JS-driven animations, glassmorphism, Chart.js, Puppeteer render, YouTube upload. ONE skill for the whole workflow.
version: 8
tags: [youtube, video, production, 10x, tts, render, upload, scheduling]
---

# 10x Video Pipeline 🎬

Premium AI explainer video: topic → script → TTS → HTML slides → render → thumbnail → YouTube.

## When to Use
- "make a video", "tạo video", "sản xuất video", "10x video"
- Any video creation / rendering / YouTube upload

## ⚡ Quick Start

```
0. Reset data (./scripts/clean-assets.sh)
1. Research & write script (Vietnamese, ≥60s)
2. TTS voiceover (./scripts/tts.sh)
3. HTML slides (v5.1 design — see references/)
4. JS validation (./scripts/validate-html.sh — MUST before render)
5. Render MP4 (./scripts/render-safe.js)
6. Pixel QC (verify not blank)
7. Thumbnail + SEO metadata
8. Upload YouTube (./scripts/upload_youtube.py)
9. Cleanup (./scripts/clean-assets.sh)
```

## 📦 Setup (First Time)

### 1. Install Dependencies
```bash
# Node.js + Puppeteer
npm install puppeteer chart.js

# System tools (Debian/Ubuntu)
apt-get install -y ffmpeg ffprobe python3 python3-pip
pip3 install Pillow cairosvg

# macOS
brew install ffmpeg cairo
pip3 install Pillow cairosvg
```

### 2. Configure API Keys (Environment Variables)
```bash
# TTS — iterA102 API (MiniMax + ElevenLabs)
export ITERA102_API_KEY="your_itera102_api_key_here"
export ITERA102_BASE_URL="https://api.itera102.space/v1"  # optional, default

# YouTube OAuth2
export YOUTUBE_CLIENT_ID="your_client_id.apps.googleusercontent.com"
export YOUTUBE_CLIENT_SECRET="your_client_secret"
export YOUTUBE_REFRESH_TOKEN="your_refresh_token"
```

### 3. Project Directory Structure
```
your-project/
├── scripts/
│   ├── tts.sh              # TTS generation
│   ├── render-safe.js      # Puppeteer renderer
│   ├── validate-html.sh    # JS syntax + runtime check
│   ├── clean-assets.sh     # Disk cleanup
│   └── upload_youtube.py   # YouTube upload
├── templates/
│   └── card-comparison-v5.1.html
├── voices/                 # TTS text files (.txt) + audio (.mp3)
├── output/                 # Rendered MP4s
├── thumbnails/             # Thumbnail JPEGs
├── video1_example.html     # Your video HTML slides
└── package.json            # Node deps
```

## Pipeline Details

### Phase 1: Content

#### 1.1 Topic Research
- Search for latest trends
- 3-5 key points for ≥60s video
- Vietnamese audience, tech/AI niche

#### 1.2 Script Writing
- File: `voices/video{N}_{name}.txt`
- Vietnamese, conversational, ≥60s (~150-200 words)
- Hook → Key points → CTA
- **CTA Brand:** Use the "Brand Name" and "CTA Slogan" defined in `GEMINI.md`.
- No emoji

#### 1.3 Slide Concept
- Map slides to script sections (~3-5s per slide)
- Plan: charts, bullets, icons, stats, terminal mockups
- 12-15 slides per 60s (see references/design-system.md)

### Phase 2: Assets

#### 2.1 TTS Voiceover
```bash
# Local (VieNeu - Default)
bash scripts/tts.sh <N> vieneu

# Legacy Remote (ITERA102)
ITERA102_API_KEY="your_key" bash scripts/tts.sh <N> [minimax|elevenlabs]
```

| Provider | Voice | Speed | Notes |
|----------|-------|-------|-------|
| `vieneu` (default) | Local high-quality | 1.0 | Standard/Turbo modes |
| `minimax` | Podcast Host (Vietnamese) | 1.1 | Fast, resonant |
| `elevenlabs` | Ton (male, north) | 1.0 | Warm |
| `elevenlabs-female` | Man Nghi (female, south) | 1.0 | Calm |

- Output: `voices/video{N}_{name}_podcast.mp3`
- **MUST ffprobe duration** → update HTML `AUDIO_DURATION` + `render-safe.js audioDurations`
- TTS is async: poll `GET /v1/history/{id}` for `status:completed`
- ⚠️ ElevenLabs: Do NOT pass `language_code` — auto-detects from text
- ⚠️ If MiniMax fails, switch to ElevenLabs — same key, same API

#### 2.2 HTML Slides
- **Design:** v5.1 (see `references/design-system.md` for tokens, typography, rules)
- **Patterns:** Copy from `references/slide-patterns.md` or `templates/card-comparison-v5.1.html`
- **JS-driven animations ONLY** — NO CSS transitions (causes strobing)
- **Vietnamese diacritics MANDATORY** on all text
- **SVG only** for icons — NO emoji (VPS lacks emoji fonts)
- **idle animations** after content reveals to prevent dead space

#### 2.3 JS Validation — MUST DO Before Rendering
```bash
bash scripts/validate-html.sh video{N}_{name}
```
Runs: (1) Node.js syntax check, (2) Puppeteer runtime check. **Both must PASS.**

#### 2.4 Render
```bash
node scripts/render-safe.js <N>
# ~3-5 min per video, 24fps 1080x1920 h264+aac
```
**Before first render:** Edit `render-safe.js` → update `videoNames` and `audioDurations` config.

For long videos (>60s), if ffmpeg times out, split encoding:
```bash
# Step 1: Encode frames → video
ffmpeg -y -framerate 24 -i frames_N/frame_%05d.png -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p -an output_video.mp4
# Step 2: Mux audio
ffmpeg -y -i output_video.mp4 -i voices/audio.mp3 -c:v copy -c:a aac -b:a 128k -shortest output.mp4
```

#### 2.5 QC
```bash
ffprobe output/video{N}_{name}.mp4
# Pixel analysis (mandatory):
ffmpeg -y -ss 5 -i output/video{N}_{name}.mp4 -frames:v 1 -update 1 /tmp/qc5s.png
python3 -c "from PIL import Image; import numpy as np; arr=np.array(Image.open('/tmp/qc5s.png')); print(f'mean={arr.mean():.1f} max={arr.max()} unique={len(np.unique(arr.reshape(-1,3),axis=0))}')"
```
- **PASS:** mean > 18, max = 255, unique > 5000
- **FAIL (blank):** max < 50, unique < 1000 → JS crash, fix HTML
- ⚠️ Test mid-slide (t=3s, 8s), NOT at slide boundaries (opacity=0)

### Phase 3: Publishing

#### 3.1 Thumbnail
1280x720, dark bg + neon text, JPEG quality=95. No text bottom-right (YouTube badge).
```bash
# SVG → PNG → JPEG pipeline
# 1. Write SVG with design tokens
# 2. Convert: python3 -c "import cairosvg; cairosvg.svg2png(bytestring=open('/tmp/thumb.svg').read().encode(), write_to='/tmp/thumb.png', dpi=150)"
# 3. ffmpeg -y -i /tmp/thumb.png -q:v 2 thumbnails/videoN_name.jpg
```
⚠️ SVG text: keep ASCII/English (Vietnamese dấu may not render in SVG without CJK fonts)

#### 3.2 SEO
- Title: ≤65 chars, keyword first, power word
- Description: 3-zone (hook+CTA, story+timestamps, AI disclosure+hashtags)
- Hashtags: 15 (5 broad + 5 specific + 5 long-tail)
- Timestamps from `window.slides`
- **NO emoji compounds (⏱️🔔📖) and NO em dash (—)** → YouTube API 400
- If video references repos/docs/prompts → add "Tài Nguyên" section with links

#### 3.3 Upload
```bash
python3 scripts/upload_youtube.py <N>
# Dry-run: add --dry-run
# Batch with 5h gaps: --batch --gap 5
```
- Channel: 3 shorts/day, 5h gap, times 07:00/12:00/17:00
- Quota resets at 15:00 VN (midnight PT). If `quotaExceeded`, schedule for 15:10 VN

## Adding New Videos — Checklist

1. Write script → `voices/video{N}_{name}.txt`
2. **Update config BEFORE TTS:**
   - `scripts/tts.sh`: add `N:videoN_name` to VIDEOS list
   - `scripts/render-safe.js`: add to `videoNames` + `audioDurations` arrays
3. Generate TTS → `ITERA102_API_KEY="key" bash scripts/tts.sh N`
4. `ffprobe` exact duration → update HTML `AUDIO_DURATION` + `render-safe.js audioDurations[N]`
5. Create HTML slides (v5.1 design)
6. **JS validation** → `bash scripts/validate-html.sh video{N}_{name}`
7. Render → `node scripts/render-safe.js N`
8. Pixel QC → `mean > 18, max = 255, unique > 5000`
9. Thumbnail → SEO → upload
10. Cleanup → `bash scripts/clean-assets.sh`
11. Log video ID

## Key Files

| File | Purpose | In Package |
|---|---|---|
| `scripts/tts.sh` | TTS generation (MiniMax + ElevenLabs) | ✅ |
| `scripts/render-safe.js` | Puppeteer renderer (config-driven) | ✅ |
| `scripts/validate-html.sh` | JS validation (run before render) | ✅ |
| `scripts/clean-assets.sh` | Disk cleanup | ✅ |
| `scripts/upload_youtube.py` | YouTube upload with scheduler | ✅ |
| `templates/card-comparison-v5.1.html` | Slide template (6 patterns) | ✅ |
| `references/design-system.md` | Design tokens, typography, rules | ✅ |
| `references/slide-patterns.md` | HTML patterns + JS animation functions | ✅ |
| `references/pitfalls.md` | 30 gotchas from production experience | ✅ |

## Deep References (load with skill_view)

| File | When to Load |
|---|---|
| `references/design-system.md` | When creating HTML slides (design tokens, timing rules) |
| `references/slide-patterns.md` | When writing HTML slide code (copy-paste patterns) |
| `references/pitfalls.md` | When debugging blank videos, strobing, or render failures |
| `templates/card-comparison-v5.1.html` | When using v5.1 card-comparison patterns |

## ⚠️ Quick Pitfall Reference (see references/pitfalls.md for full list)

| # | Pitfall | Fix |
|---|---|---|
| 1 | Unicode emoji → empty boxes on VPS | Use styled text numbers or SVG |
| 2 | Vietnamese missing dấu | Cross-reference TTS text file |
| 3 | CSS transition → strobing | JS-driven only via setVideoTime |
| 4 | Object.defineProperty crash → blank video | Rename var or add configurable:true |
| 5 | Slide 0 has class="active" → blank hero | Let JS inject setVideoTime(0) |
| 6 | QC at slide boundaries → false fail | Test 2-3s INTO each slide |
| 7 | render.js crashes | Use render-safe.js ONLY |
| 8 | ElevenLabs ~1.5x longer than MiniMax | Recalibrate slide timing |
| 9 | YouTube description em dash → API 400 | Use hyphen `-` |
| 10 | Disk full from old frames | Run clean-assets.sh before+after |

## Cron Automation

```yaml
# Example: Auto-generate every 90 minutes
cronjob create:
  name: "10x-video-auto"
  schedule: "every 90m"
  prompt: >
    Research latest AI topic, write script, generate TTS,
    create HTML, validate, render, QC, thumbnail, SEO, upload.
    Use 10x-video skill. Notify on success/fail.
```