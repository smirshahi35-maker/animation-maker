// Layout audit for every text line in compositions/sNN.html, measured by ink (glyph outlines),
// not by advance boxes: AbarHigh's periods carry wide side-bearings, so «...» lines centred by box
// read as off-centre. Rules for each `.ln`:
//   - ink stays inside its column (.txt: 96–984, the s15 card's padding box, the s07 name block);
//   - .txt lines are at most MAX_W (840px) of ink, i.e. 24px clear of the column;
//   - centred lines have their ink centred (±2px); right-aligned lines end on the column edge.
// Also reports the decorative glyphs (year, «چرا؟», the clock) so their CSS can be centred by ink.
// Run: node tools/measure_lines.cjs [out.json]   check only (optionally save rows), exits 1 on any violation
//      node tools/measure_lines.cjs --fit    also write tools/line_fit.json (per-line dx), then
//                                            re-run tools/build_scenes.py and check again
const fs = require('fs'), path = require('path'), os = require('os');
let pw;
try { pw = require('playwright-core'); } catch { pw = require('/opt/node-tools/node_modules/playwright-core'); }
const ROOT = path.dirname(__dirname);
const FIT_PATH = path.join(__dirname, 'line_fit.json');
const MAX_W = 840, TOL = 2;
const BROWSER = process.env.HYPERFRAMES_BROWSER_PATH || '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell';
const FIT = process.argv.includes('--fit');
const OUT_JSON = process.argv.slice(2).find((a) => !a.startsWith('--'));

