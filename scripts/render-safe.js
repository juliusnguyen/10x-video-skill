// render-safe.js — Puppeteer frame capture + ffmpeg muxing for 10x video pipeline
// Usage: node render-safe.js <video_number>
// 
// IMPORTANT: Before rendering, edit the videoNames and audioDurations config below
// to match YOUR video project. Then create the corresponding HTML file.
//
// Dependencies: npm install puppeteer
// Requires: ffprobe, ffmpeg (system)

const puppeteer = require('puppeteer');
const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

// ══════════════════════════════════════════════════
// CONFIG — Edit this section for your video project
// ══════════════════════════════════════════════════
const videoNames = {
  // Example: 1: 'video1_example',
  // Add your video entries here
};
const audioDurations = {
  // Example: 1: 60.0,
  // Must match exact ffprobe duration of each TTS audio file
  // GET EXACT VALUE: ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 voices/videoN_name_podcast.mp3
};

const FPS = 24;
const WIDTH = 1080;
const HEIGHT = 1920;
const BATCH = 50; // frames per browser batch (reduce if OOM)
const MAX_RETRIES = 2;

// ══════════════════════════════════════════════════
// END CONFIG — Don't edit below unless you know what you're doing
// ══════════════════════════════════════════════════

const videoNum = parseInt(process.argv[2]);
const validNums = Object.keys(videoNames).map(Number);
if (!videoNum || validNums.indexOf(videoNum) === -1) {
  console.error('Usage: node render-safe.js <number>');
  console.error('Valid numbers:', validNums.sort().join(', '));
  console.error('Edit videoNames and audioDurations in this file first!');
  process.exit(1);
}

const name = videoNames[videoNum];
const duration = audioDurations[videoNum];
const htmlFile = path.resolve(__dirname, `${name}.html`);
const outputDir = path.resolve(__dirname, `frames_${videoNum}`);
const outputMp4 = path.resolve(__dirname, `output/${name}.mp4`);
const audioFile = path.resolve(__dirname, `voices/${name}_podcast.mp3`);

// Validate files exist
if (!fs.existsSync(htmlFile)) { console.error(`HTML not found: ${htmlFile}`); process.exit(1); }
if (!fs.existsSync(audioFile)) { console.error(`Audio not found: ${audioFile}`); process.exit(1); }

console.log(`🎬 Rendering video ${videoNum}: ${name}`);
console.log(`   HTML: ${htmlFile}`);
console.log(`   Audio: ${audioFile}`);
console.log(`   Duration: ${duration}s`);
console.log(`   FPS: ${FPS}, Resolution: ${WIDTH}x${HEIGHT}`);

async function captureBatch(startFrame, endFrame, retry = 0) {
  try {
    const browser = await puppeteer.launch({
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage',
             '--disable-gpu', '--disable-software-rasterizer',
             '--js-flags=--max-old-space-size=2048']
    });
    const page = await browser.newPage();
    await page.setViewport({ width: WIDTH, height: HEIGHT, deviceScaleFactor: 1 });
    await page.goto(`file://${htmlFile}`, { waitUntil: 'networkidle0', timeout: 60000 });
    await new Promise(r => setTimeout(r, 3000));

    for (let i = startFrame; i < endFrame; i++) {
      const targetMs = Math.round((i / FPS) * 1000);
      const audioMs = Math.round(duration * 1000);

      await page.evaluate((ms, audioDurMs) => {
        if (typeof window.setVideoTime === 'function') {
          window.setVideoTime(ms);
        } else {
          window.__VIDEO_TIME_MS = ms;
          if (typeof window.onVideoTime === 'function') window.onVideoTime(ms);
        }
        const progressEl = document.getElementById('progress');
        if (progressEl) progressEl.style.width = (Math.min(ms / audioDurMs, 1) * 100) + '%';
      }, targetMs, audioMs);

      const frameNum = String(i + 1).padStart(5, '0');
      await page.screenshot({
        path: path.join(outputDir, `frame_${frameNum}.png`),
        clip: { x: 0, y: 0, width: WIDTH, height: HEIGHT }
      });
    }
    await browser.close();
    return true;
  } catch (err) {
    console.log(`   ⚠️ Batch ${startFrame}-${endFrame} failed (retry ${retry}): ${err.message}`);
    if (retry < MAX_RETRIES) {
      console.log(`   Retrying batch ${startFrame}-${endFrame}...`);
      await new Promise(r => setTimeout(r, 3000));
      return captureBatch(startFrame, endFrame, retry + 1);
    }
    return false;
  }
}

async function render() {
  const totalFrames = Math.ceil(duration * FPS);
  console.log(`📊 Total frames: ${totalFrames} (${duration}s × ${FPS}fps)`);
  console.log(`   Batches: ${Math.ceil(totalFrames / BATCH)} (batch size: ${BATCH})`);

  // Create output directories
  if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir, { recursive: true });
  if (!fs.existsSync(path.resolve(__dirname, 'output'))) fs.mkdirSync(path.resolve(__dirname, 'output'), { recursive: true });

  // Capture frames in batches
  let failedBatches = [];
  for (let b = 0; b < totalFrames; b += BATCH) {
    const batchEnd = Math.min(b + BATCH, totalFrames);
    console.log(`  📸 Batch ${Math.floor(b/BATCH)+1}/${Math.ceil(totalFrames/BATCH)}: frames ${b+1}-${batchEnd}`);
    const ok = await captureBatch(b, batchEnd);
    if (!ok) failedBatches.push([b, batchEnd]);
  }

  if (failedBatches.length > 0 && failedBatches.length >= Math.ceil(totalFrames / BATCH)) {
    console.error('❌ All batches failed!');
    process.exit(1);
  }

  // Encode: frames → video
  console.log('🎞️ Encoding frames to video...');
  const tempVideo = outputMp4.replace('.mp4', '.temp.mp4');
  execSync(`ffmpeg -y -framerate ${FPS} -i "${path.join(outputDir, 'frame_%05d.png')}" ` +
    `-c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p -an "${tempVideo}"`,
    { stdio: 'inherit' });

  // Mux: video + audio
  console.log('🔊 Muxing audio...');
  execSync(`ffmpeg -y -i "${tempVideo}" -i "${audioFile}" ` +
    `-c:v copy -c:a aac -b:a 128k -shortest "${outputMp4}"`,
    { stdio: 'inherit' });

  // Cleanup temp
  if (fs.existsSync(tempVideo)) fs.unlinkSync(tempVideo);

  console.log(`✅ Done! Output: ${outputMp4}`);
  console.log(`   Size: ${(fs.statSync(outputMp4).size / 1024 / 1024).toFixed(1)} MB`);

  // Print ffprobe info
  try {
    const info = execSync(`ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 "${outputMp4}"`).toString();
    console.log(`   ${info.trim()}`);
  } catch (e) {}

  // Pixel QC reminder
  console.log('');
  console.log('🔍 Run QC check:');
  console.log(`   ffmpeg -y -ss 5 -i "${outputMp4}" -frames:v 1 -update 1 /tmp/qc5s.png`);
  console.log(`   ffmpeg -y -ss 30 -i "${outputMp4}" -frames:v 1 -update 1 /tmp/qc30s.png`);
}

render().catch(err => { console.error('Fatal:', err); process.exit(1); });
