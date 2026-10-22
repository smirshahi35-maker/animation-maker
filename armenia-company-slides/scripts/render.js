// NODE_PATH=/opt/node-tools/node_modules node scripts/render.js [outdir]  ->  <outdir>/slide-1.png ... slide-7.png (1080x1080)
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
(async () => {
  const root = path.resolve(__dirname, '..');
  const out = path.resolve(process.argv[2] || path.join(root, 'renders'));
  fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--no-sandbox', '--allow-file-access-from-files'] })
    .catch(() => chromium.launch());
  const p = await b.newPage({ viewport: { width: 1080, height: 1080 } });
  await p.goto('file://' + path.join(root, 'slides.html'), { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  const missing = await p.evaluate(() => [...document.fonts].filter(f => f.status !== 'loaded').map(f => f.family + ' ' + f.status));
  const report = await p.evaluate(() => window.fitAll());
  console.log(JSON.stringify(report));
  if (missing.length) console.log('fonts not loaded:', missing);
  await p.waitForTimeout(200);
  const n = await p.evaluate(() => document.querySelectorAll('.slide').length);
  for (let i = 1; i <= n; i++) {
    await (await p.$('#s' + i)).screenshot({ path: path.join(out, `slide-${i}.png`) });
  }
  await b.close();
})();
