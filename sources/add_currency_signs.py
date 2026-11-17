"""Generate the Dastkhat toman and rial currency signs into the UFO sources.

Adds three glyphs to every master of every family:

    tomansign        U+E000   «ت» whose two dots stretch into the two bars of a
                              currency sign (=). Dastkhat Bar already merges dots
                              into bars; here they become the "=" of ₹ € ¥.
    rialsign         U+E001   «ا» and «ل» as two stems, crossed by a rising «ر».
                              The same reading as the Saudi riyal sign and the
                              #تایپوپول sketches: the word reduced to its strokes.
    tomansign.word   U+E002   «ن» stacked over «توما», the toman icon Iranian
                              sites already use, redrawn in Dastkhat letters.
                              It pairs with the standard rial sign ﷼ U+FDFC.

Nothing is drawn freehand: every sign is built from the outlines of real letters
in the master it is written into, so proportion and dot style (square, diamond,
bar, circle, circle bar) follow the family. The only drawn parts are the bars
and stems, one dot or one stem thick. The stacked sign is scaled down, so its
letters are taken from a heavier interpolation of the family's masters first,
which keeps its strokes as thick as the text around it.

Toman has no Unicode code point (UTC rejected L2/17-060 in 2017), hence the
Private Use Area. ﷼ U+FDFC itself is left as it is.

Usage: python3 -I sources/add_currency_signs.py [repo_root]   (needs fonttools)
"""
import math
import os
import sys
import xml.etree.ElementTree as ET

from fontTools.misc import plistlib        # writes plists the way ufoLib does

FAMILIES = ('Dastkhat', 'DastkhatDiamond', 'DastkhatBar', 'DastkhatDots', 'DastkhatBarDots')
WEIGHTS = ('Thin', 'Regular', 'Black')

# glyphs the new signs are built from
TEH = 'uni062A'           # ت isolated
REH = 'uni0631'           # ر isolated
NOON = 'uni0646'          # ن isolated; its single dot is the family's dot shape
ALEF = 'uni0627'          # ا isolated, a plain vertical bar: gives us the stem width
ONE = 'uni06F1'           # ۱, whose height is the digit height the signs line up with
STACK_ROW = ('uniFE8E', 'uniFEE3', 'uniFEEE', 'uniFE97')   # ـا مـ ـو تـ, left to right

# Shaped glyph sequences, in logical order, for the two words. ss02/ss03 run after
# the Arabic shaper has picked positional forms, so these are the joined shapes.
TOMAN_SEQ = 'uniFE97 uniFEEE uniFEE3 uniFE8E uni0646'          # تـ ـو مـ ـا ن
RIAL_SEQS = ('uni0631 uniFBFE uniFE8E uni0644',                # ر یـ ـا ل, Persian yeh U+06CC
             'uni0631 uniFEF3 uniFE8E uni0644')                # the same with Arabic yeh U+064A

FEATURE_MARK = '# --- Dastkhat currency signs'

FEATURE_CODE = f'''

{FEATURE_MARK} ---------------------------------------------
# ss02 turns the typed words into the compact signs, ss03 into the word signs.
# Both are opt-in: nothing changes unless the feature is switched on.

lookup CurrencySignCompact {{
    lookupflag 0;
    sub {TOMAN_SEQ} by tomansign;
    sub {RIAL_SEQS[0]} by rialsign;
    sub {RIAL_SEQS[1]} by rialsign;
}} CurrencySignCompact;

lookup CurrencySignWord {{
    lookupflag 0;
    sub {TOMAN_SEQ} by tomansign.word;
    sub {RIAL_SEQS[0]} by uniFDFC;
    sub {RIAL_SEQS[1]} by uniFDFC;
}} CurrencySignWord;

feature ss02 {{
    featureNames {{ name "Toman and rial signs"; }};
    script DFLT;
    language dflt;
            lookup CurrencySignCompact;
}} ss02;

feature ss02 {{
    script arab;
    language dflt;
            lookup CurrencySignCompact;
    language URD;
            lookup CurrencySignCompact;
}} ss02;

feature ss03 {{
    featureNames {{ name "Toman and rial word signs"; }};
    script DFLT;
    language dflt;
            lookup CurrencySignWord;
}} ss03;

feature ss03 {{
    script arab;
    language dflt;
            lookup CurrencySignWord;
    language URD;
            lookup CurrencySignWord;
}} ss03;
'''

