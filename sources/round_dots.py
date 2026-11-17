"""Derive the round-dot Dastkhat families from the square and bar UFO masters.

    sources/ufo/Dastkhat      ->  sources/ufo/DastkhatDots      (Dastkhat Dots)
    sources/ufo/DastkhatBar   ->  sources/ufo/DastkhatBarDots   (Dastkhat BarDots)

Every square dot becomes a circle of the same area, and every bar becomes the
capsule those circles would form if they merged, so the round families keep the
metrics, spacing, kerning and features of the families they come from. A circle
of the square's own width would carry only 79% of its area and read as a lighter,
smaller dot, so the circle is GROW times wider than the square instead.

Finding the dots: the square and the diamond masters differ only where a dot
sits, so the contours of Dastkhat-<w>.ufo that differ from DastkhatDiamond-<w>.ufo
are exactly its dots. In DastkhatBar the untouched contours of a glyph come
first and the bars last, so the bars are the contours past the untouched ones.

Usage: python3 -I sources/round_dots.py [sources/ufo]
Re-runnable: the two output families are rewritten from scratch each time.
"""
import os, sys, shutil, plistlib, math
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
UFO = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(HERE, 'ufo')
MASTERS = ('Thin', 'Regular', 'Black')
K = 0.5522847498307936        # circle-to-cubic constant
GROW = 2 / math.sqrt(math.pi)  # a circle this much wider than a square has the same area


# ---------------------------------------------------------------- glif helpers
def read(path):
    tree = ET.parse(path)
    root = tree.getroot()
    outline = root.find('outline')
    contours = [] if outline is None else [c for c in outline if c.tag == 'contour']
    return tree, root, outline, contours


def points(contour):
    return [(float(p.get('x')), float(p.get('y')), p.get('type')) for p in contour.findall('point')]


def norm(contour):
    """A contour's points with its position taken out, for comparing shapes."""
    pts = points(contour)
    x0 = min(p[0] for p in pts)
    y0 = min(p[1] for p in pts)
    return [(x - x0, y - y0, t) for x, y, t in pts]


def alike(a, b, tol=4):
    """True when two contours draw the same shape.

    Two families draw the same letter at the same size, but a glyph assembled
    from other glyphs can sit a few units apart in one of them and round to
    slightly different coordinates, so position is ignored and a few units of
    difference are allowed. A square dot and a diamond one are nowhere near
    this close, so dots never match.
    """
    if len(a) != len(b):
        return False
    return all(t1 == t2 and abs(x1 - x2) <= tol and abs(y1 - y2) <= tol
               for (x1, y1, t1), (x2, y2, t2) in zip(a, b))


def unmatched(contours, pool):
    """Indices of `contours` that nothing in `pool` draws; each pool contour matches once."""
    free = [norm(c) for c in pool]
    used = [False] * len(free)
    out = []
    for i, c in enumerate(contours):
        n = norm(c)
        for j, f in enumerate(free):
            if not used[j] and alike(n, f):
                used[j] = True
                break
        else:
            out.append(i)
    return out


def box(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def area(pts):
    n = len(pts)
    return sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n)) / 2


def is_rect(pts):
    """A 4-point axis-aligned rectangle of straight segments."""
    if len(pts) != 4 or any(t != 'line' for _, _, t in pts):
        return False
    xs = sorted({p[0] for p in pts})
    ys = sorted({p[1] for p in pts})
    return len(xs) == 2 and len(ys) == 2


def is_dot(pts):
    """A dot of the square family: a rectangle that is square but for rounding.

    It tells a dot apart from the other rectangles a glyph may be drawn with,
    such as the crossbars of the toman and rial signs, which are far wider than
    they are tall and belong to the mark rather than to its dots.
    """
    if not is_rect(pts):
        return False
    x0, y0, x1, y1 = box(pts)
    return abs((x1 - x0) - (y1 - y0)) <= 2


def num(v):
    return str(int(round(v)))


def build(contour, pts):
    """Replace a contour's points, keeping the element itself."""
    for p in list(contour):
        contour.remove(p)
    for x, y, typ in pts:
        a = {'x': num(x), 'y': num(y)}
        if typ:
            a['type'] = typ
            a['smooth'] = 'yes'
        contour.append(ET.Element('point', a))


