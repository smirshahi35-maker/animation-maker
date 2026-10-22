// NODE_PATH=/opt/node-tools/node_modules node scripts/render.js [outdir] [--h 1350] [--only 1,7]
//   ->  <outdir>/slide-1.png ... slide-7.png (1080x1080), or slide-N-1080x1350.png with --h
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
(async () => {
  const root = path.resolve(__dirname, '..');
  const args = process.argv.slice(2);
  const opt = k => { const i = args.indexOf(k); return i < 0 ? null : args.splice(i, 2)[1]; };
  const H = +(opt('--h') || 1080);
  const only = (opt('--only') || '').split(',').filter(Boolean).map(Number);
  const out = path.resolve(args[0] || path.join(root, 'renders'));
  fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--no-sandbox', '--allow-file-access-from-files'] })
    .catch(() => chromium.launch());
  const p = await b.newPage({ viewport: { width: 1080, height: H } });
  await p.goto('file://' + path.join(root, 'slides.html') + (H !== 1080 ? `?h=${H}` : ''), { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  const missing = await p.evaluate(() => [...document.fonts].filter(f => f.status !== 'loaded').map(f => f.family + ' ' + f.status));
  const report = await p.evaluate(() => window.fitAll());
  console.log(JSON.stringify(report));
  if (missing.length) console.log('fonts not loaded:', missing);
  await p.waitForTimeout(200);
  const n = await p.evaluate(() => document.querySelectorAll('.slide').length);
  for (let i = 1; i <= n; i++) {
    if (only.length && !only.includes(i)) continue;
    const name = H === 1080 ? `slide-${i}.png` : `slide-${i}-1080x${H}.png`;
    await (await p.$('#s' + i)).screenshot({ path: path.join(out, name) });
  }
  await b.close();
})();
