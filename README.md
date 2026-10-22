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

## نکته‌های تلفظ گوینده (ElevenLabs v3)

- «آرگون مدیکال» را «مدینال» می‌خواند. نوشتنش به شکل «مدی‌کال» (با نیم‌فاصله) درستش کرد. «مِدیکال» با اعراب گاهی «آرگون» را «آرگان» می‌خواند و حروف لاتین (Argon Medical) هم «آرگان» شد.
- «شهرت» (شهرِ تو) را «شُهرَت» می‌خواند. کلمه‌ای که دو خوانش دارد را با عبارتی که یک خوانش دارد عوض کنید («شهرِ خودت»)، چون حتی تشخیص گفتار هم شَهرِت و شُهرَت را یک‌جور می‌نویسد و نمی‌شود درستی‌اش را چک کرد.
- برای چک تلفظ، فایل صدا را به‌صورت asset (با URL) به Scribe بدهید. اگر خودِ نود TTS را رونویسی کنید، فقط متن اسکریپت را برمی‌گرداند و تلفظ واقعی را نمی‌سنجد.

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

## ریل داستان استیو جابز (موشن دیزاین)

پروژهٔ `jobs-reel/` (حدود ۹۴ ثانیه، ۳۰ فریم بر ثانیه): سناریو، متن و استوری‌بورد از کاربر، به سبک
طراحی مدادی رفرنس (`jobs-reel/references/`). ۱۵ صحنه را `jobs-reel/tools/build_scenes.py` می‌سازد؛
طراحی در `jobs-reel/frame.md`، برنامهٔ صحنه‌ها در `jobs-reel/STORYBOARD.md`، و روش رندر دوباره در
`jobs-reel/HANDOFF.md`. خروجی نهایی: `deliverables/jobs-reel.mp4`.

- فونت لاتین «Steve Jobs» و «NeXT»: Oswald (مجوز OFL، داخل گیت). فونت فارسی همان Abar High است.
- عکس‌ها با `tools/prep_images.py` کاغذشان حذف می‌شود تا همه روی یک کاغذ مشترک بنشینند.
- صدای گوینده با مکث‌های دراماتیک بازچینی شده (`assets/audio/vo/narration.retime.json`) تا جملهٔ
  «بیشتر از یک دقیقه موندی» بعد از دقیقهٔ یک گفته شود.

## ریل «اعتماد، نه ترند» (شاهین، ادیتور و موشن دیزاینر)

پروژهٔ `trust-reel/` (۵۰ ثانیه، ۱۰۸۰×۱۹۲۰، ۳۰ فریم بر ثانیه): سناریوی کاربر در `trust-reel/BRIEF.md`، طراحی
اپل‌گونه در `trust-reel/frame.md` و روش رندر دوباره در `trust-reel/HANDOFF.md`. خروجی نهایی:
`deliverables/trust-reel.mp4`.

- بدون کات: هر صحنه با حرکت دوربین به صحنهٔ بعد می‌رود (شیرجه در سطل، عبور از حلقهٔ اعتماد، ویپ‌پن، عقب‌کشیدن به دیوار ۵۰۰ پروژه).
- عکس‌ها با GPT Image 2.5 و دو ویدیوی کوتاه با Veo 3.1 Lite؛ گوینده: Shahram (ElevenLabs v3) با دو برداشت دوباره برای قلاب و جملهٔ آخر (`tools/tighten_vo.py`).
- عکس شاهین شخصی است و در گیت نیست (`trust-reel/assets/portrait/`)؛ برای رندر دوباره لازم است.

### نسخهٔ انگلیسی

پروژهٔ `trust-reel-en/` (۴۸٫۶۵ ثانیه): همان فیلم با گویندهٔ انگلیسی (Liam، ElevenLabs v4)، متن انگلیسی، چیدمان چپ‌به‌راست
و فونت کاربر Superline Italic. متن و تصمیم‌ها در `trust-reel-en/BRIEF.md`، قوانین فونت و متن‌های روی صفحه در
`trust-reel-en/frame.md`، زمان‌بندی در `trust-reel-en/TIMING.md` و روش رندر دوباره در `trust-reel-en/HANDOFF.md`.
خروجی نهایی: `deliverables/trust-reel-en.mp4`.

