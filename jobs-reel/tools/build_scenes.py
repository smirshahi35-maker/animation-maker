"""Generate compositions/sNN.html for the Jobs reel.

Word cues come from assets/audio/vo/narration.lines.json ("L05:6" = line L05, word 6), so every
word lands on the narration. Scene windows live in SCENES (comp seconds); each scene overlaps the
next by OVERLAP seconds and cross-fades on the shared paper (except hard cuts).

Run: python3 tools/build_scenes.py
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINES = {l['id']: l for l in json.load(open(os.path.join(ROOT, 'assets/audio/vo/narration.lines.json')))['lines']}
OVERLAP = 0.5
LEAD = 0.08  # words appear just before they are spoken

# id, start, end (boundary with the next scene), flags
SCENES = [
    ('s01', 0.00, 2.20, {}),
    ('s02', 2.20, 8.70, {}),
    ('s03', 8.70, 11.75, {}),
    ('s04', 11.75, 14.45, {}),
    ('s05', 14.45, 18.70, {}),
    ('s06', 18.70, 28.80, {}),
    ('s07', 28.80, 33.55, {}),
    ('s08', 33.55, 37.05, {}),
    ('s09', 37.05, 46.45, {}),
    ('s10', 46.45, 55.30, {'cut_out': True}),
    ('s11', 55.30, 59.45, {'cut_in': True}),
    ('s12', 59.45, 65.75, {}),
    ('s13', 65.75, 73.40, {}),
    ('s14', 73.40, 78.80, {}),
    ('s15', 78.80, 94.30, {'last': True}),
]
WIN = {s[0]: s for s in SCENES}


def cue(ref, sid):
    """'L05:6' -> scene-relative seconds; numbers pass through."""
    start = WIN[sid][1]
    if isinstance(ref, (int, float)):
        return round(ref, 3)
    lid, idx = ref.split(':')
    return round(LINES[lid]['words'][int(idx)]['t'] - start - LEAD, 3)


def dur(sid):
    _, a, b, f = WIN[sid]
    return round(b - a + (0 if f.get('cut_out') or f.get('last') else OVERLAP), 3)


# ---------- markup helpers ----------
def W(text, ref, cls=''):
    return ('w', text, ref, cls)


def UL(*words, at=None):
    """Words with a hand-drawn underline that draws at `at` (cue ref)."""
    return ('ul', words, at)


def line(sid, items, size, cls='', extra=''):
    out = []
    for it in items:
        if it[0] == 'w':
            out.append(word(sid, it))
        else:
            inner = ' '.join(word(sid, w) for w in it[1])
            out.append(f'<span class="ulw">{inner}<i class="ul" data-t="{cue(it[2], sid)}"></i></span>')
    style = f'font-size:{size}px;{extra}'
    return f'<div class="ln {cls}" style="{style}">' + ' '.join(out) + '</div>'


def word(sid, w):
    _, text, ref, cls = w
    return f'<span class="w {cls}" data-t="{cue(ref, sid)}">{text}</span>'


def block(sid, top, lines, pid=None, out=None, cls=''):
    attrs = f' id="{sid}-{pid}"' if pid else ''
    if out is not None:
        attrs += f' data-out="{cue(out, sid)}"'
    return f'<div class="txt fa ph {cls}"{attrs} style="top:{top}px">' + ''.join(lines) + '</div>'


def art(sid, img=None, cam_origin='50% 60%'):
    img = img or sid
    return (f'<div class="cam" id="{sid}-cam" style="transform-origin:{cam_origin}">'
            f'<img class="lines" id="{sid}-lines" src="assets/ai/{img}-lines.webp" alt="" />'
            f'<img class="shade" id="{sid}-shade" src="assets/ai/{img}.webp" alt="" /></div>')


HEAD = '''<!doctype html>
<html lang="fa">
  <head>
    <meta charset="UTF-8" />
  </head>
  <body>
    <template>
      <style>
        @font-face { font-family: "AbarHigh"; src: url("assets/fonts/AbarHigh-Regular.otf") format("opentype"); font-weight: 400; font-style: normal; font-display: block; }
        @font-face { font-family: "Oswald"; src: url("assets/fonts/Oswald-Variable.ttf") format("truetype"); font-weight: 200 700; font-style: normal; font-display: block; }
        #root { position: absolute; inset: 0; overflow: hidden; font-family: "AbarHigh", sans-serif; font-synthesis: none; color: #2a231c; }
        .scene { position: absolute; inset: 0; }
        .cam { position: absolute; inset: 0; }
        .cam img { position: absolute; left: -36px; top: -64px; width: 1152px; height: 2048px; display: block; }
        .lines { --m: 100%; -webkit-mask-image: linear-gradient(200deg, #000 42%, transparent 58%); mask-image: linear-gradient(200deg, #000 42%, transparent 58%); -webkit-mask-size: 100% 300%; mask-size: 100% 300%; -webkit-mask-repeat: no-repeat; mask-repeat: no-repeat; -webkit-mask-position: 0% var(--m); mask-position: 0% var(--m); }
        .shade { opacity: 0; }
        .fa { direction: rtl; unicode-bidi: isolate; }
        .txt { position: absolute; left: 96px; right: 96px; text-align: center; }
        .ln { display: block; line-height: 1.34; white-space: nowrap; }
        .w { display: inline-block; opacity: 0; }
        .acc { color: #8b2f1f; }
        .gr { color: #5b5044; }
        .lat { font-family: "Oswald", sans-serif; font-weight: 600; direction: ltr; unicode-bidi: isolate; letter-spacing: 0.01em; }
        .ulw { position: relative; display: inline-block; }
        .ul { position: absolute; display: block; left: -4%; right: -4%; bottom: 0.04em; height: 0.16em;
              background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 20' preserveAspectRatio='none'%3E%3Cpath d='M3 13 C 40 6, 80 15, 120 9 S 180 7, 197 10' fill='none' stroke='%238b2f1f' stroke-width='5' stroke-linecap='round'/%3E%3Cpath d='M10 16 C 60 11, 120 17, 190 12' fill='none' stroke='%238b2f1f' stroke-width='2.5' stroke-linecap='round' opacity='.7'/%3E%3C/svg%3E") no-repeat center / 100% 100%;
              transform-origin: 100% 50%; }
        .frame { position: absolute; overflow: visible; }
        .frame rect { fill: none; stroke: #2a231c; stroke-width: 3; }
__CSS__
      </style>
      <div id="root" data-composition-id="__ID__" data-width="1080" data-height="1920">
        <div class="scene" id="__ID__-scene">
__BODY__
        </div>
      </div>
      <script>
        (function () {
          const ID = "__ID__", D = __DUR__;
          const tl = gsap.timeline({ paused: true });
          const scene = document.getElementById(ID + "-scene");
          const q = (s) => scene.querySelectorAll(s);
          // Scene in/out on the shared paper
          __INOUT__
          // Pencil reveal: contour pass wipes in, shading follows, contours settle under it
          function sketch(id, t, o) {
            o = o || {};
            const lines = "#" + id + "-lines", shade = "#" + id + "-shade";
            tl.fromTo(lines, { "--m": (o.from || 100) + "%" }, { "--m": "0%", duration: o.d || 1.0, ease: "power1.inOut" }, t);
            tl.fromTo(shade, { opacity: o.shade0 || 0 }, { opacity: 1, duration: o.sd || 1.1, ease: "power1.inOut" }, t + (o.lag == null ? 0.45 : o.lag));
            tl.to(lines, { opacity: 0.35, duration: 0.6, ease: "none" }, t + (o.lag == null ? 0.45 : o.lag) + (o.sd || 1.1));
          }
          // Words: soft blur + rise, timed to the narration
          q(".w[data-t]").forEach((el) => {
            tl.fromTo(el, { opacity: 0, y: 26, filter: "blur(8px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.45, ease: "power3.out" }, +el.dataset.t);
          });
          q(".ul[data-t]").forEach((el) => {
            tl.fromTo(el, { scaleX: 0 }, { scaleX: 1, duration: 0.5, ease: "power2.inOut" }, +el.dataset.t);
          });
          q(".ph[data-out]").forEach((el) => {
            tl.to(el, { opacity: 0, y: -34, filter: "blur(6px)", duration: 0.4, ease: "power2.in" }, +el.dataset.out);
          });
__JS__
          window.__timelines[ID] = tl;
        })();
      </script>
    </template>
  </body>
</html>
'''


def inout(sid):
    f = WIN[sid][3]
    d = dur(sid)
    out = []
    if not f.get('cut_in') and sid != 's01':
        out.append(f'tl.fromTo(scene, {{ opacity: 0 }}, {{ opacity: 1, duration: {OVERLAP}, ease: "power1.out" }}, 0);')
    if not f.get('cut_out') and not f.get('last'):
        out.append(f'tl.to(scene, {{ opacity: 0, filter: "blur(3px)", duration: {OVERLAP}, ease: "power1.in" }}, {round(d - OVERLAP, 3)});')
    return '\n          '.join(out) or '// hard cut'


def cam(sid, s0, s1, x0=0, x1=0, y0=0, y1=0, t=0, d=None, ease='sine.inOut'):
    d = dur(sid) - t if d is None else d
    return (f'tl.fromTo("#{sid}-cam", {{ scale: {s0}, x: {x0}, y: {y0} }}, '
            f'{{ scale: {s1}, x: {x1}, y: {y1}, duration: {round(d, 3)}, ease: "{ease}" }}, {t});')


def scene_html(sid, body, js, css=''):
    html = HEAD.replace('__ID__', sid).replace('__DUR__', str(dur(sid)))
    html = html.replace('__CSS__', css).replace('__BODY__', body).replace('__INOUT__', inout(sid)).replace('__JS__', js)
    open(os.path.join(ROOT, 'compositions', f'{sid}.html'), 'w').write(html)


# ---------------------------------------------------------------- scenes
def s01():
    sid = 's01'
    body = art(sid, cam_origin='45% 60%') + block(sid, 250, [
        line(sid, [W('هیچکس', 'L01:0')], 98),
        line(sid, [W('این', 'L01:1'), W('رو', 'L01:1'), W('بهت', 'L01:2')], 140),
        line(sid, [W('نمی‌گه...', 'L01:3')], 98),
    ]) + '<div id="s01-q" class="acc">؟</div>'
    css = '#s01-q { position: absolute; right: 96px; top: 650px; font-size: 520px; line-height: 1; opacity: 0; }\n        #s01-cam img { top: 170px; }'
    js = f'''
          sketch(ID, 0, {{ from: 45, d: 0.7, lag: 0, sd: 0.7, shade0: 0.55 }});
          {cam(sid, 1.0, 1.07, y1=-20)}
          tl.fromTo("#s01-q", {{ opacity: 0, scale: 0.55, rotation: -14 }}, {{ opacity: 1, scale: 1, rotation: 0, duration: 0.55, ease: "back.out(2.2)" }}, {cue('L01:3', sid) + 0.12});
          tl.to("#s01-q", {{ rotation: 6, duration: 0.9, ease: "sine.inOut" }}, {cue('L01:3', sid) + 0.7});'''
    scene_html(sid, body, js, css)


def s02():
    sid = 's02'
    body = art(sid, cam_origin='50% 45%') + block(sid, 205, [
        line(sid, [W('ولی', 'L02:0'), W('گاهی', 'L02:1')], 86, 'gr'),
        line(sid, [W('بزرگ‌ترین', 'L02:2'), W('موفقیت‌ها', 'L02:3')], 116),
        line(sid, [W('از', 'L02:4'), UL(W('بدترین', 'L02:5', 'acc'), W('شکست‌ها', 'L02:6', 'acc'), at=cue('L02:6', sid) + 0.35)], 104),
        line(sid, [W('شروع', 'L02:7'), W('میشن...', 'L02:8')], 86, 'gr'),
    ])
    js = f'''
          sketch(ID, 0.15, {{ d: 1.2, sd: 1.4 }});
          {cam(sid, 1.0, 1.09, y1=30)}'''
    scene_html(sid, body, js)


def s03():
    sid = 's03'
    # Year card after the style reference: year behind the head, head breaking out of the frame.
    body = '''
          <div id="s03-year">۱۹۸۵</div>
          <div id="s03-panel"></div>
          <svg class="frame" id="s03-frame" width="801" height="1006" style="left:153px;top:647px"><rect x="1.5" y="1.5" width="798" height="1003" pathLength="1" /></svg>
          <div class="cam" id="s03-cam" style="transform-origin:50% 40%"><div id="s03-clip"><img id="s03-cut" src="assets/ai/s03-cut.webp" alt="" /></div></div>
          ''' + block(sid, 92, [line(sid, [W('سال', 'L03:0', 'gr')], 84)])
    css = '''
        #s03-year { position: absolute; left: 0; right: 0; top: 236px; text-align: center; direction: ltr; font-size: 470px; line-height: 1; color: #33291f; opacity: 0; letter-spacing: -0.02em; }
        #s03-panel { position: absolute; left: 156px; top: 650px; width: 795px; height: 1000px; background: rgba(233, 225, 211, 0.45); opacity: 0; }
        #s03-frame rect { stroke-dasharray: 1; stroke-dashoffset: 1; }
        #s03-clip { position: absolute; inset: 0; clip-path: polygon(0 0, 100% 0, 100% 650px, 951px 650px, 951px 1650px, 156px 1650px, 156px 650px, 0 650px); }
        #s03-cut { position: absolute; left: 79px; top: 46px; width: 922px; height: 1638px; opacity: 0; }'''
    t_year = cue('L03:1', sid) + LEAD
    js = f'''
          tl.fromTo("#s03-panel", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.6, ease: "power1.out" }}, 0.05);
          tl.fromTo("#s03-frame rect", {{ strokeDashoffset: 1 }}, {{ strokeDashoffset: 0, duration: 0.9, ease: "power2.inOut" }}, 0.05);
          tl.fromTo("#s03-cut", {{ opacity: 0, y: 70 }}, {{ opacity: 1, y: 0, duration: 0.8, ease: "power3.out" }}, 0.1);
          tl.fromTo("#s03-year", {{ opacity: 0, scale: 1.35, filter: "blur(14px)" }}, {{ opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.32, ease: "power4.out" }}, {t_year - 0.12});
          tl.fromTo("#s03-cam", {{ x: 0 }}, {{ x: 0, keyframes: [{{ x: -9, duration: 0.05 }}, {{ x: 7, duration: 0.05 }}, {{ x: -4, duration: 0.05 }}, {{ x: 0, duration: 0.07 }}], immediateRender: false }}, {t_year + 0.2});
          tl.fromTo("#s03-cam", {{ scale: 1.0 }}, {{ scale: 1.04, duration: {dur(sid)}, ease: "sine.inOut" }}, 0);
          tl.to("#s03-year", {{ scale: 1.04, duration: {round(dur(sid) - t_year - 0.2, 3)}, ease: "sine.out" }}, {round(t_year + 0.2, 3)});'''
    scene_html(sid, body, js, css)


def s04():
    sid = 's04'
    body = art(sid, cam_origin='70% 62%') + block(sid, 230, [
        line(sid, [W('مردی', 'L04:0'), W('که', 'L04:1'), W('خودش', 'L04:2')], 94, 'gr'),
        line(sid, [W('اپل', 'L04:3'), W('رو', 'L04:4'), W('ساخته', 'L04:5'), W('بود...', 'L04:6')], 124),
    ])
    js = f'''
          sketch(ID, 0.15, {{ d: 0.9, sd: 1.0, lag: 0.35 }});
          {cam(sid, 1.0, 1.035, x1=-16)}'''
    scene_html(sid, body, js, '#s04-cam img { top: 10px; }')


def s05():
    sid = 's05'
    body = art(sid, cam_origin='52% 58%') + block(sid, 215, [
        line(sid, [W('از', 'L05:0'), W('شرکتی', 'L05:1'), W('که', 'L05:2'), W('ساخته', 'L05:3'), W('بود', 'L05:4')], 90, 'gr'),
        line(sid, [UL(W('اخراج', 'L05:5', 'acc'), W('شد.', 'L05:6', 'acc'), at=cue('L05:6', sid) + 0.3)], 156),
    ])
    t_slam = cue('L05:6', sid) + LEAD
    css = '#s05-cam img { top: 46px; }'
    js = f'''
          sketch(ID, 0.15, {{ d: 1.0, sd: 1.1, lag: 0.4 }});
          tl.fromTo("#s05-cam", {{ scale: 1.0, y: 0 }}, {{ scale: 1.035, y: 0, duration: {round(t_slam, 3)}, ease: "sine.inOut" }}, 0);
          tl.to("#s05-cam", {{ keyframes: [{{ scale: 1.07, y: 10, duration: 0.08, ease: "power2.out" }}, {{ scale: 1.06, y: 4, duration: 0.25, ease: "power2.out" }}] }}, {t_slam});
          tl.to("#s05-cam", {{ scale: 1.12, y: -40, duration: {round(dur(sid) - t_slam - 0.33, 3)}, ease: "sine.inOut" }}, {round(t_slam + 0.33, 3)});'''
    scene_html(sid, body, js, css)


def s06():
    sid = 's06'
    a_out = cue('L08:0', sid) - 0.45
    b_out = cue('L09:0', sid) - 0.45
    body = art(sid, cam_origin='50% 47%') + block(sid, 215, [
        line(sid, [W('تصور', 'L06:0'), W('کن...', 'L06:1')], 132),
        line(sid, [W('تو', 'L07:0'), W('یک', 'L07:1'), W('شرکت', 'L07:2'), W('تأسیس', 'L07:3'), W('می‌کنی،', 'L07:4')], 82, 'gr'),
        line(sid, [W('رشدش', 'L07:5'), W('میدی،', 'L07:6')], 82, 'gr'),
    ], 'a', out=a_out) + block(sid, 215, [
        line(sid, [W('بعد', 'L08:0'), W('یک', 'L08:1'), W('روز', 'L08:2')], 90, 'gr'),
        line(sid, [W('هیئت', 'L08:3'), W('مدیره', 'L08:4')], 126),
        line(sid, [W('بهت', 'L08:5'), W('میگه...', 'L08:6')], 90, 'gr'),
    ], 'b', out=b_out) + block(sid, 250, [
        line(sid, [W('«دیگه', 'L09:0', 'acc'), W('اینجا', 'L09:1', 'acc')], 126),
        line(sid, [UL(W('جایی', 'L09:2', 'acc'), W('نداری.»', 'L09:3', 'acc'), at=cue('L09:3', sid) + 0.3)], 126),
    ], 'c')
    js = f'''
          sketch(ID, 0.55, {{ d: 1.3, sd: 1.5 }});
          tl.fromTo("#s06-cam", {{ scale: 1.0, y: 0 }}, {{ scale: 1.03, y: 0, duration: {round(a_out, 3)}, ease: "sine.inOut" }}, 0);
          tl.to("#s06-cam", {{ scale: 1.16, y: 40, duration: {round(b_out - a_out, 3)}, ease: "power1.inOut" }}, {round(a_out, 3)});
          tl.to("#s06-cam", {{ scale: 1.2, y: 52, duration: {round(dur(sid) - b_out, 3)}, ease: "sine.out" }}, {round(b_out, 3)});'''
    scene_html(sid, body, js)


def s07():
    sid = 's07'
    body = '''
          <div id="s07-panel"></div>
          <svg class="frame" id="s07-frame" width="801" height="1046" style="left:153px;top:607px"><rect x="1.5" y="1.5" width="798" height="1043" pathLength="1" /></svg>
          <div class="cam" id="s07-cam" style="transform-origin:45% 40%"><div id="s07-clip"><img id="s07-cut" src="assets/ai/s07-cut.webp" alt="" /></div></div>
          <div id="s07-name" class="fa">
            ''' + line(sid, [W('استیو', 'L11:0')], 128) + line(sid, [W('جابز', 'L11:1', 'acc')], 128) + '''
            <i id="s07-rule"></i>
            <div class="ln lat" style="font-size:104px;line-height:1.02"><span class="w" data-t="''' + str(cue('L11:2', sid)) + '''">Steve</span></div>
            <div class="ln lat" style="font-size:104px;line-height:1.02"><span class="w" data-t="''' + str(cue('L11:2', sid) + 0.12) + '''">Jobs</span></div>
          </div>
          ''' + block(sid, 190, [line(sid, [W('اسم', 'L10:0'), W('اون', 'L10:1'), W('آدم...', 'L10:2')], 92, 'gr')])
    css = '''
        #s07-panel { position: absolute; left: 156px; top: 610px; width: 795px; height: 1040px; background: rgba(233, 225, 211, 0.45); opacity: 0; }
        #s07-frame rect { stroke-dasharray: 1; stroke-dashoffset: 1; }
        #s07-clip { position: absolute; inset: 0; clip-path: polygon(0 0, 100% 0, 100% 610px, 951px 610px, 951px 1650px, 156px 1650px, 156px 610px, 0 610px); }
        #s07-cut { position: absolute; left: -10px; top: 40px; width: 922px; height: 1638px; opacity: 0; }
        #s07-name { position: absolute; right: 168px; top: 760px; text-align: right; }
        #s07-name .ln { line-height: 1.12; }
        #s07-rule { display: block; width: 250px; height: 4px; margin: 26px 0 30px auto; background: #2a231c; transform-origin: 100% 50%; }'''
    js = f'''
          tl.fromTo("#s07-panel", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.6, ease: "power1.out" }}, 0.1);
          tl.fromTo("#s07-frame rect", {{ strokeDashoffset: 1 }}, {{ strokeDashoffset: 0, duration: 1.0, ease: "power2.inOut" }}, 0.1);
          tl.fromTo("#s07-cut", {{ opacity: 0, y: 60 }}, {{ opacity: 1, y: 0, duration: 1.0, ease: "power3.out" }}, 0.25);
          tl.fromTo("#s07-rule", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.45, ease: "power2.inOut" }}, {cue('L11:1', sid) + 0.35});
          tl.fromTo("#s07-cam", {{ scale: 1.0 }}, {{ scale: 1.045, duration: {dur(sid)}, ease: "sine.inOut" }}, 0);'''
    scene_html(sid, body, js, css)


def s08():
    sid = 's08'
    body = art(sid, cam_origin='50% 60%') + '<div class="fog" id="s08-fog1"></div><div class="fog" id="s08-fog2"></div>' + block(sid, 235, [
        line(sid, [W('خیلی‌ها', 'L12:0'), W('فکر', 'L12:1'), W('می‌کردن', 'L12:2')], 94, 'gr'),
        line(sid, [W('دورانش', 'L12:3'), W('تموم', 'L12:4'), W('شده...', 'L12:5')], 124),
    ])
    css = '''
        .fog { position: absolute; width: 1100px; height: 420px; border-radius: 50%; background: radial-gradient(closest-side, rgba(226, 218, 204, 0.75), rgba(226, 218, 204, 0)); }
        #s08-fog1 { left: -300px; top: 980px; }
        #s08-fog2 { left: 300px; top: 1180px; }'''
    js = f'''
          sketch(ID, 0.15, {{ d: 1.1, sd: 1.3 }});
          {cam(sid, 1.08, 1.0, y0=-20)}
          tl.fromTo("#s08-fog1", {{ x: 0, opacity: 0.6 }}, {{ x: 260, opacity: 1, duration: {dur(sid)}, ease: "none" }}, 0);
          tl.fromTo("#s08-fog2", {{ x: 0, opacity: 0.9 }}, {{ x: -240, opacity: 0.6, duration: {dur(sid)}, ease: "none" }}, 0);'''
    scene_html(sid, body, js, css)


def s09():
    sid = 's09'
    a_out = cue('L14:0', sid) - 0.4
    t_next = cue('L14:12', sid)
    body = art(sid, cam_origin='50% 66%') + block(sid, 330, [
        line(sid, [W('اما', 'L13:0'), W('چیزی', 'L13:1'), W('که', 'L13:2')], 98, 'gr'),
        line(sid, [W('هیچکس', 'L13:3'), W('نمی‌دید...', 'L13:4')], 132),
    ], 'a', out=a_out) + block(sid, 205, [
        line(sid, [W('این', 'L14:0'), W('بود', 'L14:1'), W('که', 'L14:2'), W('همین', 'L14:3'), W('شکست', 'L14:4')], 84, 'gr'),
        line(sid, [W('باعث', 'L14:5'), W('شد', 'L14:6'), W('جابز', 'L14:7'), W('شرکت', 'L14:8'), W('جدیدی', 'L14:9')], 84, 'gr'),
        line(sid, [W('به', 'L14:10'), W('اسم', 'L14:11'), W('NeXT', 'L14:12', 'acc lat next'), W('رو', 'L14:13')], 92, extra='line-height:1.25'),
        line(sid, [W('راه‌اندازی', 'L14:14'), W('کنه...', 'L14:15')], 92),
    ], 'b')
    css = '.next { font-size: 150px; vertical-align: -0.12em; margin: 0 0.12em; }'
    js = f'''
          sketch(ID, {round(a_out + 0.1, 3)}, {{ d: 1.2, sd: 1.3 }});
          tl.fromTo("#s09-cam", {{ scale: 1.0 }}, {{ scale: 1.05, duration: {round(t_next, 3)}, ease: "sine.inOut" }}, 0);
          tl.to("#s09-cam", {{ keyframes: [{{ scale: 1.1, duration: 0.12, ease: "power2.out" }}, {{ scale: 1.09, duration: 0.3, ease: "power2.out" }}] }}, {t_next + LEAD});
          tl.to("#s09-cam", {{ scale: 1.13, duration: {round(dur(sid) - t_next - LEAD - 0.42, 3)}, ease: "sine.inOut" }}, {round(t_next + LEAD + 0.42, 3)});'''
    scene_html(sid, body, js, css)


def s10():
    sid = 's10'
    a_out = cue('L16:0', sid) - 0.42
    body = art(sid, cam_origin='50% 52%') + '<div id="s10-glow"></div>' + block(sid, 205, [
        line(sid, [W('و', 'L15:0'), W('بعدها', 'L15:1'), W('همین', 'L15:2'), W('تجربه', 'L15:3')], 86, 'gr'),
        line(sid, [W('باعث', 'L15:4'), W('شد', 'L15:5'), W('وقتی', 'L15:6'), W('دوباره', 'L15:7')], 86, 'gr'),
        line(sid, [W('به', 'L15:8'), W('اپل', 'L15:9'), W('برگشت،', 'L15:10')], 108),
    ], 'a', out=a_out) + block(sid, 215, [
        line(sid, [W('مسیر', 'L16:0'), W('این', 'L16:1'), W('شرکت', 'L16:2'), W('رو', 'L16:3')], 104, 'gr'),
        line(sid, [UL(W('تغییر', 'L16:4', 'acc'), W('بده...', 'L16:5', 'acc'), at=cue('L16:5', sid) + 0.3)], 148),
    ], 'b')
    css = '#s10-glow { position: absolute; left: 140px; top: 640px; width: 800px; height: 800px; border-radius: 50%; background: radial-gradient(closest-side, rgba(255, 246, 226, 0.55), rgba(255, 246, 226, 0)); opacity: 0; }'
    js = f'''
          sketch(ID, 0.2, {{ d: 1.2, sd: 1.3 }});
          {cam(sid, 1.0, 1.12, y1=20)}
          tl.fromTo("#s10-glow", {{ opacity: 0, scale: 0.8 }}, {{ opacity: 1, scale: 1.05, duration: 2.2, ease: "power2.out" }}, 1.4);
          tl.to("#s10-glow", {{ scale: 1.15, opacity: 0.75, duration: 1.1, ease: "sine.inOut", yoyo: true, repeat: 3 }}, 3.6);'''
    scene_html(sid, body, js, css)


def s11():
    sid = 's11'
    t_erase = cue('L17:6', sid) + 0.5
    body = art(sid, cam_origin='40% 60%') + block(sid, 230, [
        line(sid, [W('اما', 'L17:0'), W('اصلاً', 'L17:1'), W('مهم', 'L17:2'), W('نیست', 'L17:3')], 100, 'gr'),
        line(sid, [W('جابز', 'L17:4'), W('چطور', 'L17:5'), W('برگشت...', 'L17:6')], 124),
    ])
    js = f'''
          // Hard cut in: the sketch is already half drawn, as if the story froze mid-stroke
          sketch(ID, 0, {{ from: 30, d: 0.5, lag: 0.1, sd: 0.6, shade0: 0.35 }});
          {cam(sid, 1.03, 1.0)}
          // ...then it is erased: the story no longer matters
          tl.to(["#s11-lines", "#s11-shade"], {{ "--m": "100%", opacity: 0, duration: 0.9, ease: "power2.in" }}, {round(t_erase, 3)});'''
    scene_html(sid, body, js)


def s12():
    sid = 's12'
    body = art(sid, cam_origin='50% 70%') + block(sid, 200, [
        line(sid, [W('مهم', 'L18:0'), W('اینه', 'L18:1'), W('که', 'L18:2'), W('تو', 'L18:3'), W('الان', 'L18:4')], 88, 'gr'),
        line(sid, [W('بیشتر', 'L18:5'), W('از', 'L18:6'), UL(W('یک', 'L18:7', 'acc'), W('دقیقه', 'L18:8', 'acc'), at=cue('L18:8', sid) + 0.3)], 126),
        line(sid, [W('موندی', 'L18:9'), W('و', 'L18:10'), W('این', 'L18:11'), W('داستان', 'L18:12'), W('رو', 'L18:13')], 88, 'gr'),
        line(sid, [W('دنبال', 'L18:14'), W('کردی.', 'L18:15')], 88, 'gr'),
    ]) + '<div id="s12-clock"><span id="s12-time">۰۰:۵۹</span></div>'
    css = '''
        #s12-clock { position: absolute; left: 0; right: 0; top: 735px; display: flex; justify-content: center; }
        #s12-time { display: block; direction: ltr; font-family: "Oswald", sans-serif; font-weight: 500; font-size: 64px; line-height: 1; padding: 16px 34px 18px; border: 3px solid #2a231c; border-radius: 60px; color: #2a231c; opacity: 0; }'''
    start = WIN[sid][1]
    js = f'''
          sketch(ID, 0.2, {{ d: 1.1, sd: 1.3 }});
          {cam(sid, 1.0, 1.06)}
          // The film's own elapsed time: it rolls over to 1:00 as the line begins
          const FA = "۰۱۲۳۴۵۶۷۸۹", fa = (n) => String(n).padStart(2, "0").replace(/\\d/g, (d) => FA[d]);
          const timeEl = document.getElementById("s12-time");
          const clock = {{ t: {start} }};
          const paint = () => {{ const s = Math.floor(clock.t + 1e-6); timeEl.textContent = fa(Math.floor(s / 60)) + ":" + fa(s % 60); }};
          paint();
          tl.fromTo(clock, {{ t: {start} }}, {{ t: {round(start + dur(sid), 3)}, duration: {dur(sid)}, ease: "none", onUpdate: paint }}, 0);
          tl.fromTo("#s12-time", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power2.out" }}, 0.15);
          tl.fromTo("#s12-time", {{ scale: 1 }}, {{ scale: 1.12, duration: 0.12, ease: "power2.out", yoyo: true, repeat: 1, immediateRender: false }}, {round(60 - start, 3)});'''
    scene_html(sid, body, js, css)


def s13():
    sid = 's13'
    t_shift = cue('L20:0', sid) - 0.15
    body = art(sid, cam_origin='50% 47%') + '<div id="s13-why" class="acc fa">چرا؟</div>' + block(sid, 1125, [
        line(sid, [W('چون', 'L20:0'), W('من', 'L20:1'), W('تونستم', 'L20:2')], 80, 'gr'),
        line(sid, [W('یک', 'L20:3'), W('اتفاق', 'L20:4'), W('ساده', 'L20:5'), W('رو', 'L20:6')], 80, 'gr'),
        line(sid, [W('تبدیل', 'L20:7'), W('کنم', 'L20:8'), W('به', 'L20:9'), W('یک', 'L20:10'), W('تصویر', 'L20:11')], 96),
        line(sid, [W('توی', 'L21:0'), W('ذهن', 'L21:1'), W('تو.', 'L21:2')], 96),
    ])
    css = '#s13-why { position: absolute; left: 0; right: 0; top: 150px; text-align: center; font-size: 300px; line-height: 1.2; opacity: 0; transform-origin: 50% 0%; }'
    js = f'''
          tl.fromTo("#s13-why", {{ opacity: 0, scale: 1.6, filter: "blur(16px)" }}, {{ opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.35, ease: "power4.out" }}, {cue('L19:0', sid)});
          sketch(ID, 0.75, {{ d: 1.1, sd: 1.2 }});
          tl.fromTo("#s13-cam", {{ scale: 1.0, y: 0 }}, {{ scale: 1.02, y: 0, duration: {round(t_shift, 3)}, ease: "sine.inOut" }}, 0);
          tl.to("#s13-cam", {{ scale: 0.92, y: -150, duration: 0.8, ease: "power3.inOut" }}, {round(t_shift, 3)});
          tl.to("#s13-cam", {{ scale: 0.97, y: -140, duration: {round(dur(sid) - t_shift - 0.8, 3)}, ease: "sine.inOut" }}, {round(t_shift + 0.8, 3)});
          tl.to("#s13-why", {{ scale: 0.55, y: -40, duration: 0.8, ease: "power3.inOut" }}, {round(t_shift, 3)});'''
    scene_html(sid, body, js, css)


def s14():
    sid = 's14'
    # Monitor screen rect in comp px (tuned to the generated image; stand-in values until then)
    scr = {'left': 92, 'top': 690, 'width': 896, 'height': 330}
    thumbs = ['s03', 's05', 's06', 's10', 's09', 's13']
    imgs = ''.join(f'<img class="th" src="assets/ai/{t}.webp" alt="" />' for t in thumbs)
    body = art(sid, cam_origin='50% 55%') + f'<div id="s14-screen" style="left:{scr["left"]}px;top:{scr["top"]}px;width:{scr["width"]}px;height:{scr["height"]}px">{imgs}<i id="s14-head"></i></div>' + block(sid, 200, [
        line(sid, [W('و', 'L22:0'), W('این', 'L22:1'), W('دقیقاً', 'L22:2'), W('کاریه', 'L22:3'), W('که', 'L22:4'), W('یک', 'L22:5')], 82, 'gr'),
        line(sid, [W('ادیتور', 'L22:6'), W('و', 'L22:7'), UL(W('موشن', 'L22:8', 'acc'), W('دیزاینر', 'L22:9', 'acc'), at=cue('L22:9', sid) + 0.3)], 114),
        line(sid, [W('انجام', 'L22:10'), W('میده...', 'L22:11')], 82, 'gr'),
    ])
    css = '''
        #s14-screen { position: absolute; overflow: hidden; background: #e9e1d3; opacity: 0; }
        #s14-screen .th { position: absolute; left: 50%; top: 50%; width: 46%; height: auto; transform-origin: 50% 50%; opacity: 0; }
        #s14-head { position: absolute; top: 0; bottom: 0; left: 0; width: 3px; background: #8b2f1f; }'''
    js = f'''
          sketch(ID, 0.2, {{ d: 1.1, sd: 1.2 }});
          {cam(sid, 1.0, 1.08, y1=-10)}
          // The editor's monitor plays this very film: our sketches cut on the playhead
          tl.fromTo("#s14-screen", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.5, ease: "power1.out" }}, 1.2);
          const th = q(".th");
          th.forEach((el, i) => {{
            const t = 1.3 + i * 0.68;
            tl.fromTo(el, {{ opacity: 0, xPercent: -50, yPercent: -38, scale: 1.0 }}, {{ opacity: 1, xPercent: -50, yPercent: -38, scale: 1.06, duration: 0.7, ease: "none" }}, t);
            if (i < th.length - 1) tl.set(el, {{ opacity: 0 }}, t + 0.68);
          }});
          tl.fromTo("#s14-head", {{ x: 0 }}, {{ x: {scr['width'] - 3}, duration: {round(dur(sid) - 1.3, 3)}, ease: "none" }}, 1.3);'''
    scene_html(sid, body, js, css)


def s15():
    sid = 's15'
    t_on = cue('L23:9', sid) + LEAD
    t_card = cue('L24:0', sid) - 0.35
    body = art(sid, cam_origin='50% 50%') + '<div id="s15-glow"></div>' + block(sid, 205, [
        line(sid, [W('هر', 'L23:0'), W('چیزی', 'L23:1'), W('که', 'L23:2'), W('تو', 'L23:3'), W('ذهنت', 'L23:4')], 88, 'gr'),
        line(sid, [W('تصور', 'L23:5'), W('می‌کنی،', 'L23:6')], 122),
        line(sid, [W('میشه', 'L23:7'), W('به', 'L23:8'), UL(W('تصویر', 'L23:9', 'acc'), at=cue('L23:9', sid) + 0.3), W('تبدیل', 'L23:10'), W('کرد.', 'L23:11')], 96),
    ]) + '<div id="s15-card" class="fa">' + line(sid, [W('و', 'L24:0'), W('وقتی', 'L24:1'), W('بتونی', 'L24:2'), W('ایده‌هات', 'L24:3'), W('رو', 'L24:4'), W('تصویری', 'L24:5'), W('کنی،', 'L24:6')], 58) + \
        line(sid, [W('داری', 'L25:0'), W('یک', 'L25:1', 'gold'), W('قدم', 'L25:2', 'gold'), W('بزرگ', 'L25:3', 'gold'), W('برای', 'L25:4'), W('رشد', 'L25:5')], 58) + \
        line(sid, [W('برند', 'L25:6'), W('و', 'L25:7'), W('کسب‌وکارت', 'L25:8'), W('برمی‌داری.', 'L25:9')], 58) + '</div>'
    css = '''
        #s15-glow { position: absolute; left: 190px; top: 560px; width: 700px; height: 760px; border-radius: 50%; background: radial-gradient(closest-side, rgba(255, 238, 196, 0.9), rgba(255, 232, 180, 0.35) 55%, rgba(255, 232, 180, 0)); opacity: 0; }
        #s15-card { position: absolute; left: 84px; right: 84px; top: 1215px; padding: 36px 40px 40px; border-radius: 30px; background: #2a231c; color: #efe6d6; text-align: center; opacity: 0; }
        #s15-card .ln { line-height: 1.42; }
        #s15-card .gold { color: #e3b67c; }'''
    js = f'''
          sketch(ID, 0.2, {{ d: 1.2, sd: 1.4 }});
          tl.fromTo("#s15-cam", {{ scale: 1.0, y: 0 }}, {{ scale: 1.04, y: 0, duration: {round(t_card, 3)}, ease: "sine.inOut" }}, 0);
          tl.to("#s15-cam", {{ scale: 0.9, y: -150, duration: 0.9, ease: "power3.inOut" }}, {round(t_card, 3)});
          tl.to("#s15-cam", {{ scale: 0.93, y: -150, duration: {round(dur(sid) - t_card - 0.9, 3)}, ease: "sine.inOut" }}, {round(t_card + 0.9, 3)});
          tl.to("#s15-glow", {{ y: -140, scale: 0.9, duration: 0.9, ease: "power3.inOut" }}, {round(t_card, 3)});
          // The bulb lights on «تصویر»
          tl.fromTo("#s15-glow", {{ opacity: 0, scale: 0.7 }}, {{ opacity: 1, scale: 1, duration: 0.6, ease: "power2.out" }}, {round(t_on, 3)});
          tl.to("#s15-glow", {{ opacity: 0.8, duration: 1.2, ease: "sine.inOut", yoyo: true, repeat: 7 }}, {round(t_on + 0.6, 3)});
          tl.fromTo("#s15-card", {{ opacity: 0, y: 70 }}, {{ opacity: 1, y: 0, duration: 0.7, ease: "power3.out" }}, {round(t_card + 0.2, 3)});'''
    scene_html(sid, body, js, css)


if __name__ == '__main__':
    for fn in (s01, s02, s03, s04, s05, s06, s07, s08, s09, s10, s11, s12, s13, s14, s15):
        fn()
    json.dump([{'id': s, 'start': a, 'end': b, 'duration': dur(s)} for s, a, b, _ in SCENES],
              open(os.path.join(ROOT, 'compositions', 'scenes.json'), 'w'), indent=1)
    print('wrote', len(SCENES), 'scenes')
