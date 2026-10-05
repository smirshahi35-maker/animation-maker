# animation-maker

موشن‌گرافیک فارسی برای ریلز اینستاگرام (1080×1920) با [HyperFrames](https://hyperframes.heygen.com).

- تصاویر: GPT Image 2.5 (از طریق ElevenLabs)
- صدای گوینده، موسیقی و افکت‌ها: ElevenLabs
- فونت: Abar High (فونت‌ایران)

## راه‌اندازی

```bash
# فونت لایسنس‌دار است و در گیت نیست؛ قبل از رندر کپی‌اش کنید:
cp AbarHigh-Regular.otf reel/assets/fonts/

cd reel
# در محیط ابری Claude، از Chrome نصب‌شده استفاده کنید:
export HYPERFRAMES_BROWSER_PATH=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell
npx hyperframes check
npx hyperframes render -o renders/reel.mp4
```

GSAP به‌صورت محلی در `reel/assets/vendor/` قرار دارد، چون رندر نباید به CDN وابسته باشد.

## قوانین فونت Abar High

نتیجهٔ بررسی فونت (`AbarHigh-Regular.otf`، نسخهٔ 2.200، CFF، 1080 گلیف):

| مورد | وضعیت |
| --- | --- |
| حروف فارسی (پ چ ژ گ ک ی)، اعراب، همزه‌ها | کامل |
| اعداد فارسی، عربی و لاتین | کامل |
| نیم‌فاصله (ZWNJ)، «»، ؟، ،، ؛، ٪ | کامل |
| اتصال حروف (init/medi/fina/rlig) و لا | درست در Chrome و رندر HyperFrames |
| کرنینگ و جای اعراب (kern/mark/mkmk) | دارد |
| وزن | فقط Regular |
| fsType = 8 | اجازهٔ embed دارد |

قوانینی که باید در کد رعایت شود:

1. **`dir="rtl"` روی `<html>` ممنوع.** HyperFrames با آن ویدیوی سیاه رندر می‌کند. جهت را با کلاس `.fa` (`direction: rtl`) روی خود متن بگذارید.
2. **انیمیشن حرف‌به‌حرف با `inline-block` ممنوع.** اتصال حروف فارسی می‌شکند. انیمیشن متن را کلمه‌به‌کلمه بسازید (`<span class="w">`).
3. **بولد مصنوعی نه.** فونت یک وزن دارد؛ `font-synthesis: none` فعال است. سلسله‌مراتب را با اندازه، رنگ و حرکت بسازید.
4. **اعداد:** کلاس `.fa-num` (ویژگی `ss01` فونت) رقم‌های لاتین را فارسی نشان می‌دهد؛ برای شمارنده‌های GSAP مناسب است. برای جداکنندهٔ هزارگان فارسی از `toLocaleString("fa-IR")` استفاده کنید.
5. **ی و ک فارسی** (U+06CC و U+06A9) بنویسید، نه ي و ك عربی؛ شکل گلیف‌هایشان فرق دارد.
6. **ارتفاع خط:** ascent+descent فونت ‎1.8em است؛ برای تیترها `line-height` حدود ‎1.25 تا ‎1.4 بگذارید.
7. `@font-face` باید داخل همان فایل HTML باشد و `font-display: block` داشته باشد؛ تایم‌لاین را منتظر `document.fonts.ready` نگذارید. مسیرها (فونت، عکس) حتی داخل `compositions/` نسبت به ریشهٔ پروژه نوشته می‌شوند: `assets/...` نه `../assets/...`.
8. **اعداد فارسی بالاتر از وسط می‌نشینند** (۰٫۷۳em بالای خط پایه، حروف حدود ۰٫۴۵em). برای وسط‌چین کردن عدد در یک قاب، آن را حدود ‎0.155em پایین بیاورید. صفرِ فارسی (۰) کوچک است و نیازی به جابه‌جایی ندارد.
9. **متن گرادیانی:** گرادیان (`background-clip: text`) را روی خود هر کلمه بگذارید، نه روی والد؛ اگر کلمه‌ها جدا انیمیت شوند، گرادیانِ والد ناپدید می‌شود.
10. **نقطهٔ وسط (·) کنار عدد فارسی شبیه صفر (۰) دیده می‌شود.** به‌جایش از خط عمودی یا فاصله استفاده کنید.

ویژگی‌های اختیاری فونت: `swsh` (کاف و میم کشیده)، `ss02`–`ss04`، `dlig`.

## ریل وبینار آرگون مدیکال

پروژهٔ `reel/` (۴۴٫۶ ثانیه): هفت صحنه در `reel/compositions/`، برنامهٔ صحنه‌ها در `reel/STORYBOARD.md`، طراحی در `reel/frame.md` و بریف در `reel/BRIEF.md`.

- عکس‌ها با GPT Image 2.5، صدای گوینده (Roya، ElevenLabs v3)، موسیقی و افکت‌ها از ElevenLabs. زمان‌بندی کلمات گوینده در `reel/assets/audio/vo/narration.lines.json` است.
- موسیقی زیر صدای گوینده با ابزار carve هایپرفریمز جا باز کرده است. اگر صدای گوینده عوض شد، carve را دوباره اجرا کنید:
  `node ~/.claude/skills/hyperframes-audio/scripts/carve.mjs --comp index.html --bed music-bed --voice narration --strength 0.6` (و همین برای `music-tail`). سپس خط `volume` (فید) را دوباره در `data-automation` اضافه کنید، چون carve آن را بازنویسی می‌کند.
- خروجی نهایی برای اینستاگرام روی ‎-14 LUFS مستر می‌شود (ویدیو بدون تغییر کپی می‌شود):

```bash
npx hyperframes render -q high -f 30 -o renders/argon-webinar-reel.mp4
ffmpeg -i renders/argon-webinar-reel.mp4 -c:v copy -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:a aac -b:a 192k -movflags +faststart renders/argon-webinar-reel-final.mp4
```
