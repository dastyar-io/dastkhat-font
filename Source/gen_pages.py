"""Generate the Dastkhat release HTML pages. Usage: python3 -I gen_pages.py <package_dir> <build_dir>"""
import sys, os, json, html
import unicodedata as ud
from fontTools.ttLib import TTFont

PKG, BUILD = sys.argv[1], sys.argv[2]
os.makedirs(BUILD, exist_ok=True)
CSS_FONTS = os.path.join(PKG, 'Webfonts', 'dastkhat.css')
CSS_SITE = os.path.join(PKG, 'Demos', 'assets', 'site.css')

WEIGHTS = [(100, 'Thin'), (200, 'ExtraLight'), (300, 'Light'), (400, 'Regular'), (500, 'Medium'),
           (600, 'SemiBold'), (700, 'Bold'), (800, 'ExtraBold'), (900, 'Black')]
WEIGHT_FA = {100: 'نازک', 200: 'خیلی سبک', 300: 'سبک', 400: 'معمولی', 500: 'متوسط', 600: 'نیمه‌ضخیم',
             700: 'ضخیم', 800: 'خیلی ضخیم', 900: 'سیاه'}
FAMS = [('Dastkhat', 'مربع', 'نقطه‌های مربعی، پیش‌فرض برای رابط کاربری و متن'),
        ('Dastkhat Diamond', 'لوزی', 'مربع چرخیده ۴۵ درجه، ظاهری نرم‌تر و کلاسیک'),
        ('Dastkhat Bar', 'ادغام‌شده', 'دو نقطه یک خط، سه نقطه خط و مربع؛ برای لوگو و تیتر')]
PARA = ('دستخط برای صفحه‌هایی طراحی شده که هر روز خوانده می‌شوند: فروشگاه‌ها، داشبوردها، اپلیکیشن‌ها و '
        'دستیارهای هوشمند. بدنه بلندتر حروف، خوانایی را در اندازه‌های کوچک بالا می‌برد و نقطه‌های هندسی، '
        'به متن ظاهری منظم و امروزی می‌دهند. اعداد فارسی پهن‌تر شده‌اند تا قیمت‌ها و ارقام با یک نگاه خوانده شوند.')
PANGRAM = 'ژرف‌اندیشی، پیگیری صبورانه و ذوق، ضامن خلق طرح‌هایی است که چشم را غافلگیر می‌کنند.'
DOTS = 'تث ش چ پ ق ئة بیتی'
KEYWORDS = ['دستیار', 'ایجنت', 'دستیار هوشمند خلاق', 'هوشنگ', 'هوش مصنوعی']
KW_LINE = 'هوشنگ، دستیار هوشمند خلاق و ایجنت هوش مصنوعی شما'

def kw_grid(size=44, weight=700):
    head = ''.join(f'<div class="kwh" style="font-family:\'{f}\'">{fa}</div>' for f, fa, _ in FAMS)
    rows = ''.join(f'<div class="kwr">' + ''.join(f'<div style="font-family:\'{f}\';font-size:{size}px;font-weight:{weight}">{k}</div>' for f, _, _ in FAMS) + '</div>' for k in KEYWORDS)
    return f'<div class="kw"><div class="kwr kwhead">{head}</div>{rows}</div>'
KW_CSS = '.kw{margin-top:24px;border:1px solid var(--line);border-radius:18px;overflow:hidden;background:#fff}.kwr{display:grid;grid-template-columns:repeat(3,1fr);border-bottom:1px solid var(--line)}.kwr:last-child{border:0}.kwr>div{padding:14px 22px;line-height:1.5}.kwr>div+div{border-inline-start:1px solid var(--line)}.kwhead{background:var(--primary-soft)}.kwhead div{font-size:15px;font-weight:700;color:var(--primary)}'

# ---------- glyph inventory ----------
cmap = TTFont(os.path.join(PKG, 'Fonts/Main/Dastkhat/TTF/Dastkhat-Regular.ttf')).getBestCmap()
cps = sorted(cmap)
def chars(pred):
    return [chr(c) for c in cps if pred(c)]
GLYPH_GROUPS = [
    ('حروف فارسی', 'Persian letters', list('ابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی') + list('آأإؤئءةۀ')),
    ('حروف عربی و گسترده', 'Arabic & extended', [ch for ch in chars(lambda c: (0x621 <= c <= 0x6D5) and ud.category(chr(c)).startswith('L'))
                                                if ch not in 'ابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهیآأإؤئءةۀ']),
    ('اعداد', 'Numerals', list('۰۱۲۳۴۵۶۷۸۹') + list('٠١٢٣٤٥٦٧٨٩') + list('0123456789')),
    ('نشانه‌ها', 'Punctuation & signs', list('،؛؟٪٫٬«»()[]{}!?.,:;-–—/\\@#&*+=<>%$€£¥﷼') + ['ـ']),
    ('حروف لاتین', 'Latin', chars(lambda c: 0x41 <= c <= 0x5A or 0x61 <= c <= 0x7A) +
     chars(lambda c: 0xC0 <= c <= 0x17F and ud.category(chr(c)).startswith('L'))),
]
GLYPH_GROUPS = [(a, b, [ch for ch in g if ord(ch) in cmap]) for a, b, g in GLYPH_GROUPS]
TOTAL_GLYPHS = 1333
faN = lambda n: ''.join('۰۱۲۳۴۵۶۷۸۹'[int(d)] for d in str(n))


def page(title, body, rel_css='../Webfonts/dastkhat.css', rel_site='../Demos/assets/site.css', extra_css='', dir_='rtl', script=''):
    return f'''<!DOCTYPE html>
<html lang="fa" dir="{dir_}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="{rel_css}"><link rel="stylesheet" href="{rel_site}">
<style>{extra_css}</style></head><body>
{body}
<script>{script}</script>
</body></html>'''


def nav(active=''):
    links = [('index.html', 'معرفی'), ('type-tester.html', 'تست متن'), ('glyph-map.html', 'نقشه حروف'),
             ('ui-demo.html', 'نمونه رابط'), ('poster.html', 'پوستر')]
    a = ''.join(f'<a href="{h}" style="{"color:var(--primary)" if h == active else ""}">{t}</a>' for h, t in links)
    return f'<div class="wrap"><div class="nav"><div class="brand">دستخط<span></span></div><div>{a}</div></div></div>'


FOOT = ('<div class="wrap"><div class="foot"><span>© ۱۴۰۵ دستیار · dastyar.io</span>'
        '<span dir="ltr">Dastkhat · SIL OFL 1.1</span></div></div>')


