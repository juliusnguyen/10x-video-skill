# 10x Video — Slide Patterns & JS Animation Reference

Copy-paste patterns for rapid slide creation. All animations are JS-driven (NO CSS transitions).

## Core JS Animation Functions

These MUST be included in every video HTML `<script>`:

```javascript
// Slide management
let currentSlide = -1;

function applyActiveIndex(idx) {
  if (idx === currentSlide) return;
  if (currentSlide >= 0) {
    document.getElementById(window.slides[currentSlide].id).classList.remove('active');
    resetSlideAnimations(currentSlide);
  }
  if (idx >= 0) {
    const el = document.getElementById(window.slides[idx].id);
    el.style.opacity = '0';
    el.style.transform = 'translateY(24px) scale(0.97)';
    el.classList.add('active');
    currentSlide = idx;
  }
}

// Per-frame update — call from setVideoTime
function updateAnimations(sec) {
  if (currentSlide < 0) return;
  const slideTime = sec - window.slides[currentSlide].start;
  const slideDur = window.slides[currentSlide].end - window.slides[currentSlide].start;
  const slideProgress = Math.min(Math.max(slideTime / slideDur, 0), 1);

  // Entrance: first 0.4s
  const slideEl = document.getElementById(window.slides[currentSlide].id);
  if (slideTime < 0.4) {
    const t = slideTime / 0.4, ease = 1 - Math.pow(1 - t, 3);
    slideEl.style.opacity = String(ease);
    slideEl.style.transform = `translateY(${(1-ease)*24}px) scale(${0.97+0.03*ease})`;
  } else {
    slideEl.style.opacity = '1';
    slideEl.style.transform = 'translateY(0) scale(1)';
  }

  // Add slide-specific animations here
  switch (currentSlide) {
    case 1: revealBullets('bullets-s1', slideTime, [0.15, 0.45, 0.75]); break;
    case 3: revealTermLines(slideTime, [0.08,0.2,0.38,0.55,0.7,0.85]); break;
    case 4: animateCounter('counter1', 70, slideProgress, 0.2, 0.7); break;
    case 5: animateChart('myChart', slideProgress, 0.1, 0.8); break;
  }
}

// Time slider
window.setVideoTime = function(ms) { window.__VIDEO_TIME_MS = ms; updateSlidesFromMs(ms); };
(function(){ let last=-1; setInterval(()=>{ const ms=window.__VIDEO_TIME_MS||0; if(ms!==last){last=ms;updateSlidesFromMs(ms);} },40); })();
```

## Bullet Points: slide-up + fade-in

```javascript
function revealBullets(listId, slideTime, thresholds) {
  const list = document.getElementById(listId); if(!list) return;
  const items = list.querySelectorAll('li');
  const slideDur = window.slides[currentSlide].end - window.slides[currentSlide].start;
  items.forEach((li, i) => {
    if(i>=thresholds.length) return;
    const revealAt = thresholds[i]*slideDur;
    if(slideTime>=revealAt){
      const t=Math.min((slideTime-revealAt)/0.35,1), ease=1-Math.pow(1-t,3);
      li.style.opacity=String(ease);
      li.style.transform=`translateY(${(1-ease)*18}px) scale(${0.97+0.03*ease})`;
    } else { li.style.opacity='0'; li.style.transform='translateY(18px) scale(0.97)'; }
  });
}
```

## Terminal Lines: slide-in from left

```javascript
function revealTermLines(slideTime, thresholds) {
  const ids=['t1','t2','t3','t4','t5','t6'];
  const slideDur = window.slides[currentSlide].end - window.slides[currentSlide].start;
  ids.forEach((id,i)=>{
    if(i>=thresholds.length) return;
    const el=document.getElementById(id); if(!el) return;
    const revealAt=thresholds[i]*slideDur;
    if(slideTime>=revealAt){
      const t=Math.min((slideTime-revealAt)/0.3,1), ease=1-Math.pow(1-t,3);
      el.style.opacity=String(ease);
      el.style.transform=`translateX(${(1-ease)*30}px)`;
    } else { el.style.opacity='0'; el.style.transform='translateX(30px)'; }
  });
}
```

## Counter: count-up from 0

```javascript
function animateCounter(id, target, slideProgress, startAt, endAt) {
  const el=document.getElementById(id); if(!el) return;
  if(slideProgress<startAt){el.textContent='0';return;}
  if(slideProgress>endAt){el.textContent=String(target);return;}
  const t=(slideProgress-startAt)/(endAt-startAt), eased=1-Math.pow(1-t,2);
  el.textContent=String(Math.round(eased*target));
}
```

## Chart.js: progressive data

```javascript
function animateChart(chartId, slideProgress, startAt, endAt) {
  const chart=window[chartId]; if(!chart) return;
  const t=Math.min(Math.max((slideProgress-startAt)/(endAt-startAt),0),1);
  const eased=1-Math.pow(1-t,2);
  if(chart._finalData){
    chart.data.datasets[0].data=chart._finalData.map(v=>Math.round(v*eased));
    chart.update('none');
  }
}
```

## HTML Slide Patterns

### Hero Slide (Hook)
```html
<div class="slide" id="s0">
  <div class="content" style="display:flex;flex-direction:column;justify-content:center;align-items:center;height:100%;gap:24px;">
    <div class="badge" style="background:linear-gradient(90deg,#00f5d4,#bf5af2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:32px;font-weight:700;">CHỦ ĐỀ</div>
    <h1 style="font-size:72px;font-weight:900;color:#f0f0f5;text-align:center;max-width:920px;text-shadow:0 0 40px rgba(0,245,212,0.3);">Tiêu đề chính</h1>
    <p style="font-size:32px;color:rgba(240,240,245,0.7);">Subtitle</p>
  </div>
</div>
```

