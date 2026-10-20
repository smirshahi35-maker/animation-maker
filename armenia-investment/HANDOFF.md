# Armenia investment reel — how to rebuild

50 s, 1080×1920, 30 fps. Script approved by the client (see the scenario doc). Style follows the client's reference:
cream paper, real palm-leaf shadow, cut-out apricots in the corners, real footage inside a tilted white "sticker",
camera viewfinder UI, pixel-mosaic transitions. Fonts: Abar Mid Bold (headlines) and Abar Low Regular (secondary text).

## Inputs that are not in git

- `fonts/AbarMid-Bold.ttf`, `fonts/AbarLow-Regular.ttf` — licensed (FontIran); ask the user for them.
- `footage/` — Pexels clips, listed with ids in `FOOTAGE.md`; `scripts/pexels_get.sh <id> <name>` downloads one.
- `build/` — generated (frames, palm matte, grain).

## Steps

```bash
python3 -I scripts/prep_assets.py $PWD                 # apricot cut-outs (styleframes/assets)
python3 -I scripts/prep_frames.py $PWD                 # footage → 30 fps sticker frames, palm shadow matte, grain
python3 -I scripts/fit_vo.py audio/vo/takes/take1.mp3 audio/vo/takes/take1.words.json 48.9
python3 -c "import json;d=json.load(open('audio/vo/narration.words.json'));open('comp/vo_words.js','w').write('window.VO_WORDS = '+json.dumps([[w['start'],w['end']] for w in d['words']])+';\n')"
python3 -I scripts/mix_audio.py                        # → audio/mix.wav (-14 LUFS)
# render in 3 parallel parts, then join with the mix
for r in "0 500" "500 1000" "1000 1500"; do set -- $r; NODE_PATH=/opt/node-tools/node_modules node scripts/render.js video build/seg/seg_$1.mp4 $1 $2 & done; wait
printf "file '%s'\n" build/seg/seg_0.mp4 build/seg/seg_500.mp4 build/seg/seg_1000.mp4 > build/seg/list.txt
ffmpeg -f concat -safe 0 -i build/seg/list.txt -i audio/mix.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart renders/armenia-investment-reel.mp4
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
