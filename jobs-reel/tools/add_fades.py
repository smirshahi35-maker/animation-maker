"""Add (or replace) the volume fade lane in an <audio>'s data-automation, keeping carve lanes.
carve.mjs rewrites data-automation, so run this after every carve.  Times are clip-relative."""
import html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FADES = {
    'music-story': [(0, 1), (52.2, 1), (54.3, 0)],
    'music-pitch': [(0, 0), (0.6, 1), (21.83, 1), (22.08, 0)],
    'music-pitch-end': [(0, 0), (0.25, 1), (4.05, 1), (4.63, 0)],
}

path = os.path.join(ROOT, 'index.html')
s = open(path).read()
for aid, pts in FADES.items():
    m = re.search(r'<audio\b[^>]*\bid="' + aid + r'"[^>]*>', s)
    tag = m.group(0)
    am = re.search(r'data-automation="([^"]*)"', tag)
    auto = json.loads(html.unescape(am.group(1))) if am else {'version': 1, 'lanes': []}
    auto['lanes'] = [l for l in auto['lanes'] if l['target'] != 'volume']
    auto['lanes'].append({'target': 'volume', 'points': [{'t': t, 'v': v} for t, v in pts]})
    attr = 'data-automation="' + html.escape(json.dumps(auto, separators=(',', ':')), quote=True) + '"'
    new = tag.replace(am.group(0), attr) if am else tag[:-1] + ' ' + attr + '>'
    s = s.replace(tag, new)
    print(aid, 'lanes:', [l['target'] for l in auto['lanes']][-3:])
open(path, 'w').write(s)
