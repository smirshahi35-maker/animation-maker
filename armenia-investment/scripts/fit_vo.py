# Tighten long pauses in the VO take, then time-stretch it (pitch kept) so it fits the target length.
# Writes audio/vo/narration.wav and audio/vo/narration.words.json (word times in the new audio).
import json, subprocess, sys
src, words_json, target = sys.argv[1], sys.argv[2], float(sys.argv[3])
words = [w for w in json.load(open(words_json))["words"] if w["type"] == "word"]
CAP, END_CAP, HOOK_CAP, PAD = 0.16, 0.30, 0.55, 0.06   # max pause kept mid-sentence / after a sentence / after the hook
words_src = sys.argv[4] if len(sys.argv) > 4 else None   # optional: transcript of a different file than the audio
total = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src]))

# keep-segments: speech runs with gaps capped
keep, removed = [], []                        # removed: (orig_time, seconds_removed_so_far)
start = max(0.0, words[0]["start"] - PAD)
cut = 0.0
for a, b in zip(words, words[1:]):
    gap = b["start"] - a["end"]
    cap = HOOK_CAP if a["text"].startswith("نکن") else (END_CAP if a["text"].endswith((".", "!", "؟")) else CAP)
    if gap > cap:
        end = a["end"] + cap / 2
        keep.append((start, end))
        start = b["start"] - cap / 2
        cut += gap - cap
        removed.append((b["start"], cut))
keep.append((start, min(total, words[-1]["end"] + 0.25)))
cut_total = words[0]["start"] - PAD  # leading silence is dropped too
length = sum(e - s for s, e in keep)
tempo = length / target
print(f"kept {length:.2f}s of {total:.2f}s, tempo {tempo:.3f}")

parts = "".join(f"[0:a]atrim={s:.3f}:{e:.3f},asetpts=PTS-STARTPTS[s{i}];" for i, (s, e) in enumerate(keep))
graph = parts + "".join(f"[s{i}]" for i in range(len(keep))) + f"concat=n={len(keep)}:v=0:a=1,rubberband=tempo={tempo:.5f}:pitchq=quality:formant=preserved[out]"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", graph, "-map", "[out]", "-ar", "48000", "audio/vo/narration.wav"], check=True)

def remap(t):
    # position of original time t in the tightened, stretched audio
    acc = 0.0
    for s, e in keep:
        if t < s: return acc / tempo
        if t <= e: return (acc + t - s) / tempo
        acc += e - s
    return acc / tempo
out = [{"text": w["text"], "start": round(remap(w["start"]), 3), "end": round(remap(w["end"]), 3)} for w in words]
json.dump({"tempo": tempo, "words": out}, open("audio/vo/narration.words.json", "w"), ensure_ascii=False, indent=1)
print("last word ends at", out[-1]["end"])
