// Renders each slide of carousel.html to a 1080×1350 PNG: node render.js [outdir]
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

(async () => {
  const outDir = path.resolve(process.argv[2] || path.join(__dirname, '../deliverables/rent-carousel'));
  fs.mkdirSync(outDir, { recursive: true });
  const abar = ['otf', 'ttf'].some(ext => fs.existsSync(path.join(__dirname, 'fonts', `Abar-Regular.${ext}`)));
  if (!abar) console.warn('fonts/Abar-Regular.otf not found: body text falls back to Vazirmatn');

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.join(__dirname, 'carousel.html'));
  await page.waitForSelector('body[data-ready="1"]');
  await page.waitForTimeout(200);
  const slides = page.locator('.slide');
  const n = await slides.count();
  for (let i = 0; i < n; i++) {
    const out = path.join(outDir, `slide-${i + 1}.png`);
    await slides.nth(i).screenshot({ path: out });
    console.log(out);
  }
  await browser.close();
})();
