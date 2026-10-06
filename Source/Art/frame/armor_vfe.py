"""Our Heavy (Bulwark) pieces rendered in the warcasket *style* (VFE Pirates' look, not its designs), as SVG.
The style, from docs/DESIGN.md: light grey plates (the game tints them), soft form shading darkening toward the
rim with light from the upper left, crisp chamfer side faces (lit facing the upper left, darker facing away),
soft cast shadows, thin dark lines between plates, a heavy black outline round the whole silhouette, and detail
only suggested (a seam, a couple of bolts, a slot). Known no-gos are avoided (no T visor, no twin back exhausts,
no round grille snout with hoses).
    python3 armor_vfe.py <out dir>"""
import math, sys
import frame_svg as S
from frame4 import X

OLC = '#1c1a19'
LIGHT = (-0.55, -0.84)                       # towards the upper left (screen y down)
TOP = ('#ececee', '#cdcdd1', '#a2a2a9')      # top face: lit centre -> mid -> rim
TOP_DARK = ('#6c6e75', '#4d4f55', '#34353a') # dark plates: the undersuit and joints
ACC = '#e8603a'                              # one accent: the visor glow
# RimWorld-weight lines (owner): a light silhouette outline, no dark lines between plates - shading suggests form
SIL_W, EDGE_W, EDGE_OP = 3.4, 0.6, 0.35

def P(p):
    return ' '.join(f'{x:.2f},{y:.2f}' for x, y in p)

def circle(cx, cy, r, n=28):
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]

def orient(p):
    return sum(p[i - 1][0] * p[i][1] - p[i][0] * p[i - 1][1] for i in range(len(p)))

def inset(p, c):
    """offset a polygon inward by c along each vertex's bisector (mitre-limited)"""
    s = 1 if orient(p) > 0 else -1           # inward normal side
    out = []
    n = len(p)
    for i in range(n):
        a, b, cpt = p[i - 1], p[i], p[(i + 1) % n]
        def nrm(u, v):
            dx, dy = v[0] - u[0], v[1] - u[1]; L = math.hypot(dx, dy) or 1
            return (-dy / L * s, dx / L * s)
        n1, n2 = nrm(a, b), nrm(b, cpt)
        bx, by = n1[0] + n2[0], n1[1] + n2[1]; L = math.hypot(bx, by) or 1
        bx, by = bx / L, by / L
        cosh = max(0.35, bx * n1[0] + by * n1[1])
        out.append((b[0] + bx * c / cosh, b[1] + by * c / cosh))
    return out

def face_colour(a, b, inward_sign, tone='light'):
    """the chamfer face along edge a-b: lit when its outward normal points to the light"""
    dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy) or 1
    nx, ny = dy / L * inward_sign, -dx / L * inward_sign     # outward normal
    t = nx * LIGHT[0] + ny * LIGHT[1]                         # -1 .. 1
    lo, hi = ((112, 112, 120), (246, 246, 248)) if tone == 'light' else ((34, 34, 38), (120, 122, 130))
    f = min(1.0, max(0.0, (t + 1) / 2)) ** 1.4
    return '#%02x%02x%02x' % tuple(int(lo[k] + (hi[k] - lo[k]) * f) for k in range(3))