(async () => {
  const fit = fs.existsSync(FIT_PATH) ? JSON.parse(fs.readFileSync(FIT_PATH, 'utf8')) : {};
  const browser = await pw.chromium.launch({ executablePath: BROWSER });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'hf-lines-'));
  const scenes = JSON.parse(fs.readFileSync(path.join(ROOT, 'compositions/scenes.json'))).map((s) => s.id);
  const rows = [];
  for (const sid of scenes) {
    const src = fs.readFileSync(path.join(ROOT, `compositions/${sid}.html`), 'utf8');
    // Static layout only: the template without its timeline script.
    const tpl = src.split('<template>')[1].split('</template>')[0].replace(/<script[\s\S]*?<\/script>/g, '');
    const file = path.join(tmpDir, `${sid}.html`);
    fs.writeFileSync(file, `<!doctype html><html lang="fa"><head><meta charset="utf-8"><base href="file://${ROOT}/">` +
      `<style>body{margin:0;width:1080px;height:1920px;position:relative;overflow:hidden}</style></head><body>${tpl}</body></html>`);
    await page.goto('file://' + file);
    await page.evaluate(() => Promise.all([document.fonts.load('100px AbarHigh'), document.fonts.load('100px Oswald')]));
    if (!(await page.evaluate(() => document.fonts.check('100px AbarHigh')))) {
      console.error(`${sid}: AbarHigh did not load (assets/fonts/AbarHigh-Regular.otf missing?)`);
      process.exit(2);
    }
    rows.push(...(await page.evaluate(({ sid, MAX_W, TOL }) => {
      const ctx = document.createElement('canvas').getContext('2d');
      // Ink extent of one run of text laid out in `el`, from canvas glyph bounds at the box's left edge.
      const ink = (el, text) => {
        const cs = getComputedStyle(el), r = el.getBoundingClientRect();
        ctx.font = `${cs.fontStyle} ${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
        ctx.direction = cs.direction; ctx.textAlign = 'left'; ctx.letterSpacing = cs.letterSpacing === 'normal' ? '0px' : cs.letterSpacing;
        const m = ctx.measureText(text);
        return { l: r.left - m.actualBoundingBoxLeft, r: r.left + m.actualBoundingBoxRight, adv: m.width, box: r.width };
      };
      const out = [];
      document.querySelectorAll('.ln').forEach((ln) => {
        const box = ln.closest('.txt, #s15-card, #s07-name');
        const cs = getComputedStyle(box), br = box.getBoundingClientRect();
        const cl = br.left + parseFloat(cs.paddingLeft), cr = br.right - parseFloat(cs.paddingRight);
        let l = 1e9, r = -1e9, drift = 0;
        ln.querySelectorAll('.w').forEach((w) => {
          const k = ink(w, w.textContent);
          drift = Math.max(drift, Math.abs(k.adv - k.box));
          l = Math.min(l, k.l); r = Math.max(r, k.r);
        });
        ln.querySelectorAll('.ul').forEach((u) => { const k = u.getBoundingClientRect(); l = Math.min(l, k.left); r = Math.max(r, k.right); });
        const align = getComputedStyle(ln).textAlign;
        const target = align === 'right' ? cr : (cl + cr) / 2;
        const err = align === 'right' ? r - cr : (l + r) / 2 - target;
        // #s07-name shrink-wraps its widest line, so only the right edge is checked there.
        const over = box.id === 's07-name' ? 0 : Math.max(0, cl - l, r - cr), wide = box.classList.contains('txt') && r - l > MAX_W;
        const lr = ln.getBoundingClientRect();
        out.push({ sid, key: `${sid}|${ln.textContent.trim().replace(/\s+/g, ' ')}`, text: ln.textContent.trim(), size: parseFloat(getComputedStyle(ln).fontSize), top: Math.round(lr.top), bottom: Math.round(lr.bottom),
          align, left: Math.round(l), right: Math.round(r), width: Math.round(r - l), err: Math.round(err), over: Math.round(over), wide,
          drift: Math.round(drift), bad: over > 0.5 || wide || Math.abs(err) > TOL });
      });
      // Decorative glyphs centred by CSS: ink error against the frame centre (the clock: its pill).
      for (const sel of ['#s03-year', '#s13-why', '#s12-time']) {
        const el = document.querySelector(sel); if (!el) continue;
        const rg = document.createRange(); rg.selectNodeContents(el);
        const tb = rg.getBoundingClientRect(), cs = getComputedStyle(el);
        ctx.font = `${cs.fontStyle} ${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
        ctx.direction = cs.direction; ctx.textAlign = 'left'; ctx.letterSpacing = cs.letterSpacing === 'normal' ? '0px' : cs.letterSpacing;
        const m = ctx.measureText(el.textContent);
        const l = tb.left - m.actualBoundingBoxLeft, r = tb.left + m.actualBoundingBoxRight;
        const ref = sel === '#s12-time' ? el.getBoundingClientRect() : { left: 0, right: 1080 };
        out.push({ sid, deco: sel, text: el.textContent.trim(), left: Math.round(l), right: Math.round(r), err: Math.round((l + r) / 2 - (ref.left + ref.right) / 2) });
      }
      return out;
    }, { sid, MAX_W, TOL })));
  }
  await browser.close();
  fs.rmSync(tmpDir, { recursive: true, force: true });

  if (OUT_JSON) fs.writeFileSync(OUT_JSON, JSON.stringify(rows, null, 1));
  const lines = rows.filter((r) => !r.deco);
  for (const r of rows) {
    if (r.deco) { console.log(`deco ${r.sid} ${r.deco} ink [${r.left},${r.right}] err ${r.err}  ${r.text}`); continue; }
    const notes = [r.over ? `over ${r.over}` : '', r.wide ? `wider than ${MAX_W}` : '', r.drift > 1 ? `canvas/box drift ${r.drift}` : ''].filter(Boolean).join(', ');
    console.log(`${r.bad ? 'FAIL' : ' ok '} ${r.sid} ${String(r.size).padStart(3)}px ink w${String(r.width).padStart(4)} [${r.left},${r.right}] err ${String(r.err).padStart(3)} dx ${String(fit[r.key] || 0).padStart(3)}${notes ? '  ' + notes : ''}  ${r.text}`);
  }
  if (FIT) {
    const next = {};
    for (const r of lines) {
      const dx = Math.round((fit[r.key] || 0) - r.err);
      if (dx) next[r.key] = dx;
    }
    fs.writeFileSync(FIT_PATH, JSON.stringify(next, null, 1) + '\n');
    console.log(`wrote ${path.relative(ROOT, FIT_PATH)} (${Object.keys(next).length} offsets); now run python3 tools/build_scenes.py and check again`);
  }
  const bad = lines.filter((r) => r.bad).length;
  console.log(bad ? `${bad} line(s) off-centre or too wide` : `all ${lines.length} lines inside their column and centred by ink`);
  process.exit(bad && !FIT ? 1 : 0);
})();
