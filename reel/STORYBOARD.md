---
format: 1080x1920
duration: 44.6s
message: "Free Argon Medical webinar teaches clinics to turn followers into patients — register in 5 steps"
arc: Hook → Problem → Cause → Offer → How (5 steps) → Payoff → CTA
audience: clinic owners, doctors and clinic staff in Iran
mode: autonomous
music: dark sparse tension → steady build → warm hopeful resolve (assets/audio/music/bed.mp3)
---

Narration: `assets/audio/vo/narration.mp3`, placed at 0.4s. Times below are absolute
(video time). Word marks come from `assets/audio/vo/take1.lines.json` + 0.4s.

## Frame 1 — Empty chairs

- src: compositions/s1-hook.html
- duration: 5.2s
- transition_in: cut
- scene: Empty waiting room, slow push-in; "بهترین دستگاه‌ها" then red "صندلی‌های خالی"; bookings counter ticks down to ۰
- voiceover: "کلینیکت بهترین دستگاه‌ها رو داره... پس چرا صندلی‌های انتظار خالیه؟"
- poster: 4.2
- rules: multi-phase-camera (push), kinetic-beat-slam, vertical-spring-ticker (countdown)
- status: animated

Hook at frame 1. Clock ticks under it. The counter is the reference's "purchasing power" mechanic, applied to bookings.

## Frame 2 — Likes, no bookings

- src: compositions/s2-likes.html
- duration: 5.2s
- transition_in: cut
- scene: Doctor alone at night on her phone; followers and likes roll up, bookings stay ۰ in red; "لایک داری. نوبت نداری."
- voiceover: "فالوور داری، لایک داری؛ ولی پیام‌ها به نوبت تبدیل نمی‌شن."
- poster: 4.6
- rules: vertical-spring-ticker, counting-dynamic-scale, kinetic-beat-slam
- status: animated

## Frame 3 — The broken path

- src: compositions/s3-path.html
- duration: 4.9s
- transition_in: cut
- scene: Typographic. "مشکل از تخصص تو نیست" struck through; "مسیر جذب" slams in red; path دیده‌شدن → پیام → نوبت with the last link broken
- voiceover: "مشکل از تخصص تو نیست؛ مشکل از مسیر جذب مراجعه‌کننده‌ست."
- poster: 4.4
- rules: kinetic-beat-slam, svg-path-draw, ambient-glow-bloom
- status: animated

## Frame 4 — The offer

- src: compositions/s4-reveal.html
- duration: 10.5s
- transition_in: cut (impact + flash)
- scene: Argon logo blooms with rings; "وبینار رایگان" pill; title «مدیریت نوین کلینیک»; host photo card with name plate; "یاد بگیر چطور مراجعه‌کننده جذب کنی"
- voiceover: "آرگون مدیکال یه وبینار رایگان برگزار می‌کنه: مدیریت نوین کلینیک، با مهندس حسام هاشمی؛ تا یاد بگیری چطور مراجعه‌کننده جذب کنی."
- poster: 9.5
- rules: spring-pop-entrance, ambient-glow-bloom, waterfall-entry, multi-phase-camera (card push)
- status: animated

## Frame 5 — Five steps

- src: compositions/s5-steps.html
- duration: 10.0s
- transition_in: cut
- scene: Phone with the real Porsline form; each step on its VO word: type name, type phone, tap role, tap challenge, type city; progress bar fills; success check
- voiceover: "ثبت‌نامش فقط پنج قدمه: اسمت... شماره‌ت... نقشت توی کلینیک... بزرگ‌ترین چالشت... و شهرت. تمام!"
- poster: 9.5
- rules: cursor-click-ripple, discrete-text-sequence (typing), stat-bars-and-fills (progress), vertical-spring-ticker (step label)
- status: animated

Step marks: s1 28.08 · s2 29.19 · s3 30.37 · s4 31.92 · s5 33.84 · done 34.93.

## Frame 6 — Full chairs

- src: compositions/s6-full.html
- duration: 3.0s
- transition_in: cut
- scene: Same waiting room, light sweep wipes empty → full; counter rolls ۰ → ۲۴ in blue; booking notifications pop
- voiceover: "حالا نوبت توئه که صندلی‌ها پر بشن."
- poster: 2.6
- rules: vertical-spring-ticker, spring-pop-entrance
- status: animated

## Frame 7 — CTA

- src: compositions/s7-cta.html
- duration: 5.8s
- transition_in: cut
- scene: Ring end card; "لینک ثبت‌نام / در هایلایت «وبینار»"; Instagram highlight bubble (host photo) gets tapped; @argonmed + logo
- voiceover: "لینک ثبت‌نام، توی هایلایت وبینار، پیج آرگون مدیکاله."
- poster: 4.5
- rules: cursor-click-ripple, sine-wave-loop (rings), ambient-glow-bloom
- status: animated
