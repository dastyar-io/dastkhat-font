"""Build Dastkhat from Vazirmatn (used with permission) by parametric reshaping of Vazirmatn's own outlines.
Usage: python3 -I build.py <Vazirmatn[wght].ttf> <outdir>
"""
import sys, os, copy
from fontTools.ttLib import TTFont, newTable
from fontTools.varLib import instancer
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.designspaceLib import DesignSpaceDocument, SourceDescriptor, AxisDescriptor, InstanceDescriptor
from fontTools import varLib

SRC, OUT = sys.argv[1], sys.argv[2]
DOT_STYLE = sys.argv[3] if len(sys.argv) > 3 else 'square'   # square | diamond | bar
FAMILY = {'square': 'Dastkhat', 'diamond': 'Dastkhat Diamond', 'bar': 'Dastkhat Bar'}[DOT_STYLE]
FILEFAM = FAMILY.replace(' ', '')
SQUARE_HALF = 0.36       # square dot half-side, as a share of the original diamond's width
RIGID = {}               # glyph -> [(start, end, cx, cy)] contours moved without distortion

os.makedirs(OUT, exist_ok=True)
MASTERS = {100: -1, 400: 0, 900: 1}

# ---- design parameters (in 1000-unit space, scaled to UPM) ----
ARABIC_X = 1.04          # wider Persian letters
BODY_LIFT = 65           # how much the letter body (teeth, bowls) is raised
BODY_FROM = {100: 50, 400: 90, 900: 150}   # keep baseline stroke intact (per weight)
BODY_TO = 400
ASC_DROP = 45            # pull ascenders back a bit so alef/kaf don't grow too tall
ASC_FROM, ASC_TO = 450, 800
DIGIT_X = 1.07           # wider Persian digits
LATIN_SCALE = 0.93       # Latin sits smaller next to Persian


def smooth(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def make_ymap(upm, wght):
    k = upm / 1000.0
    y0, y1 = BODY_FROM[wght] * k, BODY_TO * k
    a0, a1 = ASC_FROM * k, ASC_TO * k
    lift, drop = BODY_LIFT * k, ASC_DROP * k
    def f(y):
        if y <= y0:
            return y
        return y + lift * smooth((y - y0) / (y1 - y0)) - drop * smooth((y - a0) / (a1 - a0))
    return f


def ranges(*rs):
    s = set()
    for a, b in rs:
        s.update(range(a, b + 1))
    return s


ARABIC_CP = ranges((0x0600, 0x06FF), (0x0750, 0x077F), (0x08A0, 0x08FF), (0xFB50, 0xFDFF), (0xFE70, 0xFEFF))
DIGIT_CP = ranges((0x0660, 0x0669), (0x06F0, 0x06F9))
LATIN_CP = ranges((0x0021, 0x024F), (0x1E00, 0x1EFF))


def closure(font, cps):
    from fontTools import subset
    cmap = font.getBestCmap()
    s = subset.Subsetter(subset.Options(layout_features=['*'], notdef_glyph=False))
    s.populate(unicodes=[c for c in cps if c in cmap])
    f2 = copy.deepcopy(font)
    s._prune_pre_subset(f2)
    s._closure_glyphs(f2)
    return set(s.glyphs_gsubed) - {'.notdef'}


def classify(font):
    marks = set()
    gdef = font['GDEF'].table
    if gdef.GlyphClassDef:
        marks = {g for g, c in gdef.GlyphClassDef.classDefs.items() if c == 3}
    digits = closure(font, DIGIT_CP)
    # Latin digits get Farsi alternates through a feature; those alternates are digits too
    farsi_alt = {g for g in font.getGlyphOrder() if g.startswith('uni06F') and ('.' in g)}
    digits |= farsi_alt
    arabic = closure(font, ARABIC_CP) - digits - marks
    arabic |= {g for g in font.getGlyphOrder()
               if (g.startswith('arabic_') or g.startswith('uni06') or g.startswith('afii57'))
               and g not in digits and g not in marks}
    glyf = font['glyf']
    latin = {g for g in font.getGlyphOrder()
             if g not in arabic and g not in digits and g not in marks
             and glyf[g].numberOfContours != 0 and g != '.notdef'
             and not g.startswith('uni25') and not g.startswith('uniFFF')}
    return arabic, digits, latin, marks


def decompose_all(font):
    gs = font.getGlyphSet()
    glyf = font['glyf']
    for name in font.getGlyphOrder():
        if glyf[name].isComposite():
            rp = DecomposingRecordingPen(gs)
            gs[name].draw(rp)
            tp = TTGlyphPen(None)
            rp.replay(tp)
            glyf[name] = tp.glyph()



# ---------------- dots ----------------
from array import array
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates


def split_contours(g):
    pts, flags, out, s = list(g.coordinates), list(g.flags), [], 0
    for e in g.endPtsOfContours:
        out.append((pts[s:e + 1], flags[s:e + 1])); s = e + 1
    return out


def area(pts):
    return sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts))) / 2


