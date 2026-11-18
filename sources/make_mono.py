"""Derive the monospaced family (Dastkhat Mono) from the Dastkhat UFO masters.

    sources/ufo/Dastkhat  ->  sources/ufo/DastkhatMono   (Dastkhat Mono)

What becomes fixed-width: everything that is not a joining Arabic-script letter,
that is Latin, Greek and Cyrillic letters, digits (Latin, Persian, Arabic-Indic),
punctuation, symbols, the currency signs and the space. Each takes one CELL, so
a column of code, a table or a terminal lines up. A glyph wider than the cell is
narrowed to fit; a narrower one is centred in it. Ligatures such as f_i take as
many cells as they have letters.

What does not: Persian and Arabic letters. They join, and a letter forced into a
fixed cell would break the join, so they keep their proportional widths and
their kerning and shaping features. A terminal that lays text out cell by cell
(as terminals do) is unaffected; a web page or editor sets them at natural width.

Two small aids for code: the zero carries a square dot, the family's own
dot, so 0 and O never get confused, and the Latin kerning is dropped.

Usage: python3 -I sources/make_mono.py [sources/ufo]
Needs ufoLib2 (installed with fontmake). Re-runnable: the output is rewritten
from scratch each time.
"""
import os, sys, shutil
import ufoLib2
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.recordingPen import RecordingPen

HERE = os.path.dirname(os.path.abspath(__file__))
UFO = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(HERE, 'ufo')
SRC_FAMILY, DST_FAMILY = 'Dastkhat', 'DastkhatMono'
MASTERS = ('Thin', 'Regular', 'Black')
CELL = 1280          # advance of one cell, 0.625 em on a 2048 em
MIN_SB = 70          # least side bearing left on a glyph that had to be narrowed

# Unicode ranges that become fixed width. Combining marks have no advance and are skipped anyway.
RANGES = [
    (0x20, 0x7E), (0xA0, 0x2FF),             # Basic Latin, Latin-1, Latin Extended, IPA, modifier letters
    (0x370, 0x52F),                          # Greek, Cyrillic
    (0x1E00, 0x1FFF),                        # Latin Extended Additional, Greek Extended
    (0x2010, 0x2027), (0x2030, 0x205E),      # general punctuation (not the em, en or thin spaces)
    (0x2070, 0x218F),                        # super/subscripts, currency, letterlike, number forms
    (0x2190, 0x22FF), (0x2500, 0x25FF),      # arrows, math, box drawing, shapes
    (0xFB00, 0xFB06),                        # Latin ligatures
    (0x0660, 0x0669), (0x06F0, 0x06F9),      # Arabic-Indic and Persian digits
    (0x060C, 0x060C), (0x061B, 0x061B), (0x061F, 0x061F), (0x066A, 0x066D),   # Arabic punctuation
    (0xE000, 0xE002),                        # toman and rial signs
    (0xFDFC, 0xFDFC),                        # rial sign
]
ZEROS = ('zero', 'zero.tnum')      # glyphs that get the dot


def wanted(u):
    return any(a <= u <= b for a, b in RANGES)


LIGATURES = {'st': 2}        # ligature glyphs whose names do not spell their letters


def code_of(part, name_to_u):
    """The code point of a glyph name: from the cmap, else from a uniXXXX name."""
    u = name_to_u.get(part)
    if u is None and part.startswith('uni') and len(part) == 7:
        try:
            u = int(part[3:], 16)
        except ValueError:
            pass
    return u


def fixed_cells(name, name_to_u):
    """How many cells a glyph takes, or 0 if it stays proportional."""
    base = name.split('.')[0]
    if base in LIGATURES:
        return LIGATURES[base]
    parts = base.split('_')
    for p in parts:
        u = code_of(p, name_to_u)
        if u is None or not wanted(u):
            return 0
    return len(parts)


def decomposed(font, glyph):
    """The outline of a glyph with its components resolved, as a recording."""
    rec = RecordingPen()
    glyph.draw(_Decomposing(font, rec))
    return rec


class _Decomposing:
    """Segment pen that resolves components against the font."""
    def __init__(self, font, pen):
        self.font, self.pen = font, pen

    def __getattr__(self, name):
        return getattr(self.pen, name)

    def addComponent(self, base, transform):
        t = TransformPen(self.pen, transform)
        self.font[base].draw(_Decomposing(self.font, t))


def bounds_x(font, glyph):
    bp = BoundsPen(font)
    glyph.draw(bp)
    return bp.bounds


def reset_outline(glyph, rec, sx, dx):
    """Rewrite a glyph's outline from a recording, scaled by sx and moved by dx."""
    glyph.clearContours()
    glyph.clearComponents()
    pen = glyph.getPen()
    tp = TransformPen(pen, (sx, 0, 0, 1, dx, 0))
    rec.replay(tp)