class Suit:
    """pieces are collected first (plates as polygons, details as SVG), then drawn: the silhouette outline
    of every plate, then each plate with shadow, chamfers and face, then the details"""
    def __init__(self, prefix):
        self.p, self.n, self.defs, self.items = prefix, 0, [], []
    def id(self):
        self.n += 1; return f'{self.p}{self.n}'
    def plate(self, pts, chamfer=3.2, shadow=True, tone='light'):
        self.items.append(('plate', pts, chamfer, shadow, tone))
    def detail(self, svg):
        self.items.append(('detail', svg))
    def render(self):
        blur = self.id()
        self.defs.append(f'<filter id="{blur}" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="2.2"/></filter>')
        glow = self.id()
        self.defs.append(f'<filter id="{glow}" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="1.5"/></filter>')
        self.glow = glow
        soft = self.id()
        self.defs.append(f'<filter id="{soft}" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="2.6"/></filter>')
        out = []
        plates = [it for it in self.items if it[0] == 'plate']
        for _, p, *_ in plates:                                   # heavy silhouette outline
            out.append(f'<polygon points="{P(p)}" fill="{OLC}" stroke="{OLC}" stroke-width="{SIL_W}" stroke-linejoin="round"/>')
        for it in self.items:
            if it[0] == 'detail':
                out.append(it[1].replace('GLOW', glow).replace('SOFT', soft)); continue
            _, p, c, shadow, tone = it
            top = TOP if tone == 'light' else TOP_DARK
            if shadow:
                out.append(f'<polygon points="{P([(x + 2.4, y + 3.2) for x, y in p])}" fill="#000" fill-opacity="0.45" filter="url(#{blur})"/>')
            ins = inset(p, c)
            sgn = -1 if orient(p) > 0 else 1
            for i in range(len(p)):                                 # chamfer side faces
                q = [p[i - 1], p[i], ins[i], ins[i - 1]]
                col = face_colour(p[i - 1], p[i], sgn, tone)
                out.append(f'<polygon points="{P(q)}" fill="{col}" stroke="{col}" stroke-width="0.5" stroke-linejoin="round"/>')
            xs = [x for x, _ in ins]; ys = [y for _, y in ins]
            gid = self.id()                                         # soft form shading on the top face
            cx = min(xs) + (max(xs) - min(xs)) * 0.38; cy = min(ys) + (max(ys) - min(ys)) * 0.3
            r = max(max(xs) - min(xs), max(ys) - min(ys)) * 0.85
            self.defs.append(f'<radialGradient id="{gid}" gradientUnits="userSpaceOnUse" cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}">'
                             f'<stop offset="0" stop-color="{top[0]}"/><stop offset="0.6" stop-color="{top[1]}"/>'
                             f'<stop offset="1" stop-color="{top[2]}"/></radialGradient>')
            out.append(f'<polygon points="{P(ins)}" fill="url(#{gid})"/>')
            # no line between plates: shadow and chamfer faces carry the form; only a faint edge
            out.append(f'<polygon points="{P(p)}" fill="none" stroke="{OLC}" stroke-width="{EDGE_W}" stroke-opacity="{EDGE_OP}" stroke-linejoin="round"/>')
        return f'<defs>{"".join(self.defs)}</defs>' + ''.join(out)

def seam(a, b):
    return (f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="{OLC}" stroke-width="0.8" stroke-opacity="0.4"/>'
            f'<line x1="{a[0]}" y1="{a[1] + 1}" x2="{b[0]}" y2="{b[1] + 1}" stroke="#f4f4f6" stroke-width="0.7" stroke-opacity="0.6"/>')

def bolt(x, y, r=1.5):
    return (f'<circle cx="{x}" cy="{y}" r="{r + 0.6}" fill="{OLC}" fill-opacity="0.85"/><circle cx="{x}" cy="{y}" r="{r}" fill="#9d9da4"/>'
            f'<circle cx="{x - r * 0.35}" cy="{y - r * 0.35}" r="{r * 0.45}" fill="#f2f2f4"/>')

def slot(x0, y0, x1, y1):
    return (f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="1.2" fill="#2a282b" stroke="{OLC}" stroke-width="0.8"/>'
            f'<line x1="{x0 + 1}" y1="{y1 - 0.3}" x2="{x1 - 1}" y2="{y1 - 0.3}" stroke="#e8e8ea" stroke-width="0.7" stroke-opacity="0.6"/>')

