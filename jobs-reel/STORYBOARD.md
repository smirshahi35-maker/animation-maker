# STORYBOARD — Jobs reel (94.3s, 1080×1920, 30 fps)

Source: the user's 15-slide storyboard (`references/panels/NN.jpg`) and script, built in the style
of `references/style-reference.jpg` (see `frame.md`). Times are composition seconds; word cues come
from `assets/audio/vo/narration.lines.json`. Scenes overlap by 0.5s and cross-fade on the shared
paper, except the hard cut into the twist (s10 → s11); each scene's text clears just before the
next scene's first word, so two lines never ghost over each other. Generator: `tools/build_scenes.py`.

Narration pacing: dramatic pauses were added between sentences (`narration.retime.json`) so the
line «بیشتر از یک دقیقه موندی» is spoken at 1:01 — the claim is true when the viewer hears it.

## Frame 1 — s01 hook · 0.00–2.20
status: built · src: compositions/s01.html · rules: svg-path-draw (pencil reveal), spring-pop-entrance (؟)
«هیچکس / این رو بهت / نمی‌گه...» over a young man seen from behind; a red «؟» pops beside his head.

## Frame 2 — s02 · 2.20–8.70
status: built · src: compositions/s02.html · rules: multi-phase-camera (push to summit), css-marker-patterns (underline)
«ولی گاهی / بزرگ‌ترین موفقیت‌ها / از بدترین شکست‌ها / شروع میشن...» — a lone figure on a peak at sunrise.

## Frame 3 — s03 year card · 8.70–11.75
status: built · src: compositions/s03.html · rules: kinetic-beat-slam (year slam + boom), svg-path-draw (frame)
«سال ۱۹۸۵» — reference layout: huge year behind young Jobs's head, head breaking out of the ink frame.

## Frame 4 — s04 · 11.75–14.45
status: built · src: compositions/s04.html
«مردی که خودش / اپل رو ساخته بود...» — Jobs, arms crossed, beside the 1984 Macintosh.

## Frame 5 — s05 · 14.45–18.70
status: built · src: compositions/s05.html · rules: physics-press-reaction (camera punch on the door slam)
«از شرکتی که ساخته بود / اخراج شد.» — leaving through the Apple door with a box; door SFX on «شد».

## Frame 6 — s06 · 18.70–28.80
status: built · src: compositions/s06.html · rules: coordinate-target-zoom (push to the board)
Three text states: «تصور کن... تو یک شرکت تأسیس می‌کنی، رشدش میدی،» → «بعد یک روز / هیئت مدیره / بهت میگه...» → «دیگه اینجا / جایی نداری.» over the boardroom.

## Frame 7 — s07 name card · 28.80–33.55
status: built · src: compositions/s07.html · rules: svg-path-draw (frame, rule)
«اسم اون آدم...» then the reference name lockup inside the frame: «استیو / جابز» — rule — «Steve / Jobs».

## Frame 8 — s08 · 33.55–37.05
status: built · src: compositions/s08.html · rules: sine-wave-loop (drifting fog)
«خیلی‌ها فکر می‌کردن / دورانش تموم شده...» — alone before a foggy landscape, camera pulls back.

## Frame 9 — s09 · 37.05–46.45
status: built · src: compositions/s09.html
«اما چیزی که / هیچکس نمی‌دید...» on empty paper, then «این بود که همین شکست / باعث شد جابز شرکت جدیدی / به اسم NeXT رو / راه‌اندازی کنه...» as the NeXT cube is drawn; punch-in on «NeXT».

## Frame 10 — s10 · 46.45–55.30
status: built · src: compositions/s10.html · rules: ambient-glow-bloom (logo light)
«و بعدها همین تجربه / باعث شد وقتی دوباره / به اپل برگشت،» → «مسیر این شرکت رو / تغییر بده...» — the keynote; applause swells, then a tape-stop.

## Frame 11 — s11 twist · 55.30–59.45
status: built · src: compositions/s11.html
Hard cut. «اما اصلاً مهم نیست / جابز چطور برگشت...» — the sketch freezes half-drawn, then is erased.

## Frame 12 — s12 · 59.45–65.75
status: built · src: compositions/s12.html · rules: counting-dynamic-scale (elapsed-time pill)
«مهم اینه که تو الان / بیشتر از یک دقیقه / موندی و این داستان رو / دنبال کردی.» — hourglass; a pill shows the film's own time rolling ۰۰:۵۹ → ۰۱:۰۰; clock ticks on the second.

## Frame 13 — s13 · 65.75–73.40
status: built · src: compositions/s13.html
«چرا؟» (heartbeat) → the eye is drawn; «چون من تونستم / یک اتفاق ساده رو / تبدیل کنم به یک تصویر / توی ذهن تو.» — on «تصویر» the story's own sketches (1985, the door, NeXT, the keynote) flicker in the pupil.

## Frame 14 — s14 · 73.40–78.80
status: built · src: compositions/s14.html
«و این دقیقاً کاریه که یک / ادیتور و موشن دیزاینر / انجام میده...» — an editor at the timeline; the monitor's preview (a lone figure on a summit, slide 2) glows and flickers.

## Frame 15 — s15 · 78.80–94.30
status: built · src: compositions/s15.html · rules: ambient-glow-bloom (bulb)
«هر چیزی که تو ذهنت / تصور می‌کنی، / میشه به تصویر تبدیل کرد.» — the bulb lights on «تصویر»; then the dark card: «و وقتی بتونی ایده‌هات رو تصویری کنی، / داری یک قدم بزرگ برای رشد / برند و کسب‌وکارت برمی‌داری.» Holds to the end.

## Sound

- Story bed (`music/story.mp3`) from 1.0s; its swell lands on the return to Apple and decays into the applause, which tape-stops into the twist.
- 55.3–68.1: no music — narration, clock ticks (stretched to one per second, aligned to the timer), sand, heartbeat on «چرا؟».
- Pitch bed (`music/pitch.mp3`, 88 BPM) from 68.09s, with a bar-aligned jump (media 21.828 → 40.919) so its final chord rings under the last line.
- Both beds are carved under the narration (`carve.mjs --strength 0.6`), fades in `tools/add_fades.py`.
