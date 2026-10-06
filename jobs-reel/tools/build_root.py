"""Write index.html (root composition) from compositions/scenes.json + the audio cue list below.

Keeps any data-automation / data-fx-* attributes already on an <audio> in index.html (carve output),
so re-running this after a carve does not lose the mix.
Run: python3 tools/build_root.py
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOTAL = 94.3
scenes = json.load(open(os.path.join(ROOT, 'compositions/scenes.json')))

# id, src, start, duration, volume, media_start
AUDIO = [
    ('narration', 'assets/audio/vo/narration.wav', 0.0, 94.26, 1.0, None),
    # Story bed: offset 1s so its swell lands on the return to Apple; it decays into the applause
    ('music-story', 'assets/audio/music/story.mp3', 1.0, 54.3, 0.55, None),
    # Pitch bed (88 BPM): enters after «چرا؟», then a bar-aligned jump (media 21.828 -> 40.919)
    # so its own final chord rings out under the last line
    ('music-pitch', 'assets/audio/music/pitch.mp3', 68.09, 22.08, 0.5, 0.0),
    ('music-pitch-end', 'assets/audio/music/pitch.mp3', 89.67, 4.63, 0.5, 40.669),
    # SFX
    ('sfx-pencil-1', 'assets/audio/sfx/pencil.mp3', 0.0, 1.3, 0.22, 0.2),
    ('sfx-paper-1', 'assets/audio/sfx/paper-loud.wav', 1.85, 1.0, 0.5, None),
    ('sfx-riser-1', 'assets/audio/sfx/riser.mp3', 7.9, 1.65, 0.45, None),
    ('sfx-boom', 'assets/audio/sfx/boom.mp3', 9.47, 3.0, 0.85, None),
    ('sfx-pencil-3', 'assets/audio/sfx/pencil.mp3', 8.75, 1.1, 0.2, 0.6),
    ('sfx-paper-4', 'assets/audio/sfx/paper-loud.wav', 11.4, 1.0, 0.45, None),
    ('sfx-door', 'assets/audio/sfx/door.mp3', 16.33, 2.5, 0.7, None),
    ('sfx-paper-6', 'assets/audio/sfx/paper-loud.wav', 18.35, 1.0, 0.45, None),
    ('sfx-pencil-6', 'assets/audio/sfx/pencil.mp3', 19.25, 1.4, 0.18, 0.4),
    ('sfx-riser-7', 'assets/audio/sfx/riser.mp3', 29.66, 1.65, 0.4, None),
    ('sfx-pencil-7', 'assets/audio/sfx/pencil.mp3', 28.9, 1.2, 0.18, 0.9),
    ('sfx-paper-8', 'assets/audio/sfx/paper-loud.wav', 33.2, 1.0, 0.45, None),
    ('sfx-pencil-9', 'assets/audio/sfx/pencil.mp3', 38.95, 1.3, 0.18, 0.3),
    ('sfx-whoosh-9', 'assets/audio/sfx/whoosh.mp3', 43.62, 1.2, 0.4, None),
    ('sfx-paper-10', 'assets/audio/sfx/paper-loud.wav', 46.1, 1.0, 0.45, None),
    ('sfx-applause', 'assets/audio/sfx/applause-stop.wav', 51.62, 3.68, 0.5, None),
    ('sfx-clock', 'assets/audio/sfx/clock-1s.wav', 59.125, 6.72, 0.55, None),
    ('sfx-sand', 'assets/audio/sfx/sand-loud.wav', 59.6, 5.0, 0.35, None),
    ('sfx-heart-1', 'assets/audio/sfx/heartbeat.mp3', 66.0, 1.5, 0.9, None),
    ('sfx-heart-2', 'assets/audio/sfx/heartbeat.mp3', 66.78, 1.5, 0.55, None),
    ('sfx-pencil-13', 'assets/audio/sfx/pencil.mp3', 66.5, 1.2, 0.16, 1.0),
    ('sfx-paper-14', 'assets/audio/sfx/paper-loud.wav', 73.05, 1.0, 0.45, None),
    ('sfx-keys', 'assets/audio/sfx/keyboard.mp3', 74.3, 3.0, 0.3, None),
    ('sfx-paper-15', 'assets/audio/sfx/paper-loud.wav', 78.45, 1.0, 0.45, None),
    ('sfx-bulb', 'assets/audio/sfx/bulb.mp3', 81.35, 2.5, 0.6, None),
    ('sfx-whoosh-15', 'assets/audio/sfx/whoosh.mp3', 83.15, 1.2, 0.3, None),
]


def keep_attrs(old_html, aid):
    m = re.search(r'<audio\b[^>]*\bid="' + re.escape(aid) + r'"[^>]*>', old_html, re.S)
    if not m:
        return ''
    return ''.join(f' {a}' for a in re.findall(r'(data-(?:automation|fx-[a-z-]+)=\'[^\']*\'|data-(?:automation|fx-[a-z-]+)="[^"]*")', m.group(0)))


def main():
    path = os.path.join(ROOT, 'index.html')
    old = open(path).read() if os.path.exists(path) else ''
    hosts = []
    hosts.append(f'''      <div id="paper" data-composition-id="paper" data-composition-src="compositions/paper.html" data-start="0" data-duration="{TOTAL}" data-track-index="0" data-track-kind="graphics" data-width="1080" data-height="1920"></div>''')
    for i, s in enumerate(scenes):
        hosts.append(f'''      <div id="{s['id']}" data-composition-id="{s['id']}" data-composition-src="compositions/{s['id']}.html" data-start="{s['start']}" data-duration="{s['duration']}" data-track-index="{1 + i % 2}" data-track-kind="graphics" data-width="1080" data-height="1920"></div>''')
    hosts.append(f'''      <div id="fx" data-composition-id="fx" data-composition-src="compositions/fx.html" data-start="0" data-duration="{TOTAL}" data-track-index="3" data-track-kind="graphics" data-width="1080" data-height="1920"></div>''')
    audio = []
    for n, (aid, src, start, d, vol, ms) in enumerate(AUDIO):
        track = 10 if aid == 'narration' else 19 if aid == 'music-pitch-end' else 11 if aid.startswith('music') else 12 + (n % 6)
        extra = f' data-media-start="{ms}"' if ms is not None else ''
        audio.append(f'      <audio id="{aid}" src="{src}" data-start="{start}" data-duration="{d}"{extra} data-track-index="{track}" data-volume="{vol}"{keep_attrs(old, aid)}></audio>')
    html = f'''<!doctype html>
<!-- Never put dir="rtl" on <html>: HyperFrames renders a black video. Direction lives on the text blocks. -->
<html lang="fa" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
      * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }}
      html,
      body {{
        margin: 0;
        width: 1080px;
        height: 1920px;
        overflow: hidden;
        background: #cfc4b2;
      }}
      #root {{
        position: relative;
        width: 100%;
        height: 100%;
        overflow: hidden;
        background: #cfc4b2;
      }}
      #root > div[data-composition-src] {{
        position: absolute;
        inset: 0;
      }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
{chr(10).join(hosts)}

{chr(10).join(audio)}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
'''
    open(path, 'w').write(html)
    print('index.html:', len(scenes), 'scenes,', len(AUDIO), 'audio clips')


if __name__ == '__main__':
    main()
