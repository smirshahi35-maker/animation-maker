# HANDOFF — re-rendering or changing trust-reel-en (English version) in a new session

English version of `../trust-reel` (Persian), 1080×1920, 30 fps, 48.65 s. Brief, English script and decisions:
`BRIEF.md`. Type rules + copy deck: `frame.md`. Scene plan, every word time, every SFX time: `TIMING.md`.
Final film: `../deliverables/trust-reel-en.mp4`. The user writes Persian; reply in Persian.

## Before you start

1. **Two files are not in git** (the repo is public):
   - `assets/fonts/Superline-Italic.ttf` — the user's licensed font. Ask the user to attach it again.
   - `../trust-reel/assets/portrait/` (the user's photo, shared through the `assets/portrait` symlink) — see
     `../trust-reel/HANDOFF.md`.
2. Shared assets are symlinks into `../trust-reel/assets/` (ai, video, vendor, portrait, audio/music, audio/sfx);
   `node_modules` is a symlink to `../trust-reel/node_modules` (run `npm install` in `../trust-reel/` first).
3. Render browser: `export HYPERFRAMES_BROWSER_PATH=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell`

## Superline gotchas (all handled in the compositions)

- Straight `'` and `"` are blank glyphs: use ’ “ ”. The em dash renders as a short hyphen.
- Default ligatures underline IS / IN / IT / AN / THE: `font-variant-ligatures: none; font-feature-settings: "liga" 0, "clig" 0`.
- One weight, already italic: `font-synthesis: none`, never bold/italic it. No ♪ glyph (falls back to Inter).

## Narration

`assets/audio/vo/narration.wav` is built by `python3 tools/make_vo.py` from `takes/en-take1.mp3` (ElevenLabs
eleven_v4, voice Liam `TX3LPaxmHKxFdv7VOQHJ`, flow `AhMefwlyje0ZZkipn80R`; the TTS text spells the name
"Shaheen"). Word times are Scribe on the uploaded take (`en-take1.words.json`). The script only lengthens pauses
(`EXTRA`), lifts swallowed words and normalises to the Persian narration's loudness (-18.3 LUFS: the carve's
level-match duck bottoms out at -16.8 dB, so a quieter voice leaves the music too loud). If the narration
changes, every `data-t`, the scene starts in `index.html`, `tools/sfx_en.json` and `TIMING.md` must follow.

## Rebuild and render

```bash
python3 tools/make_vo.py             # only if the narration changes
python3 tools/build_s4.py            # after editing tools/s4.src.html
python3 tools/build_root.py          # audio block of index.html (narration, beds, 47 SFX from tools/sfx_en.json)
node ~/.claude/skills/hyperframes-audio/scripts/carve.mjs --comp index.html --bed music-story --voice narration --strength 0.7
node ~/.claude/skills/hyperframes-audio/scripts/carve.mjs --comp index.html --bed music-tip --voice narration --strength 0.7
npx --yes hyperframes@0.8.137 check   # must pass (the 4 lint warnings come from the 220 generated wall tiles)
npx --yes hyperframes@0.8.137 render -q high -f 30 -o renders/trust-reel-en.mp4
python3 tools/master.py               # -14 LUFS, H.264 CRF 19 ≤7 Mbps -> ../deliverables/trust-reel-en.mp4
```

Wait for a render by watching its log for "rendered in", not with `pgrep -f "...render"` (that matches the wait
loop's own command line and never exits).

Audio checks (from this folder): `python3 tools/mixcheck.py renders/trust-reel-en.mp4 .` and `python3 tools/sfxmask.py`.
mixcheck's bed-under-speech includes every SFX that overlaps a word; the English narration is denser than the
Persian, so judge the music margin on speech windows without SFX (14-17 dB in the final mix).
