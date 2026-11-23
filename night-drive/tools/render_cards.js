const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const dir = process.argv[2];
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  await p.goto('file://' + path.join(dir, 'cards.html'));
  await p.evaluate(() => document.fonts.ready);
  for (const id of ['opening', 'title_fa', 'title_en', 'end']) {
    await p.evaluate(id => { document.querySelectorAll('.card').forEach(c => c.style.display = c.id === id ? 'flex' : 'none'); }, id);
    await p.waitForTimeout(100);
    await p.screenshot({ path: path.join(dir, id + '.png'), omitBackground: true });
  }
  await b.close();
})();
