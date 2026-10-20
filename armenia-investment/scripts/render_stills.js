// node render_stills.js <html> <outdir> <frameId...>
const { chromium } = require('playwright');
const [,, html, outdir, ...ids] = process.argv;
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', headless: true, args: ['--no-sandbox'] }).catch(() => chromium.launch({ headless: true }));
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  for (const id of ids) {
    await p.goto('file://' + html + '#' + id, { waitUntil: 'load' });
    await p.reload({ waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    await p.waitForTimeout(300);
    await p.screenshot({ path: `${outdir}/${id}.png` });
    console.log('wrote', id);
  }
  await b.close();
})();
