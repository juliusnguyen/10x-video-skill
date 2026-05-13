Autopilot video production. Initializes a new video and executes all steps until it is ready for review.

Usage: `/video VIDEO-NAME`

**Steps to execute:**

1. **Initialize**: Execute logic of `/feature VIDEO-NAME`.
   - Determine next `NNNNN`.
   - Create directory `production_videos/NNNNN-NAME/`.
   - Create subdirs: `output`, `production_plans`, `thumbnails`, `voices`.
   - Switch branch: `production/NNNNN-NAME`.

2. **Step 1 - Script**: Research the topic and write a ~200 word Vietnamese script.
   - Use the **Brand Name** and **CTA Slogan** from `GEMINI.md` for the outro.
   - Save to `production_videos/NNNNN-NAME/voices/videoN_NAME.txt`.
   - Log to history.

3. **Step 2 - TTS**: Generate voiceover using VieNeu local engine.
   - Run `bash scripts/tts.sh <N> vieneu`.
   - ffprobe for duration.

4. **Step 3 - Slides**: Create `videoN_NAME.html` using v5.1 design system.
   - Set `AUDIO_DURATION` correctly.
   - Map script to 10-15 engagement-focused slides.
   - **Outro:** Use the **Brand Name** from `GEMINI.md` on the final slide.

5. **Step 4 - Validate**: Run `bash scripts/validate-html.sh <N>`.
   - Fix any syntax errors found.

6. **Step 5 - Render**: Execute the render process.
   - Update `scripts/render-safe.js` configuration.
   - Run `node scripts/render-safe.js <N>`.

7. **Step 6 - QC**: Extract a frame and perform pixel analysis.
   - If failed, debug HTML (e.g. missing `setVideoTime`) and re-render once.

8. **Step 7 - SEO & Thumbnail**:
   - Generate SEO metadata (title, tags, description) to `videoN.03-SEO.md`.
   - Generate high-quality thumbnail `thumbnails/videoN_name.jpg`.

9. **Handoff**:
   - Report that the video is ready for review at `production_videos/NNNNN-NAME/output/videoN_NAME.mp4`.
   - Prompt user to review and then run `/upload <N>` or `/ship`.