- فونت Superline لایسنس‌دار است و در گیت نیست (`trust-reel-en/assets/fonts/Superline-Italic.ttf`)؛ برای رندر دوباره لازم است.
- تصاویر، ویدیوها، موسیقی و افکت‌ها با symlink از `trust-reel/assets/` خوانده می‌شوند.

## ریل «سرمایه‌گذاری در ارمنستان»

پروژهٔ `armenia-investment/` (۵۰ ثانیه، ۱۰۸۰×۱۹۲۰، ۳۰ فریم بر ثانیه): سناریوی تأییدشدهٔ کارفرما با هوک «تو ارمنستان
سرمایه‌گذاری نکن...»، ۳ حقیقت تلخ و ۴ فرصت. سبک بر اساس رفرنس کارفرما: کاغذ کرم، سایهٔ واقعی برگ نخل، زردآلوی بریده در گوشه‌ها،
فوتیج واقعی (Pexels) داخل استیکر کج، UI منظره‌یاب دوربین و ترنزیشن پیکسلی. فونت: Abar Mid Bold و Abar Low Regular (لایسنس‌دار،
داخل گیت نیست). روش ساخت دوباره در `armenia-investment/HANDOFF.md` و منابع فوتیج در `armenia-investment/FOOTAGE.md`.
خروجی نهایی: `deliverables/armenia-investment-reel.mp4`.

- گوینده: Shahram (ElevenLabs v3)؛ خوانش ۶۰٫۵ ثانیه‌ای با کوتاه کردن مکث‌ها و کشش زمانی rubberband (حدود ۱٫۲ برابر، بدون تغییر زیر و بمی) به ۴۸٫۹ ثانیه رسید.
- رندر: صفحهٔ `comp/index.html` فریم‌به‌فریم با Playwright گرفته می‌شود (`scripts/render.js`)؛ زمان‌بندی همهٔ متن‌ها و زیرنویس‌ها از زمان کلمات گوینده (Scribe) است.

## پست اسلایدی «ثبت شرکت در ارمنستان»

پروژهٔ `armenia-company-slides/` (۷ اسلاید ۱۰۸۰×۱۰۸۰): سناریو در `armenia-company-slides/SCENARIO.md`، متن و چیدمان
اسلایدها در آرایهٔ `SLIDES` داخل `armenia-company-slides/slides.html`. سبک از پست‌های اسلایدی پیج کارفرما: پس‌زمینهٔ
سبز تیره (روشن از چپ، تیره به راست و پایین)، تیتر سفید با دورخط قرمز ضخیم، متن سفید با دورخط آبی، ایموجی سر خط‌ها و لوگوی
IRAM CO. پایین راست. فونت: Lalezar (مجوز OFL، داخل گیت). خروجی: `deliverables/armenia-company-slides/`.

- دورخط با حلقه‌های `text-shadow` ساخته می‌شود (گوشه‌های گرد و بدون خوردن پرشدگی سفید)، نه `-webkit-text-stroke`.
- اگر خطی از ۹۹۰ پیکسل پهن‌تر شود، اندازهٔ همان گروه کوچک می‌شود؛ گزارش اندازه‌ها هنگام رندر چاپ می‌شود.
- لوگو در گیت نیست؛ از کاور ریل قبلی بریده می‌شود.

```bash
cd armenia-company-slides
python3 -I scripts/logo_from_cover.py ../deliverables/armenia-investment-cover.png assets/logo.png
NODE_PATH=/opt/node-tools/node_modules node scripts/render.js   # renders/slide-1.png … slide-7.png
```

سناریو برای کارفرما به‌صورت PDF (A4، ۷ صفحه، فونت Lalezar و Vazirmatn، رنگ‌های سبز و طلایی لوگو) از
`armenia-company-slides/pdf/scenario.html` ساخته می‌شود؛ پیش‌نمایش اسلایدها در آن JPEG کوچک‌شده‌اند (`pdf/img/`) تا
حجم فایل حدود ۱٫۵ مگابایت بماند. خروجی: `deliverables/armenia-company-scenario.pdf`.

```bash
NODE_PATH=/opt/node-tools/node_modules node scripts/render_pdf.js
```
