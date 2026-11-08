<div dir="rtl">

<div align="center">

<img src="Demos/images/dastkhat-cover.png" alt="دستخط، فونت فارسی و لاتین برای رابط کاربری" width="100%">

# دستخط (Dastkhat)

**فونت فارسی و لاتین برای رابط کاربری، با نقطه‌های هندسی.**

[![Version](https://img.shields.io/badge/version-1.200-blue)](FONTLOG.txt)
[![License: Commercial](https://img.shields.io/badge/license-Commercial-red)](License/EULA.txt)
[![Formats](https://img.shields.io/badge/formats-TTF%20%7C%20Variable%20%7C%20WOFF2-lightgrey)](#محتویات-بسته)

[English](README.md) · **فارسی**

</div>

---

دستخط برای رابط کاربری محصولات، فروشگاه‌های اینترنتی و متن‌های فارسی پرحجم روی صفحه طراحی شده است. این فونت در ۹ وزن (از Thin با وزن ۱۰۰ تا Black با وزن ۹۰۰) و یک نسخه متغیر منتشر می‌شود، در سه سبک نقطه، و برای نیازهای رایج، نسخه‌های FaNum و NoEn هم دارد.

دستخط را [دستیار](https://dastyar.io) منتشر کرده و بر پایه [وزیرمتن](https://github.com/rastikerdar/vazirmatn) ساخته شده است.

## فهرست

- [شروع سریع](#شروع-سریع)
- [کدام نسخه را انتخاب کنم؟](#کدام-نسخه-را-انتخاب-کنم)
- [محتویات بسته](#محتویات-بسته)
- [نصب](#نصب)
- [استفاده در وب](#استفاده-در-وب)
- [نکات تایپوگرافی](#نکات-تایپوگرافی)
- [مجوز استفاده](#مجوز-استفاده)
- [سازندگان](#سازندگان)

## شروع سریع

برای وب‌سایت، پوشه `Webfonts` را در پروژه کپی کنید و این چند خط را اضافه کنید:

```html
<link rel="stylesheet" href="/Webfonts/dastkhat.css">
<style>
  body { font-family: var(--font-dastkhat); }
</style>
```

برای نرم‌افزارهای طراحی مثل فیگما، فتوشاپ و ایلاستریتور، فایل‌های TTF پوشه `Fonts/Main/Dastkhat/TTF` را نصب کنید. جزئیات در بخش [نصب](#نصب) آمده است.

## کدام نسخه را انتخاب کنم؟

### سبک‌های نقطه

| خانواده | نقطه‌ها | کاربرد پیشنهادی |
|---|---|---|
| **Dastkhat** | مربع | پیش‌فرض برای رابط کاربری و متن |
| **Dastkhat Diamond** | مربع چرخیده ۴۵ درجه (لوزی) | ظاهر نرم‌تر و کلاسیک |
| **Dastkhat Bar** | دو نقطه یک خط می‌شود، سه نقطه یک خط و یک مربع | لوگو، تیتر و هویت بصری |

<img src="Demos/images/dastkhat-dot-styles.png" alt="مقایسه سه سبک نقطه" width="100%">

### نسخه‌ها

هر خانواده در سه نسخه ارائه می‌شود.

| نسخه | تفاوت | چه زمانی استفاده کنم؟ |
|---|---|---|
| **Main** | فارسی و لاتین کامل | بیشتر پروژه‌ها |
| **FaNum** | عددهای لاتین `0-9` با شکل فارسی `۰-۹` نمایش داده می‌شوند | قیمت، جدول و داشبورد. داده و کد شما تغییری نمی‌کند. |
| **NoEn** | حروف لاتین حذف شده‌اند | می‌خواهید دستخط را با فونت لاتین دلخواه خودتان (مثل Inter یا Geist) ترکیب کنید |

### ثابت یا متغیر؟

| نیاز شما | پوشه پیشنهادی |
|---|---|
| کنترل دقیق هر وزن در نرم‌افزار طراحی | `Fonts/Main/<Family>/TTF` (۹ وزن) |
| حجم کمتر و همه وزن‌های ۱۰۰ تا ۹۰۰ در یک فایل | `Fonts/Main/<Family>/Variable` |
| وب‌سایت و اپلیکیشن وب | `Webfonts/` (فرمت WOFF2) |

## محتویات بسته

```
Dastkhat-v1.200/
├── Fonts/
│   ├── Main/      Dastkhat, DastkhatDiamond, DastkhatBar   (۹ وزن TTF + Variable)
│   ├── FaNum/     همان خانواده‌ها، با عددهای فارسی
│   └── NoEn/      همان خانواده‌ها، فقط فارسی
├── Webfonts/      dastkhat.css, fonts/*.woff2, webfont-test.html
├── Specimen/      Dastkhat-Specimen.pdf
├── Demos/         صفحه معرفی، تست‌کننده متن، نقشه حروف، نمونه رابط کاربری، تصاویر
├── Helps/         راهنمای نصب و استفاده (فارسی و انگلیسی)
├── License/       EULA، اطلاعیه اجزای دیگران و خلاصه مجوز (PDF)
├── Source/        اسکریپت‌های ساخت
├── FONTLOG.txt    تاریخچه تغییرات
├── README.md      راهنمای انگلیسی
└── README.fa.md   همین فایل
```

## نصب

> [!IMPORTANT]
> روی هر سیستم **یا** نسخه ثابت را نصب کنید **یا** نسخه متغیر را، نه هر دو را. نام‌های یکسان در بسیاری از نرم‌افزارها تداخل ایجاد می‌کند.

### ویندوز

۱. پوشه `Fonts/Main/Dastkhat/TTF` را باز کنید.
۲. همه فایل‌ها را انتخاب کنید (`Ctrl+A`)، راست‌کلیک کنید و گزینه **Install for all users** را بزنید.
۳. نرم‌افزار طراحی را یک بار ببندید و دوباره باز کنید.

### مک

۱. برنامه **Font Book** را باز کنید.
۲. فایل‌های TTF را به داخل پنجره بکشید.
۳. اگر هشدار تکراری بودن دیدید، ابتدا نسخه قبلی دستخط را حذف کنید.

### لینوکس

```bash
mkdir -p ~/.local/share/fonts/Dastkhat
cp Fonts/Main/Dastkhat/TTF/*.ttf ~/.local/share/fonts/Dastkhat/
fc-cache -f
```

## استفاده در وب

### CSS ساده

فایل CSS برای هر خانواده یک متغیر تعریف کرده است:

```css
body    { font-family: var(--font-dastkhat); }                         /* نقطه مربع */
.price  { font-family: var(--font-dastkhat-fanum); }                   /* اعداد فارسی */
.logo   { font-family: var(--font-dastkhat-bar); font-weight: 900; }   /* نقطه‌های ادغام‌شده */
```

| متغیر | خانواده |
|---|---|
| `--font-dastkhat` | Dastkhat |
| `--font-dastkhat-diamond` | Dastkhat Diamond |
| `--font-dastkhat-bar` | Dastkhat Bar |
| `--font-dastkhat-fanum` | Dastkhat FaNum |

نام خانواده‌های متغیر `Dastkhat`، `Dastkhat Diamond` و `Dastkhat Bar` است (برای نسخه‌های دیگر، `FaNum` یا `NoEn` را به انتهای نام اضافه کنید). نسخه‌های ثابت همین نام‌ها را با پسوند `Static` دارند. همه قانون‌های `@font-face` از `font-display: swap` استفاده می‌کنند.

### ترکیب با فونت لاتین دیگر (NoEn)

```css
body { font-family: 'Dastkhat NoEn', 'Inter', sans-serif; }
```

دستخط NoEn حروف لاتین ندارد، پس مرورگر متن انگلیسی را با Inter نمایش می‌دهد.

### Next.js

```js
import localFont from 'next/font/local'

export const dastkhat = localFont({
  src: './Dastkhat-Variable.woff2',
  weight: '100 900',
  variable: '--font-dastkhat',
  display: 'swap',
})
```

### Tailwind CSS

در تنظیمات Tailwind، مقدار `fontFamily.sans` را برابر `var(--font-dastkhat)` قرار دهید.

### صفحه‌های راست‌به‌چپ

جهت و زبان را روی سند تعیین کنید تا علائم نگارشی و عددها درست نمایش داده شوند:

```html
<html lang="fa" dir="rtl">
```

### سرعت بارگذاری

- اگر از سه وزن یا بیشتر استفاده می‌کنید، WOFF2 متغیر را انتخاب کنید.
- فقط فایلی را پیش‌بارگذاری (preload) کنید که در بخش اول صفحه لازم است:
  ```html
  <link rel="preload" href="/Webfonts/fonts/Dastkhat-Variable.woff2" as="font" type="font/woff2" crossorigin>
  ```
- فایل‌ها را روی سرور خودتان قرار دهید و برای فونت به CDN شخص ثالث تکیه نکنید.

برای اطمینان از بارگذاری درست، فایل `Webfonts/webfont-test.html` را در مرورگر باز کنید.

## نکات تایپوگرافی

| بخش | پیشنهاد |
|---|---|
| متن بدنه | اندازه ۱۵ تا ۱۸ پیکسل، فاصله خطوط ۱٫۸ تا ۲ |
| تیتر | وزن ۷۰۰ تا ۹۰۰، فاصله خطوط ۱٫۲ تا ۱٫۳ |
| قیمت و جدول | نسخه FaNum |
| متن فارسی | **از `letter-spacing` استفاده نکنید.** اتصال حروف را می‌شکند. |

متن فارسی به‌خاطر کشیدگی بالای حروف و نقطه‌ها به فاصله خطوط بیشتری از لاتین نیاز دارد. اگر متن فشرده به نظر می‌رسد، به‌جای کوچک‌کردن اندازه، اول فاصله خطوط را زیاد کنید.

## پیش‌نمایش

| | |
|---|---|
| <img src="Demos/images/dastkhat-weights.png" alt="نه وزن"> | <img src="Demos/images/dastkhat-ui.png" alt="نمونه رابط کاربری"> |
| نه وزن | نمونه رابط کاربری |

نمونه‌های بیشتر را در `Demos/index.html`، تست‌کننده متن (`Demos/type-tester.html`) و نقشه حروف (`Demos/glyph-map.html`) ببینید. نمونه‌نامه کامل در `Specimen/Dastkhat-Specimen.pdf` قرار دارد.

## مجوز استفاده

دستخط یک **نرم‌افزار تجاری** است و با [قرارداد مجوز دستخط](License/EULA.fa.md) ارائه می‌شود. خرید مجوز: [dastyar.io](https://dastyar.io)

| مجوز | آنچه شامل می‌شود |
|---|---|
| **دسکتاپ** | نصب روی تعداد رایانه‌های رسید؛ چاپ، بسته‌بندی، ویدیو، تصویر، PDF و لوگو |
| **وب** | میزبانی فایل‌های WOFF2 روی دامنه‌های رسید و تا سقف بازدید ماهانه |
| **اپ / نرم‌افزار** | تعبیه در یک اپلیکیشن یا محصول مشخص |

| | |
|---|---|
| ❌ | کپی، اشتراک، فروش یا بازنشر فایل‌های فونت مجاز نیست |
| ❌ | تغییر فونت و ساخت نسخه مشتق مجاز نیست |
| ✅ | لوگو و طرح‌های تبدیل‌شده به منحنی یا تصویر بدون محدودیت قابل استفاده‌اند |

این فقط خلاصه است. متن کامل در [License/EULA.txt](License/EULA.txt) ملاک است. نسخه ۱٫۲۰۰ و قبل‌تر که با مجوز OFL منتشر شده‌اند، برای دریافت‌کنندگانشان همچنان تحت آن مجوز می‌مانند.

## سازندگان

- **دستیار** ([dastyar.io](https://dastyar.io)): سبک‌های نقطه، تغییرات و انتشار.
- **صابر راستی‌کردار**: طراح [وزیرمتن](https://github.com/rastikerdar/vazirmatn) که پایه دستخط است و با اجازه ایشان استفاده شده است.
- حروف لاتین از Roboto (مجوز Apache 2.0) گرفته شده است.

تاریخچه کامل تغییرات در [FONTLOG.txt](FONTLOG.txt) آمده است.

---

<div align="center">

© ۱۴۰۵ دستیار · [dastyar.io](https://dastyar.io)

</div>

</div>
