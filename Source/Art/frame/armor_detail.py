"""Detailed armour pieces, written straight as SVG (gradients, cast shadows, bevels, glow), fitted to the frame.
First set: Heavy (Bulwark). Frame canvas coordinates (320 = 2.717 tiles); light comes from the top left.
    python3 armor_detail.py <out dir>"""
import math, sys
import frame_svg as S
from frame4 import X

OLC = '#201c1a'

class Svg:
    def __init__(self, prefix):
        self.p, self.n, self.defs, self.out = prefix, 0, [], []
    def id(self):
        self.n += 1; return f'{self.p}{self.n}'
    def add(self, s):
        self.out.append(s)
    def text(self):
        return f'<defs>{"".join(self.defs)}</defs>' + ''.join(self.out)

def pts(p):
    return ' '.join(f'{x:.2f},{y:.2f}' for x, y in p)

def hexc(c):
    return '#%02x%02x%02x' % c

def mix(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)

class Pal:
    def __init__(self, base, accent, glow):
        self.base, self.acc, self.glow = base, accent, glow
        self.hi, self.lit, self.dk, self.deep = mix(base, 1.38), mix(base, 1.16), mix(base, 0.74), mix(base, 0.5)

def grad(g, pal, vertical=True):
    gid = g.id()
    x2, y2 = ('0', '1') if vertical else ('1', '0')
    g.defs.append(f'<linearGradient id="{gid}" x1="0" y1="0" x2="{x2}" y2="{y2}">'
                  f'<stop offset="0" stop-color="{hexc(pal.lit)}"/><stop offset="0.45" stop-color="{hexc(pal.base)}"/>'
                  f'<stop offset="1" stop-color="{hexc(pal.dk)}"/></linearGradient>')
    return gid

def glow_filter(g):
    fid = g.id()
    g.defs.append(f'<filter id="{fid}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="1.6"/></filter>')
    return fid

def plate(g, pal, p, shadow=True, fill=None, bevel=True, lw=2.6):
    """an armour plate: cast shadow, gradient body, inner bevel (lit top-left edge, shaded bottom-right), outline"""
    if shadow:
        g.add(f'<polygon points="{pts([(x + 2.2, y + 3) for x, y in p])}" fill="#000" fill-opacity="0.32"/>')
    f = fill or f'url(#{grad(g, pal)})'
    g.add(f'<polygon points="{pts(p)}" fill="{f}"/>')
    if bevel:
        cid = g.id()
        g.defs.append(f'<clipPath id="{cid}"><polygon points="{pts(p)}"/></clipPath>')
        g.add(f'<g clip-path="url(#{cid})">'
              f'<polygon points="{pts([(x + 2, y + 2) for x, y in p])}" fill="none" stroke="{hexc(pal.hi)}" stroke-width="2.4" stroke-opacity="0.85"/>'
              f'<polygon points="{pts([(x - 2, y - 2) for x, y in p])}" fill="none" stroke="{hexc(pal.deep)}" stroke-width="2.4" stroke-opacity="0.55"/></g>')
    g.add(f'<polygon points="{pts(p)}" fill="none" stroke="{OLC}" stroke-width="{lw}" stroke-linejoin="round"/>')

def line(g, p, w, col, op=1.0, cap='round'):
    g.add(f'<polyline points="{pts(p)}" fill="none" stroke="{col}" stroke-width="{w}" stroke-opacity="{op}" stroke-linecap="{cap}" stroke-linejoin="round"/>')

def seam(g, pal, p):
    line(g, p, 1.3, OLC, 0.85)
    line(g, [(x + 0.6, y + 1.1) for x, y in p], 0.9, hexc(pal.hi), 0.6)

def bolt(g, x, y, r=1.9, pal=None):
    g.add(f'<circle cx="{x}" cy="{y}" r="{r + 0.7}" fill="{OLC}"/>')
    g.add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{hexc(pal.dk) if pal else "#555"}"/>')
    g.add(f'<circle cx="{x - r * 0.35}" cy="{y - r * 0.35}" r="{r * 0.45}" fill="{hexc(pal.hi) if pal else "#bbb"}"/>')

def scratch(g, p):
    line(g, p, 0.8, '#ffffff', 0.35)

