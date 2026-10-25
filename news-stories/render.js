// Renders every story in news.html to 1080×1920 PNGs: node render.js [outdir]
const path = require('path');
const { chromium } = require('playwright');

(async () => {
  const outDir = path.resolve(process.argv[2] || path.join(__dirname, '../deliverables'));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  for (let i = 1; i <= 3; i++) {
    await page.goto('about:blank');
    await page.goto('file://' + path.join(__dirname, 'news.html') + '#' + i);
    await page.waitForSelector('body[data-ready="1"]');
    await page.waitForTimeout(200);
    const out = path.join(outDir, `armenia-news-${i}.png`);
    await page.screenshot({ path: out });
    console.log(out);
  }
  await browser.close();
})();
