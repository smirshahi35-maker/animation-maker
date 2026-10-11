#!/usr/bin/env python3
"""Tighten the narration take: shorten long pauses, speed up slightly, write word timings.

Input : assets/audio/vo/takes/take2.mp3 + take2.words.json (ElevenLabs Scribe, real audio), with two
        re-takes spliced in where take2's sentence ends were swallowed by the voice:
        - the hook up to «بریز دور!» from takes/hook/hook2.mp3 (take2 whispers «دور»),
        - the CTA from «کلمه‌ی» from takes/cta/cta1.mp3 (take2 cuts off «کن»).
        Splices sit in the silent pause between sentences. Every word that is still far softer than
        the take's median gets clip gain before the cuts.
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
TAKES = ROOT / "assets/audio/vo/takes"
TAKE = TAKES / "take2.mp3"
WORDS = TAKES / "take2.words.json"
HOOK, HOOK_WORDS = TAKES / "hook/hook2.mp3", TAKES / "hook/hook2.words.json"
CTA, CTA_WORDS = TAKES / "cta/cta1.mp3", TAKES / "cta/cta1.words.json"
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
    if nxt["text"] in SECTION_STARTS and t[-1:] in ".?؟!":
        return SECTION
    if t.endswith((".", "?", "؟", ":", "!")):
        return SENTENCE
    if t.endswith(("،", ",")):
        return COMMA
    return PLAIN


def load_words(path):
    return [w for w in json.load(open(path))["words"] if w.get("type") == "word"]


def pause_mid(audio, t0, t1):
    """Middle of the longest silent run between t0 and t1 (seconds) - where a splice is inaudible."""
    db = rms_db(audio)
    lo, hi = int(t0 * SR) // WIN, int(t1 * SR) // WIN
    best, start = (lo, lo), None
    for i in range(lo, hi + 1):
        s = i < hi and db[i] < SILENT_DB
        if s and start is None:
            start = i
        elif not s and start is not None:
            if i - start > best[1] - best[0]:
                best = (start, i)
            start = None
    if best[1] == best[0]:
        return (t0 + t1) / 2
    return (best[0] + best[1]) / 2 * WIN / SR


def word_peak_db(audio, w):
    seg = audio[int(w["start"] * SR):int(w["end"] * SR)]
    n = int(0.05 * SR)
    if len(seg) <= n:
        return 20 * np.log10(np.sqrt(np.mean(seg ** 2) + 1e-12))
    return max(20 * np.log10(np.sqrt(np.mean(seg[i:i + n] ** 2) + 1e-12)) for i in range(0, len(seg) - n, SR // 100))


def piece(audio, words, t0, t1, ref_db=None):
    """audio[t0:t1] (levelled to ref_db, the median word peak, if given) and its words, re-timed to 0."""
    ws = [dict(w) for w in words if w["start"] >= t0 and w["end"] <= t1 + 0.3]
    gain = 0.0 if ref_db is None else ref_db - float(np.median([word_peak_db(audio, w) for w in ws]))
    seg = audio[int(t0 * SR):int(t1 * SR)] * np.float32(10 ** (np.clip(gain, -6, 6) / 20))
    print(f"  piece {t0:.2f}-{t1:.2f}s gain {gain:+.1f} dB")
    for w in ws:
        w["start"], w["end"] = round(w["start"] - t0, 3), round(min(w["end"], t1) - t0, 3)
    return seg, ws


def source():
    """take2 with the hook and the CTA re-takes spliced in; returns (audio, words)."""
    main_a, main_w = decode(TAKE), load_words(WORDS)
    hook_a, hook_w = decode(HOOK), load_words(HOOK_WORDS)
    cta_a, cta_w = decode(CTA), load_words(CTA_WORDS)
    ref = float(np.median([word_peak_db(main_a, w) for w in main_w]))

    def find(ws, text, nth=0):
        return [w for w in ws if w["text"].rstrip(".!،؟?") == text][nth]

    # hook: start .. pause after «دور!»
    h_end = pause_mid(hook_a, find(hook_w, "دور")["end"], find(hook_w, "ویدیوت")["start"])
    # take2: pause after «دور.» .. pause before «کلمه‌ی»
    m_start = pause_mid(main_a, find(main_w, "دور")["end"], find(main_w, "ویدیوت")["start"])
    m_end = pause_mid(main_a, find(main_w, "نمیاره")["end"], find(main_w, "کلمه‌ی")["start"])
    # CTA: pause before «کلمه‌ی» .. just before the throwaway «منتظرتم.»
    c_start = pause_mid(cta_a, find(cta_w, "نمیاره")["end"], find(cta_w, "کلمه‌ی")["start"])
    c_end = find(cta_w, "منتظرتم")["start"] - 0.1

    parts = [piece(hook_a, hook_w, 0.0, h_end, ref),
             piece(main_a, main_w, m_start, m_end),
             piece(cta_a, cta_w, c_start, c_end, ref)]
    out, words, t = [], [], 0.0
    for seg, ws in parts:
        out.append(seg)
        words += [dict(w, start=round(w["start"] + t, 3), end=round(w["end"] + t, 3)) for w in ws
                  if not w["text"].startswith("منتظرتم")]
        t += len(seg) / SR
    out.append(np.zeros(int(TAIL * SR), dtype=np.float32))  # room for the final tail
    return np.concatenate(out), words


def level_words(audio, words):
    """Clip gain on words far softer than the take's median (sentence ends the voice swallows)."""
    peaks = [word_peak_db(audio, w) for w in words]
    med = float(np.median(peaks))
    ramp = int(0.015 * SR)
    for w, p in zip(words, peaks):
        if p >= med - 8:
            continue
        g = 10 ** (min(med - 4 - p, 10) / 20)
        a, b = int((w["start"] - 0.02) * SR), int((w["end"] + 0.04) * SR)
        env = np.full(b - a, g, dtype=np.float32)
        env[:ramp] = np.linspace(1, g, ramp)
        env[-ramp:] = np.linspace(g, 1, ramp)
        audio[a:b] *= env
        print(f"  clip gain {20 * np.log10(g):+.1f} dB on {w['text']} ({p:.1f} dB, median {med:.1f})")
    return audio


def main():
    audio, words = source()
    audio = level_words(audio, words)
    db = rms_db(audio)

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
    json.dump({"source": f"{TAKE.name} + {HOOK.name} (hook) + {CTA.name} (CTA)", "tempo": TEMPO, "duration": round(dur, 3), "cuts": len(cuts),
               "words": final}, open(OUT_JSON, "w"), ensure_ascii=False, indent=1)
    removed = sum(b - a for a, b in cuts) / SR
    print(f"cuts={len(cuts)} removed={removed:.2f}s tempo={TEMPO} duration={dur:.2f}s")


if __name__ == "__main__":
    main()
