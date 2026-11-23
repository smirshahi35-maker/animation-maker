# شبگرد — ادیت سینمایی کلیپ رانندگی شبانه

خروجی: `deliverables/night-drive-cinematic.mp4` (۱۹۲۰×۱۰۸۰، کادر ‎2.39:1 با نوار سیاه، ۲۴ فریم، ‎18.7 ثانیه)

## ساختار ادیت

| زمان خروجی | منبع | اتفاق |
| --- | --- | --- |
| ‎0–1.0 | — | سیاهی، تایتل «۰۲:۲۰ بامداد»، درون (drone) در F |
| ‎1.0–5.87 | ‎0–4.87 | کابین تاریک، زوم آهسته، آهنگ ضبط ماشین خفه (low-pass)، رایزر |
| ‎5.87 | ‎4.87 | روشن شدن چراغ‌ها: فلش، پانچ زوم، لرزش، ضربهٔ ساب، آهنگ یک‌باره باز می‌شود |
| ‎5.87–7.5 | ‎4.87–5.6 | اسلوموشن ‎0.32x و برگشت نرم به سرعت عادی، تایتل «شبگرد / NIGHT DRIVE» |
| ‎13.76 | ‎11.90 | خاموش شدن چراغ‌ها، دیده شدن شهر، ضربهٔ دوم، آهنگ خفه و پر از ریورب |
| ‎13.76–17.8 | ‎11.9–13.93 | نیم‌سرعت، زوم به سمت نور شهر، «شهر خواب بود، ما نه.» |

رنگ: سایه‌های فیروزه‌ای، قرمزهای زنده (خوشبوکننده و برچسب)، مشکی مات، هاله و بلوم روی نورها، گرین فیلم، ویگنت، کمی اعوجاج رنگی لبه‌ها.

## ساخت دوباره

```bash
pip install opencv-python-headless scipy numpy
export NIGHT_DRIVE_SRC=/path/to/20261123_022028.mp4
cd night-drive/tools
node render_cards.js "$PWD/../titles"          # PNGهای تایتل (Chromium + Playwright)
python3 render_audio.py mix.wav
python3 render_video.py ../titles video.mp4     # مستر 10-bit بدون صدا
ffmpeg -i video.mp4 -i mix.wav -af volume=-1.5dB -map 0:v -map 1:a \
  -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -c:a aac -b:a 256k \
  -movflags +faststart ../../deliverables/night-drive-cinematic.mp4
```

فونت‌ها: Vazirmatn (OFL) و Inter (OFL).
