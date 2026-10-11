# trust-reel-en — brief (English version of trust-reel)

workflow: general-video

## 2026-10-11 — English version requested

The user (writes Persian) approved the Persian reel (`../trust-reel`, delivered as
`../deliverables/trust-reel.mp4`) and asked: translate the whole video into English, make an English version,
and use the font they supplied (Superline Italic, uploaded as `Superline-Italic.ttf`).

Decisions taken without asking (stated to the user, open to change):
- Same film, same aspect (1080×1920), same world, camera, assets, music and SFX; only narration, copy and type change.
- Voice: ElevenLabs premade "Liam - Energetic, Social Media Creator" (`TX3LPaxmHKxFdv7VOQHJ`), model eleven_v4;
  4 takes, take 1 chosen (Scribe heard "Shaheen" correctly; takes 2 and 4 sounded like "Shaheem").
  TTS text spells the name "Shaheen" for pronunciation; on screen it is "SHAHIN".
- Superline Italic for all display type, Inter (OFL) for in-phone UI microcopy. Superline is licensed to the
  user: kept out of the public repo (`.gitignore`), like the portrait.
- Currency on the invoice card: $2,400 (the Persian card showed tomans).

## Script (English)

If you don't know this one tip... everything you've spent on content so far? Throw it in the trash.

Your videos get views... but your DMs are empty?

One of my clients used a trending song and got eighty thousand views. But not a single order. Because the
video entertained... but it didn't build trust.

Here's the tip: content that gets views is about the trend. Content that sells is about your customer's
problem. So instead of trends, we showed the behind-the-scenes, the quality of the work, and happy customers.
Views went down... but the DMs filled up.

I'm Shahin, an editor and motion designer with over five hundred projects. If you own a business, follow. And
if you want to know why your page isn't bringing in customers, comment the word "PAGE".

On-screen copy: `frame.md` (copy deck). Timing: `TIMING.md`.

## Status

1. English narration built (`tools/make_vo.py`, 47.8 s); preview sent to the user.
2. Scenes s1–s4 adapted by one agent per scene, each followed by an independent critic-fixer.
3. Draft 1: narration 6 dB quieter than the Persian one -> music too loud; narration normalised to -18.3 LUFS.
4. Draft 2 reviewed by four lenses (transitions, English text, art direction, audio), each verified. Applied: payoff
   line "BUT THE DMS FILLED UP." held 0.25 s longer, one-line bento labels below the subjects, symmetric split
   sub-labels, roomier intro card, Sara's DM copy, 0.65 s dead pause before "Views" removed (film now 48.65 s),
   hook music dip, counter ticks trimmed, two whooshes lowered. Rejected: re-wording "80K VIEWS… / 0 CUSTOMERS"
   (the client's on-screen text, kept as in the Persian film).
