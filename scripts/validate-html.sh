     1|#!/bin/bash
     2|# JS Validation for video HTML — run BEFORE rendering
     3|# Usage: bash scripts/validate-html.sh videoN_name
     4|# Example: bash scripts/validate-html.sh video10_kimi26
     5|
     6|set -e
     7|NAME="${1:?Usage: validate-html.sh videoN_name}"
     8|HTML="./${NAME}.html"
     9|
    10|if [ ! -f "$HTML" ]; then echo "❌ HTML not found: $HTML"; exit 1; fi
    11|
    12|echo "=== Step 1: Node.js syntax check ==="
    13|cd /root/ai-video-project
    14|node -e "
    15|const fs = require('fs');
    16|const html = fs.readFileSync('${NAME}.html', 'utf8');
    17|const scripts = html.match(/<script[^>]*>([\s\S]*?)<\/script>/g) || [];
    18|let fail = 0;
    19|scripts.forEach((s, i) => {
    20|  const code = s.replace(/<\/?script[^>]*>/g, '');
    21|  try { new Function(code); console.log('Script ' + i + ': OK'); }
    22|  catch(e) { console.log('Script ' + i + ': ERROR - ' + e.message); fail++; }
    23|});
    24|if (fail > 0) process.exit(1);
    25|"
    26|
    27|echo "=== Step 2: Puppeteer runtime check ==="
    28|node -e "
    29|const puppeteer = require('puppeteer');
    30|(async () => {
    31|  const browser = await puppeteer.launch({headless:'new',args:['--no-sandbox','--disable-setuid-sandbox']});
    32|  const page = await browser.newPage();
    33|  const errors = [];
    34|  page.on('pageerror', e => errors.push(e.message));
    35|  await page.goto('file://./${NAME}.html', {waitUntil:'networkidle0',timeout:60000});
    36|  await page.evaluate(() => { window.__VIDEO_TIME_MS = 5000; });
    37|  await new Promise(r => setTimeout(r, 500));
    38|  const active = await page.evaluate(() => {
    39|    const slides = document.querySelectorAll('.slide');
    40|    let a = [];
    41|    slides.forEach((s,i) => { const cs = window.getComputedStyle(s); if(cs.display!=='none') a.push({idx:i,id:s.id,opacity:cs.opacity}); });
    42|    return {activeSlides: a, currentSlide: window.currentSlide};
    43|  });
    44|  console.log('JS errors:', errors.length ? JSON.stringify(errors) : 'NONE');
    45|  console.log('Active at 5s:', JSON.stringify(active));
    46|  if(errors.length > 0) { console.log('FAIL: JS errors detected!'); process.exit(1); }
    47|  if(active.activeSlides.length === 0) { console.log('FAIL: No slides visible!'); process.exit(1); }
    48|  console.log('PASS: slides rendering correctly');
    49|  await browser.close();
    50|})();
    51|"
    52|
    53|echo "=== Step 3: Pixel QC (run AFTER render) ==="
    54|echo "Run after rendering:"
    55|echo "  ffmpeg -y -ss 5 -i output/${NAME}.mp4 -frames:v 1 -update 1 /tmp/qc5s.png"
    56|echo "  python3 -c \"from PIL import Image; import numpy as np; arr=np.array(Image.open('/tmp/qc5s.png')); m=arr.mean(); mx=arr.max(); u=len(np.unique(arr.reshape(-1,3),axis=0)); print(f'mean={m:.1f} max={mx} unique={u}'); print('PASS' if mx>50 and u>1000 else 'FAIL: blank video')\""
    57|echo ""
    58|echo "=== All pre-render checks passed ==="