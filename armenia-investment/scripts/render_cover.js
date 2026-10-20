// node render_cover.js  -> cover/cover-1080x1920.png and cover/cover-grid-1080x1440.png (centre crop shown on the profile grid)
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', headless: true, args: ['--no-sandbox', '--allow-file-access-from-files'] })
    .catch(() => chromium.launch({ headless: true }));
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.resolve(__dirname, '../cover/cover.html'), { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(300);
  const dir = path.resolve(__dirname, '../cover');
  await p.screenshot({ path: `${dir}/cover-1080x1920.png` });
  await p.screenshot({ path: `${dir}/cover-grid-1080x1440.png`, clip: { x: 0, y: 240, width: 1080, height: 1440 } });
  const w = await p.evaluate(() => [...document.querySelectorAll('.title div')].map(d => { const r = document.createRange(); r.selectNodeContents(d); return Math.round(r.getBoundingClientRect().width); }));
  console.log('title widths', w);
  await b.close();
})();