# tomansign: two bars where the dots were, in units of the family's dot size
TOMAN_BAR = 0.78          # bar thickness
TOMAN_GAP = 0.55          # gap between the bars
TOMAN_LIFT = 0.25         # gap between the bowl and the lower bar
TOMAN_INSET = 0.16        # each bar is inset from the bowl ends by this share of its width

# rialsign: two stems crossed by ر, in units of the stem
RIAL_GAP = 1.25           # gap between the stems
RIAL_TILT = -38           # degrees ر is turned so its arm becomes a rising stroke
RIAL_SHIFT = 0.15         # nudge of ر to the left of the stems' centre
RIAL_HEIGHT = 0.47        # centre of ر, as a share of digit height

# tomansign.word: scale of the stacked letters, and how far past Black we may
# extrapolate to find heavy enough letters (beyond this Black comes out lighter)
STACK_SCALE = 0.60
STACK_MAX_EXTRAPOLATION = 1.35
STACK_NOON_FLOOR = 1180   # ن sits on this line, in unscaled units
SIDEBEARING = 0.6         # sidebearings, in stems; matches the digits


# ---------------------------------------------------------------- glif I/O

def contents_path(ufo):
    return os.path.join(ufo, 'glyphs', 'contents.plist')


def read_contents(ufo):
    return load_plist(contents_path(ufo))


def load_plist(path):
    with open(path, 'rb') as fh:
        return plistlib.load(fh)


def dump_plist(path, data):
    with open(path, 'wb') as fh:
        plistlib.dump(data, fh)


def read_glyph(ufo, name):
    """Return (advance_width, [contour, ...]); a contour is [(x, y, type), ...]."""
    fn = read_contents(ufo)[name]
    root = ET.parse(os.path.join(ufo, 'glyphs', fn)).getroot()
    adv = root.find('advance')
    width = float(adv.get('width')) if adv is not None and adv.get('width') else 0.0
    contours = []
    outline = root.find('outline')
    if outline is not None:
        for el in outline.findall('contour'):
            contours.append([(float(p.get('x')), float(p.get('y')), p.get('type'))
                             for p in el.findall('point')])
    return width, contours


def shift(contours, dx=0.0, dy=0.0):
    return [[(x + dx, y + dy, t) for x, y, t in c] for c in contours]


def bbox(contours):
    xs = [x for c in contours for x, _, _ in c]
    ys = [y for c in contours for _, y, _ in c]
    return min(xs), min(ys), max(xs), max(ys)


def rect(x0, y0, x1, y1):
    # counter-clockwise, matching the direction of the outer contours in these sources,
    # so the bar merges with the letter instead of punching a hole in it
    return [(x0, y0, 'line'), (x1, y0, 'line'), (x1, y1, 'line'), (x0, y1, 'line')]


def write_glyph(ufo, name, codepoint, width, contours):
    g = ET.Element('glyph', {'name': name, 'format': '2'})
    ET.SubElement(g, 'advance', {'width': f'{round(width)}'})
    if codepoint is not None:
        ET.SubElement(g, 'unicode', {'hex': f'{codepoint:04X}'})
    outline = ET.SubElement(g, 'outline')
    for c in contours:
        el = ET.SubElement(outline, 'contour')
        for x, y, t in c:
            attrs = {'x': f'{round(x)}', 'y': f'{round(y)}'}
            if t:
                attrs['type'] = t
            ET.SubElement(el, 'point', attrs)
    ET.indent(g, '  ')
    xml = ("<?xml version='1.0' encoding='UTF-8'?>\n"
           + ET.tostring(g, encoding='unicode') + '\n')

    fn = name + '.glif'
    open(os.path.join(ufo, 'glyphs', fn), 'w').write(xml)

    c = read_contents(ufo)
    c[name] = fn
    dump_plist(contents_path(ufo), dict(sorted(c.items())))
    return fn