def write(rel, content):
    p = os.path.join(PKG, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w').write(content)


# =========================================================== index.html (product page)
def index_page():
    weights = ''.join(f'''<div class="wrow"><span class="lbl">{w} {s}</span><span class="wfa">{WEIGHT_FA[w]}</span>
      <p style="font-weight:{w}">دستیار هوشمند خلاق · Dastkhat</p></div>''' for w, s in WEIGHTS)
    fams = ''.join(f'''<div class="card fam"><div class="lbl">{f}</div>
      <div class="fam-big" style="font-family:'{f}'">تث شق</div>
      <h3>{fa}</h3><p class="lead" style="font-size:15px">{d}</p></div>''' for f, fa, d in FAMS)
    glyphs = ''.join(f'<span>{html.escape(c)}</span>' for c in GLYPH_GROUPS[0][2])
    css = '''
.hero{padding:80px 0 60px;display:grid;grid-template-columns:1.2fr 1fr;gap:40px;align-items:end;border-bottom:1px solid var(--line)}
.hero h1{font-size:200px;font-weight:900;line-height:1;letter-spacing:-.02em}
.hero h1 em{font-style:normal;color:var(--primary)}
.hero .meta{display:grid;grid-template-columns:1fr 1fr;gap:14px 30px;margin-top:30px}
.hero .meta b{display:block;font-size:30px;font-weight:800}
.hero .meta span{color:var(--mute);font-size:14px}
.tester{background:var(--ink);color:#fff;border-radius:22px;padding:34px;margin-top:40px}
.tester .bar{display:flex;gap:16px;align-items:center;flex-wrap:wrap;margin-bottom:20px}
.tester .seg{background:#2A2725}.tester .seg button{color:#fff}.tester .seg button.on{background:var(--secondary);color:var(--on-secondary)}
.tester label{color:#bbb;font-size:14px;display:flex;gap:10px;align-items:center}
#live{font-size:64px;line-height:1.5;outline:none;min-height:120px}
.fams{grid-template-columns:repeat(3,1fr);margin-top:30px}
.fam-big{font-size:84px;white-space:nowrap;line-height:1.3;margin:10px 0}
.wrow{display:grid;grid-template-columns:180px 120px 1fr;align-items:baseline;border-bottom:1px solid var(--line);padding:12px 0}
.wrow p{margin:0;font-size:38px}.wfa{color:var(--mute);font-size:14px}.wrow .lbl{text-align:right}
.feat{grid-template-columns:repeat(4,1fr);margin-top:30px}
.feat .card b{font-size:46px;font-weight:900;color:var(--primary);display:block}
.gl{display:grid;grid-template-columns:repeat(auto-fill,minmax(76px,1fr));gap:8px;margin-top:24px}
.gl span{background:var(--card);border:1px solid var(--line);border-radius:10px;aspect-ratio:1;display:flex;align-items:center;justify-content:center;font-size:40px}
.lic{grid-template-columns:1fr 1fr}
.lic li{margin:6px 0}
.dl{background:var(--secondary);border-radius:22px;padding:44px;display:flex;justify-content:space-between;align-items:center}
.dl h2{font-size:44px;font-weight:900;color:var(--on-secondary)}
'''
    body = nav('index.html') + f'''
<div class="wrap">
 <div class="hero">
  <div><span class="pill">نسخه ۱٫۲۰۰ · متن‌باز (OFL)</span>
   <h1>دستخط</h1>
   <p class="lead">فونتی فارسی و لاتین برای رابط‌های کاربری امروز؛ با بدنه بلندتر، نقطه‌های هندسی و سه سبک نقطه، از طرف دستیار.</p>
   <div style="display:flex;gap:12px;margin-top:24px"><a class="btn" href="#download">دانلود رایگان</a><a class="btn alt" href="type-tester.html">تست متن</a></div>
  </div>
  <div class="meta">
   <div><b>۹</b><span>وزن، از نازک تا سیاه</span></div>
   <div><b>۳</b><span>سبک نقطه</span></div>
   <div><b>متغیر</b><span>محور وزن ۱۰۰ تا ۹۰۰</span></div>
   <div><b>۸۱۱</b><span>نویسه یونیکد</span></div>
  </div>
 </div>
 <div class="tester">
  <div class="bar">
   <div class="seg" id="fam"><button class="on" data-f="Dastkhat">مربع</button><button data-f="Dastkhat Diamond">لوزی</button><button data-f="Dastkhat Bar">ادغام‌شده</button></div>
   <label>وزن <input type="range" id="w" min="100" max="900" value="700"><span id="wv">۷۰۰</span></label>
   <label>اندازه <input type="range" id="s" min="20" max="140" value="64"></label>
  </div>
  <div id="live" contenteditable="true" spellcheck="false" style="font-weight:700">دستیار هوشمند خلاق</div>
 </div>
</div>
<div class="sec"><div class="wrap"><h2>سه سبک نقطه</h2><p class="lead">یک فونت، سه شخصیت. هر سه خانواده وزن‌ها و فاصله‌گذاری یکسان دارند و می‌توانید بدون جابه‌جایی متن، بینشان جابه‌جا شوید.</p>
 <div class="grid fams">{fams}</div></div></div>
<div class="sec"><div class="wrap"><h2>کلیدواژه‌های تست</h2><p class="lead">پنج واژه پرکاربرد محصولات دستیار در هر سه سبک نقطه.</p>{kw_grid(30, 800)}</div></div>
<div class="sec"><div class="wrap"><h2>۹ وزن</h2><p class="lead">از نازک برای تیترهای ظریف تا سیاه برای بنرها، به‌همراه نسخه متغیر برای هر وزن دلخواه بین ۱۰۰ تا ۹۰۰.</p>
 <div style="margin-top:24px">{weights}</div></div></div>
<div class="sec"><div class="wrap"><h2>برای خوانایی ساخته شده</h2>
 <div class="grid feat">
  <div class="card"><b>+۱۸٪</b>بدنه بلندتر حروف برای خوانایی در اندازه‌های کوچک</div>
  <div class="card"><b>۷٪</b>اعداد فارسی پهن‌تر برای قیمت‌ها و داده‌ها</div>
  <div class="card"><b>FaNum</b>اعداد لاتین به‌صورت فارسی، بدون تغییر در کد</div>
  <div class="card"><b>NoEn</b>نسخه فقط فارسی برای ترکیب با فونت لاتین دلخواه</div>
 </div>
 <p style="font-size:22px;line-height:2.1;max-width:900px;margin-top:40px">{PARA}</p></div></div>
<div class="sec"><div class="wrap"><h2>حروف</h2><p class="lead">پوشش کامل فارسی و عربی، اعداد سه‌گانه و لاتین. <a href="glyph-map.html">نقشه کامل حروف ←</a></p>
 <div class="gl">{glyphs}</div></div></div>
<div class="sec"><div class="wrap"><h2>مجوز استفاده</h2>
 <div class="grid lic" style="margin-top:20px">
  <div class="card"><h3>آزادی‌ها</h3><ul>
   <li>استفاده رایگان در وب، اپ، چاپ، ویدیو و لوگو</li><li>مناسب کار شخصی، مشتری و محصول تجاری</li>
   <li>تغییر و انتشار نسخه تغییریافته با همین مجوز</li></ul></div>
  <div class="card"><h3>شرط‌ها</h3><ul>
   <li>فروش خود فایل‌های فونت به‌تنهایی مجاز نیست</li><li>مجوز SIL OFL 1.1 باید همراه فونت بماند</li>
   <li>متن کامل در فایل OFL.txt</li></ul></div>
 </div></div></div>
<div class="sec" id="download" style="border:0"><div class="wrap"><div class="dl">
 <div><h2>دستخط را دانلود کنید</h2><p style="color:var(--on-secondary);margin:6px 0 0">TTF · Variable · WOFF2 · FaNum · NoEn</p></div>
 <a class="btn" href="../">بسته کامل ←</a></div></div></div>
''' + FOOT
    script = '''
const live=document.getElementById('live'),w=document.getElementById('w'),wv=document.getElementById('wv'),s=document.getElementById('s');
const fa=n=>String(n).replace(/\\d/g,d=>'۰۱۲۳۴۵۶۷۸۹'[d]);
w.oninput=()=>{live.style.fontWeight=w.value;wv.textContent=fa(w.value)};
s.oninput=()=>{live.style.fontSize=s.value+'px'};
document.querySelectorAll('#fam button').forEach(b=>b.onclick=()=>{document.querySelectorAll('#fam button').forEach(x=>x.classList.remove('on'));b.classList.add('on');live.style.fontFamily="'"+b.dataset.f+"'"});
'''
    write('Demos/index.html', page('دستخط · Dastkhat', body, extra_css=css + KW_CSS, script=script))


# =========================================================== type tester
def tester_page():
    css = '''
.ctl{display:flex;gap:18px;flex-wrap:wrap;align-items:center;padding:22px 0;border-bottom:1px solid var(--line);position:sticky;top:0;background:var(--paper);z-index:2}
.ctl label{display:flex;gap:8px;align-items:center;font-size:14px;color:var(--mute)}
select{font-family:inherit;font-size:15px;padding:8px 10px;border-radius:10px;border:1px solid var(--line);background:#fff}
.t{outline:none;padding:30px 0;border-bottom:1px solid var(--line);line-height:1.6}
.wf div{white-space:nowrap;overflow:hidden;line-height:1.5}
'''
    opts = ''.join(f'<option value="{f}{s}">{f}{s}</option>' for f, _, _ in FAMS for s in ['', ' FaNum', ' NoEn'])
    wf = ''.join(f'<div style="font-size:{s}px"><span class="lbl" style="font-size:11px;display:inline-block;width:60px">{s}px</span> {KW_LINE}</div>'
                 for s in [12, 14, 16, 20, 24, 32, 48, 64, 96])
    body = nav('type-tester.html') + f'''<div class="wrap">
<div class="ctl">
 <label>خانواده <select id="fam">{opts}</select></label>
 <label>وزن <input type="range" id="w" min="100" max="900" value="400"><b id="wv">400</b></label>
 <label>اندازه <input type="range" id="s" min="12" max="160" value="56"><b id="sv">56</b></label>
 <label>فاصله خطوط <input type="range" id="lh" min="10" max="30" value="18"></label>
 <label>رنگ <div class="seg" id="th"><button class="on" data-t="l">روشن</button><button data-t="d">تیره</button></div></label>
</div>
<div id="area">
<div class="t" contenteditable="true" spellcheck="false" id="big">دستیار، ایجنت، هوشنگ، هوش مصنوعی</div>
<div class="t" contenteditable="true" spellcheck="false" id="para" style="font-size:20px;line-height:2">{PARA}</div>
<div class="t"><div class="lbl">Keyword test · تست کلیدواژه‌ها</div>{kw_grid(30, 400)}</div>
<div class="t wf">{wf}</div>
</div></div>''' + FOOT
    script = '''
const $=id=>document.getElementById(id),area=$('area');
const apply=()=>{area.style.fontFamily="'"+$('fam').value+"'";area.style.fontWeight=$('w').value;$('wv').textContent=$('w').value;
$('big').style.fontSize=$('s').value+'px';$('sv').textContent=$('s').value;$('para').style.lineHeight=$('lh').value/10;};
['fam','w','s','lh'].forEach(i=>$(i).oninput=apply);apply();
document.querySelectorAll('#th button').forEach(b=>b.onclick=()=>{document.querySelectorAll('#th button').forEach(x=>x.classList.remove('on'));b.classList.add('on');
const d=b.dataset.t=='d';document.body.style.background=d?'#151312':'';document.body.style.color=d?'#F5F2EC':'';document.querySelector('.ctl').style.background=d?'#151312':''});
'''
    write('Demos/type-tester.html', page('دستخط · تست متن', body, extra_css=css + KW_CSS, script=script))


# =========================================================== glyph map
def glyph_page():
    css = '''
.g{display:grid;grid-template-columns:repeat(auto-fill,minmax(92px,1fr));gap:8px;margin:18px 0 40px}
.g div{background:#fff;border:1px solid var(--line);border-radius:10px;aspect-ratio:1;display:flex;flex-direction:column;align-items:center;justify-content:center;cursor:pointer;transition:.15s}
.g div:hover{border-color:var(--primary);transform:translateY(-2px)}
.g b{font-size:44px;font-weight:400;line-height:1.3}.g small{font-family:ui-monospace,monospace;font-size:10px;color:var(--mute)}
#zoom{position:fixed;inset:auto 30px 30px auto;background:var(--ink);color:#fff;border-radius:18px;padding:20px 30px;text-align:center;min-width:220px;display:none}
#zoom b{font-size:140px;line-height:1.2;display:block}
.forms{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:8px;margin:18px 0 40px}
.forms div{background:#fff;border:1px solid var(--line);border-radius:10px;padding:14px;text-align:center;font-size:38px}
.forms small{display:block;font-size:12px;color:var(--mute)}
'''
    secs = ''
    for fa, en, gl in GLYPH_GROUPS:
        cells = ''.join(f'<div data-c="{html.escape(c)}" data-u="U+{ord(c):04X}"><b>{html.escape(c)}</b><small>{ord(c):04X}</small></div>' for c in gl)
        secs += f'<h2 style="font-size:28px;margin-top:40px">{fa} <span class="lbl">{en} · {len(gl)}</span></h2><div class="g">{cells}</div>'
    letters = 'ب ت ث پ ج چ ح خ س ش ص ض ط ظ ع غ ف ق ک گ ل م ن ه ی'.split()
    ZW = '‍'
    forms = ''.join(f'<div>{c} {c}{ZW} {ZW}{c}{ZW} {ZW}{c}<small>جدا · آغازی · میانی · پایانی</small></div>' for c in letters)
    body = nav('glyph-map.html') + f'''<div class="wrap" style="padding-top:40px">
<h1 style="font-size:56px;font-weight:900">نقشه حروف</h1>
<p class="lead">{faN(len(cps))} نویسه یونیکد و {faN(TOTAL_GLYPHS)} گلیف. روی هر حرف کلیک کنید تا بزرگ دیده شود.</p>
<div class="seg" id="fam" style="margin-top:14px"><button class="on" data-f="Dastkhat">مربع</button><button data-f="Dastkhat Diamond">لوزی</button><button data-f="Dastkhat Bar">ادغام‌شده</button></div>
<div id="all">{secs}
<h2 style="font-size:28px">شکل‌های اتصال <span class="lbl">Contextual forms</span></h2><div class="forms">{forms}</div></div>
</div><div id="zoom"><b></b><span class="lbl"></span></div>''' + FOOT
    script = '''
const z=document.getElementById('zoom');document.querySelectorAll('.g div').forEach(d=>d.onclick=()=>{z.style.display='block';z.querySelector('b').textContent=d.dataset.c;z.querySelector('.lbl').textContent=d.dataset.u});
z.onclick=()=>z.style.display='none';
document.querySelectorAll('#fam button').forEach(b=>b.onclick=()=>{document.querySelectorAll('#fam button').forEach(x=>x.classList.remove('on'));b.classList.add('on');document.getElementById('all').style.fontFamily="'"+b.dataset.f+"'";z.style.fontFamily="'"+b.dataset.f+"'"});
'''
    write('Demos/glyph-map.html', page('دستخط · نقشه حروف', body, extra_css=css, script=script))


# =========================================================== UI demo (app + shop)
UI_CSS = '''
.ui{display:grid;grid-template-columns:1.1fr 1fr;gap:28px;padding:40px 0}
.app{background:#121110;color:#EDE9E2;border-radius:24px;overflow:hidden;box-shadow:0 30px 60px -30px #0006}
.app .top{display:flex;justify-content:space-between;align-items:center;padding:18px 22px;border-bottom:1px solid #2a2725}
.app .top b{font-weight:800}
.dot{width:10px;height:10px;border-radius:3px;background:var(--secondary);display:inline-block;margin-inline-start:8px}
.msgs{padding:22px;display:flex;flex-direction:column;gap:14px;min-height:430px}
.m{max-width:80%;padding:14px 18px;border-radius:16px;font-size:16px;line-height:1.9}
.m.u{align-self:flex-start;background:var(--primary);color:#fff;border-end-start-radius:4px}
.m.a{align-self:flex-end;background:#221F1D;border-end-end-radius:4px}
.m.a ul{margin:6px 0 0;padding-inline-start:18px}
.chips{display:flex;gap:8px;flex-wrap:wrap;padding:0 22px 14px}
.chips span{border:1px solid #3a3634;border-radius:999px;padding:6px 14px;font-size:13px;color:#cfc8bf}
.inp{margin:0 22px 22px;background:#1C1A18;border-radius:14px;padding:14px 18px;color:#8a837b;display:flex;justify-content:space-between}
.inp i{font-style:normal;background:var(--secondary);color:var(--on-secondary);border-radius:9px;padding:2px 12px;font-weight:700}
.shop{display:flex;flex-direction:column;gap:20px}
.prod{background:#fff;border:1px solid var(--line);border-radius:22px;padding:22px;display:grid;grid-template-columns:150px 1fr;gap:20px;align-items:center}
.ph{aspect-ratio:1;border-radius:16px;background:linear-gradient(135deg,#EFE9DF,#DDD5C8);display:flex;align-items:center;justify-content:center;font-size:56px;font-weight:900;color:var(--primary)}
.prod h3{font-size:20px;font-weight:700}
.tag{display:inline-block;background:var(--primary-soft);color:var(--primary);border-radius:8px;padding:2px 10px;font-size:13px;font-weight:700}
.price{font-family:'Dastkhat FaNum';font-size:30px;font-weight:900}
.old{font-family:'Dastkhat FaNum';color:var(--mute);text-decoration:line-through;font-size:16px;margin-inline-start:10px}
.stat{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.stat div{background:#fff;border:1px solid var(--line);border-radius:18px;padding:18px}
.stat b{font-family:'Dastkhat FaNum';font-size:34px;font-weight:900;display:block;line-height:1.3}
.stat small{color:var(--mute)}
.stat .up{color:#2D7A3E;font-size:13px;font-weight:700}
.banner{background:var(--primary);color:#fff;border-radius:22px;padding:26px;display:flex;justify-content:space-between;align-items:center}
.banner h3{font-family:'Dastkhat Bar';font-size:40px;font-weight:900}
'''
UI_BODY = '''<div class="ui">
 <div class="app">
  <div class="top"><b>دستیار<span class="dot"></span></b><span style="color:#8a837b;font-size:13px">مدل: هوشنگ ۲</span></div>
  <div class="msgs">
   <div class="m u">یک خلاصه از جلسه امروز و کارهای باقی‌مانده بنویس</div>
   <div class="m a">خلاصه جلسه محصول، ۱۷ آبان:
    <ul><li>نسخه جدید افزونه پنجشنبه منتشر می‌شود</li><li>فونت دستخط در همه صفحه‌ها جایگزین می‌شود</li><li>گزارش رشد کاربران تا شنبه آماده شود</li></ul></div>
   <div class="m u">برای هر کار یک یادآور بساز</div>
   <div class="m a">سه یادآور ساخته شد ✓ اولی فردا ساعت ۹ صبح است.</div>
  </div>
  <div class="chips"><span>ترجمه کن</span><span>ایمیل بنویس</span><span>خلاصه کن</span><span>جدول بساز</span></div>
  <div class="inp">از دستیار بپرسید…<i>ارسال</i></div>
 </div>
 <div class="shop">
  <div class="banner"><div><h3>جشنواره پاییز</h3><span>تا ۴۰٪ تخفیف روی همه اشتراک‌ها</span></div><span class="pill">کد: DASTKHAT</span></div>
  <div class="prod"><div class="ph">پ</div><div><span class="tag">۲۵٪ تخفیف</span><h3 style="margin-top:8px">اشتراک یک‌ساله دستیار پرو</h3>
   <p style="margin:4px 0;color:var(--mute);font-size:14px">دسترسی نامحدود به همه مدل‌ها و ابزارها</p>
   <span class="price">1,490,000</span><span style="font-weight:700"> تومان</span><span class="old">1,990,000</span></div></div>
  <div class="stat">
   <div><small>کاربران فعال</small><b>128,400</b><span class="up">▲ 12.4%</span></div>
   <div><small>پیام امروز</small><b>2.3M</b><span class="up">▲ 8.1%</span></div>
   <div><small>رضایت</small><b>4.8</b><span class="up">از ۵</span></div>
  </div>
 </div>
</div>'''


def ui_page():
    body = nav('ui-demo.html') + '<div class="wrap"><h1 style="font-size:56px;font-weight:900;margin-top:40px">دستخط در رابط کاربری</h1>' \
        '<p class="lead">یک دستیار گفتگو و یک کارت فروشگاهی. قیمت‌ها با نسخه FaNum نوشته شده‌اند: عدد لاتین در کد، عدد فارسی روی صفحه.</p>' \
        + UI_BODY + '</div>' + FOOT
    write('Demos/ui-demo.html', page('دستخط · نمونه رابط', body, extra_css=UI_CSS))


# =========================================================== poster
POSTER_CSS = '''
.poster{width:1080px;height:1350px;background:var(--primary);color:#fff;position:relative;overflow:hidden;margin:0 auto}
.poster .big{font-family:'Dastkhat Bar';font-weight:900;font-size:280px;line-height:1.1;position:absolute;right:60px;top:170px}
.poster .big2{font-family:'Dastkhat Bar';font-weight:100;font-size:280px;line-height:1.1;position:absolute;right:60px;top:530px;color:#FFFFFF}
.poster .meta{position:absolute;right:60px;left:60px;bottom:60px;display:flex;justify-content:space-between;align-items:flex-end;font-size:22px}
.poster .meta b{font-size:56px;font-weight:900;display:block;line-height:1.2}
.poster .ptag{position:absolute;top:60px;right:60px;left:60px;display:flex;justify-content:space-between;font-size:20px}
.poster .sq{width:110px;height:110px;background:var(--secondary);position:absolute;left:60px;top:930px}
'''
POSTER_BODY = '''<div class="poster">
 <div class="ptag"><span>دستیار معرفی می‌کند</span><span class="ltr">Dastkhat v1.200</span></div>
 <div class="sq"></div>
 <div class="big">دستخط</div>
 <div class="big2">دستخط</div>
 <div class="meta"><div><b>۹ وزن · ۳ سبک نقطه</b>فونت فارسی برای رابط‌های امروز</div><div class="ltr" style="text-align:left">SIL OFL 1.1<br>dastyar.io</div></div>
</div>'''


def poster_page():
    body = nav('poster.html') + f'<div style="padding:40px 0">{POSTER_BODY}</div>' + FOOT
    write('Demos/poster.html', page('دستخط · پوستر', body, extra_css=POSTER_CSS))


# =========================================================== webfont test
def webfont_test():
    rows = ''
    for f, _, _ in FAMS:
        for s in ['', ' FaNum', ' NoEn']:
            fam = f + s
            kw = KEYWORDS[len(rows) % 5] if False else ''
            rows += f'<div class="r"><div class="lbl">{fam}</div><p style="font-family:\'{fam}\'">دستیار · ایجنت · هوشنگ · هوش مصنوعی · 1,250,000 · Dastkhat</p>' \
                    f'<p class="st" style="font-family:\'{fam} Static\';font-weight:700">دستیار هوشمند خلاق · Static Bold 2026</p></div>'
    css = '.r{padding:16px 0;border-bottom:1px solid var(--line)}.r p{margin:4px 0;font-size:30px}.r .st{font-size:22px;color:var(--mute)}'
    body = f'''<div class="wrap" style="padding:40px"><h1 style="font-size:44px;font-weight:900">تست وب‌فونت دستخط</h1>
<p class="lead">اگر همه خطوط زیر با دستخط نمایش داده شوند، فایل dastkhat.css و پوشه fonts درست کار می‌کنند. در نسخه FaNum عددهای لاتین فارسی دیده می‌شوند و در NoEn متن انگلیسی با فونت جایگزین.</p>
<pre class="ltr" style="background:#151312;color:#8AB4F8;padding:18px;border-radius:12px;font-size:14px">&lt;link rel="stylesheet" href="dastkhat.css"&gt;
body {{ font-family: var(--font-dastkhat); }}</pre>{rows}</div>'''
    write('Webfonts/webfont-test.html', page('Dastkhat Webfont Test', body, rel_css='dastkhat.css', rel_site='../Demos/assets/site.css', extra_css=css))


# =========================================================== help guide
def help_page():
    css = '''
.doc{max-width:900px;margin:0 auto;padding:50px 40px}
.doc h1{font-size:46px;font-weight:900}.doc h2{font-size:28px;margin:44px 0 10px;padding-top:20px;border-top:1px solid var(--line)}
.doc ol li,.doc ul li{margin:8px 0}
pre{background:#151312;color:#8AB4F8;padding:18px;border-radius:12px;font-size:14px;direction:ltr;text-align:left;overflow:auto}
.en{direction:ltr;text-align:left;font-family:'Dastkhat',sans-serif}
table{border-collapse:collapse;width:100%}td,th{border:1px solid var(--line);padding:10px;text-align:start}
'''
    body = f'''<div class="doc">
<span class="pill">راهنما · Guide</span>
<h1>نصب و استفاده از دستخط</h1>
<p class="lead">این راهنما نصب فونت روی ویندوز، مک و لینوکس، استفاده در وب و نرم‌افزارهای طراحی و انتخاب نسخه مناسب را توضیح می‌دهد.</p>

<h2>کدام نسخه را نصب کنم؟</h2>
<table><tr><th>نیاز شما</th><th>نسخه پیشنهادی</th></tr>
<tr><td>طراحی در فیگما، فتوشاپ، ایلاستریتور</td><td>Fonts/Main ← پوشه TTF (۹ وزن)</td></tr>
<tr><td>طراحی با کنترل دقیق وزن</td><td>Fonts/Main ← پوشه Variable</td></tr>
<tr><td>وب‌سایت و اپلیکیشن وب</td><td>پوشه Webfonts</td></tr>
<tr><td>عدد فارسی بدون تغییر کد یا تنظیمات</td><td>Fonts/FaNum</td></tr>
<tr><td>ترکیب با فونت لاتین دیگر (مثلاً Inter یا Geist)</td><td>Fonts/NoEn</td></tr></table>
<p>روی یک سیستم، یا نسخه ثابت (TTF) را نصب کنید یا نسخه متغیر، نه هر دو؛ نام‌های یکسان باعث تداخل در نرم‌افزارها می‌شود.</p>

<h2>ویندوز</h2><ol><li>پوشه Fonts/Main/Dastkhat/TTF را باز کنید.</li><li>همه فایل‌ها را انتخاب کنید (Ctrl+A).</li><li>راست‌کلیک کنید و گزینه Install for all users را بزنید.</li><li>نرم‌افزار طراحی را یک بار ببندید و دوباره باز کنید.</li></ol>
<h2>مک</h2><ol><li>برنامه Font Book را باز کنید.</li><li>فایل‌های TTF را به داخل پنجره بکشید.</li><li>اگر هشدار تکراری بودن دیدید، نسخه قبلی دستخط را حذف کنید.</li></ol>
<h2>لینوکس</h2><pre>mkdir -p ~/.local/share/fonts/Dastkhat
cp Fonts/Main/Dastkhat/TTF/*.ttf ~/.local/share/fonts/Dastkhat/
fc-cache -f</pre>

<h2>وب</h2>
<p>پوشه Webfonts را در پروژه کپی کنید و فایل CSS را اضافه کنید. نسخه متغیر کم‌حجم‌تر است و همه وزن‌ها را در یک فایل دارد.</p>
<pre>&lt;link rel="stylesheet" href="/Webfonts/dastkhat.css"&gt;

body      {{ font-family: var(--font-dastkhat); }}          /* نقطه مربع */
.price    {{ font-family: var(--font-dastkhat-fanum); }}    /* اعداد فارسی */
.logo     {{ font-family: var(--font-dastkhat-bar); font-weight: 900; }}</pre>
<p>برای Next.js با next/font/local:</p>
<pre>import localFont from 'next/font/local'
export const dastkhat = localFont({{
  src: './Dastkhat-Variable.woff2',
  weight: '100 900',
  variable: '--font-dastkhat',
  display: 'swap',
}})</pre>
<p>در Tailwind کافی است در تنظیمات، fontFamily.sans را برابر var(--font-dastkhat) قرار دهید.</p>

<h2>نسخه FaNum</h2><p>در این نسخه، عددهای لاتین ۰ تا ۹ با شکل فارسی نمایش داده می‌شوند. داده‌ها و کد شما بدون تغییر می‌مانند و فقط ظاهر عوض می‌شود. برای قیمت، جدول و داشبورد مناسب است.</p>
<h2>نسخه NoEn</h2><p>حروف لاتین در این نسخه حذف شده‌اند تا مرورگر برای متن انگلیسی از فونت بعدی در لیست استفاده کند:</p>
<pre>font-family: 'Dastkhat NoEn', 'Inter', sans-serif;</pre>

<h2>فاصله‌گذاری پیشنهادی</h2><ul><li>متن بدنه: اندازه ۱۵ تا ۱۸ پیکسل، فاصله خطوط ۱٫۸ تا ۲</li><li>تیتر: وزن ۷۰۰ تا ۹۰۰، فاصله خطوط ۱٫۲ تا ۱٫۳</li><li>از letter-spacing روی متن فارسی استفاده نکنید؛ اتصال حروف را می‌شکند.</li></ul>

<div class="en">
<h2>English quick guide</h2>
<ul><li><b>Desktop:</b> install the TTF files from <code>Fonts/Main/&lt;Family&gt;/TTF</code>, or the variable font, not both.</li>
<li><b>Web:</b> copy <code>Webfonts/</code>, link <code>dastkhat.css</code>, use <code>var(--font-dastkhat)</code>.</li>
<li><b>FaNum:</b> Latin digits render as Persian digits. <b>NoEn:</b> Persian only, pair it with your own Latin font.</li>
<li><b>License:</b> SIL Open Font License 1.1, free for personal and commercial use. See <code>OFL.txt</code>.</li></ul></div>
</div>''' + FOOT
    write('Helps/guide.html', page('راهنمای دستخط', body, extra_css=css))



# =========================================================== specimen (PDF source)
def specimen_doc():
    css = '''
@page{size:297mm 210mm;margin:0}
body{background:#fff}
.s{width:297mm;height:210mm;padding:16mm 18mm;position:relative;page-break-after:always;overflow:hidden;background:var(--paper)}
.s .hd{display:flex;justify-content:space-between;font-size:12px;color:var(--mute);border-bottom:1px solid var(--line);padding-bottom:6px}
.s .ft{position:absolute;bottom:10mm;right:18mm;left:18mm;display:flex;justify-content:space-between;font-size:11px;color:var(--mute)}
.cover{background:var(--primary);color:#fff}
.cover .ft,.cover .hd{color:#ffffffaa;border-color:#ffffff33}
.ttl{font-size:46px;font-weight:900;margin:16px 0 4px}
.wl{display:grid;grid-template-columns:62mm 1fr;align-items:baseline;border-bottom:1px solid var(--line);padding:2.3mm 0}.wl .lbl{text-align:right;white-space:nowrap}
.wfr{display:grid;grid-template-columns:16mm 1fr;align-items:baseline;line-height:1.45}.wfr div{white-space:nowrap;overflow:hidden}
.wl p{margin:0;font-size:30px;line-height:1.3}
.cols{display:grid;grid-template-columns:repeat(3,1fr);gap:8mm;margin-top:8mm}
.gg{display:flex;flex-wrap:wrap;gap:3mm 6mm;font-size:30px;line-height:1.5}
'''
    W = lambda s: f'<div class="s{" " + s if s else ""}">'
    hd = lambda t: f'<div class="hd"><span>دستخط · نمونه‌نامه</span><span>{t}</span></div>'
    ft = lambda n: f'<div class="ft"><span>Dastkhat v1.200 · Dastyar</span><span class="ltr">{len(pages) + 1:02d}</span></div>'
    pages = []
    pages.append(W('cover') + hd('۱۴۰۵') + '''<div style="font-family:'Dastkhat Bar';font-weight:900;font-size:230px;line-height:1;margin-top:18mm">دستخط</div>
<div style="display:flex;justify-content:space-between;align-items:flex-end;margin-top:10mm">
<div style="font-size:22px;max-width:150mm">فونت فارسی و لاتین برای رابط‌های کاربری<br><b>۹ وزن · ۳ سبک نقطه · نسخه متغیر</b></div>
<div style="width:34mm;height:34mm;background:var(--secondary)"></div></div>''' + ft('01') + '</div>')
    fams = ''.join(f'''<div><div class="lbl">{f}</div><div style="font-family:'{f}';font-size:92px;line-height:1.25;margin:4mm 0">تث شق</div>
<div style="font-family:'{f}';font-size:30px;line-height:1.6">{DOTS}</div><p style="font-size:14px;color:var(--mute)">{d}</p></div>''' for f, fa, d in FAMS)
    pages.append(W('') + hd('سبک نقطه‌ها') + f'<div class="ttl">سه سبک نقطه</div><div class="cols">{fams}</div>' + ft('02') + '</div>')
    kwrows = ''.join(f'<div style="display:grid;grid-template-columns:repeat(3,1fr);border-bottom:1px solid var(--line);padding:2mm 0">' + ''.join(f'<div style="font-family:\'{f}\';font-size:30px;font-weight:700;line-height:1.4;white-space:nowrap">{k}</div>' for f, _, _ in FAMS) + '</div>' for k in KEYWORDS)
    kwhead = '<div style="display:grid;grid-template-columns:repeat(3,1fr);margin-top:4mm">' + ''.join(f'<div class="lbl" style="text-align:right">{f}</div>' for f, _, _ in FAMS) + '</div>'
    pages.append(W('') + hd('کلیدواژه‌ها') + f'<div class="ttl">کلیدواژه‌های تست</div>{kwhead}{kwrows}' + ft('03') + '</div>')
    wl = ''.join(f'<div class="wl"><span class="lbl">{w} {s} · {WEIGHT_FA[w]}</span><p style="font-weight:{w}">دستیار هوشمند خلاق · هوشنگ</p></div>' for w, s in WEIGHTS)
    pages.append(W('') + hd('وزن‌ها') + f'<div class="ttl" style="margin-bottom:3mm">۹ وزن</div>{wl}' + ft('03') + '</div>')
    wf = ''.join(f'<div class="wfr"><span class="lbl" style="text-align:right">{s}pt</span><div style="font-size:{s}px">{KW_LINE}</div></div>'
                 for s in [9, 11, 14, 18, 24, 32, 44, 60])
    pages.append(W('') + hd('اندازه‌ها') + f'<div class="ttl">از متن ریز تا تیتر</div>{wf}' + ft('04') + '</div>')
    pages.append(W('') + hd('متن') + f'''<div class="ttl">متن بدنه</div><div class="cols" style="grid-template-columns:1fr 1fr">
<div><div class="lbl">Regular 400 · 14/28</div><p style="font-size:14px;line-height:2">{PARA} {PARA}</p></div>
<div><div class="lbl">Medium 500 · 18/34</div><p style="font-size:18px;line-height:1.9;font-weight:500">{PARA}</p>
<div class="lbl" style="margin-top:6mm">Black 900 · 40/50</div><p style="font-size:40px;line-height:1.25;font-weight:900;margin:2mm 0">خوانایی در هر اندازه</p></div></div>''' + ft('05') + '</div>')
    g1 = ''.join(f'<span>{html.escape(c)}</span>' for c in GLYPH_GROUPS[0][2])
    g3 = ''.join(f'<span>{html.escape(c)}</span>' for c in GLYPH_GROUPS[2][2][:20])
    g4 = ''.join(f'<span>{html.escape(c)}</span>' for c in GLYPH_GROUPS[3][2])
    pages.append(W('') + hd('حروف') + f'''<div class="ttl">حروف و نشانه‌ها</div>
<div class="lbl" style="margin-top:3mm">حروف فارسی</div><div class="gg" style="font-size:40px">{g1}</div>
<div class="lbl" style="margin-top:4mm">اعداد</div><div class="gg">{g3}</div>
<div class="lbl" style="margin-top:4mm">نشانه‌ها</div><div class="gg" style="font-size:26px">{g4}</div>''' + ft('06') + '</div>')
    pages.append(W('') + hd('نسخه‌ها') + f'''<div class="ttl">FaNum و NoEn</div><div class="cols" style="grid-template-columns:1fr 1fr">
<div class="card"><div class="lbl">Dastkhat · Main</div><p style="font-size:34px;margin:3mm 0">قیمت: 1,250,000 تومان</p><p style="color:var(--mute);font-size:14px">نسخه اصلی: عددهای لاتین همان‌طور که نوشته شده‌اند نمایش داده می‌شوند.</p></div>
<div class="card"><div class="lbl">Dastkhat FaNum</div><p style="font-family:'Dastkhat FaNum';font-size:34px;margin:3mm 0">قیمت: 1,250,000 تومان</p><p style="color:var(--mute);font-size:14px">همان متن، همان کد؛ عددها فارسی دیده می‌شوند.</p></div>
<div class="card"><div class="lbl">Dastkhat NoEn + Georgia</div><p style="font-family:'Dastkhat NoEn',Georgia;font-size:34px;margin:3mm 0">دستخط with Georgia</p><p style="color:var(--mute);font-size:14px">حروف لاتین حذف شده‌اند تا با فونت لاتین دلخواه ترکیب شود.</p></div>
<div class="card"><div class="lbl">Variable · wght 100-900</div><p style="font-size:34px;margin:3mm 0"><span style="font-weight:150">دستخط</span> <span style="font-weight:450">دستخط</span> <span style="font-weight:850">دستخط</span></p><p style="color:var(--mute);font-size:14px">هر وزن دلخواه بین ۱۰۰ تا ۹۰۰ در یک فایل.</p></div></div>''' + ft('07') + '</div>')
    pages.append(W('cover') + hd('اطلاعات') + '''<div class="ttl" style="margin-top:14mm">دستخط</div>
<div class="cols" style="grid-template-columns:1fr 1fr;font-size:15px;line-height:2.1">
<div>ناشر: دستیار<br>نسخه: ۱٫۲۰۰<br>وزن‌ها: ۹ + متغیر<br>خانواده‌ها: Dastkhat · Dastkhat Diamond · Dastkhat Bar<br>نسخه‌ها: اصلی · FaNum · NoEn<br>فرمت‌ها: TTF · WOFF2</div>
<div>مجوز: OFL 1.1 (متن‌باز)<br>بر پایه: وزیرمتن، اثر صابر راستی‌کردار<br>وب‌سایت:<br><span class="ltr">dastyar.io</span></div></div>''' + ft('08') + '</div>')
    open(os.path.join(BUILD, 'specimen.html'), 'w').write(
        page('Dastkhat Specimen', ''.join(pages), rel_css='file://' + CSS_FONTS, rel_site='file://' + CSS_SITE, extra_css=css))


# =========================================================== image frames (PNG renders)
def frames_doc():
    css = UI_CSS + POSTER_CSS + '''
body{background:#fff}
.f{position:relative;overflow:hidden;background:var(--paper)}
.sq1080{width:1080px;height:1080px}.wide{width:1920px;height:1080px}
.c{position:absolute;inset:70px}
'''
    fr = []
    fr.append('''<div class="f wide" id="cover" style="background:var(--primary);color:#fff"><div class="c">
<div style="display:flex;justify-content:space-between;font-size:26px;opacity:.8"><span>دستیار معرفی می‌کند</span><span class="ltr">Dastkhat v1.200</span></div>
<div style="font-family:'Dastkhat Bar';font-weight:900;font-size:400px;line-height:1.05;margin-top:60px">دستخط</div>
<div style="display:flex;justify-content:space-between;align-items:flex-end;font-size:34px;margin-top:30px"><span>فونت فارسی برای رابط‌های امروز · ۹ وزن · ۳ سبک نقطه</span><span style="width:120px;height:120px;background:var(--secondary);display:block"></span></div>
</div></div>''')
    cols = ''.join(f'''<div style="text-align:center"><div style="font-family:'{f}';font-size:250px;line-height:1.3">تث</div>
<div style="font-family:'{f}';font-size:120px;line-height:1.3">ش چ ق</div><div style="font-size:40px;font-weight:800;margin-top:20px">{fa}</div><div class="lbl" style="font-size:20px">{f}</div></div>''' for f, fa, _ in FAMS)
    fr.append(f'<div class="f wide" id="dot-styles"><div class="c"><div style="font-size:70px;font-weight:900">سه سبک نقطه</div><div style="display:grid;grid-template-columns:repeat(3,1fr);margin-top:40px">{cols}</div></div></div>')
    wl = ''.join(f'<div style="display:flex;justify-content:space-between;align-items:baseline;border-bottom:1px solid var(--line);padding:6px 0"><p style="margin:0;font-size:64px;line-height:1.25;font-weight:{w}">دستیار هوشمند خلاق · Dastkhat</p><span class="lbl" style="font-size:20px">{w} {s}</span></div>' for w, s in WEIGHTS)
    fr.append(f'<div class="f wide" id="weights"><div class="c" style="inset:50px 70px">{wl}</div></div>')
    g = ''.join(f'<span>{html.escape(c)}</span>' for c in GLYPH_GROUPS[0][2])
    fr.append(f'''<div class="f wide" id="glyphs" style="background:var(--ink);color:#fff"><div class="c"><div style="font-size:60px;font-weight:900;color:var(--secondary)">حروف</div>
<div style="display:flex;flex-wrap:wrap;gap:24px 54px;font-size:110px;line-height:1.35;margin-top:30px">{g}</div></div></div>''')
    kwr = ''.join('<div style="display:grid;grid-template-columns:repeat(3,1fr);border-bottom:1px solid var(--line)">' + ''.join(f'<div style="font-family:\'{f}\';font-size:52px;font-weight:800;line-height:1.5;padding:4px 0;white-space:nowrap">{k}</div>' for f, _, _ in FAMS) + '</div>' for k in KEYWORDS)
    kwh = '<div style="display:grid;grid-template-columns:repeat(3,1fr);margin:24px 0 6px">' + ''.join(f'<div style="font-size:28px;font-weight:700;color:var(--primary)">{fa} <span class="lbl" style="font-size:18px">{f}</span></div>' for f, fa, _ in FAMS) + '</div>'
    fr.append(f'<div class="f wide" id="keywords"><div class="c" style="inset:60px 70px"><div style="font-size:56px;font-weight:900">کلیدواژه‌های تست</div>{kwh}{kwr}</div></div>')
    fr.append(f'<div class="f wide" id="ui" style="padding:30px 70px;height:760px">{UI_BODY}</div>')
    fr.append(f'<div id="poster" style="width:1080px">{POSTER_BODY}</div>')
    fr.append(f'''<div class="f sq1080" id="social-1" style="background:var(--secondary);color:var(--on-secondary)"><div class="c">
<div style="font-size:30px;font-weight:700">فونت تازه دستیار</div>
<div style="font-family:'Dastkhat Bar';font-size:300px;font-weight:900;line-height:1.1;margin-top:120px">دستخط</div>
<div style="font-size:40px;font-weight:500;margin-top:40px">رایگان و متن‌باز برای وب، اپ و چاپ</div>
<div style="position:absolute;bottom:0;right:0;font-size:26px">dastyar.io</div></div></div>''')
    fr.append(f'''<div class="f sq1080" id="social-2" style="background:var(--ink);color:#fff"><div class="c">
<div style="font-size:30px;color:var(--secondary)">FaNum</div>
<div style="font-family:'Dastkhat FaNum';font-size:150px;font-weight:900;line-height:1.2;margin-top:110px">1,490,000</div>
<div style="font-size:60px;font-weight:300">تومان</div>
<div style="font-size:34px;margin-top:80px;color:#bbb;line-height:1.8">عدد لاتین در کد<br>عدد فارسی روی صفحه</div></div></div>''')
    fr.append(f'''<div class="f sq1080" id="social-3"><div class="c">
<div style="font-size:30px;color:var(--primary);font-weight:700">۹ وزن در یک فایل متغیر</div>
<div style="font-size:150px;line-height:1.3;margin-top:60px"><div style="font-weight:100">دستیار</div><div style="font-weight:500">ایجنت</div><div style="font-weight:900">هوشنگ</div></div></div></div>''')
    open(os.path.join(BUILD, 'frames.html'), 'w').write(
        page('frames', '<div style="display:flex;flex-direction:column;gap:40px;align-items:flex-start">' + ''.join(fr) + '</div>',
             rel_css='file://' + CSS_FONTS, rel_site='file://' + CSS_SITE, extra_css=css))


if __name__ == '__main__':
    index_page(); tester_page(); glyph_page(); ui_page(); poster_page(); webfont_test(); help_page()
    specimen_doc(); frames_doc()
    print('pages written')