def is_diamond(pts, flags, D):
    if len(pts) != 4 or not all(f & 1 for f in flags):
        return False
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    w, h = max(xs) - min(xs), max(ys) - min(ys)
    if not (0.75 * D < w < 1.25 * D and 0.75 * D < h < 1.25 * D):
        return False
    cx, cy, t = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2, 0.12 * D
    for x, y in pts:
        if not ((abs(x - cx) < t and abs(abs(y - cy) - h / 2) < t) or (abs(y - cy) < t and abs(abs(x - cx) - w / 2) < t)):
            return False
    return True


def plan_dots(font, names):
    """On one master: find dot contours and group them into rows. Returns glyph -> list of rows (contour indices)."""
    glyf = font['glyf']
    db = glyf['arabic_dot']; db.recalcBounds(glyf)
    D = db.xMax - db.xMin
    plan = {}
    for n in names:
        g = glyf[n]
        if g.isComposite() or g.numberOfContours <= 0:
            continue
        cs = split_contours(g)
        dots = []
        for i, (p, f) in enumerate(cs):
            if is_diamond(p, f, D):
                xs, ys = [q[0] for q in p], [q[1] for q in p]
                dots.append((i, (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2))
        if not dots:
            continue
        # connected clusters
        clusters, left = [], dots[:]
        while left:
            cl = [left.pop(0)]; changed = True
            while changed:
                changed = False
                for d in left[:]:
                    if any(((d[1] - c[1]) ** 2 + (d[2] - c[2]) ** 2) ** .5 < 1.5 * D for c in cl):
                        cl.append(d); left.remove(d); changed = True
            clusters.append(cl)
        rows = []
        for cl in clusters:
            cl.sort(key=lambda d: d[2])
            crow = []
            for d in cl:
                if crow and abs(d[2] - crow[-1][2]) < 0.35 * D:
                    crow.append(d)
                else:
                    if crow: rows.append(crow)
                    crow = [d]
            rows.append(crow)
            rows[-len(rows):]  # noqa
        # keep cluster membership: tag rows with their cluster id
        plan[n] = [[d[0] for d in sorted(r, key=lambda d: d[1])] for r in rows]
        plan[n + '#clusters'] = [[d[0] for d in cl] for cl in clusters]
    return plan


def rect(x0, y0, x1, y1, sign):
    pts = [(x0, y0), (x0, y1), (x1, y1), (x1, y0)]
    return pts if (area(pts) > 0) == (sign > 0) else pts[::-1]


def apply_dots(font, plan, style):
    glyf = font['glyf']
    for n, rows in plan.items():
        if n.endswith('#clusters'):
            continue
        g = glyf[n]
        cs = split_contours(g)
        info = {}
        for r in rows:
            for i in r:
                p = cs[i][0]; xs, ys = [q[0] for q in p], [q[1] for q in p]
                info[i] = ((max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2, max(xs) - min(xs), area(p))
        dot_idx = set(info)
        keep = [c for i, c in enumerate(cs) if i not in dot_idx]
        new = []   # (pts, cx, cy)
        hcap = {}
        for cl in plan[n + '#clusters']:
            cheb = [max(abs(info[a][0] - info[b][0]), abs(info[a][1] - info[b][1])) for a in cl for b in cl if a < b]
            for i in cl:
                hcap[i] = min(cheb) / 2.5 if cheb else 1e9   # gap between squares >= half a half-side
        if style in ('square', 'diamond'):
            for i in sorted(dot_idx):
                cx, cy, w, sg = info[i]
                if style == 'square':
                    h = min(SQUARE_HALF * w, hcap[i])
                    new.append((rect(cx - h, cy - h, cx + h, cy + h, sg), cx, cy))
                else:
                    r = w / 2
                    pts = [(cx, cy + r), (cx - r, cy), (cx, cy - r), (cx + r, cy)]
                    if (area(pts) > 0) != (sg > 0): pts = pts[::-1]
                    new.append((pts, cx, cy))
        else:  # bar: each row of 2+ dots becomes one bar; single dots stay squares
            for cl in plan[n + '#clusters']:
                crow = [r for r in rows if r[0] in cl]
                h = SQUARE_HALF * max(info[i][2] for i in cl)
                sg = info[cl[0]][3]
                shapes = []
                for r in crow:
                    cy = sum(info[i][1] for i in r) / len(r)
                    x0 = min(info[i][0] for i in r) - h; x1 = max(info[i][0] for i in r) + h
                    shapes.append([x0, x1, cy, len(r)])
                # keep a clear gap between stacked rows (e.g. bar + square for three dots)
                shapes.sort(key=lambda s: s[2])
                for a, b in zip(shapes, shapes[1:]):
                    gap = (b[2] - a[2]) - 2 * h
                    need = 0.6 * h
                    if gap < need:
                        d = need - gap
                        # move the single dot, keep the bar where it is
                        if b[3] == 1 and a[3] > 1: b[2] += d
                        elif a[3] == 1 and b[3] > 1: a[2] -= d
                        else: a[2] -= d / 2; b[2] += d / 2
                for x0, x1, cy, _ in shapes:
                    new.append((rect(x0, cy - h, x1, cy + h, sg), (x0 + x1) / 2, cy))
        pts, flags, ends, rigid = [], [], [], []
        for p, f in keep:
            pts += p; flags += f; ends.append(len(pts) - 1)
        for p, cx, cy in new:
            s = len(pts)
            pts += [(round(x), round(y)) for x, y in p]; flags += [1] * len(p); ends.append(len(pts) - 1)
            rigid.append((s, len(pts) - 1, cx, cy))
        g.coordinates = GlyphCoordinates(pts); g.flags = array('B', flags)
        g.endPtsOfContours = ends; g.numberOfContours = len(ends)
        g.recalcBounds(glyf)
        RIGID[(id(font), n)] = rigid


def transform_master(font, wght, groups):
    arabic, digits, latin, marks = groups
    upm = font['head'].unitsPerEm
    ymap = make_ymap(upm, wght)
    glyf, hmtx = font['glyf'], font['hmtx']
    kind = {}
    for g in arabic: kind[g] = 'ar'
    for g in digits: kind[g] = 'dg'
    for g in latin: kind[g] = 'la'

    def pt(g, x, y):
        k = kind.get(g)
        if k == 'ar':
            return x * ARABIC_X, ymap(y)
        if k == 'la':
            return x * LATIN_SCALE, y * LATIN_SCALE
        return x, y

    for name in font.getGlyphOrder():
        k = kind.get(name)
        if not k:
            continue
        adv, lsb = hmtx[name]
        g = glyf[name]
        if g.numberOfContours > 0:
            coords = g.coordinates
            if k == 'dg':
                cx = adv / 2.0
                for i, (x, y) in enumerate(coords):
                    coords[i] = (round(cx + (x - cx) * DIGIT_X + adv * (DIGIT_X - 1) / 2), y)
            else:
                rigid = RIGID.get((id(font), name), [])
                moves = {}
                for s, e, cx, cy in rigid:
                    tx, ty = pt(name, cx, cy)
                    for j in range(s, e + 1): moves[j] = (tx - cx, ty - cy)
                for i, (x, y) in enumerate(coords):
                    if i in moves:
                        nx, ny = x + moves[i][0], y + moves[i][1]
                    else:
                        nx, ny = pt(name, x, y)
                    coords[i] = (round(nx), round(ny))
            g.program = None
            from fontTools.ttLib.tables import ttProgram
            g.program = ttProgram.Program(); g.program.fromBytecode(b'')
            g.recalcBounds(glyf)
        if k == 'ar':
            nadv = round(adv * ARABIC_X)
        elif k == 'la':
            nadv = round(adv * LATIN_SCALE)
        else:
            nadv = round(adv * DIGIT_X)
        nlsb = g.xMin if g.numberOfContours > 0 else 0
        hmtx[name] = (nadv, nlsb)

    xfac = {'ar': ARABIC_X, 'la': LATIN_SCALE, 'dg': DIGIT_X}

    def fx(g):
        return xfac.get(kind.get(g), 1.0)

    def scale_vr(vr, f, latin_y=False):
        if vr is None:
            return
        for attr in ('XPlacement', 'XAdvance'):
            if getattr(vr, attr, None):
                setattr(vr, attr, round(getattr(vr, attr) * f))
        if latin_y:
            for attr in ('YPlacement', 'YAdvance'):
                if getattr(vr, attr, None):
                    setattr(vr, attr, round(getattr(vr, attr) * f))

    def anchor_xf(a, g):
        if a is None:
            return
        x, y = pt(g, a.XCoordinate, a.YCoordinate)
        if kind.get(g) == 'dg':
            x = a.XCoordinate * DIGIT_X
        a.XCoordinate, a.YCoordinate = round(x), round(y)

    gpos = font['GPOS'].table
    for lk in gpos.LookupList.Lookup:
        for st in lk.SubTable:
            t = st.ExtSubTable if lk.LookupType == 9 else st
            lt = t.LookupType
            if lt == 1:
                cov = t.Coverage.glyphs
                if t.Format == 1:
                    f = fx(cov[0]); scale_vr(t.Value, f, kind.get(cov[0]) == 'la')
                else:
                    for g, v in zip(cov, t.Value):
                        scale_vr(v, fx(g), kind.get(g) == 'la')
            elif lt == 2:
                cov = t.Coverage.glyphs
                if t.Format == 1:
                    for g, ps in zip(cov, t.PairSet):
                        for pvr in ps.PairValueRecord:
                            scale_vr(pvr.Value1, fx(g)); scale_vr(pvr.Value2, fx(g))
                else:
                    cd1 = t.ClassDef1.classDefs
                    cls_glyph = {}
                    for g in cov:
                        cls_glyph.setdefault(cd1.get(g, 0), g)
                    for ci, rec in enumerate(t.Class1Record):
                        g = cls_glyph.get(ci)
                        f = fx(g) if g else 1.0
                        for c2 in rec.Class2Record:
                            scale_vr(c2.Value1, f); scale_vr(c2.Value2, f)
            elif lt == 3:
                for g, er in zip(t.Coverage.glyphs, t.EntryExitRecord):
                    anchor_xf(er.EntryAnchor, g); anchor_xf(er.ExitAnchor, g)
            elif lt == 4:
                for g, br in zip(t.BaseCoverage.glyphs, t.BaseArray.BaseRecord):
                    for a in br.BaseAnchor:
                        anchor_xf(a, g)
            elif lt == 5:
                for g, la in zip(t.LigatureCoverage.glyphs, t.LigatureArray.LigatureAttach):
                    for cr in la.ComponentRecord:
                        for a in cr.LigatureAnchor:
                            anchor_xf(a, g)
            # lt 6 (mark-to-mark): anchors live on mark glyphs, which keep their shape
    return font


def rename(font, style=None, variable=False):
    name = font['name']
    fam = FAMILY
    copyright_ = ('Copyright 2015 The Vazirmatn Project Authors (https://github.com/rastikerdar/vazirmatn). '
                  'Copyright 2026 Alireza Eskandari (Dastkhat modifications).')
    desc = ('Dastkhat is a modified version of Vazirmatn (used with permission) with a taller letter body, '
            'wider Persian letters and digits, and a smaller Latin. Latin glyphs derive from Roboto (Apache 2.0).')
    style = style or 'Regular'
    ribbi = style in ('Regular', 'Bold')
    ps = f'{fam}-{style}'.replace(' ', '')
    recs = {0: copyright_, 1: fam if ribbi else f'{fam} {style}', 2: style if ribbi else 'Regular',
            3: f'1.000;ESKD;{ps}', 4: f'{fam} {style}' if style != 'Regular' else f'{fam} Regular',
            5: 'Version 1.000', 6: ps, 7: 'Dastkhat is a trademark of Alireza Eskandari.',
            8: 'Alireza Eskandari', 9: 'Saber Rastikerdar (Vazirmatn); Alireza Eskandari (Dastkhat)',
            10: desc, 11: '', 13: 'Licensed under the Dastkhat End User License Agreement. Licenses and terms: https://dastyar.io',
            14: 'https://dastyar.io', 16: fam, 17: style}
    if variable:
        recs[1] = fam; recs[2] = 'Regular'; recs[4] = f'{fam} Regular'; recs[6] = f'{fam}-Regular'.replace(' ', '')
        recs[3] = f'1.000;ESKD;{fam}-Regular'.replace(' ', ''); recs[25] = fam.replace(' ', '')
    # Drop old family-level names on all platforms, keep instance/axis names (>=256)
    name.names = [n for n in name.names if n.nameID >= 256]
    for nid, val in recs.items():
        if val:
            name.setName(val, nid, 3, 1, 0x409)
    if 7 in recs:
        pass
    font['head'].fontRevision = 1.0
    os2 = font['OS/2']
    os2.achVendID = 'ESKD'


def main():
    vf = TTFont(SRC)
    avar_segments = vf['avar'].segments
    masters = {}
    for w in MASTERS:
        inst = instancer.instantiateVariableFont(copy.deepcopy(vf), {'wght': w}, inplace=False)
        decompose_all(inst)
        masters[w] = inst
    groups = classify(masters[400])
    dot_names = [g for g in masters[400].getGlyphOrder() if g in groups[0] or g in groups[3]]
    plan = plan_dots(masters[400], dot_names)
    print('glyphs with dots', len([k for k in plan if not k.endswith('#clusters')]))
    for m in masters.values():
        apply_dots(m, plan, DOT_STYLE)
    print('arabic', len(groups[0]), 'digits', len(groups[1]), 'latin', len(groups[2]), 'marks', len(groups[3]))
    paths = {}
    for w, m in masters.items():
        transform_master(m, w, groups)
        for t in ('STAT',):
            if t in m:
                del m[t]
        p = os.path.join(OUT, f'_master_{w}.ttf')
        m.save(p)
        paths[w] = p

    ds = DesignSpaceDocument()
    ax = AxisDescriptor(); ax.tag = 'wght'; ax.name = 'Weight'; ax.minimum = 100; ax.default = 400; ax.maximum = 900
    ds.addAxis(ax)
    for w, p in paths.items():
        s = SourceDescriptor(); s.path = p; s.location = {'Weight': w}
        if w == 400:
            s.copyInfo = s.copyLib = s.copyGroups = s.copyFeatures = True
        ds.addSource(s)
    styles = [(100, 'Thin'), (200, 'ExtraLight'), (300, 'Light'), (400, 'Regular'), (500, 'Medium'),
              (600, 'SemiBold'), (700, 'Bold'), (800, 'ExtraBold'), (900, 'Black')]
    for w, st in styles:
        i = InstanceDescriptor(); i.familyName = FAMILY; i.styleName = st; i.location = {'Weight': w}
        ds.addInstance(i)
    newvf, _, _ = varLib.build(ds)
    # restore Vazirmatn's weight curve
    newvf['avar'] = newTable('avar'); newvf['avar'].segments = avar_segments
    if 'avar' in newvf and hasattr(newvf['avar'], 'majorVersion'):
        newvf['avar'].majorVersion = 1
    rename(newvf, variable=True)
    # STAT
    from fontTools.otlLib.builder import buildStatTable
    buildStatTable(newvf, [dict(tag='wght', name='Weight', values=[
        dict(value=w, name=st, **({'flags': 2, 'linkedValue': 700} if w == 400 else {})) for w, st in styles])])
    os.makedirs(os.path.join(OUT, 'variable'), exist_ok=True)
    vpath = os.path.join(OUT, 'variable', f'{FILEFAM}[wght].ttf')
    newvf.save(vpath)

    os.makedirs(os.path.join(OUT, 'ttf'), exist_ok=True)
    for w, st in styles:
        v = TTFont(vpath)
        inst = instancer.instantiateVariableFont(v, {'wght': w}, inplace=False)
        rename(inst, style=st)
        inst['OS/2'].usWeightClass = w
        sel = inst['OS/2'].fsSelection & ~0b1100001  # clear italic, bold, regular
        if st == 'Regular': sel |= 0x40
        if st == 'Bold': sel |= 0x20
        inst['OS/2'].fsSelection = sel
        inst['head'].macStyle = 1 if st == 'Bold' else 0
        for t in ('STAT',):
            if t in inst: del inst[t]
        inst.save(os.path.join(OUT, 'ttf', f'{FILEFAM}-{st}.ttf'))
    for p in paths.values():
        os.remove(p)
    print('done')


if __name__ == '__main__':
    main()