def add_features(ufo):
    path = os.path.join(ufo, 'features.fea')
    text = open(path).read()
    if FEATURE_MARK in text:
        text = text[:text.index(FEATURE_MARK)].rstrip('\n#- ')
    open(path, 'w').write(text.rstrip('\n') + FEATURE_CODE)


def add_to_glyph_order(ufo, names):
    path = os.path.join(ufo, 'lib.plist')
    lib = load_plist(path)
    order = lib.get('public.glyphOrder', [])
    for n in names:
        if n not in order:
            order.append(n)
    lib['public.glyphOrder'] = order
    dump_plist(path, lib)


# ---------------------------------------------------------------- geometry

def transform(contours, a=1.0, b=0.0, c=0.0, d=1.0, e=0.0, f=0.0):
    return [[(a * x + c * y + e, b * x + d * y + f, t) for x, y, t in k] for k in contours]


def rotate(contours, degrees, cx, cy):
    r = math.radians(degrees)
    co, si = math.cos(r), math.sin(r)
    return [[(cx + (x - cx) * co - (y - cy) * si, cy + (x - cx) * si + (y - cy) * co, t)
             for x, y, t in k] for k in contours]


def area(contour):
    return 0.5 * sum(x0 * y1 - x1 * y0 for (x0, y0, _), (x1, y1, _)
                     in zip(contour, contour[1:] + contour[:1]))


def with_sidebearings(contours, sb):
    x0, _, x1, _ = bbox(contours)
    return x1 - x0 + 2 * sb, shift(contours, dx=sb - x0)


class Master:
    """One UFO, plus the measurements the signs are built from."""

    def __init__(self, root, fam, weight):
        self.root, self.fam = root, fam
        self.ufo = ufo_path(root, fam, weight)
        x0, _, x1, _ = bbox(read_glyph(self.ufo, ALEF)[1])
        self.stem = x1 - x0
        self.digit_height = bbox(read_glyph(self.ufo, ONE)[1])[3]
        dot = read_glyph(self.ufo, NOON)[1][-1]
        self.dot = math.sqrt(abs(area(dot)))     # side of a square of the same area, so
                                                 # diamonds and circles size like squares

    def glyph(self, name):
        return read_glyph(self.ufo, name)

    def heavier(self, name, stem):
        """Outlines of `name` at the weight whose stem is `stem`, interpolated between
        this family's masters (they are point-compatible)."""
        st = {w: bbox(read_glyph(ufo_path(self.root, self.fam, w), ALEF)[1]) for w in WEIGHTS}
        st = {w: b[2] - b[0] for w, b in st.items()}
        if stem <= st['Regular']:
            a, b, t = 'Thin', 'Regular', (stem - st['Thin']) / (st['Regular'] - st['Thin'])
        else:
            a, b = 'Regular', 'Black'
            t = min((stem - st['Regular']) / (st['Black'] - st['Regular']), STACK_MAX_EXTRAPOLATION)
        c0 = read_glyph(ufo_path(self.root, self.fam, a), name)[1]
        c1 = read_glyph(ufo_path(self.root, self.fam, b), name)[1]
        assert [len(k) for k in c0] == [len(k) for k in c1], f'{name} not compatible'
        return [[(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, ty)
                 for (x0, y0, ty), (x1, y1, _) in zip(k0, k1)] for k0, k1 in zip(c0, c1)]