# ------------------------------------------------------------------ the Heavy pieces (our designs)
def helmet(s):
    s.plate([(130, 60), (190, 60), (200, 76), (200, 104), (190, 116), (130, 116), (120, 104), (120, 76)], 4)
    s.plate([(124, 66), (196, 66), (202, 80), (196, 84), (124, 84), (118, 80)], 3)
    s.plate([(154, 50), (166, 50), (169, 68), (151, 68)], 2.4)
    s.detail(f'<rect x="130" y="85" width="60" height="9" rx="2" fill="#1d1b1e" stroke="{OLC}" stroke-width="1.2"/>'
             f'<rect x="134" y="88" width="52" height="3" rx="1.5" fill="{ACC}" filter="url(#GLOW)"/>'
             f'<rect x="135" y="88.6" width="50" height="1.8" rx="0.9" fill="#ffd7c4"/>')
    for sd in (-1, 1):
        s.plate(X([(184, 94), (200, 92), (202, 108), (190, 116), (180, 112)], sd), 2.6)
    s.plate([(146, 96), (174, 96), (178, 110), (168, 118), (152, 118), (142, 110)], 2.8)
    s.detail(slot(150, 103, 170, 106) + slot(152, 109, 168, 112) + bolt(127, 98) + bolt(193, 98))

def chest(s):
    for sd in (-1, 1):
        s.plate(X([(176, 104), (204, 106), (212, 118), (180, 118)], sd), 2.4)
    for k, y in enumerate((190, 180, 170)):
        w = 38 + k * 4
        s.plate([(160 - w, y), (160 + w, y), (160 + w - 3, y + 11), (160 - w + 3, y + 11)], 2.2)
    for sd in (-1, 1):
        s.plate(X([(162, 112), (204, 112), (222, 126), (220, 156), (204, 172), (164, 174)], sd), 4.2)
    s.plate([(154, 110), (166, 110), (170, 176), (160, 184), (150, 176)], 3)
    s.detail(seam((170, 142), (212, 139)) + seam((150, 142), (108, 139)) + bolt(210, 126) + bolt(110, 126)
             + f'<rect x="180" y="150" width="16" height="4" rx="1" fill="#1d1b1e"/><rect x="182" y="151.2" width="12" height="1.6" fill="#8ef08a" filter="url(#GLOW)"/>')

def arm(s, sd):
    Q = lambda p: X(p, sd)
    s.plate(Q([(232, 150), (252, 148), (254, 182), (236, 184)]), 2.6)
    s.plate(circle(160 + sd * 85, 194, 10.5, 20), 3)
    s.plate(Q([(226, 222), (262, 220), (266, 236), (256, 244), (232, 244)]), 3)
    s.plate(Q([(222, 200), (262, 196), (268, 214), (262, 222), (226, 224)]), 3.4)
    for k, y in enumerate((126, 114, 100)):
        s.plate(Q([(204 + k * 3, y), (242, y - 8 + k * 2), (270 - k * 2, y + 4), (274 - k * 3, y + 22), (246, y + 28), (208 + k * 3, y + 22)]), 3.6)
    a, b = Q([(234, 206)])[0], Q([(256, 213)])[0]
    s.detail(slot(min(a[0], b[0]), 206, max(a[0], b[0]), 211) + bolt(*Q([(214, 106)])[0]) + bolt(*Q([(262, 110)])[0]))

def leg(s, sd):
    Q = lambda p: X(p, sd)
    s.plate(Q([(176, 290), (210, 290), (212, 304), (178, 306)]), 2.6)
    s.plate(Q([(170, 246), (212, 246), (214, 268), (206, 274), (178, 274), (170, 266)]), 3.2)
    s.plate(Q([(168, 224), (212, 224), (218, 244), (212, 252), (172, 252), (166, 244)]), 3.6)
    s.plate(Q([(176, 266), (208, 266), (214, 280), (204, 292), (180, 292), (170, 280)]), 3.4)
    s.detail(seam(*Q([(178, 260), (206, 260)])) + bolt(*Q([(208, 232)])[0]))

def helmet_back(s):
    s.plate([(130, 58), (190, 58), (200, 74), (200, 102), (190, 114), (130, 114), (120, 102), (120, 74)], 4)
    s.plate([(154, 48), (166, 48), (169, 66), (151, 66)], 2.4)
    s.plate([(132, 96), (188, 96), (194, 108), (184, 118), (136, 118), (126, 108)], 3)
    s.detail(seam((126, 78), (194, 78)) + ''.join(slot(142 + k * 9, 102, 146 + k * 9, 112) for k in range(4)))