def wear(g, pal, p, every=9):
    """edge wear: small light chips along an edge"""
    for (x0, y0), (x1, y1) in zip(p, p[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        for k in range(1, int(L // every)):
            t = k * every / L
            if (k * 7) % 3 == 0:
                x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
                line(g, [(x - 1.5, y + 0.8), (x + 1.2, y + 1.6)], 1.0, hexc(pal.hi), 0.7)

def slot(g, x0, y0, x1, y1, r=1.5):
    """a recessed dark slot: shadowed top, lit bottom lip"""
    g.add(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="{r}" fill="#1b1a1c" stroke="{OLC}" stroke-width="1"/>')
    line(g, [(x0 + 1, y1 - 0.4), (x1 - 1, y1 - 0.4)], 0.9, '#9aa3ad', 0.6)

def chevrons(g, p_box, step=6):
    cid = g.id()
    g.defs.append(f'<clipPath id="{cid}"><polygon points="{pts(p_box)}"/></clipPath>')
    xs = [x for x, _ in p_box]; ys = [y for _, y in p_box]
    s = f'<g clip-path="url(#{cid})"><rect x="{min(xs)}" y="{min(ys)}" width="{max(xs) - min(xs)}" height="{max(ys) - min(ys)}" fill="#e2b03c"/>'
    h = max(ys) - min(ys); x = min(xs) - h
    while x < max(xs) + h:
        s += f'<polygon points="{pts([(x, max(ys)), (x + step / 2, max(ys)), (x + step / 2 + h, min(ys)), (x + h, min(ys))])}" fill="#262220"/>'
        x += step
    g.add(s + '</g>')
    g.add(f'<polygon points="{pts(p_box)}" fill="none" stroke="{OLC}" stroke-width="1.2"/>')

def stencil(g, x, y, txt, size=6, col='#e8e4da', op=0.75, anchor='middle'):
    g.add(f'<text x="{x}" y="{y}" font-family="DejaVu Sans Mono, monospace" font-weight="bold" font-size="{size}" '
          f'fill="{col}" fill-opacity="{op}" text-anchor="{anchor}" letter-spacing="0.4">{txt}</text>')

def piston(g, a, b, pal):
    line(g, [a, b], 5.4, OLC); line(g, [a, b], 3.6, '#8b9198')
    mx, my = a[0] + (b[0] - a[0]) * 0.55, a[1] + (b[1] - a[1]) * 0.55
    line(g, [a, (mx, my)], 5.6, OLC); line(g, [a, (mx, my)], 4, hexc(pal.dk))
    line(g, [(a[0] - 0.8, a[1] - 0.8), (mx - 0.8, my - 0.8)], 1, hexc(pal.hi), 0.7)

# ======================================================================= HEAVY (Bulwark)
HEAVY = Pal((112, 124, 138), (196, 52, 40), (255, 90, 60))

def helmet_heavy(g, pal):
    glow = glow_filter(g)
    plate(g, pal, [(130, 60), (190, 60), (200, 76), (200, 104), (190, 116), (130, 116), (120, 104), (120, 76)])
    # brow plate overhanging the visor
    plate(g, pal, [(124, 66), (196, 66), (202, 80), (196, 84), (124, 84), (118, 80)])
    seam(g, pal, [(128, 72), (192, 72)])
    # crest ridge with a stripe
    plate(g, pal, [(154, 50), (166, 50), (169, 68), (151, 68)])
    g.add(f'<rect x="157.5" y="53" width="5" height="12" fill="{hexc(pal.acc)}" stroke="{OLC}" stroke-width="0.8"/>')
    # recessed visor slit with a red glow
    g.add(f'<rect x="130" y="85" width="60" height="9" rx="2" fill="#141214" stroke="{OLC}" stroke-width="1.4"/>')
    g.add(f'<rect x="134" y="88" width="52" height="3" rx="1.5" fill="{hexc(pal.glow)}" filter="url(#{glow})"/>')
    g.add(f'<rect x="135" y="88.5" width="50" height="2" rx="1" fill="#ffd2c0"/>')
    # cheek guards with vent slats, chin guard with a breathing grille
    for s in (-1, 1):
        plate(g, pal, X([(184, 94), (200, 92), (202, 108), (190, 116), (180, 112)], s), lw=2.2)
        for k in range(3):
            slot(g, *(X([(186 + k * 4.2, 98)], s)[0]), *(X([(188.4 + k * 4.2, 108)], s)[0])) if s > 0 else \
                slot(g, X([(188.4 + k * 4.2, 98)], s)[0][0], 98, X([(186 + k * 4.2, 108)], s)[0][0], 108)
    plate(g, pal, [(146, 96), (174, 96), (178, 110), (168, 118), (152, 118), (142, 110)], lw=2.2)
    for r in range(2):
        for c in range(4):
            g.add(f'<circle cx="{151.5 + c * 5.7}" cy="{103 + r * 6}" r="1.5" fill="#141214"/>')
    for x, y in ((126, 98), (194, 98), (128, 76), (192, 76)):
        bolt(g, x, y, 1.6, pal)
    scratch(g, [(136, 62), (144, 64)]); scratch(g, [(178, 106), (184, 103)])
    stencil(g, 186, 80, 'B-07', 4.6, anchor='middle')
    wear(g, pal, [(130, 60), (190, 60), (200, 76)])

def chest_heavy(g, pal):
    glow = glow_filter(g)
    # gorget plates by the collar
    for s in (-1, 1):
        plate(g, pal, X([(176, 104), (204, 106), (212, 118), (180, 118)], s), lw=2.2)
    # abdominal lamellar bands (behind the breastplate)
    for k, y in enumerate((170, 180, 190)):
        w = 46 - k * 4
        plate(g, pal, [(160 - w, y), (160 + w, y), (160 + w - 3, y + 11), (160 - w + 3, y + 11)], lw=2.2)
        for x in (160 - w + 8, 160 + w - 8):
            bolt(g, x, y + 5.5, 1.3, pal)
    # the breastplate: two pectoral plates on a keel
    for s in (-1, 1):
        plate(g, pal, X([(162, 112), (204, 112), (222, 126), (220, 156), (204, 172), (164, 174)], s))
        seam(g, pal, X([(170, 142), (214, 138)], s))
        for x, y in ((210, 126), (212, 152), (172, 120), (172, 166)):
            bolt(g, *X([(x, y)], s)[0], 1.7, pal)
        wear(g, pal, X([(162, 112), (204, 112), (222, 126)], s), 7)
    plate(g, pal, [(154, 110), (166, 110), (170, 176), (160, 184), (150, 176)])
    line(g, [(160, 114), (160, 178)], 1.4, hexc(pal.hi), 0.7)
    # a status strip and a hazard decal, a stencilled number
    g.add(f'<rect x="176" y="148" width="22" height="5" rx="1.2" fill="#141214" stroke="{OLC}" stroke-width="0.8"/>')
    for k, c in enumerate(('#7cf07a', '#7cf07a', '#f0c050')):
        g.add(f'<rect x="{178 + k * 6.6}" y="149.4" width="4.6" height="2.2" fill="{c}" filter="url(#{glow})"/>')
        g.add(f'<rect x="{178 + k * 6.6}" y="149.6" width="4.6" height="1.8" fill="{c}"/>')
    chevrons(g, [(124, 128), (148, 128), (148, 136), (124, 136)])
    stencil(g, 136, 158, '07', 9, op=0.55)
    scratch(g, [(186, 120), (196, 126)]); scratch(g, [(128, 150), (134, 147)]); scratch(g, [(190, 164), (198, 160)])

def arm_heavy(g, pal, s):
    Q = lambda p: X(p, s)
    # upper arm plate
    plate(g, pal, Q([(232, 150), (252, 148), (254, 182), (236, 184)]), lw=2.2)
    seam(g, pal, Q([(236, 166), (252, 165)]))
    # elbow cop
    cx = 160 + s * 85
    g.add(f'<circle cx="{cx + 2}" cy="{197}" r="11" fill="#000" fill-opacity="0.3"/>')
    gid = grad(g, pal)
    g.add(f'<circle cx="{cx}" cy="{194}" r="10.5" fill="url(#{gid})" stroke="{OLC}" stroke-width="2.4"/>')
    g.add(f'<circle cx="{cx}" cy="{194}" r="5" fill="{hexc(pal.dk)}" stroke="{OLC}" stroke-width="1.4"/>')
    bolt(g, cx, 194, 2, pal)
    # vambrace: a forearm guard of two segments with vents, a piston alongside
    piston(g, Q([(256, 186)])[0], Q([(260, 226)])[0], pal)
    plate(g, pal, Q([(222, 200), (262, 196), (268, 214), (262, 222), (226, 224)]))
    plate(g, pal, Q([(226, 222), (262, 220), (266, 236), (256, 244), (232, 244)]))
    for k in range(3):
        a, b = Q([(234 + k * 8, 205)])[0], Q([(239 + k * 8, 215)])[0]
        slot(g, min(a[0], b[0]), 205, max(a[0], b[0]), 215, 1)
    bolt(g, *Q([(230, 232)])[0], 1.6, pal); bolt(g, *Q([(258, 230)])[0], 1.6, pal)
    # pauldron: three lames, the biggest on top, with a rim and an emblem
    for k, y in enumerate((126, 114, 100)):
        sc = 1 - k * 0.04
        p = [(204 + k * 3, y), (242, y - 8 + k * 2), (270 - k * 2, y + 4), (274 - k * 3, y + 22), (246, y + 28), (208 + k * 3, y + 22)]
        plate(g, pal, Q(p))
        line(g, Q([(210 + k * 3, y + 21), (246, y + 27), (272 - k * 3, y + 21)]), 1.6, hexc(pal.acc) if k == 2 else hexc(pal.deep), 0.9)
    em = Q([(240, 108)])[0]
    g.add(f'<path d="M{em[0] - 6},{em[1] - 5} h12 v5 q0,6 -6,9 q-6,-3 -6,-9 z" fill="{hexc(pal.acc)}" stroke="{OLC}" stroke-width="1.2"/>')
    g.add(f'<path d="M{em[0]},{em[1] - 3} v9" stroke="#f3e6d2" stroke-width="1.2" stroke-opacity="0.8"/>')
    for x, y in ((214, 104), (264, 108), (216, 130)):
        bolt(g, *Q([(x, y)])[0], 1.7, pal)
    scratch(g, Q([(226, 116), (234, 112)])); scratch(g, Q([(250, 128), (258, 132)]))

def leg_heavy(g, pal, s):
    Q = lambda p: X(p, s)
    # tasset: two lames over the thigh
    plate(g, pal, Q([(168, 224), (212, 224), (218, 244), (212, 252), (172, 252), (166, 244)]))
    plate(g, pal, Q([(170, 246), (212, 246), (214, 268), (206, 274), (178, 274), (170, 266)]))
    seam(g, pal, Q([(176, 260), (208, 260)]))
    for x, y in ((174, 232), (208, 232), (176, 254), (206, 254)):
        bolt(g, *Q([(x, y)])[0], 1.5, pal)
    # piston along the outside of the knee
    piston(g, Q([(214, 258)])[0], Q([(212, 294)])[0], pal)
    # knee cop with a ridge
    plate(g, pal, Q([(176, 266), (208, 266), (214, 280), (204, 292), (180, 292), (170, 280)]))
    line(g, Q([(192, 268), (192, 290)]), 2.2, hexc(pal.hi), 0.8)
    line(g, Q([(193.5, 269), (193.5, 290)]), 1.2, OLC, 0.6)
    # greave with ribbing
    plate(g, pal, Q([(176, 290), (210, 290), (212, 304), (178, 306)]), lw=2.2)
    for k in range(4):
        seam(g, pal, Q([(181 + k * 8, 292), (181 + k * 8, 304)]))
    chevrons(g, Q([(180, 240), (198, 240), (198, 246), (180, 246)]), 5)
    wear(g, pal, Q([(168, 224), (212, 224), (218, 244)]), 6)

def pack_heavy(g, pal):
    glow = glow_filter(g)
    # radiator fins down both sides
    for s in (-1, 1):
        plate(g, pal, X([(192, 112), (206, 116), (206, 188), (192, 192)], s), lw=2.2)
        for k in range(8):
            y = 120 + k * 8.6
            line(g, X([(194, y), (205, y + 1)], s), 1.6, OLC, 0.85)
    # housing
    plate(g, pal, [(126, 102), (194, 102), (200, 116), (198, 194), (122, 194), (120, 116)])
    plate(g, pal, [(132, 108), (188, 108), (190, 118), (130, 118)], lw=1.8)
    # three recessed cell caps with charge rings
    for k, (y, ch) in enumerate(((132, 1.0), (156, 1.0), (180, 0.4))):
        g.add(f'<circle cx="160" cy="{y}" r="11" fill="#141214" stroke="{OLC}" stroke-width="1.6"/>')
        gid = grad(g, pal)
        g.add(f'<circle cx="160" cy="{y}" r="8" fill="url(#{gid})" stroke="{OLC}" stroke-width="1.4"/>')
        col = '#7cf07a' if ch > 0.5 else '#f0b040'
        ang = 360 * ch
        x1 = 160 + 9.6 * math.sin(math.radians(ang)); y1 = y - 9.6 * math.cos(math.radians(ang))
        large = 1 if ang > 180 else 0
        arc = f'M160,{y - 9.6} A9.6,9.6 0 {large} 1 {x1:.2f},{y1:.2f}' if ch < 1 else f'M160,{y - 9.6} a9.6,9.6 0 1 1 -0.01,0'
        g.add(f'<path d="{arc}" fill="none" stroke="{col}" stroke-width="1.8" filter="url(#{glow})"/>')
        g.add(f'<path d="{arc}" fill="none" stroke="{col}" stroke-width="1.1"/>')
        line(g, [(156, y - 2), (164, y - 2)], 1.2, OLC); line(g, [(156, y + 2), (164, y + 2)], 1.2, OLC)
    # shield emitter dish on top, glowing
    g.add(f'<ellipse cx="160" cy="92" rx="24" ry="8" fill="#000" fill-opacity="0.3"/>')
    gid = grad(g, pal)
    g.add(f'<ellipse cx="160" cy="90" rx="23" ry="7.5" fill="url(#{gid})" stroke="{OLC}" stroke-width="2.2"/>')
    g.add(f'<ellipse cx="160" cy="89" rx="15" ry="4.4" fill="#2c6fb0" stroke="{OLC}" stroke-width="1.2"/>')
    g.add(f'<ellipse cx="160" cy="88.5" rx="11" ry="3" fill="#8fd0ff" filter="url(#{glow})"/>')
    line(g, [(160, 96), (160, 104)], 5, OLC); line(g, [(160, 96), (160, 104)], 3, '#8b9198')
    # handles, cable conduits, decals
    for s in (-1, 1):
        line(g, X([(178, 196), (184, 204), (192, 204)], s), 4.4, OLC); line(g, X([(178, 196), (184, 204), (192, 204)], s), 2.6, '#6b7076')
        line(g, X([(184, 122), (184, 190)], s), 3.6, OLC); line(g, X([(184, 122), (184, 190)], s), 2, hexc(pal.acc))
    chevrons(g, [(130, 186), (190, 186), (190, 192), (130, 192)], 6)
    stencil(g, 140, 116, 'PWR', 5, op=0.7, anchor='start')
    for x, y in ((126, 108), (194, 108), (126, 188), (194, 188)):
        bolt(g, x, y, 1.6, pal)
    scratch(g, [(130, 150), (138, 146)]); scratch(g, [(184, 168), (190, 172)])

def helmet_back_heavy(g, pal):
    """the helmet from behind: the shell, the crest, a neck guard with cooling slats"""
    plate(g, pal, [(130, 58), (190, 58), (200, 74), (200, 102), (190, 114), (130, 114), (120, 102), (120, 74)])
    plate(g, pal, [(154, 48), (166, 48), (169, 66), (151, 66)])
    g.add(f'<rect x="157.5" y="51" width="5" height="12" fill="{hexc(pal.acc)}" stroke="{OLC}" stroke-width="0.8"/>')
    seam(g, pal, [(126, 76), (194, 76)])
    plate(g, pal, [(132, 96), (188, 96), (194, 108), (184, 118), (136, 118), (126, 108)], lw=2.2)
    for k in range(5):
        slot(g, 140 + k * 8.4, 101, 144 + k * 8.4, 112, 1)
    for x, y in ((128, 82), (192, 82)):
        bolt(g, x, y, 1.6, pal)
    scratch(g, [(140, 64), (150, 62)])
    wear(g, pal, [(130, 58), (190, 58), (200, 74)])

# ======================================================================= sheet
def piece(fn, pal, prefix, *args):
    g = Svg(prefix); fn(g, pal, *args); return g.text()

def frame(facing, prefix):
    return ''.join(S.view(facing, 0.0)).replace('id="c', f'id="{prefix}').replace('#c', f'#{prefix}')

CELLS = [('Helmet', (108, 40, 104, 86), 'south', lambda: piece(helmet_heavy, HEAVY, 'h')),
         ('Chest plate', (86, 96, 148, 112), 'south', lambda: piece(chest_heavy, HEAVY, 'c')),
         ('Arms', (34, 84, 252, 170), 'south', lambda: piece(arm_heavy, HEAVY, 'al', -1) + piece(arm_heavy, HEAVY, 'ar', 1)),
         ('Legs', (96, 216, 128, 96), 'south', lambda: piece(leg_heavy, HEAVY, 'll', -1) + piece(leg_heavy, HEAVY, 'lr', 1)),
         ('Pack', (98, 76, 124, 140), 'north', lambda: piece(pack_heavy, HEAVY, 'p'))]

def assembled(facing):
    if facing == 'south':
        return (piece(leg_heavy, HEAVY, 'Al', -1) + piece(leg_heavy, HEAVY, 'Ar', 1) + piece(chest_heavy, HEAVY, 'Ac')
                + piece(arm_heavy, HEAVY, 'Aal', -1) + piece(arm_heavy, HEAVY, 'Aar', 1) + piece(helmet_heavy, HEAVY, 'Ah'))
    # north: arm and leg plates (they read the same from behind), the pack on the hatch, the back of the helmet
    return (piece(leg_heavy, HEAVY, 'Nl', -1) + piece(leg_heavy, HEAVY, 'Nr', 1)
            + piece(arm_heavy, HEAVY, 'Nal', -1) + piece(arm_heavy, HEAVY, 'Nar', 1)
            + piece(helmet_back_heavy, HEAVY, 'Nh') + piece(pack_heavy, HEAVY, 'Np'))   # the pack is nearer us than the helmet

if __name__ == '__main__':
    out = sys.argv[1]
    C, PAD = 230, 12
    Wd = PAD + 3 * C + 2 * 300 + PAD * 2
    Hd = 60 + 2 * C + 40
    parts = [f'<rect width="{Wd}" height="{Hd}" fill="#ece6dc"/>',
             f'<text x="{PAD}" y="32" font-family="DejaVu Sans, sans-serif" font-size="18" fill="#222">Heavy (Bulwark) - detailed pass</text>']
    for i, (name, box, f, fn) in enumerate(CELLS):
        cx, cy = PAD + (i % 3) * C, 50 + (i // 3) * C
        x, y, w, h = box
        parts.append(f'<rect x="{cx + 4}" y="{cy + 4}" width="{C - 8}" height="{C - 8}" rx="6" fill="#605c62"/>')
        parts.append(f'<svg x="{cx + 6}" y="{cy + 6}" width="{C - 12}" height="{C - 30}" viewBox="{x} {y} {w} {h}" preserveAspectRatio="xMidYMid meet">'
                     f'<g opacity="0.22">{frame(f, f"g{i}_")}</g>{fn()}</svg>')
        parts.append(f'<text x="{cx + C / 2}" y="{cy + C - 12}" font-family="DejaVu Sans, sans-serif" font-size="13" text-anchor="middle" fill="#eee">{name}</text>')
    for j, f in enumerate(('south', 'north')):
        cx = PAD + 3 * C + PAD + j * 300
        parts.append(f'<rect x="{cx}" y="54" width="292" height="{2 * C - 8}" rx="6" fill="#605c62"/>')
        parts.append(f'<svg x="{cx}" y="58" width="292" height="{2 * C - 40}" viewBox="20 30 280 292" preserveAspectRatio="xMidYMid meet">'
                     f'{frame(f, f"F{j}_")}{assembled(f)}</svg>')
        parts.append(f'<text x="{cx + 146}" y="{50 + 2 * C - 16}" font-family="DejaVu Sans, sans-serif" font-size="13" text-anchor="middle" fill="#eee">Assembled ({f})</text>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {Wd} {Hd}" width="{Wd}" height="{Hd}">'
           f'<title>Armour pieces - Heavy, detailed</title>{"".join(parts)}</svg>')
    open(f'{out}/svg/armor_heavy_detailed.svg', 'w').write(svg)
    # the assembled suit alone at game scale (320 canvas)
    for f in ('south', 'north'):
        game = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 320" width="320" height="320"><title>Heavy suit, game scale</title>'
                f'{frame(f, "G_")}{assembled(f)}</svg>')
        open(f'{out}/svg/armor_heavy_suit_{f}.svg', 'w').write(game)
    print(Wd, Hd)
