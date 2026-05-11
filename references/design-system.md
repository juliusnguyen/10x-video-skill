# 10x Video — Design System v5.1

Premium dark-theme design system for 1080×1920 portrait explainer videos.

## Design Tokens

| Token | Value |
|---|---|
| Background | `#0a0a12` + radial-gradient (cyan 6%, purple 6%) |
| Text | `#f0f0f5` |
| Accent Cyan | `#00f5d4` |
| Accent Purple | `#bf5af2` |
| Accent Pink | `#ff2d55` |
| Accent Green | `#30d158` |
| Accent Orange | `#ff9f0a` |
| Glass BG | `rgba(255,255,255,0.04)`, blur(16px), radius 24px |
| Neon Effect | `text-shadow` + `box-shadow` with accent colors |
| Icons | SVG only (NO emoji — VPS lacks emoji fonts) |
| Fonts | System stack: `-apple-system, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif` |

## Typography Scale (1080×1920 Portrait)

| Element | Size | Weight |
|---|---|---|
| h1 (Hero) | 80-88px | 900 |
| h2 (Section) | 52-64px | 800 |
| h3 (Subsection) | 38-44px | 700 |
| p (Body) | 34-40px | 400 |
| sub (Caption) | 28-32px | 400 |
| badge | 32-34px | 700 |
| Counter number | 96px | 900 |

## Required JS API

Every video HTML MUST define these:

```javascript
window.AUDIO_DURATION = X.XX; // EXACT duration from ffprobe
window.slides = [
  { id: 's0', start: 0, end: 7.0 },
  { id: 's1', start: 7.0, end: 18.0 },
  // ...
];
```

**⚠️ Naming conflict:** The DOM `.slide` class creates a `document.querySelectorAll('.slide')` NodeList that can overwrite `window.slides`. **Fix:** Define as `window.slideData` first, then `window.slides = window.slideData`.

## Slide Timing Rule (Effective April 2026)

**OLD (boring):** 5-6 slides × 10-12s = static screens → viewers scroll away  
**NEW (engaging):** 12-15 slides × 4-5s + continuous micro-animations

| Metric | Before | Target Now |
|---|---|---|
| Slides per 60s | 5-6 | **12-15** |
| Seconds per slide | 10-12s | **3-6s** |
| Dead time (no motion) | ~8s | **0s** |
| Animations per slide | 1-2 | **≥3** |

### Slide Planning Formula (60s video)
```
Slide 0 (Hook):         0s  →  5s   = 5s
Slide 1 (Problem):      5s  →  10s  = 5s
Slide 2 (Problem cont): 10s →  14s  = 4s
Slide 3 (Solution):     14s →  19s  = 5s
Slide 4-7 (Features):   19s →  31s  = 4s each
Slide 8 (Demo):         31s →  36s  = 5s
Slide 9-11 (Evidence):  36s →  49s  = 4s each
Slide 12 (CTA/Outro):   49s →  60s  = 6s
```

### Rule: NO Dead Space
After content reveal finishes on a slide, micro-animations MUST continue until transition:
- 🔵 Pulsing glow on accent elements (opacity oscillation via Math.sin)
- 🟣 Subtle floating/bobbing icons (translateY ±4px, 2s cycle)
- 🟢 Progress bar filling / counter ticking
- 🟡 Gradient background shift (hue rotate slow)
- ⚪ Marquee/scrolling text bar at bottom
- **NO freeze frame** — if content is static, idle animation must run background

## 3 GOLDEN RULES

### Rule 1: Vietnamese Diacritics (Dấu) — MANDATORY
| ❌ Wrong | ✅ Correct |
|---|---|
| DUNG BO LO | ĐỪNG BỎ LỠ |
| la gi | là gì |

### Rule 2: JS-Driven Animations ONLY — NO CSS Transitions
CSS `transition` / `animation` = **STROBING** in Puppeteer frame capture.
```css
/* ❌ DO NOT — causes strobing! */
.slide { transition: opacity 0.4s; }
```
```javascript
// ✅ DO: set style directly each frame
li.style.opacity = String(ease);
li.style.transform = `translateY(${offset}px)`;
```

### Rule 3: Slide Transitions + Content Animations MANDATORY
- **Every slide:** entrance fade-in + slide-up (0.3-0.5s, JS-driven)
- **Bullets:** slide-up + fade-in
- **Counters:** count-up from 0
- **Charts:** data animates progressively
- **Terminal lines:** slide-in from left

## Glassmorphism Card Style

```css
.card {
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(16px);
  border-radius: 20px;
  padding: 32px;
  border: 1px solid rgba(0, 245, 212, 0.15);
}
```

## Neon Glow Effects

```css
/* Text glow */
.neon-text {
  text-shadow: 0 0 40px rgba(0, 245, 212, 0.3);
}

/* Box glow */
.neon-box {
  box-shadow: 0 0 30px rgba(191, 90, 242, 0.15),
              inset 0 0 30px rgba(191, 90, 242, 0.05);
}
```