def circle(cx, cy, r, ccw):
    """Four cubic segments, starting at the point on the right (or left, if clockwise)."""
    k = r * K
    e, n, w, s = (cx + r, cy), (cx, cy + r), (cx - r, cy), (cx, cy - r)
    if ccw:
        quads = [(e, (cx + r, cy + k), (cx + k, cy + r), n),
                 (n, (cx - k, cy + r), (cx - r, cy + k), w),
                 (w, (cx - r, cy - k), (cx - k, cy - r), s),
                 (s, (cx + k, cy - r), (cx + r, cy - k), e)]
    else:
        quads = [(e, (cx + r, cy - k), (cx + k, cy - r), s),
                 (s, (cx - k, cy - r), (cx - r, cy - k), w),
                 (w, (cx - r, cy + k), (cx - k, cy + r), n),
                 (n, (cx + k, cy + r), (cx + r, cy + k), e)]
    # a 'curve' point closes the segment its two preceding offcurves describe,
    # wrapping around the closed contour for the first one
    pts = []
    for start, c1, c2, _end in quads:
        pts.append((start[0], start[1], 'curve'))
        pts.append((c1[0], c1[1], None))
        pts.append((c2[0], c2[1], None))
    return pts


def axis(x0, y0, x1, y1, wide):
    """A rounded shape as its centre segment and its radius before growing.

    A circle's segment is a point; a capsule's runs between the centres of the
    two end arcs, which are where the bar's own end dots sat. Growing the shape
    moves neither, so the distance between two shapes' axes does not change.
    """
    cy = (y0 + y1) / 2.0
    if wide:
        r = (y1 - y0) / 2.0
        return (x0 + r, cy), (x1 - r, cy), r
    c = ((x0 + x1) / 2.0, cy)
    return c, c, (x1 - x0 + y1 - y0) / 4.0


def seg_gap(a0, a1, b0, b1):
    """Shortest distance between two segments."""
    def dot_seg(p, s0, s1):
        vx, vy = s1[0] - s0[0], s1[1] - s0[1]
        L = vx * vx + vy * vy
        t = 0.0 if L == 0 else max(0.0, min(1.0, ((p[0] - s0[0]) * vx + (p[1] - s0[1]) * vy) / L))
        return math.hypot(p[0] - (s0[0] + t * vx), p[1] - (s0[1] + t * vy))
    return min(dot_seg(a0, b0, b1), dot_seg(a1, b0, b1), dot_seg(b0, a0, a1), dot_seg(b1, a0, a1))


def box_gap(p, q):
    """Space between two boxes, counting a diagonal pair by its widest axis."""
    return max(max(p[0] - q[2], q[0] - p[2]), max(p[1] - q[3], q[1] - p[3]))


def growth(shapes, boxes):
    """How far the shapes of one glyph may grow without closing on each other.

    Rounding must never bring two shapes closer than the squares and bars they
    replace were, so each pair caps the growth and the whole glyph takes the
    smallest cap. One factor for the glyph keeps its dots the same size.
    """
    g = GROW
    for i in range(len(shapes)):
        for j in range(i + 1, len(shapes)):
            (a0, a1, ra), (b0, b1, rb) = shapes[i], shapes[j]
            room = seg_gap(a0, a1, b0, b1) - box_gap(boxes[i], boxes[j])
            if ra + rb > 0:
                g = min(g, room / (ra + rb))
    return max(1.0, g)


