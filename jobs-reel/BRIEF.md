---
workflow: general-video
flow: automation
storyboard: no
message: "A story about failure (Steve Jobs fired from Apple) keeps you watching — that is what an editor and motion designer does for a brand"
destination: instagram-reels
aspect: 1080x1920
fps: 30
language: fa
audience: Persian-speaking business owners and brands on Instagram
length: ~94s (the line «بیشتر از یک دقیقه موندی» must land after 1:00)
angle: story
voice: elevenlabs/ndcUYGFbbd96WXiZVVaQ (Roya – Warm Tehrani Narrator, eleven_v3)
---

## Intent

The user supplied everything: the script (hook → Jobs story → twist → pitch), a 15-slide
storyboard (`references/storyboard.jpg`, cropped to `references/panels/01–15.jpg`) and a style
reference (`references/style-reference.jpg`). Our job is to build it in HyperFrames: AI images with
GPT Image 2.5 (via ElevenLabs), narration, music and SFX from ElevenLabs, 30 fps, for Instagram.

Style reference: graphite cross-hatched pencil portrait on warm beige paper; a huge dark year
behind the head; the head breaks out of a thin ink frame; the name set inside the frame in Persian
and English (condensed), split by a short rule; soft light leaks and vignette on the paper.

## Script (verbatim from the user)

Hook: «هیچکس اینو بهت نمیگه، ولی گاهی بزرگ‌ترین موفقیت‌ها از بدترین شکست‌ها شروع میشن…»
Story: «سال ۱۹۸۵، مردی که خودش اپل رو ساخته بود، از شرکتی که ساخته بود اخراج شد. تصور کن… تو یک
شرکت تأسیس می‌کنی، رشدش میدی، بعد یک روز هیئت مدیره بهت میگه دیگه اینجا جایی نداری. اسم اون
آدم استیو جابز بود. خیلی‌ها فکر می‌کردن دورانش تموم شده. اما چیزی که هیچکس نمی‌دید این بود که همین
شکست باعث شد جابز شرکت جدیدی به اسم NeXT رو راه‌اندازی کنه و بعدها همین تجربه باعث شد وقتی
دوباره به اپل برگشت، مسیر این شرکت رو تغییر بده… اما اصلاً مهم نیست جابز چطور برگشت… مهم اینه که
تو الان بیشتر از یک دقیقه موندی و این داستان رو دنبال کردی. چرا؟ چون من تونستم یک اتفاق ساده رو
تبدیل کنم به یک تصویر توی ذهن تو. و این دقیقاً کاریه که یک ادیتور و موشن دیزاینر انجام میده… هر
چیزی که تو ذهنت تصور می‌کنی، میشه به تصویر تبدیل کرد. و وقتی بتونی ایده‌هات رو تصویری کنی، داری یک
قدم بزرگ برای رشد برند و کسب‌وکارت برمی‌داری.»

TTS spelling only: the year is written out in words and NeXT as «نِکست»; wording is unchanged.

## Assets

- `assets/ai/src/sNN-*.png` — GPT Image 2.5 Sunburst, 2K 9:16, style reference wired in.
  `tools/prep_images.py` makes `sNN.jpg` (paper → white, multiplied onto the shared paper),
  `sNN-lines.jpg` (pencil contour pass) and `sNN-cut.png` (portrait cutouts for s03/s07).
  A slide without a generated image falls back to its storyboard panel (`sNN.placeholder` marks it).
- `assets/audio/vo/narration.wav` — Roya, eleven_v3, retimed with dramatic pauses
  (`narration.retime.json`, word times in `narration.lines.json`, verified with Scribe).
- `assets/audio/music/story.mp3` (story bed) and `pitch.mp3` (pitch bed, 88 BPM) — ElevenLabs Music.
- `assets/audio/sfx/*.mp3` — ElevenLabs SFX.
- Fonts: Abar High (licensed, not committed) for Persian; Oswald (OFL) for the English name lockup.

## Customizations

- No CTA/handle was given, so none is invented: the film ends on the user's last line.
- ElevenLabs free plan has a daily image cap; slides without images use storyboard stand-ins
  until the cap allows (or the plan is upgraded).

## Notes

- 2026-10-06: drawings for slides 1–6 done (GPT Image 2.5, style reference wired in). Slides 7–15
  blocked by the old ElevenLabs account's free-plan image cap; the user is connecting a paid account.
  Next steps: `HANDOFF.md`.
