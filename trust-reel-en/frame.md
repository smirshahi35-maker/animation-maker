# frame.md — "One take, Apple keynote" (trust-reel-en, English version)

English version of `../trust-reel` (Persian). Same world, same camera, same assets; English narration and
copy, set in the user's font **Superline Italic**. Concept: one continuous camera through an Apple-style
product world. No cuts: every scene hands off to the next with a camera move (dive into the bin, push
through the ring, whip pan, pull out).

## Canvas

- 1080×1920, 30 fps, 48.65 s. Text column x 96–984; keep type between y 200 and y 1460 (Reels UI covers
  the bottom ~420 px and the right-hand icons). Layout is left-to-right; no `direction: rtl` anywhere.

## Palette (unchanged)

| Token | Hex | Use |
| --- | --- | --- |
| studio | `#f5f5f7` → `#ffffff` centre | light world (hook, problem, story, DM, CTA) |
| stage | `#000000`, `#161617` centre | dark keynote stage ("trust ring" → tip) |
| ink | `#1d1d1f` | headlines on light |
| gray | `#6e6e73` light / `#86868b` dark | secondary lines, labels |
| blue | `#0071e3` / `#2997ff`, gradient `#6cc4ff → #0071e3` | trust, sales, DMs, CTA |
| warm | `#ffb340 → #ff375f` gradient | views / trend (the "wrong" metric) |
| red | `#ff3b30` | the single "0 CUSTOMERS" / "IN THE TRASH." accent |

## Type

- **Superline Italic** (`assets/fonts/Superline-Italic.ttf`, the user's font, licensed: not in git) for all
  display type: headlines, kinetic words, numbers, labels, equations, card names, the CTA keyword.
  - It is an ultra-condensed, all-caps italic with one weight. Declare it `font-style: normal;
    font-weight: normal` and use `font-synthesis: none` (no faux bold or extra slant).
  - **Ligatures off** everywhere it is used: `font-variant-ligatures: none; font-feature-settings: "liga" 0, "clig" 0;`
    (its default ligatures underline IS / IN / IT / AN / THE). Never enable `ss01` or `salt` (they underline every letter).
  - **Apostrophes and quotes must be curly**: ’ “ ” (U+2019, U+201C, U+201D). The straight `'` and `"` glyphs are blank.
    Avoid the em dash (renders as a short hyphen).
  - Sizes: headline 160–200 px, hero/display 220–440 px, secondary lines 84–110 px (gray), labels 64–90 px.
    Line-height 0.95–1.05. Letter-spacing 0 to 0.01em. Text is set in capitals in the markup.
  - Italic overhang: glyphs lean past the right edge of their box; give word spans `padding-right: 0.06em;
    margin-right: -0.06em` and never clip text containers.
- **Inter** variable (OFL, `assets/fonts/InterVariable.ttf`) for in-phone UI microcopy only: app chrome, DM
  names and messages, search field, empty-inbox text, profile bio line, comment field and typed text.
- Numbers: Western digits with commas (`toLocaleString("en-US")`): 80,000 · 24,000 · +47 · 500 · 3%.
- Word-by-word reveal: opacity 0→1, y 28→0, blur 10→0, 0.5 s `power3.out`, on the word's narration time (`data-t`).

## Copy deck (on-screen English)

| Scene | Element | Text |
| --- | --- | --- |
| s1 | headline A | IF YOU DON’T KNOW / THIS ONE TIP… |
| s1 | line B (gray) | EVERYTHING YOU’VE SPENT / ON CONTENT SO FAR, |
| s1 | headline C | THROW IT / IN THE TRASH. (second line red) |
| s1 | cards | MP4 · 02:14 — INVOICE · Content production · $2,400 |
| s2 | t1 | YOUR VIDEOS GET VIEWS, |
| s2 | t2 | 80K VIEWS… / 0 CUSTOMERS (red) |
| s2 | phone | reel: ♪ Trending sound · café · 12K · 340 · 980 — inbox: Messages · Requests · Search · No messages yet · When someone messages you, you’ll see it here. |
| s2 | caption / chip / stat | ONE OF MY CLIENTS — ♪ TRENDING SONG — 80,000 / VIEWS |
| s2 | zero | 0 ORDERS |
| s2 | t4 | BECAUSE THE VIDEO / ENTERTAINED, (warm gradient) |
| s2 | t5 + ring | BUT IT DIDN’T / BUILD TRUST. — ring label TRUST · 3% |
| s3 | hero | HERE’S THE TIP: |
| s3 | split | left VIEWS / ABOUT THE TREND / TREND = VIEWS — right SALES / ABOUT THE CUSTOMER’S PROBLEM / TRUST = SALES |
| s3 | busy phone | POV: · TRENDING!! · ♪ ♪ ♪ · OMG · #trend · WAIT FOR IT!! · LIVE — clean phone: Quality, / up close. |
| s3 | bento | INSTEAD OF TRENDS, WE SHOWED: — BEHIND THE SCENES · QUALITY OF THE WORK · HAPPY CUSTOMERS (5 stars) |
| s4 | tA | VIEWS WENT DOWN, / BUT THE DMS FILLED UP. |
| s4 | badges | Views 80,000 → 24,000 ↓ · Messages +47 |
| s4 | DMs | 8 rows of English names + order/price/booking messages |
| s4 | glass card | SHAHIN / EDITOR & MOTION DESIGNER / OVER 500 PROJECTS |
| s4 | tC + profile | IF YOU OWN A BUSINESS, / FOLLOW. — Shahin · Editor & Motion Designer · Follow → Following |
| s4 | tD | WANT TO KNOW WHY / YOUR PAGE ISN’T BRINGING IN CUSTOMERS? |
| s4 | CTA | COMMENT THE WORD / PAGE (big keyword) — field: Add a comment… → typed P, PA, PAG, PAGE → sent |

## Objects, motion, handoffs

Unchanged from the Persian film (see `../trust-reel/frame.md`): GPT Image 2.5 stills, Veo 3.1 Lite clips,
HTML phone UI; camera = inner wrapper per segment, constant slow drift. Handoffs: s1→s2 through the bin's
black opening = the phone's black screen; s2→s3 through the centre of the trust ring into black; s3→s4 whip
pan with motion blur, black→white; s4 pull-out turns the phone into one tile of a 500-project wall.
Scene starts and every word time: `TIMING.md`.
