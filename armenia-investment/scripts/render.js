// node render.js stills <outdir> <t1> <t2> ...
// node render.js video <out.mp4> <firstFrame> <lastFrameExclusive>
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const [, , mode, out, ...rest] = process.argv;
const PAGE = 'file://' + path.resolve(__dirname, '../comp/index.html');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', headless: true, args: ['--no-sandbox', '--allow-file-access-from-files'] })
    .catch(() => chromium.launch({ headless: true, args: ['--allow-file-access-from-files'] }));
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  p.on('pageerror', e => console.error('pageerror', e.message));
  await p.goto(PAGE, { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  if (mode === 'stills') {
    for (const t of rest.map(Number)) {
      await p.evaluate(t => window.renderFrame(t), t);
      await p.screenshot({ path: `${out}/t${t.toFixed(2)}.jpg`, type: 'jpeg', quality: 88 });
    }
  } else {
    const [f0, f1] = rest.map(Number);
    const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', '30', '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    const t0 = Date.now();
    for (let f = f0; f < f1; f++) {
      await p.evaluate(t => window.renderFrame(t), f / 30);
      const buf = await p.screenshot({ type: 'jpeg', quality: 93 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if ((f - f0) % 100 === 0) console.log(`${out}: frame ${f} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
    }
    ff.stdin.end();
    await new Promise(r => ff.on('close', r));
  }
  await b.close();
})();
