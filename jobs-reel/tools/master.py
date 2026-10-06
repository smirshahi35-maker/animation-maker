"""Delivery master: renders/jobs-reel.mp4 -> ../deliverables/jobs-reel.mp4.

Audio: two-pass loudnorm to -14 LUFS / -1.5 dBTP (AAC 192k). Video: the high-quality render is
~65 Mbps (too big for git and for Instagram uploads), so it is re-encoded to H.264 High, CRF 19
capped at 7 Mbps — visually transparent on the pencil texture, ~80 MB for the 94 s film.
Run: python3 tools/master.py [src] [dst]
"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'renders', 'jobs-reel.mp4')
dst = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, '..', 'deliverables', 'jobs-reel.mp4')
TARGET = 'I=-14:TP=-1.5:LRA=11'

probe = subprocess.run(['ffmpeg', '-hide_banner', '-i', src, '-af', f'loudnorm={TARGET}:print_format=json', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
m = json.loads(re.findall(r'\{[^{}]*"input_i"[^{}]*\}', probe)[-1])
print('measured', {k: m[k] for k in ('input_i', 'input_tp', 'input_lra', 'input_thresh', 'target_offset')})

af = (f'loudnorm={TARGET}:measured_I={m["input_i"]}:measured_TP={m["input_tp"]}:measured_LRA={m["input_lra"]}'
      f':measured_thresh={m["input_thresh"]}:offset={m["target_offset"]}:linear=true:print_format=summary')
os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
VIDEO = ['-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-maxrate', '7M', '-bufsize', '14M',
         '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-r', '30', '-tag:v', 'avc1']
subprocess.run(['ffmpeg', '-hide_banner', '-y', '-i', src, *VIDEO, '-af', af, '-ar', '48000',
                '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', dst], check=True)
print('wrote', os.path.abspath(dst))
