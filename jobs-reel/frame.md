# frame.md — "Pencil documentary" (Jobs reel)

Taken from the user's style reference (`references/style-reference.jpg`): a graphite sketchbook
lit like a documentary. One sheet of warm paper runs under the whole film; every scene is drawn
onto it, and the type is set on it like a magazine page.

## Canvas

- 1080×1920, 30 fps. Title-safe: 108px sides, 192px top/bottom. Keep type above y≈1500 (Reels UI).
- Shared background (root, full length): `assets/paper/paper.jpg` (seeded, `tools/make_paper.py`),
  two diagonal light leaks drifting slowly, an edge vignette and a stepped grain tile.

## Palette

| Token | Hex | Use |
| --- | --- | --- |
| paper | `#d8cebd` centre → `#a89c89` edge | the sheet (texture, not a flat fill) |
| panel | `#e9e1d3` | the lighter inner panel of the framed portraits |
| ink | `#2a231c` | type, rules, frames |
| graphite | `#5b5044` | secondary type, labels |
| accent | `#8b2f1f` | ONE word or phrase per scene at most (اخراج، NeXT، چرا؟، تصویر) |

No gradients on type, no glows; light comes from the paper's light leaks.

## Type

- Persian: Abar High (single weight; hierarchy by size/colour, `font-synthesis: none`), per-word
  spans only (never per-letter), `direction: rtl` on the text block, not on `<html>`.
- Latin name lockup: Oswald 600, condensed caps feel (only for «Steve Jobs», «NeXT»).
- Sizes: label 46–54px · body line 72–84px · headline 104–132px · display year 420px+.
- Years and numbers as Persian digits; digit glyphs sit high, nudge down ~0.155em inside boxes.

## Image treatment

- GPT Image 2.5 pencil drawings → colour-to-alpha WebP (graphite only, paper removed), so every
  scene lands on the same sheet. Portraits that must overlap type use bg-removed cutouts.
- Reveal: contour pass (`-lines.webp`) wipes in like a pencil, then the shading fades up over it.
- Camera: slow push/drift on an inner wrapper only (scale 1.00→1.07), never on the timed clip.

## Signature layouts

- **Year card (s03):** huge dark year behind the head, thin ink frame (3px), the cutout's head
  breaking out above the frame's top edge, small label above the year.
- **Name card (s07):** same frame; Persian name stacked right of the face, a short rule, then the
  English name in Oswald — mirroring «جورج دی مسترال / George de Mestral».

## Motion

- Type: word-by-word, timed to the narration (`assets/audio/vo/narration.lines.json`), entering
  from soft blur + 24px rise, `power3.out`, 0.45s. Key words get a hand-drawn underline that draws.
- Scene changes: 0.5s overlap; the outgoing drawing fades and softens while the next one sketches in.
- Twist (s11→s12): the story stops — music cuts, the drawing is "erased" right-to-left.

## Don'ts

- No `dir="rtl"` on `<html>`, no per-letter animation of Persian, no synthetic bold.
- No new claims, handles or CTAs — the script ends the film.
