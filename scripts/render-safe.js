// render-safe.js — Puppeteer frame capture + ffmpeg muxing
const puppeteer = require('puppeteer');
const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const videoNum = parseInt(process.argv[2]);
if (!videoNum) { console.error('Usage: node render-safe.js <number>'); process.exit(1); }

const vPadded = String(videoNum).padStart(5, '0');
const rootDir = path.resolve(__dirname, '..', 'production_videos');
const vDirName = fs.readdirSync(rootDir).find(d => d.startsWith(vPadded));

if (!vDirName) { console.error(`❌ Video directory for ${vPadded} not found!`); process.exit(1); }

const vDir = path.join(rootDir, vDirName);
const htmlFile = fs.readdirSync(vDir).find(f => f.endsWith('.html'));
if (!htmlFile) { console.error(`❌ HTML not found in ${vDir}`); process.exit(1); }

const name = htmlFile.replace('.html', '');
const audioFile = path.join(vDir, 'voices', `${name}_podcast.mp3`);
if (!fs.existsSync(audioFile)) { console.error(`❌ Audio not found: ${audioFile}`); process.exit(1); }

// Get duration automatically
const duration = parseFloat(execSync(`ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "${audioFile}"`).toString().trim());

const FPS = 24;
const WIDTH = 1080;
const HEIGHT = 1920;
const BATCH = 50;
const outputDir = path.join(vDir, `frames_${videoNum}`);
const outputMp4 = path.join(vDir, 'output', `${name}.mp4`);

console.log(`🎬 Rendering: ${name} in ${vDir}`);
console.log(`📊 Duration: ${duration}s, FPS: ${FPS}`);

async function captureBatch(startFrame, endFrame) {
  const browser = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox'] });
  const page = await browser.newPage();
  await page.setViewport({ width: WIDTH, height: HEIGHT });
  await page.goto(`file://${path.join(vDir, htmlFile)}`, { waitUntil: 'networkidle0' });
  for (let i = startFrame; i < endFrame; i++) {
    const targetMs = Math.round((i / FPS) * 1000);
    await page.evaluate(ms => { if(window.setVideoTime) window.setVideoTime(ms); }, targetMs);
    await page.screenshot({ path: path.join(outputDir, `frame_${String(i+1).padStart(5, '0')}.png`) });
  }
  await browser.close();
}

async function render() {
  const totalFrames = Math.ceil(duration * FPS);
  if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir, { recursive: true });
  if (!fs.existsSync(path.join(vDir, 'output'))) fs.mkdirSync(path.join(vDir, 'output'), { recursive: true });

  for (let b = 0; b < totalFrames; b += BATCH) {
    await captureBatch(b, Math.min(b + BATCH, totalFrames));
    console.log(`  📸 Batch: ${b+1}-${Math.min(b+BATCH, totalFrames)} / ${totalFrames}`);
  }

  const tempVideo = outputMp4.replace('.mp4', '.temp.mp4');
  execSync(`ffmpeg -y -framerate ${FPS} -i "${path.join(outputDir, 'frame_%05d.png')}" -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p -an "${tempVideo}"`, { stdio: 'inherit' });
  execSync(`ffmpeg -y -i "${tempVideo}" -i "${audioFile}" -c:v copy -c:a aac -b:a 128k -shortest "${outputMp4}"`, { stdio: 'inherit' });
  if (fs.existsSync(tempVideo)) fs.unlinkSync(tempVideo);
  console.log(`✅ Done: ${outputMp4}`);
}

render().catch(console.error);
