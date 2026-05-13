# Production Plan: video2-5-SKILL-AI-HUU-ICH

Implementation checklist for the "5 Skill hữu ích khi sử dụng AI" video.

## Status: 88% Complete

- [x] **1. Script Writing**
  - Research top 5 skills (Agentic Workflow, Context Engineering, Validation, Cost Optimization, Strategic Thinking).
  - Write conversational Vietnamese script (150-200 words, ~60s).
  - Save to \`voices/video2_5_SKILL_AI_HUU_ICH.txt\`.
- [x] **2. TTS Generation**
  - Run: \`bash scripts/tts.sh 2 vieneu\`
  - Verify duration: \`ffprobe voices/video2_5_SKILL_AI_HUU_ICH_podcast.mp3\` (64.38s)
- [x] **3. Slide Concept & Creation**
  - Create \`video2_5_SKILL_AI_HUU_ICH.html\` using v5.1 template.
  - Map sections to patterns (Hero, Steps, Comparison, etc.).
  - Set \`AUDIO_DURATION\` in JS (64.38s).
- [x] **4. Validation**
  - Run: \`bash scripts/validate-html.sh video2_5_SKILL_AI_HUU_ICH\`
- [x] **5. Rendering**
  - Update \`scripts/render-safe.js\` configs.
  - Run: \`node scripts/render-safe.js 2\`
- [x] **6. Quality Control**
  - Run: \`/qc 2\` (Pixel check).
- [x] **7. Thumbnail & SEO**
  - Run: \`/thumb 2\`
  - Run: \`/seo 2\`
- [ ] **8. YouTube Upload**
  - Run: \`/upload 2\`
- [ ] **9. Finalize**
  - Run: \`/ship\`