def dot_size(font):
    """Width and height of the square dot of this master, read off the Persian beh."""
    g = font['uni0628']
    best = None
    for c in g.contours:
        bp = BoundsPen(font)
        c.draw(bp)
        x0, y0, x1, y1 = bp.bounds
        area = (x1 - x0) * (y1 - y0)
        if best is None or area < best[0]:
            best = (area, x1 - x0, y1 - y0)
    return best[1], best[2]


def add_zero_dot(font, glyph):
    """Put a square dot in the middle of the counter of a zero."""
    inner = None
    for c in glyph.contours:
        bp = BoundsPen(font)
        c.draw(bp)
        b = bp.bounds
        if inner is None or (b[2] - b[0]) < (inner[2] - inner[0]):
            inner = b
    cx, cy = (inner[0] + inner[2]) / 2, (inner[1] + inner[3]) / 2
    dw, dh = dot_size(font)
    # Leave a clear gap to the stroke: never more than half the counter's width or height.
    k = min(1.0, 0.5 * (inner[2] - inner[0]) / dw, 0.5 * (inner[3] - inner[1]) / dh)
    hw, hh = dw * k / 2, dh * k / 2
    pen = glyph.getPen()
    # Same start point and direction in every master, so the masters stay compatible.
    pen.moveTo((round(cx - hw), round(cy - hh)))
    pen.lineTo((round(cx - hw), round(cy + hh)))
    pen.lineTo((round(cx + hw), round(cy + hh)))
    pen.lineTo((round(cx + hw), round(cy - hh)))
    pen.closePath()


def process(font):
    name_to_u = {}
    for g in font:
        for u in g.unicodes:
            name_to_u.setdefault(g.name, u)
    cells = {g.name: fixed_cells(g.name, name_to_u) for g in font if g.width > 0}
    cells = {n: c for n, c in cells.items() if c}
    cells['.notdef'] = 1
    # a glyph that is built from a glyph we are about to move would drift: refuse to guess
    for g in font:
        if g.name not in cells:
            for c in g.components:
                assert c.baseGlyph not in cells, f'{g.name} uses {c.baseGlyph}'
    narrowed = 0
    for name, n in cells.items():
        g = font[name]
        w = CELL * n
        rec = decomposed(font, g)
        b = bounds_x(font, g)
        sx, dx = 1.0, 0.0
        if b:
            ink = b[2] - b[0]
            sx = min(1.0, (w - 2 * MIN_SB) / ink)
            if sx < 1:
                narrowed += 1
            dx = (w - ink * sx) / 2 - b[0] * sx
        if g.components:
            reset_outline(g, rec, sx, dx)
        else:
            for c in g.contours:
                for p in c.points:
                    p.x = round(p.x * sx + dx)
        for a in g.anchors:
            a.x = round(a.x * sx + dx)
        g.width = w
    for name in ZEROS:
        if name in font:
            add_zero_dot(font, font[name])
    # kerning: no pair that touches a fixed glyph
    def fixed_side(s):
        members = font.groups.get(s) if s.startswith('public.kern') else [s]
        return bool(members) and all(m in cells for m in members)
    for pair in list(font.kerning):
        if fixed_side(pair[0]) or fixed_side(pair[1]):
            del font.kerning[pair]
    return len(cells), narrowed


def rename(font, master):
    fam = 'Dastkhat Mono'
    ps = f'DastkhatMono-{master}'
    i = font.info
    i.familyName = fam
    i.styleMapFamilyName = fam if master in ('Regular', 'Bold') else f'{fam} {master}'
    i.postscriptFontName = ps
    i.postscriptIsFixedPitch = True
    i.openTypeOS2Panose = [0, 0, 0, 9, 0, 0, 0, 0, 0, 0]      # proportion: monospaced
    for attr in ('openTypeNamePreferredFamilyName', 'openTypeNameCompatibleFullName', 'openTypeNameUniqueID'):
        if getattr(i, attr, None):
            setattr(i, attr, None)


def main():
    src_dir, dst_dir = os.path.join(UFO, SRC_FAMILY), os.path.join(UFO, DST_FAMILY)
    if os.path.isdir(dst_dir):
        shutil.rmtree(dst_dir)
    os.makedirs(dst_dir)
    for m in MASTERS:
        font = ufoLib2.Font.open(os.path.join(src_dir, f'{SRC_FAMILY}-{m}.ufo'))
        n, narrowed = process(font)
        rename(font, m)
        font.save(os.path.join(dst_dir, f'{DST_FAMILY}-{m}.ufo'), overwrite=True)
        print(f'{m}: {n} glyphs fixed to the cell, {narrowed} narrowed to fit')
    ds = open(os.path.join(src_dir, f'{SRC_FAMILY}.designspace'), encoding='utf-8').read()
    ds = ds.replace(f'{SRC_FAMILY}-', f'{DST_FAMILY}-').replace('"Dastkhat ', '"Dastkhat Mono ')
    ds = ds.replace('familyname="Dastkhat"', 'familyname="Dastkhat Mono"')
    open(os.path.join(dst_dir, f'{DST_FAMILY}.designspace'), 'w', encoding='utf-8').write(ds)


if __name__ == '__main__':
    main()