def pack(s):
    for sd in (-1, 1):
        s.plate(X([(192, 112), (206, 116), (206, 188), (192, 192)], sd), 2.4)
    s.plate([(126, 102), (194, 102), (200, 116), (198, 194), (122, 194), (120, 116)], 4.2)
    for y in (132, 156, 180):
        s.plate(circle(160, y, 9.5, 24), 3)
    s.plate([(140, 84), (180, 84), (186, 94), (134, 94)], 2.6)
    det = ''
    for y, ch in ((132, 1), (156, 1), (180, 0.4)):
        col = '#8ef08a' if ch > 0.5 else '#f2b24a'
        det += f'<circle cx="160" cy="{y}" r="3.2" fill="#1d1b1e"/><circle cx="160" cy="{y}" r="2" fill="{col}" filter="url(#GLOW)"/>'
    det += f'<ellipse cx="160" cy="88.6" rx="12" ry="2.4" fill="#4aa8e8" filter="url(#GLOW)"/><ellipse cx="160" cy="88.6" rx="10" ry="1.6" fill="#bfe6ff"/>'
    for sd in (-1, 1):
        det += ''.join(f'<line x1="{X([(194, 0)], sd)[0][0]}" y1="{120 + k * 9}" x2="{X([(205, 0)], sd)[0][0]}" y2="{121 + k * 9}" stroke="{OLC}" stroke-width="1" stroke-opacity="0.7"/>' for k in range(8))
    s.detail(det + seam((128, 112), (192, 112)) + bolt(126, 108) + bolt(194, 108))

def build(facing, prefix):
    s = Suit(prefix)
    if facing == 'south':
        for sd in (-1, 1): leg(s, sd)
        chest(s)
        for sd in (-1, 1): arm(s, sd)
        helmet(s)
    else:
        for sd in (-1, 1): leg(s, sd)
        for sd in (-1, 1): arm(s, sd)
        helmet_back(s); pack(s)
    return s.render()

def piece(fn, prefix, *a):
    s = Suit(prefix); fn(s, *a); return s.render()

def frame(facing, prefix):
    return ''.join(S.view(facing, 0.0)).replace('id="c', f'id="{prefix}').replace('#c', f'#{prefix}')

CELLS = [('Helmet', (108, 40, 104, 86), 'south', lambda: piece(helmet, 'h')),
         ('Chest plate', (86, 96, 148, 112), 'south', lambda: piece(chest, 'c')),
         ('Arms', (34, 84, 252, 170), 'south', lambda: piece(lambda s: (arm(s, -1), arm(s, 1)), 'a')),
         ('Legs', (96, 216, 128, 96), 'south', lambda: piece(lambda s: (leg(s, -1), leg(s, 1)), 'l')),
         ('Pack', (98, 76, 124, 140), 'north', lambda: piece(pack, 'p'))]

if __name__ == '__main__':
    out = sys.argv[1]
    C, PAD = 230, 12
    Wd = PAD + 3 * C + 2 * 300 + PAD * 2; Hd = 60 + 2 * C + 40
    parts = [f'<rect width="{Wd}" height="{Hd}" fill="#ece6dc"/>',
             f'<text x="{PAD}" y="32" font-family="DejaVu Sans, sans-serif" font-size="18" fill="#222">Heavy (Bulwark) - warcasket-style rendering, our designs (grey = takes the suit tint)</text>']
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
                     f'{frame(f, f"F{j}_")}{build(f, f"B{j}_")}</svg>')
        parts.append(f'<text x="{cx + 146}" y="{50 + 2 * C - 16}" font-family="DejaVu Sans, sans-serif" font-size="13" text-anchor="middle" fill="#eee">Assembled ({f})</text>')
    open(f'{out}/svg/armor_heavy_warcasket_style.svg', 'w').write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {Wd} {Hd}" width="{Wd}" height="{Hd}"><title>Heavy, warcasket-style rendering</title>{"".join(parts)}</svg>')
    for f in ('south', 'north'):
        open(f'{out}/svg/armor_heavy_ws_suit_{f}.svg', 'w').write(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 320" width="320" height="320"><title>Heavy suit, warcasket-style</title>'
            f'{frame(f, "G_")}{build(f, "W_")}</svg>')
    print(Wd, Hd)
