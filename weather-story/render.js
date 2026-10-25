// Renders story.html to a 1080×1920 PNG: node render.js [out.png]
const path = require('path');
const { chromium } = require('playwright');

(async () => {
  const out = path.resolve(process.argv[2] || path.join(__dirname, '../deliverables/weather-story.png'));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.join(__dirname, 'story.html'));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(200);
  await page.screenshot({ path: out });
  await browser.close();
  console.log(out);
})();
