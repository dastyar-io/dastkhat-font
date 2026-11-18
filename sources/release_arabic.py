"""Produce Dastkhat Arabic (publisher: Dastyar), the Arabic-only cut of the main Dastkhat family.
Input:  the compiled variable font of the main (square-dot) family,
        for example fonts/Main/Dastkhat/Variable/Dastkhat[wght].ttf
Output: <out_dir>/{Main,ArNum,NoEn}/DastkhatArabic*/{Variable,TTF,Webfonts}

What changes against Dastkhat:
  - Persian-only letters are removed: پ چ ژ گ ک ی, the Persian digits ۰-۹, and the
    private-use toman signs. Arabic text never uses them, and the Arabic kaf ك and
    yeh ي stay.
  - ArNum build: Latin digits 0-9 display as Arabic-Indic digits ٠-٩ (the 4, 5 and 6
    differ from the Persian ones).
  - NoEn build: Latin letters removed, as in the main release.

Usage: python3 -I release_arabic.py <out_dir> <variable_font.ttf>
"""
import sys, os

OUT, SRC = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
sys.argv = [sys.argv[0], OUT, os.path.dirname(SRC)]       # release_fonts reads sys.argv when imported
sys.path.insert(0, HERE)
import release_fonts as rf
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools import subset

BASE = 'Dastkhat Arabic'
rf.DESC = ('Dastkhat Arabic is the Arabic and Latin cut of Dastkhat, a UI typeface published by Dastyar and '
           'derived from Vazirmatn by Saber Rastikerdar. It keeps the square-dot Arabic letters, drops the '
           'Persian-only letters and digits, and has a build that shows Latin digits as Arabic-Indic digits. '
           'Latin glyphs derive from Roboto (Apache License 2.0).')

PERSIAN_ONLY = {0x067E, 0x0686, 0x0698, 0x06AF, 0x06A9, 0x06CC} | set(range(0x06F0, 0x06FA)) | {0xE000, 0xE001, 0xE002}


def make_arabic(font):
    """Remove the Persian-only code points; the glyph closure drops the glyphs nothing else needs."""
    keep = [u for u in font.getBestCmap() if u not in PERSIAN_ONLY]
    opts = subset.Options(layout_features=['*'], name_IDs=['*'], name_languages=['*'], glyph_names=True,
                          notdef_outline=True, recalc_bounds=True, legacy_kern=True, hinting=True,
                          layout_scripts=['*'], drop_tables=[])
    opts.drop_tables = [t for t in opts.drop_tables if t not in ('STAT', 'avar')]
    s = subset.Subsetter(opts)
    s.populate(unicodes=keep)
    s.subset(font)
    return font


def make_arnum(font):
    """Latin digits 0-9 display as Arabic-Indic digits U+0660-0669."""
    for t in font['cmap'].tables:
        if not t.isUnicode():
            continue
        for i in range(10):
            ar = 0x0660 + i
            if ar in t.cmap:
                t.cmap[0x30 + i] = t.cmap[ar]
    return font


def main():
    builds = (('', 'Main', make_arabic),
              (' ArNum', 'ArNum', lambda f: make_arnum(make_arabic(f))),
              (' NoEn', 'NoEn', lambda f: rf.make_noen(make_arabic(f))))
    for suffix, sub, fn in builds:
        fam = BASE + suffix
        name = rf.nospace(fam)
        vf = fn(TTFont(SRC))
        rf.set_names(vf, fam, variable=True)
        if 'STAT' in vf:
            del vf['STAT']
        rf.add_stat(vf)
        group = os.path.join(OUT, sub, name)
        for d in ('Variable', 'TTF', 'Webfonts'):
            os.makedirs(os.path.join(group, d), exist_ok=True)
        vpath = os.path.join(group, 'Variable', f'{name}[wght].ttf')
        vf.save(vpath)
        rf.to_woff2(vpath, os.path.join(group, 'Webfonts', f'{name}-Variable.woff2'))
        for w, st in rf.WEIGHTS:
            inst = instancer.instantiateVariableFont(TTFont(vpath), {'wght': w}, inplace=False)
            rf.finish_static(inst, fam, w, st)
            p = os.path.join(group, 'TTF', f'{name}-{st}.ttf')
            inst.save(p)
            rf.to_woff2(p, os.path.join(group, 'Webfonts', f'{name}-{st}.woff2'))
        print('built', fam)


if __name__ == '__main__':
    main()