def capsule(x0, y0, x1, y1, ccw, grow):
    """The capsule the bar's dots form once they are grown into circles and merge.

    The end arcs keep the centres the bar's own end dots had, and the radius
    grows with them, so the capsule is as thick as a lone circular dot.
    """
    a, b = x0 + (y1 - y0) / 2.0, x1 - (y1 - y0) / 2.0   # centres of the two end arcs
    r = grow * (y1 - y0) / 2.0
    cy = (y0 + y1) / 2.0
    y0, y1 = cy - r, cy + r
    x0, x1 = a - r, b + r
    k = r * K
    if ccw:
        return [(a, y0, 'curve'),                       # end of the left arc
                (b, y0, 'line'),                        # along the bottom
                (b + k, y0, None), (x1, cy - k, None),
                (x1, cy, 'curve'),                      # right arc, lower half
                (x1, cy + k, None), (b + k, y1, None),
                (b, y1, 'curve'),                       # right arc, upper half
                (a, y1, 'line'),                        # back along the top
                (a - k, y1, None), (x0, cy + k, None),
                (x0, cy, 'curve'),                      # left arc, upper half
                (x0, cy - k, None), (a - k, y0, None)]  # left arc, lower half -> first point
    return [(a, y1, 'curve'),
            (b, y1, 'line'),
            (b + k, y1, None), (x1, cy + k, None),
            (x1, cy, 'curve'),
            (x1, cy - k, None), (b + k, y0, None),
            (b, y0, 'curve'),
            (a, y0, 'line'),
            (a - k, y0, None), (x0, cy - k, None),
            (x0, cy, 'curve'),
            (x0, cy + k, None), (a - k, y1, None)]


# ------------------------------------------------------------------ the families
def dot_indices(square_ufo, diamond_ufo, name):
    """Indices of the dot contours of one glyph, from square vs diamond.

    The two families draw the same letter and differ only where a dot sits, so
    a contour of the square glyph that the diamond glyph also has is part of the
    letter and anything else is a dot. Contours are matched by value, since the
    two families do not always hold them in the same order.
    """
    other = os.path.join(diamond_ufo, 'glyphs', name)
    if not os.path.exists(other):
        raise SystemExit(f'{name} is in the square masters but not the diamond ones; '
                         'the families have drifted apart')
    _, _, _, cs = read(os.path.join(square_ufo, 'glyphs', name))
    _, _, _, cd = read(other)
    # anything else left over is the same letter drawn a unit or two apart
    return [i for i in unmatched(cs, cd) if is_dot(points(cs[i]))]


def to_round(square, idx, out):
    """Indices of the contours of `out` that are dots or bars.

    A glyph's untouched contours are the same in every family, so whatever is
    left of `out` once each of them is matched away is a dot or a bar. Matching
    by value rather than by position keeps a drawn rectangle that belongs to the
    letter, such as the crossbar of the currency signs, out of the result.
    """
    dots = set(idx)
    return unmatched(out, [c for i, c in enumerate(square) if i not in dots])


def copy_family(src_fam, dst_fam, dst_name):
    src = os.path.join(UFO, src_fam)
    dst = os.path.join(UFO, dst_fam)
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    os.makedirs(dst)
    for m in MASTERS:
        shutil.copytree(os.path.join(src, f'{src_fam}-{m}.ufo'), os.path.join(dst, f'{dst_fam}-{m}.ufo'))
        rename_master(os.path.join(dst, f'{dst_fam}-{m}.ufo'), src_fam, dst_fam, dst_name, m)
    write_designspace(src, dst, src_fam, dst_fam, dst_name)
    return dst


def rename_master(path, src_fam, dst_fam, dst_name, style):
    """Point every family name in fontinfo.plist at the new family."""
    old_name = {'Dastkhat': 'Dastkhat', 'DastkhatBar': 'Dastkhat Bar'}[src_fam]
    p = os.path.join(path, 'fontinfo.plist')
    info = plistlib.load(open(p, 'rb'))

    def sub(s):
        return (s.replace(f'{src_fam}-{style}', f'{dst_fam}-{style}')
                 .replace(f'{old_name} {style}', f'{dst_name} {style}')
                 .replace(old_name, dst_name) if isinstance(s, str) else s)

    for k in ('familyName', 'styleMapFamilyName', 'openTypeNamePreferredFamilyName',
              'openTypeNameUniqueID', 'postscriptFontName'):
        if k in info:
            info[k] = sub(info[k])
    for rec in info.get('openTypeNameRecords', []):
        if rec.get('nameID') in (1, 3, 4, 6, 16, 25):
            rec['string'] = sub(rec['string'])
    plistlib.dump(info, open(p, 'wb'))