def ufo_path(root, fam, weight):
    return os.path.join(root, 'sources', 'ufo', fam, f'{fam}-{weight}.ufo')


# ---------------------------------------------------------------- the signs

def build_tomansign(m):
    """«ت» whose two dots stretch into two bars: the bowl, with "=" above it."""
    _, teh = m.glyph(TEH)
    bowl = teh[0]                                  # the rest of teh is its dots, replaced here
    x0, _, x1, top = bbox([bowl])
    t, g = m.dot * TOMAN_BAR, m.dot * TOMAN_GAP
    y0 = top + m.dot * TOMAN_LIFT
    inset = (x1 - x0) * TOMAN_INSET
    bars = [rect(x0 + inset, y0, x1 - inset, y0 + t),
            rect(x0 + inset, y0 + t + g, x1 - inset, y0 + 2 * t + g)]
    return with_sidebearings([bowl] + bars, m.stem * SIDEBEARING)


def build_rialsign(m):
    """«ا» and «ل» as two stems at digit height, crossed by «ر» turned into a rising stroke."""
    s, h = m.stem, m.digit_height
    left, right = 0.0, s + s * RIAL_GAP
    stems = [rect(left, 0, left + s, h), rect(right, 0, right + s, h)]
    _, reh = m.glyph(REH)
    rx0, ry0, rx1, ry1 = bbox(reh)
    reh = rotate(reh, RIAL_TILT, (rx0 + rx1) / 2, (ry0 + ry1) / 2)
    qx0, qy0, qx1, qy1 = bbox(reh)
    centre = (left + right + s) / 2
    reh = shift(reh, centre - (qx0 + qx1) / 2 - s * RIAL_SHIFT, h * RIAL_HEIGHT - (qy0 + qy1) / 2)
    return with_sidebearings(stems + reh, s * SIDEBEARING)


def build_tomanword(m):
    """«ن» stacked over «توما». The letters are scaled down, so they are first taken
    from a heavier interpolation; after scaling, their strokes match the stem again."""
    k = STACK_SCALE
    src = m.stem / k
    grow = (src / m.stem) ** 0.35                  # heavier letters need a little more room
    row, pen = [], 0.0
    for name in STACK_ROW:
        row += shift(m.heavier(name, src), dx=pen)
        pen += m.glyph(name)[0] * grow
    alef_end = m.glyph(STACK_ROW[0])[0] * grow
    _, _, row_right, _ = bbox(row)
    noon = m.heavier(NOON, src)
    nx0, ny0, nx1, _ = bbox(noon)
    over = alef_end + (row_right - alef_end) * 0.42  # over و and مـ, clear of the tall alef
    noon = shift(noon, over - (nx0 + nx1) / 2 - m.stem * 0.5, STACK_NOON_FLOOR - ny0)
    cs = transform(row + noon, a=k, d=k)
    _, _, _, top = bbox(cs)
    cs = shift(cs, dy=m.digit_height - top)        # the top of the mark meets digit height
    return with_sidebearings(cs, m.stem * SIDEBEARING)


# ---------------------------------------------------------------- driver

def main():
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..')
    made = 0
    for fam in FAMILIES:
        for weight in WEIGHTS:
            m = Master(root, fam, weight)
            ufo = m.ufo
            specs = [
                ('tomansign', 0xE000, build_tomansign(m)),
                ('rialsign', 0xE001, build_rialsign(m)),
                ('tomansign.word', 0xE002, build_tomanword(m)),
            ]
            for name, cp, (width, contours) in specs:
                write_glyph(ufo, name, cp, width, contours)
                made += 1
            add_to_glyph_order(ufo, [n for n, _, _ in specs])
            add_features(ufo)
            print(f'{fam}-{weight}: stem {m.stem:.0f}, '
                  + ', '.join(f'{n} {w:.0f}' for n, _, (w, _) in specs))
    print(f'{made} glyphs written')


if __name__ == '__main__':
    main()
