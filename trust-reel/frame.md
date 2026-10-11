# frame.md — "One take, Apple keynote" (trust-reel)

Concept: one continuous camera through an Apple-style product world. No cuts: every scene hands
off to the next with a camera move (dive into the bin, push through the ring, whip pan, pull out).

## Canvas

- 1080×1920, 30 fps, ~49.4 s. Text column x 96–984; keep type between y 200 and y 1460 (Reels UI
  covers the bottom ~420 px and the right-hand icons).

## Palette

| Token | Hex | Use |
| --- | --- | --- |
| studio | `#f5f5f7` → `#ffffff` centre | light world (hook, problem, story, DM, CTA) |
| stage | `#000000`, `#161617` centre | dark keynote stage ("trust ring" → tip) |
| ink | `#1d1d1f` | headlines on light |
| gray | `#6e6e73` light / `#86868b` dark | secondary lines, labels |
| blue | `#0071e3` / `#2997ff`, gradient `#6cc4ff → #0071e3` | trust, sales, DMs, CTA |
| warm | `#ffb340 → #ff375f` gradient | views / trend (the "wrong" metric) |
| red | `#ff3b30` | the single "۰ مشتری" / "بریز دور." accent |

One accent per beat. Gradients only on single keywords (applied per word span).

## Type

- Vazirmatn variable (OFL, `assets/fonts/Vazirmatn-Variable.ttf`), weights 300–900.
- Headline 104–124 px / 800–900, line-height 1.35. Secondary 56–64 px / 600 gray.
- Display numbers 240–700 px / 900. Persian digits always (۰–۹, `٬` thousands separator).
- Word-by-word reveal: opacity 0→1, y 28→0, blur 10→0, 0.5 s `power3.out`, on the word's VO time.
- Never `dir="rtl"` on `<html>`; never per-letter animation of Persian (joins break).

## Objects

- GPT Image 2.5 renders on seamless studio light, cut out (birefnet) where they move: paper balls,
  wastebasket. Portrait: the user's photo, background removed locally.
- Phone, Instagram-like UI, counters, rings, cards, buttons: built in HTML/CSS (crisp, editable).
- Veo 3.1 Lite: `viewer-swipe` (laughs, then swipes away) and `latte-pour` (split screen, same
  footage twice: busy trend edit vs clean edit).

## Motion

- Camera = an inner wrapper per segment (`.cam`), eased `power3.inOut` / `expo.out`, never the
  timed clip. Constant slow drift so no frame is static.
- Handoffs: s1→s2 through the bin's black opening = the phone's black screen; s2→s3 through the
  centre of the trust ring into black; s3→s4 whip pan with motion blur, black→white; s4 pull-out
  turns the phone into one tile of a 500-project wall.
