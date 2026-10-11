# HANDOFF — re-rendering or changing trust-reel in a new session

Persian Instagram Reel for Shahin (editor & motion designer), 1080×1920, 30 fps, 50.04 s.
Script (verbatim from the user) and requirements: `BRIEF.md`. Design spec: `frame.md`.
Storyboard page: https://claude.ai/artifact/VbYPDM9r3bcWgxFGrcQgkx. Final film: `../deliverables/trust-reel.mp4`.
The user writes Persian; reply in Persian.

## Before you start

1. **The portrait is not in git** (personal photo; `assets/portrait/` is ignored). s4's intro card needs
   `assets/portrait/shahin-cutout.png` (birefnet cut-out of the photo the user sent). Ask the user to attach
   the photo again, cut it out (ElevenLabs `creative_edit_image`, model `birefnet-v2-bg-removal`) and save it there.
2. `npm install` in `trust-reel/` (installs `@hyperframes/core`, needed by `carve.mjs`).
3. Render browser: `export HYPERFRAMES_BROWSER_PATH=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell`

## Structure

| scene | file | global start | what |
|---|---|---|---|
| s1 | `compositions/s1.html` | 0 (7.04 s) | hook: cards crumple, tilt down with the falling paper, dive into the bin opening |
| s2 | `compositions/s2.html` | 6.64 (13.4 s) | phone out of the bin's black: 80,000 views, empty DMs, «۰ سفارش», Veo viewer card, trust ring fly-through |
| s3 | `compositions/s3.html` | 19.79 (12.95 s) | «نکته اینه:», split screen ترند = ویو / اعتماد = فروش, crane to the bento (BTS, latte, customer), whip pan |
| s4 | `compositions/s4.html` ← **generated** from `tools/s4.src.html` by `python3 tools/build_s4.py` | 32.39 (17.65 s) | DMs fill up, pull-out to the 500-project wall, intro card, follow, comment «پیج» |

Local time inside a scene = global − its start. On-screen words carry `data-t` (local) on the spoken word
(narration starts at global 0.2; `assets/audio/vo/narration.words.json` times are file-relative).

## Narration

`assets/audio/vo/narration.wav` is built by `python3 tools/tighten_vo.py` from three ElevenLabs takes
(eleven_v3, voice Shahram `rNb3hdSf0n4ROIbYC8Bl`, language `fa`; flow `AhMefwlyje0ZZkipn80R`):
`takes/take2.mp3` (main), `takes/hook/hook2.mp3` (hook up to «بریز دور!»; take2 whispered «دور»),
`takes/cta/cta1.mp3` (CTA from «کلمه‌ی»; take2 cut off «کن»). The script splices them in sentence pauses,
clip-gains words the voice swallows, tightens pauses and speeds up ×1.05. If the narration changes, every
`data-t` and the SFX/music times in `tools/build_root.py` must follow.

## Rebuild and render

```bash
python3 tools/tighten_vo.py          # only if the narration changes
python3 tools/build_s4.py            # after editing tools/s4.src.html
python3 tools/build_root.py          # audio block of index.html (narration, beds, 47 SFX)
node ~/.claude/skills/hyperframes-audio/scripts/carve.mjs --comp index.html --bed music-story --voice narration --strength 0.7
node ~/.claude/skills/hyperframes-audio/scripts/carve.mjs --comp index.html --bed music-tip --voice narration --strength 0.7
npx --yes hyperframes@0.8.137 check   # must pass
npx --yes hyperframes@0.8.137 render -q high -f 30 -o renders/trust-reel.mp4
python3 tools/master.py               # -14 LUFS / -1.5 dBTP, H.264 CRF 19 ≤7 Mbps -> ../deliverables/trust-reel.mp4
```

`build_root.py` must run before the carve (carve keeps each bed's volume lane and appends its own lanes).
The carve's level-match lane already sets each bed against the voice from the raw file, so the volume lanes
only shape the beds (dips, fades, story +3 dB); `data-volume` stays 1.

Audio checks after a render (run from `trust-reel/`):
`python3 tools/mixcheck.py renders/trust-reel.mp4 .` (music should sit ~15-20 dB under the voice) and
`python3 tools/sfxmask.py` (each SFX against the narration words it lands on, speech band).

## Images and video

GPT Image 2.5 picks are in `assets/ai/` (web-sized copies in `assets/ai/web/`, made by `tools/prep_images.py`;
the generation sources in `assets/ai/src/` are not in git). Veo 3.1 Lite clips: `assets/video/src/`.

## Deliver

Commit `deliverables/trust-reel.mp4`, push, and give the user
`https://github.com/smirshahi35-maker/animation-maker/raw/claude/instagram-reels-motion-graphic-s1p7hu/deliverables/trust-reel.mp4`.