### Bullet Points (3-4 items)
```html
<div class="slide" id="s1">
  <div class="content" style="padding:80px 60px 0;">
    <h2 style="font-size:52px;margin-bottom:50px;">Key Points</h2>
    <ul id="bullets-s1" style="list-style:none;padding:0;gap:28px;display:flex;flex-direction:column;">
      <li style="opacity:0;transform:translateY(18px) scale(0.97);">
        <div style="background:rgba(255,255,255,0.04);border-radius:20px;padding:28px;border:1px solid rgba(0,245,212,0.15);">
          <span style="color:#00f5d4;font-weight:900;font-size:32px;margin-right:12px;">01</span>
          <span style="font-size:32px;color:#f0f0f5;">Nội dung bullet 1</span>
        </div>
      </li>
    </ul>
  </div>
</div>
```

### Chart.js Bar Chart
```html
<div class="slide" id="s2">
  <div class="content" style="padding:80px 60px 0;">
    <h2 style="font-size:52px;margin-bottom:40px;">So sánh</h2>
    <div style="background:rgba(255,255,255,0.04);border-radius:24px;padding:40px;border:1px solid rgba(191,90,242,0.2);">
      <canvas id="myChart" style="width:100%;height:480px;"></canvas>
      <script>
      (function(){
        const ctx = document.getElementById('myChart').getContext('2d');
        window.myChart = new Chart(ctx, {
          type: 'bar',
          data: { labels: ['A','B','C'], datasets: [{ data: [0,0,0], backgroundColor: ['#00f5d4','#bf5af2','#ff2d55'] }] },
          options: { animation: false, responsive: true, scales: { y: { beginAtZero: true } } }
        });
        window.myChart._finalData = [85, 62, 90];
      })();
      </script>
    </div>
  </div>
</div>
```

### Counter Stats
```html
<div class="slide" id="s4">
  <div class="content" style="padding:80px 60px 0;">
    <h2 style="font-size:52px;margin-bottom:60px;">Kết quả</h2>
    <div style="display:flex;justify-content:space-around;gap:40px;">
      <div style="text-align:center;">
        <div id="counter1" style="font-size:96px;font-weight:900;color:#00f5d4;text-shadow:0 0 60px rgba(0,245,212,0.4);">0</div>
        <div style="font-size:28px;color:rgba(240,240,245,0.7);">Label A</div>
      </div>
    </div>
  </div>
</div>
```

### Comparison Table
```html
<div class="slide" id="s5">
  <div class="content" style="padding:80px 60px 0;">
    <h2 style="font-size:52px;margin-bottom:40px;">So sánh</h2>
    <table style="width:100%;border-collapse:collapse;font-size:28px;">
      <tr style="background:rgba(0,245,212,0.1);"><th style="padding:20px;text-align:left;color:#00f5d4;">Feature</th><th style="padding:20px;text-align:center;">A</th><th style="padding:20px;text-align:center;">B</th></tr>
      <tr style="border-bottom:1px solid rgba(255,255,255,0.06);"><td style="padding:20px;">Speed</td><td style="padding:20px;text-align:center;color:#30d158;">Fast</td><td style="padding:20px;text-align:center;color:#ff2d55;">Slow</td></tr>
    </table>
  </div>
</div>
```

### Before/After Split
```html
<div class="slide" id="s6">
  <div class="content" style="padding:80px 60px 0;">
    <h2 style="font-size:52px;margin-bottom:40px;">Trước vs Sau</h2>
    <div style="display:flex;gap:24px;">
      <div id="ba-before" style="flex:1;background:rgba(255,45,85,0.06);border-radius:24px;padding:36px;border:1px solid rgba(255,45,85,0.2);opacity:0;transform:translateX(-30px);">
        <div style="font-size:24px;color:#ff2d55;font-weight:700;margin-bottom:16px;text-align:center;">TRƯỚC</div>
      </div>
      <div id="ba-after" style="flex:1;background:rgba(48,209,88,0.06);border-radius:24px;padding:36px;border:1px solid rgba(48,209,88,0.2);opacity:0;transform:translateX(30px);">
        <div style="font-size:24px;color:#30d158;font-weight:700;margin-bottom:16px;text-align:center;">SAU</div>
      </div>
    </div>
  </div>
</div>
```

### Quote Card + CTA
```html
<div class="slide" id="s7">
  <div class="content" style="padding:80px 60px 0;">
    <div style="background:rgba(255,255,255,0.04);border-radius:28px;padding:60px 50px;border:1px solid rgba(0,245,212,0.2);position:relative;margin-top:40px;">
      <div style="position:absolute;top:-30px;left:50px;font-size:80px;color:#00f5d4;opacity:0.3;font-family:Georgia,serif;">&ldquo;</div>
      <p id="quote-text" style="font-size:36px;color:#f0f0f5;line-height:1.6;font-style:italic;opacity:0;transform:translateY(20px);">
        Câu quote đầy cảm hứng.
      </p>
      <div id="quote-author" style="margin-top:30px;text-align:right;opacity:0;transform:translateY(16px);">
        <span style="font-size:26px;color:#00f5d4;font-weight:700;">&mdash; Tên tác giả</span>
      </div>
    </div>
  </div>
</div>
```