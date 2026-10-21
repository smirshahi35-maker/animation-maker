# Armenia investment reel — how to rebuild

50 s, 1080×1920, 30 fps. Script approved by the client (see the scenario doc). Style follows the client's reference:
real palm-leaf shadow, cut-out apricots in the corners, real footage inside a tilted white "sticker", camera viewfinder
UI, pixel-mosaic transitions. Colour theme follows the client's reel covers and logo: dark green gradient, gold
headlines, white text (the first cut used cream paper with pink/orange; changed on the client's request). Fonts: Abar Mid Bold (headlines) and Abar Low Regular (secondary text).

## Inputs that are not in git

- `fonts/AbarMid-Bold.ttf`, `fonts/AbarLow-Regular.ttf` — licensed (FontIran); ask the user for them.
- `footage/` — Pexels clips, listed with ids in `FOOTAGE.md`; `scripts/pexels_get.sh <id> <name>` downloads one.
- `build/` — generated (frames, palm matte, grain).
- `assets/logo.png` — the client's logo (IRAM CO.) with the background removed by
  `scripts/logo_cutout.py assets/src/logo_original.jpg assets/logo.png`; kept out of git. Shown top-right next to
  the `IRAMCO.ORG` pill for the whole video.

## Steps

```bash
python3 -I scripts/prep_assets.py $PWD                 # apricot cut-outs (styleframes/assets)
python3 -I scripts/prep_frames.py $PWD                 # footage → 30 fps sticker frames, palm shadow matte, grain
python3 -I scripts/fit_vo.py audio/vo/takes/take1.mp3 audio/vo/takes/take1.words.json 48.9
python3 -c "import json;d=json.load(open('audio/vo/narration.words.json'));open('comp/vo_words.js','w').write('window.VO_WORDS = '+json.dumps([[w['start'],w['end']] for w in d['words']])+';\n')"
python3 -I scripts/mix_audio.py                        # → audio/mix.wav (-14 LUFS)
scripts/render_all.sh                                  # 3 parallel parts (~7 min) + mux → renders/armenia-investment-reel.mp4
```

Check stills at any time: `node scripts/render.js stills <outdir> 2.5 11.9 27.9`.

## Audio

- Voice: Shahram (ElevenLabs v3), take 1 of 4. Read was 60.5 s; `fit_vo.py` caps pauses at 0.22 s (hook pause 0.55 s)
  and stretches with rubberband (pitch and formants kept, tempo ≈1.2) to 48.9 s. Word times come from Scribe and are
  remapped into `audio/vo/narration.words.json`; every on-screen cue and caption keys off those times.
- Music: ElevenLabs music take 3 (`audio/music/takes/m3.mp3`), instrumental (checked with Scribe: no words),
  ducked under the voice with a sidechain compressor.
- SFX: rubber stamp (`stamp1`, first hit only) on the three stamps; paper whoosh before each scene change.

## Timeline

Scene starts are tied to the first word of each script line (`FIRST` in `comp/index.html`):
hook → truth 1 land/cadastre → truth 2 banks → truth 3 residency (10 Aban 1405) → property 5–8% →
agriculture → production / Meghri FEZ map → tourism 180,000 → "Armenia is an opportunity" + checklist + CTA.

## Reel cover

Same look as the client's other reel covers: dark green gradient, the IRAM CO. logo, a white Abar headline
(«تو ارمنستان / سرمایه‌گذاری نکن!») and a waving Armenian flag drawn by `scripts/make_flag.py`.

```bash
python3 -I scripts/make_flag.py cover/flag.png
NODE_PATH=/opt/node-tools/node_modules node scripts/render_cover.js   # cover-1080x1920.png + cover-grid-1080x1440.png
```

The 1080×1920 file is the cover to upload; the 1080×1440 file is the centre crop the profile grid shows.
Outputs: `deliverables/armenia-investment-cover.png`, `deliverables/armenia-investment-cover-grid.png`.

## Ending (changed after the first cut)

The last line is now «ارمنستان فرصته، اگه درست وارد بشی. برای سرمایه‌گذاری یا کار ملکی، شماره‌ت رو کامنت کن تا
کارشناس‌هامون باهات تماس بگیرن.» with a gold «شماره‌ت رو کامنت کن» card. The narration will be re-recorded in the
user's own voice; `comp/vo_words.js` currently holds the Shahram timings for words 0–112 plus provisional timings for
the 21 new ending tokens (113–133), only for previews. When the recording arrives: Scribe it, align its words to the
134 script tokens, fit to ≤50 s with `fit_vo.py`, regenerate `vo_words.js`, re-mix and re-render.

## Narration: the user's own voice (current)

- Recording: `audio/vo/takes/user_take1.m4a` (65.9 s, kept out of git). Room noise removed with the ElevenLabs voice
  isolator → `user_take1.isolated.mp3`; Scribe transcript with word times → `user_take1.words.json` (both out of git).
- Fit: `python3 -I scripts/fit_vo.py audio/vo/takes/user_take1.isolated.mp3 audio/vo/takes/user_take1.words.json 48.9`
  keeps at most 0.16 s mid-sentence, 0.30 s after a sentence and 0.55 s after «نکن», then stretches ≈1.15× (pitch and
  formants kept) to 48.9 s.
- The user read «حقیقتو» and «هزار و چهارصد و پنج» and «واردش بشی»; `scripts/canon_words.py` maps the 137 spoken tokens
  onto the 134 script tokens (`audio/vo/narration.canonical.json`, `comp/vo_words.js`) so every cue keeps its index.
  Captions show what was said («حقیقتو», «واردش»).
- `mix_audio.py` adds a high-pass and light compression on the voice before the duck and the -14 LUFS master.
