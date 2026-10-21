# Mix narration, ducked music bed and SFX into audio/mix.wav (50 s, -14 LUFS for Instagram).
import json, subprocess
VO_OFF, DUR = 0.30, 50.0
w = json.load(open("audio/vo/narration.canonical.json"))        # [start, end] per script token (scripts/canon_words.py)
W = lambda i: w[i][0] + VO_OFF
scene_t = [W(i) - 0.12 for i in [13, 32, 46, 58, 73, 83, 102, 113]]
stamps = [W(4) - 0.06 + 0.12, W(18) - 0.04 + 0.12, W(56) - 0.04 + 0.12]
whooshes = [t - 0.25 for t in scene_t]

inputs = ["-i", "audio/vo/narration.wav", "-i", "audio/music/takes/m3.mp3"]
fx = []
for t in stamps:
    inputs += ["-i", "audio/sfx/takes/stamp1.mp3"]; fx.append(("stamp", t))
for t in whooshes:
    inputs += ["-i", "audio/sfx/takes/whoosh1.mp3"]; fx.append(("whoosh", t))

g = [f"[0:a]aresample=48000,highpass=f=80,acompressor=threshold=0.12:ratio=3:attack=6:release=90:makeup=1.4,"
     f"adelay={int(VO_OFF*1000)}:all=1,apad=whole_dur={DUR},asplit=2[vo][vosc]",
     f"[1:a]aresample=48000,atrim=0:{DUR},afade=t=in:d=0.4,afade=t=out:st={DUR-1.6}:d=1.6,volume=0.42[mus]",
     "[mus][vosc]sidechaincompress=threshold=0.035:ratio=5:attack=25:release=350:makeup=1[bed]"]
labels = []
for k, (kind, t) in enumerate(fx):
    i = k + 2
    if kind == "stamp":
        g.append(f"[{i}:a]aresample=48000,atrim=0:0.55,afade=t=out:st=0.35:d=0.2,volume=0.9,adelay={int(t*1000)}:all=1[f{k}]")
    else:
        g.append(f"[{i}:a]aresample=48000,atrim=0:0.6,afade=t=out:st=0.4:d=0.2,volume=0.55,adelay={int(max(0,t)*1000)}:all=1[f{k}]")
    labels.append(f"[f{k}]")
g.append(f"[vo][bed]{''.join(labels)}amix=inputs={2+len(labels)}:normalize=0:duration=first,atrim=0:{DUR},"
         f"loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[out]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(g), "-map", "[out]", "-ac", "2", "audio/mix.wav"], check=True)
print("stamps", [round(t, 2) for t in stamps]); print("whooshes", [round(t, 2) for t in whooshes])
