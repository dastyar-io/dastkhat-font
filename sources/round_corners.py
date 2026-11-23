"""Derive Dastkhat Round from the circle-dot masters.

    sources/ufo/DastkhatDots  ->  sources/ufo/DastkhatRound   (Dastkhat Round)

Dastkhat Dots already has circle dots. Dastkhat Round keeps them and rounds the
letters too: every convex corner on the visible outline becomes a circular
fillet, so stroke ends turn into near half-circles and the joints of Latin and
Persian letters lose their points. Metrics, spacing, kerning and features stay
those of Dastkhat Dots.

How a corner is rounded: the two segments that meet at it are cut back by a
length set by the master's stem (half a stem, so a stroke end is nearly a half
circle), and a cubic arc joins the two cuts. The cut never takes more than a
bit under half of a segment that has a rounded corner at its other end too.

What stays sharp:
  * concave corners. Most of a letter's inner corners are where two
    overlapping contours cross, which has no point to round, so rounding only
    the few inner corners that have one would look uneven.
  * corners hidden by, or lying on, another contour of the same glyph. The
    sources keep their overlaps, and rounding such a corner would cut a notch
    where two shapes meet.
  * the ends of joining strokes, the vertical cuts at or past a glyph's
    sidebearings, so joined Persian letters still meet without a seam.

Interpolation: the three masters must keep the same points, so which corners
are rounded is decided once for all of them. A corner is rounded when it turns
by more than TURN degrees in at least one master and is visible in every one.

Usage: python3 -I sources/round_corners.py [sources/ufo]
Run it after round_dots.py. The output family is rewritten from scratch each time.
"""
import os, sys, shutil, plistlib, math
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
UFO = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(HERE, 'ufo')
SRC_FAM, SRC_NAME = 'DastkhatDots', 'Dastkhat Dots'
DST_FAM, DST_NAME = 'DastkhatRound', 'Dastkhat Round'
MASTERS = ('Thin', 'Regular', 'Black')
RADIUS = 0.5      # cut length at a corner, in stems
TURN = 30         # degrees; gentler bends are left alone
TOL = 3           # units; a corner this close to another contour counts as touching it
SAMPLES = 48      # per segment piece, for lengths and coverage


# ------------------------------------------------------------------ geometry
def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def at(piece, t):
    """A point on a line, quadratic or cubic piece, given as its control points."""
    pts = list(piece)
    while len(pts) > 1:
        pts = [lerp(pts[i], pts[i + 1], t) for i in range(len(pts) - 1)]
    return pts[0]


def split(piece, t):
    """de Casteljau: the two halves of a piece at t."""
    left, right, pts = [piece[0]], [piece[-1]], list(piece)
    while len(pts) > 1:
        pts = [lerp(pts[i], pts[i + 1], t) for i in range(len(pts) - 1)]
        left.append(pts[0])
        right.append(pts[-1])
    return tuple(left), tuple(reversed(right))


def length(piece):
    prev, total = piece[0], 0.0
    for i in range(1, SAMPLES + 1):
        p = at(piece, i / SAMPLES)
        total += math.hypot(p[0] - prev[0], p[1] - prev[1])
        prev = p
    return total


def t_at(piece, d, from_end=False):
    """The parameter at arc length d from the start (or the end) of a piece."""
    if len(piece) == 2:
        L = length(piece)
        t = 0.0 if L == 0 else d / L
        return 1 - t if from_end else t
    acc, prev = 0.0, at(piece, 1.0 if from_end else 0.0)
    n = SAMPLES * 4
    for i in range(1, n + 1):
        t = 1 - i / n if from_end else i / n
        p = at(piece, t)
        step = math.hypot(p[0] - prev[0], p[1] - prev[1])
        if acc + step >= d:
            f = 0 if step == 0 else (d - acc) / step
            dt = (1 / n) * f
            return t + dt if from_end else t - (1 / n) + dt
        acc += step
        prev = p
    return 0.0 if from_end else 1.0


def unit(v):
    L = math.hypot(*v)
    return (0.0, 0.0) if L == 0 else (v[0] / L, v[1] / L)


