# 10x Video — Pitfalls & Gotchas (Top 30)

Quick reference for every failure mode encountered on videos 1-18+.

## Critical (Causes Blank/Broken Video)

### 1. No emoji in Puppeteer VPS renders
The VPS lacks emoji font files. Unicode emoji (⚡🔒🌐🧠) render as empty boxes or garbled symbols.
**Fix:** Use styled text numbers ("01", "02"...) in colored icon boxes, CSS-only symbols, or inline SVG.

### 2. Vietnamese diacritics (dấu) MANDATORY
All HTML text must have proper Vietnamese diacritics. Cross-reference `voices/video{N}_{name}.txt`.
- ❌ `DUNG BO LO` → ✅ `ĐỪNG BỎ LỎ`

### 3. CSS transition = STROBING in Puppeteer
CSS `transition` / `animation` causes flickering in frame capture.
**Fix:** ALL animations via `window.setVideoTime(ms)` — set style directly each frame.

### 4. Slide transitions mandatory
Every slide: entrance fade-in + slide-up (0.3-0.5s, JS-driven). Bullets: slide-up + fade-in. Counters: count-up. Charts: progressive data.

### 5. render-safe.js ONLY
NEVER use render.js — it crashes on large HTML.

### 6. Object.defineProperty crashes kill ALL JS
- **Trigger A:** `var slideProgress` + `Object.defineProperty(window, 'slideProgress', ...)` = collision → TypeError → ALL scripts die → blank video.
  **Fix:** Rename local var (`var _slideProgress`) or add `configurable: true`.
- **Trigger B:** IIFE syntax error in one `<script>` tag kills that entire block.
  **Fix:** Wrap each slide's inline JS in its OWN `<script>` tag.

### 7. Slide 0 must NOT have `class="active"` in HTML
Let render-safe.js inject `setVideoTime(0)` after load. Add explicit `page.evaluate(() => window.setVideoTime(0))` in Puppeteer.

### 8. QC timestamps — test mid-slide, NOT at boundaries
Slide start/end times show entrance animation (opacity=0). Always test 2-3s INTO each slide (e.g., t=3s, 8s, 13s).

## Important

### 9. AUDIO_DURATION must be exact ffprobe value
Not a guess. Run `ffprobe` and use the exact duration.

### 10. Min video duration ≥ 60s
User requirement. Never shorter.

### 11. Use /usr/bin/python3 for upload
NOT venv python3. `upload_youtube.py` must run with system python.

### 12. 5h gap between YouTube uploads
YouTube algorithm preference. Use `--batch --gap 5`.

### 13. Clean assets BEFORE and AFTER each job
`./clean-assets.sh` before new video + after upload. Leftover frames cause disk-full.

### 14. YouTube description: no emoji compounds, no em dash
YouTube API 400 `invalidDescription`. Use hyphen `-` instead of `—`. No emoji sequences like ⏱️🔔📖.

### 15. YouTube quota resets at 15:00 VN (midnight PT)
Each upload costs ~1600 units. If `quotaExceeded`, schedule cron for 15:10 VN.

### 16. iterA102 API key for TTS
Use `ITERA102_API_KEY` env var. Endpoint: `https://api.itera102.space/v1`. Same key for MiniMax + ElevenLabs + Clone + STT.

### 17. dry-run NOW WORKS
`--dry-run` flag properly exits without uploading. Use to verify config.

### 18. Pixel QC pass criteria
- `mean > 18`, `max = 255`, `unique_colors > 5000` = PASS
- `max < 50`, `unique < 1000` = FAIL (blank video, check JS errors)

### 19. Flickering at slide transitions
Caused by CSS `transition` properties. Remove ALL `transition` from CSS. JS-only animation per `setVideoTime(ms)`.

### 20. New AI models — subagents may have no knowledge
Browse official sites directly. Use `browser_console` with `document.body.innerText` to extract text, bypassing JS rendering issues.

### 21. render-safe.js ffmpeg timeout on long videos (>60s)
For 1500+ frames, ffmpeg can exceed 600s timeout.
**Fix:** Separate encoding + muxing:
```bash
# Step 1: Encode frames to video (no audio)
ffmpeg -y -framerate 24 -i frames_N/frame_%05d.png \
  -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p -an \
  output_video.mp4
# Step 2: Mux audio separately
ffmpeg -y -i output_video.mp4 -i voices/audio.mp3 \
  -c:v copy -c:a aac -b:a 128k -shortest output.mp4
```

### 22. SVG thumbnail text — avoid Vietnamese diacritics
Text with dấu in SVG may not render if system fonts lack Vietnamese glyphs.
**Fix:** Keep thumbnail text in ASCII/English. If Vietnamese needed, install `fonts-noto-cjk`.

### 23. Adding new video requires 3 config locations
1. `tts.sh`: Add `N:videoN_name` to VIDEOS list
2. `render-safe.js`: Add to `videoNames`, `audioDurations`, valid numbers
3. Don't forget the `{ N: 'videoN_name' }` object mapping

### 24. MiniMax + ElevenLabs can BOTH fail
- **MiniMax DOWN:** Switch to ElevenLabs (`elevenlabs` or `elevenlabs-female`)
- **Key EXPIRED:** Both providers return 401. Verify key at `/v1/models` endpoint.
- **ElevenLabs quirks:** No `language_code` param (auto-detect). Output ~1.5x longer than MiniMax.

### 25. Idle animations prevent dead space
After content reveals finish, slides MUST have continuous micro-animations: pulsing glow, floating elements, hue-rotate shifts, counter ticking, marquee text. NO freeze frames.

### 26. Font-size scaling for 1080x1920 portrait
Standard web sizes too small. Use: h1=88px, h2=64px, h3=44px, p=40px, sub=32px, badge=34px. Card padding=36px 40px.

### 27. NEVER use unicode emoji in Puppeteer renders
See #1. Replace all with styled text/SVG.

### 28. ElevenLabs output longer than MiniMax
At `speed: 1.1`, ElevenLabs ~102s vs MiniMax ~64-70s for same text. Recalibrate slide timing.

### 29. YouTube OAuth2 client secret expires
Error: `invalid_client`. Fix: Google Cloud Console → reset secret → re-run OAuth flow → update upload_youtube.py.

### 30. Stock image sites block bot traffic
Pexels, Pixabay, Unsplash detect headless browsers. Use CSS dark-gradient backgrounds + SVG icons + terminal mockups instead. Or cache images locally in `assets/`.

## Environment Changes Log

| Date | Change |
|---|---|
| 2026-05-11 | MIGRATED: genmax.io → itera102.space. New API endpoint `https://api.itera102.space/v1`. Same key format. tts.sh uses `ITERA102_API_KEY` env var. |
| 2026-05-11 | ADDED: Remotion render engine cloned to `/root/ai-video-remotion/`. React-based rendering. Puppeteer still legacy fallback. |
| 2026-04-28 | GenMax key renewed. ElevenLabs Vietnamese voices verified: Ton (male, north), Man Nghi (female, south). |
| 2026-04-27 | ElevenLabs via GenMax API working. Do NOT use `language_code` for ElevenLabs. |
| 2026-04-23 | Thumbnail SVG pipeline: cairosvg + `/usr/bin/python3` + ffmpeg. |
| 2026-04-22 | EzAI provider REMOVED (401). All models → ollama-cloud. |
| 2026-04-07 | Object.defineProperty pitfall discovered (video9). IIFE syntax variant (video10). |