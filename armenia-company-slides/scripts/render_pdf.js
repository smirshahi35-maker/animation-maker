// NODE_PATH=/opt/node-tools/node_modules node scripts/render_pdf.js [out.pdf]  ->  A4 scenario PDF from pdf/scenario.html
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const root = path.resolve(__dirname, '..');
  const out = path.resolve(process.argv[2] || path.join(root, '../deliverables/armenia-company-scenario.pdf'));
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--no-sandbox', '--allow-file-access-from-files'] })
    .catch(() => chromium.launch());
  const p = await b.newPage();
  await p.goto('file://' + path.join(root, 'pdf/scenario.html'), { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  const bad = await p.evaluate(() => [...document.images].filter(i => !i.naturalWidth).map(i => i.getAttribute('src')));
  if (bad.length) { console.error('missing images:', bad); process.exit(1); }
  await p.pdf({ path: out, preferCSSPageSize: true, printBackground: true });
  console.log(out);
  await b.close();
})();
