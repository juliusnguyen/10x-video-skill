#!/bin/bash
# JS Validation for video HTML — run BEFORE rendering
# Usage: bash scripts/validate-html.sh <video_number>

set -e
cd "$(dirname "$0")/.."

VNUM="${1:?Usage: validate-html.sh <number>}"
VPADDED=$(printf "%05d" "$VNUM")

# Find the video directory
VDIR=$(find production_videos -maxdepth 1 -name "${VPADDED}-*" -type d | head -n 1)

if [ -z "$VDIR" ]; then
    echo "❌ Video directory for ${VPADDED} not found!"
    exit 1
fi

# Find the HTML file
HTML_PATH=$(ls "$VDIR"/*.html 2>/dev/null | head -n 1)
if [ -z "$HTML_PATH" ]; then
    echo "❌ HTML file not found in $VDIR"
    exit 1
fi

NAME=$(basename "$HTML_PATH" .html)

echo "=== Step 1: Node.js syntax check ==="
node -e "
const fs = require('fs');
const html = fs.readFileSync('$HTML_PATH', 'utf8');
const scripts = html.match(/<script[^>]*>([\s\S]*?)<\/script>/g) || [];
let fail = 0;
scripts.forEach((s, i) => {
  const code = s.replace(/<\/?script[^>]*>/g, '');
  try { new Function(code); console.log('Script ' + i + ': OK'); }
  catch(e) { console.log('Script ' + i + ': ERROR - ' + e.message); fail++; }
});
if (fail > 0) process.exit(1);
"

echo "=== Step 2: Puppeteer runtime check ==="
node -e "
const puppeteer = require('puppeteer');
const path = require('path');
(async () => {
  const browser = await puppeteer.launch({headless:'new',args:['--no-sandbox']});
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  const fullPath = 'file://' + path.resolve('$HTML_PATH');
  await page.goto(fullPath, {waitUntil:'networkidle0',timeout:60000});
  
  const duration = await page.evaluate(() => window.AUDIO_DURATION);
  console.log('AUDIO_DURATION:', duration);
  if (!duration) { console.log('FAIL: window.AUDIO_DURATION not set!'); process.exit(1); }
  
  await page.evaluate(() => { if (typeof setVideoTime === 'function') setVideoTime(5000); });
  await new Promise(r => setTimeout(r, 500));
  const active = await page.evaluate(() => {
    const slides = document.querySelectorAll('.slide');
    let a = [];
    slides.forEach((s,i) => { const cs = window.getComputedStyle(s); if(cs.display!=='none') a.push({idx:i,id:s.id,opacity:cs.opacity}); });
    return {activeSlides: a, currentSlide: window.currentSlide};
  });
  console.log('JS errors:', errors.length ? JSON.stringify(errors) : 'NONE');
  console.log('Active at 5s:', JSON.stringify(active));
  if(errors.length > 0) { console.log('FAIL: JS errors detected!'); process.exit(1); }
  if(active.activeSlides.length === 0) { console.log('FAIL: No slides visible!'); process.exit(1); }
  console.log('PASS: slides rendering correctly');
  await browser.close();
})();
"

echo "=== Step 3: Pixel QC (run AFTER render) ==="
echo "Run after rendering:"
echo "  ffmpeg -y -ss 5 -i $VDIR/output/${NAME}.mp4 -frames:v 1 -update 1 /tmp/qc5s.png"
echo "  python3 -c \"from PIL import Image; import numpy as np; arr=np.array(Image.open('/tmp/qc5s.png')); m=arr.mean(); mx=arr.max(); u=len(np.unique(arr.reshape(-1,3),axis=0)); print(f'mean={m:.1f} max={mx} unique={u}'); print('PASS' if mx>50 and u>1000 else 'FAIL: blank video')\""
echo ""
echo "=== All pre-render checks passed ==="