def write_designspace(src, dst, src_fam, dst_fam, dst_name):
    old_name = {'Dastkhat': 'Dastkhat', 'DastkhatBar': 'Dastkhat Bar'}[src_fam]
    tree = ET.parse(os.path.join(src, f'{src_fam}.designspace'))
    root = tree.getroot()
    for el in root.iter():
        if 'filename' in el.attrib:
            el.set('filename', el.get('filename').replace(f'{src_fam}-', f'{dst_fam}-'))
        if 'familyname' in el.attrib:
            el.set('familyname', dst_name)
        if 'name' in el.attrib and el.tag == 'instance':
            el.set('name', el.get('name').replace(old_name, dst_name))
    ET.indent(root, space='  ')
    tree.write(os.path.join(dst, f'{dst_fam}.designspace'), encoding='UTF-8', xml_declaration=True)


def round_dots(square_fam, src_fam, dst_fam, dst_name):
    """Build one round family. Dots come from the square master, bars from src_fam."""
    square = os.path.join(UFO, square_fam)
    diamond = os.path.join(UFO, 'DastkhatDiamond')
    dst = copy_family(src_fam, dst_fam, dst_name)
    names = sorted(n for n in os.listdir(os.path.join(square, f'{square_fam}-Regular.ufo', 'glyphs'))
                   if n.endswith('.glif'))

    # topology has to match across masters, so decide circle vs capsule from all three
    shape = {}
    plans = {}
    for m in MASTERS:
        squ = os.path.join(square, f'{square_fam}-{m}.ufo')
        dia = os.path.join(diamond, f'DastkhatDiamond-{m}.ufo')
        out = os.path.join(dst, f'{dst_fam}-{m}.ufo')
        for name in names:
            idx = dot_indices(squ, dia, name)
            if not idx:
                continue
            _, _, _, cs = read(os.path.join(squ, 'glyphs', name))
            _, _, _, co = read(os.path.join(out, 'glyphs', name))
            rounds = to_round(cs, idx, co)
            plans.setdefault((m, name), rounds)
            for j in rounds:
                pts = points(co[j])
                if not is_rect(pts):
                    raise SystemExit(f'{name} in {dst_fam}-{m}: contour {j} is not a rectangle')
                x0, y0, x1, y1 = box(pts)
                # a dot is square give or take a unit of rounding; a bar is far wider
                shape.setdefault((name, j), set()).add((x1 - x0) > 1.25 * (y1 - y0))

    changed = 0
    for m in MASTERS:
        out = os.path.join(dst, f'{dst_fam}-{m}.ufo')
        for name in names:
            rounds = plans.get((m, name))
            if not rounds:
                continue
            path = os.path.join(out, 'glyphs', name)
            tree, root, outline, co = read(path)
            boxes, wides = [], []
            for j in rounds:
                boxes.append(box(points(co[j])))
                wide = shape[(name, j)]
                if len(wide) != 1:
                    raise SystemExit(f'{name} contour {j}: square in one master, wide in another')
                wides.append(next(iter(wide)))
            grow = growth([axis(*b, w) for b, w in zip(boxes, wides)], boxes)
            for j, (x0, y0, x1, y1), wide in zip(rounds, boxes, wides):
                ccw = area(points(co[j])) > 0
                if wide:
                    build(co[j], capsule(x0, y0, x1, y1, ccw, grow))
                else:   # the square is within a unit of true; average the two sides
                    build(co[j], circle((x0 + x1) / 2, (y0 + y1) / 2,
                                        grow * (x1 - x0 + y1 - y0) / 4, ccw))
            ET.indent(root, space='  ')
            tree.write(path, encoding='UTF-8', xml_declaration=True)
            changed += 1
    print(f'{dst_name}: rounded {changed // len(MASTERS)} glyphs in {len(MASTERS)} masters')


if __name__ == '__main__':
    round_dots('Dastkhat', 'Dastkhat', 'DastkhatDots', 'Dastkhat Dots')
    round_dots('Dastkhat', 'DastkhatBar', 'DastkhatBarDots', 'Dastkhat BarDots')
