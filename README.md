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
7. `@font-face` باید داخل همان فایل HTML باشد و `font-display: block` داشته باشد؛ تایم‌لاین را منتظر `document.fonts.ready` نگذارید.

ویژگی‌های اختیاری فونت: `swsh` (کاف و میم کشیده)، `ss02`–`ss04`، `dlig`.
