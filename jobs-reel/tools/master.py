"""Two-pass loudnorm master: renders/jobs-reel.mp4 -> ../deliverables/jobs-reel.mp4 (-14 LUFS, -1.5 dBTP).

The video stream is copied untouched; only the audio is re-encoded (AAC 192k).
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
subprocess.run(['ffmpeg', '-hide_banner', '-y', '-i', src, '-c:v', 'copy', '-af', af, '-ar', '48000',
                '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', dst], check=True)
print('wrote', os.path.abspath(dst))
