"""Add the glyphs Google Fonts requires to the Dastkhat UFO masters (run once; already applied).

  - 11 Latin combining marks (U+0302 0304 0306 0307 0308 030A 030B 030C 0326 0327 0328),
    built from the spacing accents of the same master, with attachment anchors
  - Latin composites: Ẁ ẁ Ẃ ẃ Ẅ ẅ Ỳ ỳ (U+1E80-1E85, U+1EF2-1EF3); where the glyph already exists only its codepoint is set and a first-draft capital sharp S (U+1E9E)
  - a drawn .notdef
  - tabular figures held to one width in all weights (re-runnable; skips steps already applied)
  - Latin anchors on the dotted circle (U+25CC) so Latin marks can attach to it

Usage: python3 -I patch_ufo_gf.py ufo/<Family>
"""
import sys, glob, os
import ufoLib2
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
from ufoLib2.objects import Component, Anchor

TOP = [('uni0302', 0x302, 'circumflex'), ('uni0304', 0x304, 'macron'), ('uni0306', 0x306, 'breve'),
       ('uni0307', 0x307, 'dotaccent'), ('uni0308', 0x308, 'dieresis'), ('uni030A', 0x30A, 'ring'),
       ('uni030B', 0x30B, 'hungarumlaut'), ('uni030C', 0x30C, 'caron')]
BOTTOM = [('uni0326', 0x326, 'commaaccent'), ('uni0327', 0x327, 'cedilla'), ('uni0328', 0x328, 'ogonek')]
COMPOSITES = [('Wgrave', 0x1E80, 'W', 'gravecomb'), ('wgrave', 0x1E81, 'w', 'gravecomb'),
              ('Wacute', 0x1E82, 'W', 'acutecomb'), ('wacute', 0x1E83, 'w', 'acutecomb'),
              ('Wdieresis', 0x1E84, 'W', 'uni0308'), ('wdieresis', 0x1E85, 'w', 'uni0308'),
              ('Ygrave', 0x1EF2, 'Y', 'gravecomb'), ('ygrave', 0x1EF3, 'y', 'gravecomb')]


def bounds(u, n):
    p = BoundsPen(u); u[n].draw(p); return p.bounds


def anchor(g, name):
    return next(a for a in g.anchors if a.name == name)


def add(u, name, unicode_, cat):
    g = u.newGlyph(name)
    g.unicodes = [unicode_] if unicode_ else []
    order = list(u.lib['public.glyphOrder']); order.append(name); u.lib['public.glyphOrder'] = order
    if cat: u.lib['public.openTypeCategories'][name] = cat
    return g


def add_glyphs(path):
    u = ufoLib2.Font.open(path)
    ac, ac_ref, db = u['acutecomb'], u['acute'], u['dotbelow']
    ydrop_top = bounds(u, 'acutecomb')[1] - bounds(u, 'acute')[1]            # how far comb accents sit above spacing ones
    att_y = anchor(ac, '_Anchor-0').y
    stack_gap = anchor(ac, 'Anchor-5').y - bounds(u, 'acutecomb')[3]
    below_gap = bounds(u, 'dotbelow')[1] - anchor(db, 'Anchor-4').y

    for name, uni, src in TOP + BOTTOM:
        g = add(u, name, uni, 'mark')
        x0, y0, x1, y1 = bounds(u, src)
        cx = (x0 + x1) / 2
        top = (name, uni, src) in TOP
        dy = ydrop_top if top else 0
        if src == 'commaaccent':
            dy = bounds(u, 'dotbelow')[3] + 70 - y1
        u[src].draw(TransformPen(g.getPen(), (1, 0, 0, 1, -cx, dy)))
        g.width = 0
        ny0, ny1 = y0 + dy, y1 + dy
        if top:
            g.anchors = [Anchor(x=0, y=att_y, name='_Anchor-0'), Anchor(x=0, y=ny1 + stack_gap, name='Anchor-5'),
                         Anchor(x=0, y=att_y, name='_Anchor-5')]
        else:
            g.anchors = [Anchor(x=0, y=0, name='_Anchor-1'), Anchor(x=0, y=ny0 - below_gap, name='Anchor-4'),
                         Anchor(x=0, y=0, name='_Anchor-4')]

    for name, uni, base, mark in COMPOSITES:
        if name in u:                      # glyph already drawn in the source, only its codepoint was missing
            if not u[name].unicodes: u[name].unicodes = [uni]
            continue
        b, m = u[base], u[mark]
        g = add(u, name, uni, 'base')
        ba, ma = anchor(b, 'Anchor-0'), anchor(m, '_Anchor-0')
        g.width = b.width
        g.components = [Component(base), Component(mark, transformation=(1, 0, 0, 1, ba.x - ma.x, ba.y - ma.y))]
        g.anchors = [Anchor(x=a.x, y=a.y, name=a.name) for a in b.anchors]

    # capital sharp S: first draft derived from the lowercase sharp s (needs a designer's review)
    sx, sy = 1.1, 0.95
    g = add(u, 'uni1E9E', 0x1E9E, 'base')
    u['germandbls'].draw(TransformPen(g.getPen(), (sx, 0, 0, sy, 0, 0)))
    g.width = round(u['germandbls'].width * sx)
    g.anchors = [Anchor(x=g.width // 2, y=anchor(u['A'], 'Anchor-0').y, name='Anchor-0'),
                 Anchor(x=g.width // 2, y=0, name='Anchor-1')]

    # dotted circle: Latin anchors
    dc = u['uni25CC']; x0, y0, x1, y1 = bounds(u, 'uni25CC'); cx = round((x0 + x1) / 2)
    gap = anchor(u['A'], 'Anchor-0').y - bounds(u, 'A')[3]
    dc.anchors = list(dc.anchors) + [Anchor(x=cx, y=round(y1 + gap), name='Anchor-0'), Anchor(x=cx, y=round(y0), name='Anchor-1')]

    # .notdef: an open box whose stroke follows the master weight
    t = {'Thin': 50, 'Regular': 100, 'Black': 190}[os.path.basename(path).split('-')[-1][:-4]]
    nd = u['.notdef']; nd.clear(); nd.width = 1000
    pen = nd.getPen()
    for (x0, y0, x1, y1), ccw in (((80, 0, 920, 1400), False), ((80 + t, t, 920 - t, 1400 - t), True)):
        pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        if ccw is False: pts = pts[::-1]
        pen.moveTo(pts[0]); [pen.lineTo(p) for p in pts[1:]]; pen.closePath()
    u.save(overwrite=True)


def fix_tnum(path):
    """Tabular figures keep one advance width in every weight (Google Fonts requires it)."""
    u = ufoLib2.Font.open(path)
    names = [n for n in u.keys() if n.endswith('.tnum')]
    target = 1508                                       # the widest (Black) tabular width
    for n in names:
        g = u[n]
        if g.width == target: continue
        dx = (target - g.width) / 2
        g.move((dx, 0)); g.width = target
        for a in g.anchors: a.x += dx
    u.save(overwrite=True)


if __name__ == '__main__':
    for p in sorted(glob.glob(os.path.join(sys.argv[1], '*.ufo'))):
        if 'uni0302' not in ufoLib2.Font.open(p).keys():
            add_glyphs(p)
        fix_tnum(p); print('patched', p)