# ------------------------------------------------------------------ contours
def parse(contour):
    """A closed contour as a list of segments (kind, offcurves, end), or None.

    Each segment starts where the one before it ends; the first starts at the
    end of the last.
    """
    pts = [(float(p.get('x')), float(p.get('y')), p.get('type'), p) for p in contour.findall('point')]
    ons = [i for i, p in enumerate(pts) if p[2]]
    if not ons or any(p[2] == 'move' for p in pts):
        return None
    k = ons[-1] + 1     # rotate so the list ends on an on-curve point
    pts = pts[k:] + pts[:k]
    segs, offs = [], []
    for x, y, typ, el in pts:
        if typ:
            segs.append({'kind': typ, 'offs': offs, 'end': (x, y), 'el': el})
            offs = []
        else:
            offs.append((x, y))
    return segs


def pieces(start, seg):
    """A segment as line, quadratic or cubic pieces with explicit ends."""
    kind, offs, end = seg['kind'], seg['offs'], seg['end']
    if kind == 'line' or not offs:
        return [(start, end)]
    if kind == 'curve':
        if len(offs) == 2:
            return [(start, offs[0], offs[1], end)]
        if len(offs) == 1:
            return [(start, offs[0], end)]
        raise ValueError('cubic segment with more than two offcurves')
    out, s = [], start           # qcurve: implied on-curves between offcurves
    for i, o in enumerate(offs):
        e = end if i == len(offs) - 1 else lerp(o, offs[i + 1], 0.5)
        out.append((s, o, e))
        s = e
    return out


def starts(segs):
    return [segs[i - 1]['end'] for i in range(len(segs))]


def polygon(segs):
    poly = []
    for s, seg in zip(starts(segs), segs):
        for pc in pieces(s, seg):
            n = 1 if len(pc) == 2 else 8
            poly += [at(pc, i / n) for i in range(n)]
    return poly


def signed_area(poly):
    n = len(poly)
    return sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1] for i in range(n)) / 2


def winding(poly, p):
    w, n = 0, len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        if a[1] <= p[1] < b[1] and (b[0] - a[0]) * (p[1] - a[1]) - (p[0] - a[0]) * (b[1] - a[1]) > 0:
            w += 1
        elif b[1] <= p[1] < a[1] and (b[0] - a[0]) * (p[1] - a[1]) - (p[0] - a[0]) * (b[1] - a[1]) < 0:
            w -= 1
    return w


def distance(poly, p):
    best, n = float('inf'), len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        vx, vy = b[0] - a[0], b[1] - a[1]
        L = vx * vx + vy * vy
        t = 0 if L == 0 else max(0, min(1, ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / L))
        best = min(best, math.hypot(p[0] - a[0] - t * vx, p[1] - a[1] - t * vy))
    return best


def join_edge(start, seg, width):
    """A vertical line at or past the glyph's edge: where a joining letter connects.

    Joining strokes run a little past the sidebearings and end in a vertical
    cut, so the neighbouring letter's stroke continues them without a seam.
    Rounding that cut would leave a notch at every join.
    """
    if seg['kind'] != 'line' and seg['offs']:
        return False
    (x0, _), (x1, _) = start, seg['end']
    return abs(x0 - x1) <= 1 and (max(x0, x1) <= 1 or min(x0, x1) >= width - 1)


def corners(segs, polys, ci, width):
    """For each on-curve point: (turn in degrees, convex, visible)."""
    own = polys[ci]
    orient = 1 if signed_area(own) > 0 else -1
    others = [p for j, p in enumerate(polys) if j != ci]
    out = []
    n = len(segs)
    for i in range(n):
        seg, nxt = segs[i], segs[(i + 1) % n]
        P = seg['end']
        prev_ctrl = seg['offs'][-1] if seg['offs'] else segs[i - 1]['end']
        next_ctrl = nxt['offs'][0] if nxt['offs'] else nxt['end']
        a, b = unit((P[0] - prev_ctrl[0], P[1] - prev_ctrl[1])), unit((next_ctrl[0] - P[0], next_ctrl[1] - P[1]))
        if a == (0, 0) or b == (0, 0):
            out.append((0.0, False, False))
            continue
        turn = math.degrees(math.atan2(a[0] * b[1] - a[1] * b[0], a[0] * b[0] + a[1] * b[1]))
        convex = turn * orient > 0
        # the corner shows only if exactly one of its two sides is filled
        w = sum(winding(p, P) for p in others)
        visible = (w == 0 or w + orient == 0) and all(distance(p, P) > TOL for p in others)
        if join_edge(segs[i - 1]['end'], seg, width) or join_edge(P, nxt, width):
            visible = False
        out.append((abs(turn), convex, visible))
    return out


