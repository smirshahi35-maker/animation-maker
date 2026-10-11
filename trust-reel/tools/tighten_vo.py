#!/usr/bin/env python3
"""Tighten the narration take: shorten long pauses, speed up slightly, write word timings.

Input : assets/audio/vo/takes/take2.mp3 + take2.words.json (ElevenLabs Scribe, real audio)
Output: assets/audio/vo/narration.wav (48 kHz mono) + narration.words.json (final timeline)

Pauses are measured on the audio itself (10 ms RMS windows), not only on Scribe's word edges,
so a cut never lands on a trailing consonant. Each pause keeps a target length that depends on
the punctuation that ends the word before it.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
TAKE = ROOT / "assets/audio/vo/takes/take2.mp3"
WORDS = ROOT / "assets/audio/vo/takes/take2.words.json"
OUT_WAV = ROOT / "assets/audio/vo/narration.wav"
OUT_JSON = ROOT / "assets/audio/vo/narration.words.json"

SR = 48000
TEMPO = float(sys.argv[1]) if len(sys.argv) > 1 else 1.05
WIN = int(0.010 * SR)
SILENT_DB = -42.0
XFADE = int(0.012 * SR)
LEAD_IN = 0.06
TAIL = 0.55

# Pause targets (seconds, before tempo change).
SENTENCE, COMMA, PLAIN = 0.40, 0.24, 0.22
SECTION = 0.50  # before a new section of the script
SECTION_STARTS = {"ویدیوت", "یکی", "نکته", "من"}


def decode(path):
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
        check=True, capture_output=True,
    ).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def rms_db(x):
    n = len(x) // WIN
    frames = x[: n * WIN].reshape(n, WIN)
    rms = np.sqrt(np.mean(frames ** 2, axis=1) + 1e-12)
    return 20 * np.log10(rms)


def target_for(word, nxt):
    t = word["text"]
    if nxt["text"] in SECTION_STARTS and t[-1:] in ".?؟":
        return SECTION
    if t.endswith((".", "?", "؟", ":")):
        return SENTENCE
    if t.endswith(("،", ",")):
        return COMMA
    return PLAIN


def main():
    audio = decode(TAKE)
    db = rms_db(audio)
    words = [w for w in json.load(open(WORDS))["words"] if w.get("type") == "word"]

    # Find each inter-word pause on the audio and decide how much to remove.
    cuts = []  # (start_sample, end_sample) to delete
    for w, nxt in zip(words, words[1:]):
        lo = max(0, int((w["end"] - 0.06) * SR) // WIN)
        hi = min(len(db), int((nxt["start"] + 0.06) * SR) // WIN)
        if hi - lo < 3:
            continue
        silent = db[lo:hi] < SILENT_DB
        best, run_start = (0, 0), None
        for i, s in enumerate(list(silent) + [False]):
            if s and run_start is None:
                run_start = i
            elif not s and run_start is not None:
                if i - run_start > best[1] - best[0]:
                    best = (run_start, i)
                run_start = None
        run_len = (best[1] - best[0]) * WIN / SR
        target = target_for(w, nxt)
        if run_len <= target + 0.04:
            continue
        remove = run_len - target
        center = (lo + (best[0] + best[1]) / 2) * WIN
        a = int(center - remove * SR / 2)
        b = int(center + remove * SR / 2)
        cuts.append((a, b))

    # Leading silence before the first word and the tail after the last word.
    first = int(max(0.0, words[0]["start"] - LEAD_IN) * SR)
    last = min(len(audio), int((words[-1]["end"] + TAIL) * SR))

    # Build the tightened audio with short crossfades at each cut.
    pieces, keep_from = [], first
    for a, b in cuts:
        pieces.append(audio[keep_from:a])
        keep_from = b
    pieces.append(audio[keep_from:last])
    out = pieces[0]
    for p in pieces[1:]:
        fade = np.linspace(0, 1, XFADE, dtype=np.float32)
        head, tail = out[:-XFADE], out[-XFADE:]
        out = np.concatenate([head, tail * (1 - fade) + p[:XFADE] * fade, p[XFADE:]])
    fade_out = int(0.18 * SR)
    out[-fade_out:] *= np.linspace(1, 0, fade_out, dtype=np.float32)

    # Map original word times to the tightened timeline, then to the tempo-changed one.
    def remap(t):
        # Each cut removes (b - a) samples plus the XFADE overlap of the crossfade.
        s = t * SR - first
        for a, b in cuts:
            if t * SR >= b:
                s -= b - a + XFADE
            elif t * SR > a:
                s -= t * SR - a
        return max(0.0, s / SR) / TEMPO

    tmp = OUT_WAV.with_suffix(".tight.wav")
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
         "-c:a", "pcm_s16le", str(tmp)],
        input=out.astype(np.float32).tobytes(), check=True,
    )
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-af",
         f"rubberband=tempo={TEMPO}:transients=smooth:formant=preserved",
         "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", str(OUT_WAV)],
        check=True,
    )
    tmp.unlink()

    final = [{"text": w["text"], "start": round(remap(w["start"]), 3), "end": round(remap(w["end"]), 3)}
             for w in words]
    dur = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(OUT_WAV)],
        capture_output=True, text=True, check=True).stdout)
    json.dump({"source": TAKE.name, "tempo": TEMPO, "duration": round(dur, 3), "cuts": len(cuts),
               "words": final}, open(OUT_JSON, "w"), ensure_ascii=False, indent=1)
    removed = sum(b - a for a, b in cuts) / SR
    print(f"cuts={len(cuts)} removed={removed:.2f}s tempo={TEMPO} duration={dur:.2f}s")


if __name__ == "__main__":
    main()
