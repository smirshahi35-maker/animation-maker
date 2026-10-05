# Argon Medical webinar reel — design truth

Concept: the empty chair is the villain. Every number on screen counts bookings, and
the same waiting room, empty then full, is the proof.

Look borrowed from the user's reference video: near-black cinematic field with a
soft radial glow and vignette, glowing display type, rolling odometer counters,
short white/red punch lines, small labels between thin rules, ring ornaments on
the end card. Re-colored to Argon's brand (blue + white, red for the problem).

## Palette

| Token        | Hex       | Use                                         |
| ------------ | --------- | ------------------------------------------- |
| `--bg`       | `#060a14` | canvas (navy-tinted, never pure black)      |
| `--bg-glow`  | `#12224a` | radial glow behind focal content            |
| `--fg`       | `#f2f5fb` | headlines, body                             |
| `--muted`    | `#9aa6c2` | labels, thin rules                          |
| `--brand`    | `#3d6fe0` | Argon blue — solution, brand, counters up   |
| `--brand-hi` | `#a9c3ff` | metallic highlight on brand type            |
| `--alarm`    | `#ff4a3d` | problem words, empty counter                |
| `--alarm-hi` | `#ff9a5c` | warm top of the alarm gradient              |

## Type

Abar High only (single Regular weight, `font-synthesis: none`). Hierarchy from size,
color and glow, never faux bold. Headlines 96–170px, body 48–64px, labels 34–40px.
Per-word animation only (per-letter inline-block breaks Persian joining). Digits are
written as Persian digits; counters use the font's `ss01` set.

## Layout

1080×1920. Title-safe 10%. Keep text out of the bottom 330px and right 120px
(Instagram UI). Headlines anchor to the upper third; photos fill the frame under a
top-dark grade so type sits on dark.

## Motion

Slams with blur for punch lines, odometer ticks for counters, slow Ken Burns on every
still, breathing glow and drifting rings in the background. Hard cuts between scenes,
each masked by a whoosh or impact.
