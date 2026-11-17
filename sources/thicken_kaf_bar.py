#!/usr/bin/env python3
"""Bring the upper bar of kaf and gaf up to the nominal stroke weight.

    python3 -I sources/thicken_kaf_bar.py            # report, change nothing
    python3 -I sources/thicken_kaf_bar.py --write    # apply to sources/ufo

Every ک/گ-shaped glyph draws that bar as the point run

    A (qcurve, inner apex) -L-> B -L-> C -L-> D -off-off-> F -off-off-> E

with A..B the bar's lower edge, B..C the vertical terminal, D..C the upper edge
and D..F..E the rounded outer apex where the bar turns into the diagonal arm.
The bar came out of Vazirmatn at about 80% of the weight of every other stroke
in the glyph (147 against 182 in Dastkhat Regular), which reads as a thin spot.

The fix raises the upper edge by a constant vertical lift, so the bar keeps the
angle and the slight taper it was drawn with. The lower edge, the diagonal arm
and the bowl do not move. Anything floating above the bar -- gaf's sarkesh, the
dots of ݢ and ݣ -- moves up by the same lift so its gap is unchanged, and the
apex points between D and E take a share of the lift that fades out at E.

The target weight is read per master from the horizontal bar of uniFB90
(initial kaf), so the script follows whatever weight the master is drawn at.
It only touches bars that measure under 95% of that, so it is idempotent.
"""
import math
import os
import plistlib
import re
import sys
import xml.etree.ElementTree as ET

FAMILIES = ['Dastkhat', 'DastkhatDiamond', 'DastkhatBar',
            'DastkhatDots', 'DastkhatBarDots']
MASTERS = ['Thin', 'Regular', 'Black']
UFO_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ufo')


def read_glif(path):
    """-> [contour], each a list of (x, y, type); type is None for off-curve."""
    outline = ET.parse(path).getroot().find('outline')
    if outline is None:
        return []
    return [[(float(p.get('x')), float(p.get('y')), p.get('type'))
             for p in c.findall('point')] for c in outline.findall('contour')]


def find_bars(contours):
    """Yield (contour index, index of A, current perpendicular bar weight)."""
    for ci, pts in enumerate(contours):
        n = len(pts)
        for i in range(n):
            a, b, c, d = (pts[(i + k) % n] for k in range(4))
            if (a[2], b[2], c[2], d[2]) != ('qcurve', 'line', 'line', 'line'):
                continue
            if abs(b[0] - c[0]) > 1 or c[1] <= b[1] or d[0] >= b[0] - 100:
                continue
            dx, dy = c[0] - d[0], c[1] - d[1]
            length = math.hypot(dx, dy)
            if length < 100:
                continue
            off = lambda p: abs(dx * (p[1] - d[1]) - dy * (p[0] - d[0])) / length
            yield ci, i, (off(a) + off(b)) / 2


def edits_for_glyph(contours, target):
    """-> {contour index: {point index: (x, y)}}; empty when nothing is thin."""
    edits = {}
    for ci, i, weight in find_bars(contours):
        if weight >= target * 0.95:
            continue
        pts = contours[ci]
        n = len(pts)
        at = lambda k: (i + k) % n
        c, d = pts[at(2)], pts[at(3)]
        dx, dy = c[0] - d[0], c[1] - d[1]
        lift = round((target - weight) * math.hypot(dx, dy) / abs(dx))

        points = edits.setdefault(ci, {})
        points[at(2)] = (c[0], c[1] + lift)
        points[at(3)] = (d[0], d[1] + lift)

        # fade the lift out across the outer apex, to zero at the 2nd on-curve
        seen = k = 0
        while seen < 2:
            k += 1
            if k > 3 and pts[at(k)][2] is not None:
                seen += 1
        end = pts[at(k)]
        span = d[1] - end[1]
        for j in range(4, k):
            x, y, _ = pts[at(j)]
            points[at(j)] = (x, y + lift * (y - end[1]) / span)

        # carry the sarkesh and the dots above the bar up with it
        lo, hi = min(d[0], c[0]), max(d[0], c[0])
        for cj, other in enumerate(contours):
            if cj == ci:
                continue
            xs = [p[0] for p in other]
            if max(xs) < lo or min(xs) > hi:
                continue
            if any(dx * (p[1] - d[1]) - dy * (p[0] - d[0]) <= 0 for p in other):
                continue
            edits.setdefault(cj, {}).update(
                {j: (p[0], p[1] + lift) for j, p in enumerate(other)})
    return edits


def patch_file(path, edits):
    """Rewrite only the x/y attributes named in edits, leaving the file as-is."""
    src = open(path, encoding='utf-8').read()
    pieces, last = [], 0
    for ci, cm in enumerate(re.finditer(r'<contour>.*?</contour>', src, re.S)):
        if ci not in edits:
            continue
        body, parts, lb = cm.group(0), [], 0
        for pi, pm in enumerate(re.finditer(r'<point [^/]*/>', body)):
            if pi not in edits[ci]:
                continue
            x, y = edits[ci][pi]
            tag = re.sub(r'x="[-\d.]+"', 'x="%d"' % round(x), pm.group(0))
            tag = re.sub(r'y="[-\d.]+"', 'y="%d"' % round(y), tag)
            parts.append(body[lb:pm.start()] + tag)
            lb = pm.end()
        parts.append(body[lb:])
        pieces.append(src[last:cm.start()] + ''.join(parts))
        last = cm.end()
    pieces.append(src[last:])
    open(path, 'w', encoding='utf-8').write(''.join(pieces))


def main(write):
    total = 0
    for family in FAMILIES:
        for master in MASTERS:
            glyphs = os.path.join(
                UFO_ROOT, family, f'{family}-{master}.ufo', 'glyphs')
            if not os.path.isdir(glyphs):
                print(f'{family}-{master}: no UFO, skipped')
                continue
            index = plistlib.load(open(os.path.join(glyphs, 'contents.plist'), 'rb'))
            ref = read_glif(os.path.join(glyphs, index['uniFB90']))[0]
            target = ref[20][1] - ref[21][1]   # initial kaf's horizontal bar
            names = []
            for name, filename in sorted(index.items()):
                path = os.path.join(glyphs, filename)
                edits = edits_for_glyph(read_glif(path), target)
                if not edits:
                    continue
                names.append(name)
                if write:
                    patch_file(path, edits)
            total += len(names)
            print(f'{family}-{master}: nominal weight {target:.0f}, '
                  f'{len(names)} glyphs')
    print(f'{total} glyphs {"rewritten" if write else "to rewrite (dry run)"}')


if __name__ == '__main__':
    main('--write' in sys.argv[1:])