# ------------------------------------------------------------------ rounding
def round_contour(contour, segs, chosen, stem):
    """Rebuild one contour with the chosen corners (indices of segment ends) filleted."""
    n = len(segs)
    st = starts(segs)
    pcs = [pieces(st[i], segs[i]) for i in range(n)]
    want = RADIUS * stem
    cut_end = [0.0] * n       # cut at the end of segment i (the corner at its end)
    cut_start = [0.0] * n     # cut at the start of segment i (the corner at its start)
    for i in chosen:
        j = (i + 1) % n
        last, first = pcs[i][-1], pcs[j][0]
        both_last = (i - 1) % n in chosen and len(pcs[i]) == 1
        both_first = j in chosen and len(pcs[j]) == 1
        d = min(want,
                length(last) * (0.47 if both_last else 0.8),
                length(first) * (0.47 if both_first else 0.8))
        cut_end[i] = cut_start[j] = d

    new = []      # (x, y, type, smooth, original element or None)
    for i in range(n):
        seg, ps = segs[i], list(pcs[i])
        trimmed = cut_start[i] > 0 or cut_end[i] > 0
        if cut_start[i] > 0:
            ps[0] = split(ps[0], t_at(ps[0], cut_start[i]))[1]
        if cut_end[i] > 0:
            ps[-1] = split(ps[-1], t_at(ps[-1], cut_end[i], from_end=True))[0]
        if not trimmed:
            for o in seg['offs']:
                new.append((o[0], o[1], None, False, None))
            new.append((*seg['end'], seg['kind'], None, seg['el']))
        else:
            for pc in ps:
                kind = {2: 'line', 3: 'qcurve', 4: 'curve'}[len(pc)]
                for o in pc[1:-1]:
                    new.append((o[0], o[1], None, False, None))
                new.append((*pc[-1], kind, True if pc is ps[-1] and cut_end[i] > 0 else None, None))
        if cut_end[i] > 0:   # the fillet from this segment's cut end to the next one's cut start
            P = seg['end']
            p1 = ps[-1][-1]
            nxt = pcs[(i + 1) % n][0]
            p2 = split(nxt, t_at(nxt, cut_start[(i + 1) % n]))[1][0]
            a = unit((P[0] - p1[0], P[1] - p1[1]))
            b = unit((p2[0] - P[0], p2[1] - P[1]))
            phi = math.atan2(a[0] * b[1] - a[1] * b[0], a[0] * b[0] + a[1] * b[1])
            phi = min(abs(phi), math.radians(170))
            k = 4 / 3 * math.tan(phi / 4) / math.tan(phi / 2)   # circular arc handle, per unit of cut
            d1 = math.hypot(P[0] - p1[0], P[1] - p1[1])
            d2 = math.hypot(p2[0] - P[0], p2[1] - P[1])
            new.append((p1[0] + a[0] * d1 * k, p1[1] + a[1] * d1 * k, None, False, None))
            new.append((p2[0] - b[0] * d2 * k, p2[1] - b[1] * d2 * k, None, False, None))
            new.append((p2[0], p2[1], 'curve', True, None))

    for p in list(contour):
        contour.remove(p)
    for x, y, typ, smooth, el in new:
        if el is not None and typ == el.get('type'):
            el.set('x', str(int(round(x))))
            el.set('y', str(int(round(y))))
            contour.append(el)
            continue
        attrs = {'x': str(int(round(x))), 'y': str(int(round(y)))}
        if typ:
            attrs['type'] = typ
            if smooth:
                attrs['smooth'] = 'yes'
        contour.append(ET.Element('point', attrs))


# ------------------------------------------------------------------ the family
def stem_of(ufo):
    """The master's vertical stem, read off the plain rectangle of the letter l."""
    root = ET.parse(os.path.join(ufo, 'glyphs', 'l.glif')).getroot()
    xs = sorted({float(p.get('x')) for p in root.iter('point')})
    return xs[-1] - xs[0]


