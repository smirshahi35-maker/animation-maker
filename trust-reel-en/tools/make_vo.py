#!/usr/bin/env python3
"""Build the English narration from one ElevenLabs take: lengthen the pauses the camera moves need,
lift words the voice swallows, limit, and write word timings.

Input : assets/audio/vo/takes/en-take1.mp3 (eleven_v4, voice Liam TX3LPaxmHKxFdv7VOQHJ)
        + en-take1.words.json (ElevenLabs Scribe on the uploaded take, real audio timings)
Output: assets/audio/vo/narration.wav (48 kHz mono) + narration.words.json (times relative to the file;
        the root composition starts the narration at global 0.2 s)

Pauses are only ever lengthened, never cut: silence is inserted at the quietest 10 ms window between
the two words (measured on the audio, not on Scribe's word edges), so no breath or consonant is split.
"""
import json
import subprocess
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
TAKES = ROOT / "assets/audio/vo/takes"
TAKE, WORDS = TAKES / "en-take1.mp3", TAKES / "en-take1.words.json"
OUT_WAV = ROOT / "assets/audio/vo/narration.wav"
OUT_JSON = ROOT / "assets/audio/vo/narration.words.json"

SR = 48000
WIN = int(0.010 * SR)
TAIL = 0.6

# Extra silence (s) after the word with this index: room for the camera moves between beats.
EXTRA = {
    18: 0.10,   # "trash."      dive into the bin
    54: 0.35,   # "trust."      trust ring, fly through it
    89: 0.95,   # "customers."  bento holds, whip pan
    97: 0.30,   # "up."         pull-out to the 500-project wall
    115: 0.25,  # "follow."     follow tap, composer rises
    127: 0.30,  # "customers,"  headline clears before "comment the word"
    130: 0.10,  # "word"        the typed word lands with "page"
}


def decode(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def rms_db(x):
    n = len(x) // WIN
    return 20 * np.log10(np.sqrt(np.mean(x[: n * WIN].reshape(n, WIN) ** 2, axis=1) + 1e-12))


def word_peak_db(db, w):
    a, b = int(w["start"] * 100), max(int(w["start"] * 100) + 1, int(w["end"] * 100))
    return float(db[a:b].max())


def level_words(audio, words):
    """Words more than 8 dB under the median word peak get clip gain (15 ms ramps)."""
    db = rms_db(audio)
    peaks = np.array([word_peak_db(db, w) for w in words])
    med = float(np.median(peaks))
    gain = np.ones_like(audio)
    ramp = int(0.015 * SR)
    for w, p in zip(words, peaks):
        if p < med - 8:
            g = 10 ** (min(med - 4 - p, 10) / 20)
            a, b = int(w["start"] * SR), int(w["end"] * SR)
            seg = np.full(b - a, g, dtype=np.float32)
            seg[:ramp] = np.linspace(1, g, min(ramp, len(seg)))[: len(seg[:ramp])]
            seg[-ramp:] = np.linspace(g, 1, min(ramp, len(seg)))[-len(seg[-ramp:]):]
            gain[a:b] = np.minimum(np.maximum(gain[a:b], seg), 10)
            print(f"  lift {w['text']!r} {20 * np.log10(g):+.1f} dB")
    return audio * gain


def main():
    audio = decode(TAKE)
    words = json.load(open(WORDS))["words"]
    audio = level_words(audio, words)
    db = rms_db(audio)

    out, new_words, src_pos, shift = [], [], 0, 0.0
    cuts = []
    for i, extra in sorted(EXTRA.items()):
        a, b = words[i]["end"], words[i + 1]["start"]
        lo, hi = int(a * 100) + 1, max(int(a * 100) + 2, int(b * 100) - 1)
        k = lo + int(np.argmin(db[lo:hi]))  # quietest 10 ms window inside the pause
        cuts.append((i, k * WIN + WIN // 2, extra))
    for i, pos, extra in cuts:
        out.append(audio[src_pos:pos])
        out.append(np.zeros(int(extra * SR), dtype=np.float32))
        src_pos = pos
    out.append(audio[src_pos:])
    out.append(np.zeros(int(TAIL * SR), dtype=np.float32))
    result = np.concatenate(out)

    for j, w in enumerate(words):
        s = sum(e for i, _, e in cuts if j > i)
        new_words.append({"text": w["text"], "start": round(w["start"] + s, 3), "end": round(w["end"] + s, 3)})

    tmp = OUT_WAV.with_suffix(".raw.f32")
    result.astype(np.float32).tofile(tmp)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", str(tmp),
                    "-af", "alimiter=limit=0.89:attack=1:release=40:level=false", "-c:a", "pcm_s16le", str(OUT_WAV)],
                   check=True)
    tmp.unlink()
    json.dump({"source": TAKE.name, "words": new_words}, open(OUT_JSON, "w"), ensure_ascii=False, indent=1)
    print(f"narration.wav {len(result) / SR:.2f} s, {len(new_words)} words")


if __name__ == "__main__":
    main()