def copy_family():
    src, dst = os.path.join(UFO, SRC_FAM), os.path.join(UFO, DST_FAM)
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    os.makedirs(dst)
    for m in MASTERS:
        to = os.path.join(dst, f'{DST_FAM}-{m}.ufo')
        shutil.copytree(os.path.join(src, f'{SRC_FAM}-{m}.ufo'), to)
        p = os.path.join(to, 'fontinfo.plist')
        info = plistlib.load(open(p, 'rb'))
        sub = lambda s: s.replace(SRC_FAM, DST_FAM).replace(SRC_NAME, DST_NAME) if isinstance(s, str) else s
        for k in ('familyName', 'styleMapFamilyName', 'openTypeNamePreferredFamilyName',
                  'openTypeNameUniqueID', 'postscriptFontName'):
            if k in info:
                info[k] = sub(info[k])
        for rec in info.get('openTypeNameRecords', []):
            rec['string'] = sub(rec['string'])
        plistlib.dump(info, open(p, 'wb'))
    tree = ET.parse(os.path.join(src, f'{SRC_FAM}.designspace'))
    for el in tree.getroot().iter():
        for k in ('filename', 'familyname', 'name'):
            if k in el.attrib:
                el.set(k, el.get(k).replace(SRC_FAM, DST_FAM).replace(SRC_NAME, DST_NAME))
    tree.write(os.path.join(dst, f'{DST_FAM}.designspace'), encoding='UTF-8', xml_declaration=True)
    return dst


def main():
    dst = copy_family()
    ufos = {m: os.path.join(dst, f'{DST_FAM}-{m}.ufo') for m in MASTERS}
    stems = {m: stem_of(u) for m, u in ufos.items()}
    names = sorted(n for n in os.listdir(os.path.join(ufos['Regular'], 'glyphs')) if n.endswith('.glif'))
    rounded_glyphs = rounded_corners = 0
    for name in names:
        trees, conts, parsed = {}, {}, {}
        for m in MASTERS:
            path = os.path.join(ufos[m], 'glyphs', name)
            tree = ET.parse(path)
            outline = tree.getroot().find('outline')
            cs = [] if outline is None else [c for c in outline if c.tag == 'contour']
            trees[m], conts[m] = (tree, path), cs
            parsed[m] = [parse(c) for c in cs]
        sig = {m: [None if s is None else [(g['kind'], len(g['offs'])) for g in s] for s in parsed[m]]
               for m in MASTERS}
        if len({repr(v) for v in sig.values()}) != 1:
            print(f'  {name}: masters differ in structure, left as is')
            continue
        if not conts['Regular']:
            continue
        info = {}
        for m in MASTERS:
            adv = trees[m][0].getroot().find('advance')
            width = float(adv.get('width', 0)) if adv is not None else 0.0
            polys = [[] if s is None else polygon(s) for s in parsed[m]]
            info[m] = [None if s is None else corners(s, polys, ci, width) for ci, s in enumerate(parsed[m])]
        plan = {}
        for ci, segs in enumerate(parsed['Regular']):
            if segs is None:
                continue
            chosen = set()
            for k in range(len(segs)):
                rows = [info[m][ci][k] for m in MASTERS]
                if (max(r[0] for r in rows) > TURN and all(r[2] for r in rows)
                        and all(r[1] for r in rows if r[0] > 1)):
                    chosen.add(k)
            if chosen:
                plan[ci] = chosen
        if not plan:
            continue
        for m in MASTERS:
            for ci, chosen in plan.items():
                round_contour(conts[m][ci], parsed[m][ci], chosen, stems[m])
            tree, path = trees[m]
            ET.indent(tree.getroot(), space='  ')
            tree.write(path, encoding='UTF-8', xml_declaration=True)
        rounded_glyphs += 1
        rounded_corners += sum(len(c) for c in plan.values())
    print(f'{DST_NAME}: rounded {rounded_corners} corners in {rounded_glyphs} glyphs '
          f'(stems {", ".join(f"{m} {stems[m]:g}" for m in MASTERS)})')


if __name__ == '__main__':
    main()
