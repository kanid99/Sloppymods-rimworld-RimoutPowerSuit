"""Variant: the warcasket-like Heavy set blended with T-51b-inspired elements (retro rounded forms, horizontal
strakes, rivet rows, a ribbed abdomen, a centre keel, a brow ridge, a ribbed respirator and filter canisters) -
influences only, not its helmet face (our recessed slit visor stays).
Based on: Heavy (Bulwark) pieces that *resemble* the warcasket design language (not copies): a massive top-heavy
silhouette, a small helmet sunk into a high collar, big rounded dome pauldrons with a rim lip, a protruding
barrel chest over banded abdomen, a wide flared hip skirt, chunky forearm cuffs, big round knee guards over
short flared greaves; big smooth rounded plates, few lines. Rendered in the warcasket style (armor_vfe.Suit).
Avoids the recorded no-gos: no T visor, no twin back exhaust stacks, no round grille snout with hoses.
    python3 armor_ws2.py <out dir>"""
import math, sys
import armor_vfe as V
from armor_vfe import Suit, seam, bolt, slot, OLC, ACC, frame
from frame4 import X

def rounded(p, r, n=5):
    """round every corner of a polygon (quadratic curve between points r along each edge)"""
    out = []
    m = len(p)
    for i in range(m):
        a, b, c = p[i - 1], p[i], p[(i + 1) % m]
        def toward(u, v, d):
            L = math.hypot(v[0] - u[0], v[1] - u[1]) or 1; d = min(d, L / 2.2)
            return (u[0] + (v[0] - u[0]) * d / L, u[1] + (v[1] - u[1]) * d / L)
        p0, p2 = toward(b, a, r), toward(b, c, r)
        for k in range(n + 1):
            t = k / n
            out.append(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * b[0] + t * t * p2[0],
                        (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * b[1] + t * t * p2[1]))
    return out

R = rounded
def M(p, s):
    return X(p, s)

def rib(a, b):
    """a raised horizontal strake: light on its top edge, a soft dark line under it"""
    return (f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="#f8f8fa" stroke-width="1" stroke-opacity="0.75" stroke-linecap="round"/>'
            f'<line x1="{a[0]}" y1="{a[1] + 1.4}" x2="{b[0]}" y2="{b[1] + 1.4}" stroke="#3c3a40" stroke-width="1" stroke-opacity="0.45" stroke-linecap="round"/>')

def rivets(a, b, n, r=1.1):
    return ''.join(bolt(a[0] + (b[0] - a[0]) * k / (n - 1), a[1] + (b[1] - a[1]) * k / (n - 1), r) for k in range(n))

# ------------------------------------------------------------------ front pieces
def helmet(s):
    s.plate(R([(134, 58), (186, 58), (198, 74), (198, 106), (122, 106), (122, 74)], 16), 4)       # rounded dome
    s.plate(R([(126, 70), (194, 70), (200, 80), (192, 86), (128, 86), (120, 80)], 7), 3)            # heavy brow ridge
    s.detail(f'<path d="M132,88 Q160,85 188,88 L187,95 Q160,97 133,95 Z" fill="#1d1b1e" stroke="{OLC}" stroke-width="1.2"/>'
             f'<path d="M137,91.5 Q160,89.5 183,91.5" stroke="{ACC}" stroke-width="2.6" fill="none" filter="url(#GLOW)"/>'
             f'<path d="M138,91.5 Q160,90 182,91.5" stroke="#ffd7c4" stroke-width="1.2" fill="none"/>'
             + rib((138, 64), (182, 64)) + rivets((130, 78), (190, 78), 7, 0.9))

def face(s):
    """the respirator and filter canisters jut forward, in front of the collar"""
    for sd in (-1, 1):
        s.plate(R(M([(186, 96), (200, 96), (202, 118), (188, 120)], sd), 6), 2.2)
    s.plate(R([(144, 97), (176, 97), (182, 111), (170, 122), (150, 122), (138, 111)], 8), 2.8)
    s.detail(''.join(rib((147, 103 + k * 4.5), (173, 103 + k * 4.5)) for k in range(3))
             + ''.join(rib(*M([(189, 102 + k * 5), (199, 102 + k * 5)], sd)) for sd in (-1, 1) for k in range(3)))

def collar(s):
    s.plate(R([(116, 96), (204, 96), (212, 110), (198, 124), (122, 124), (108, 110)], 8), 3.6)
    s.detail(seam((128, 116), (192, 116)) + rivets((118, 108), (202, 108), 9, 1))

def torso(s):
    for k, (y, w) in enumerate(((200, 28), (193, 31), (186, 34), (179, 37))):                       # ribbed accordion abdomen
        s.plate(R([(160 - w, y), (160 + w, y), (160 + w - 2, y + 8), (160 - w + 2, y + 8)], 3), 1.8)
    s.plate(R([(140, 204), (180, 204), (184, 232), (160, 242), (136, 232)], 6), 3)                   # hip skirt
    for sd in (-1, 1):
        s.plate(R(M([(180, 200), (220, 204), (232, 236), (198, 242), (182, 226)], sd), 7), 3.4)
    s.plate(R([(110, 116), (210, 116), (228, 134), (226, 162), (206, 180), (114, 180), (94, 162), (92, 134)], 18), 5)   # barrel chest
    for sd in (-1, 1):                                                                             # raised pectorals
        pec = R(M([(163, 121), (206, 118), (224, 127), (222, 140), (204, 154), (182, 164), (164, 167)], sd), 10)
        low = R(M([(222, 140), (204, 154), (182, 164), (164, 167)], sd), 10)
        edge = R(M([(222, 140), (204, 154), (182, 164), (164, 166), (163, 124)], sd), 9)[3:-3]
        # shading only: a soft light on the upper surface, a soft shadow under the lower curve
        s.detail(f'<polygon points="{V.P(pec)}" fill="#ffffff" fill-opacity="0.16" filter="url(#SOFT)"/>'
                 f'<polyline points="{V.P([(x, y + 2.5) for x, y in low])}" fill="none" stroke="#3c3a40" stroke-width="3.2" stroke-opacity="0.32" stroke-linecap="round" filter="url(#SOFT)"/>'
                 # a gentle line defining the lower curve and the inner edge, with a faint light line under it
                 + f'<polyline points="{V.P(edge)}" fill="none" stroke="#3c3a40" stroke-width="0.9" stroke-opacity="0.5" stroke-linecap="round" stroke-linejoin="round"/>'
                 + f'<polyline points="{V.P([(x, y + 1) for x, y in edge])}" fill="none" stroke="#f6f6f8" stroke-width="0.7" stroke-opacity="0.5" stroke-linecap="round" stroke-linejoin="round"/>')
    s.plate(R([(153, 118), (167, 118), (167, 180), (153, 180)], 3), 2)                             # centre ridge: straight, square-ended (not a tie)
    s.detail(rib((154, 132), (166, 132)) + rib((154, 156), (166, 156))
             + f'<rect x="184" y="172" width="14" height="3.6" rx="1" fill="#1d1b1e"/><rect x="186" y="173" width="10" height="1.6" fill="#8ef08a" filter="url(#GLOW)"/>'
             + bolt(104, 140) + bolt(216, 140))

def arm_low(s, sd):
    s.plate(R(M([(234, 150), (254, 148), (256, 184), (236, 186)], sd), 4), 2.4)                    # upper arm
    s.plate(R(M([(224, 198), (264, 196), (266, 234), (226, 236)], sd), 4), 3.6)                     # forearm cuff: smaller, squarer
    s.plate(R(M([(226, 232), (266, 231), (267, 243), (227, 244)], sd), 3), 2.2)                     # wrist lip
    s.detail(''.join(rib(*M([(228, 207 + k * 9), (262, 206 + k * 9)], sd)) for k in range(2)) + bolt(*M([(258, 226)], sd)[0]))

def pauldron(s, sd):
    s.plate(R(M([(200, 140), (264, 144), (284, 134), (288, 148), (266, 162), (202, 156)], sd), 5), 2.6)   # rim lip
    s.plate(R(M([(194, 98), (248, 88), (276, 102), (284, 136), (264, 150), (204, 146), (192, 124)], sd), 20), 5)  # dome
    s.detail(''.join(rib(*M([(210, 106 + k * 10), (270, 104 + k * 10)], sd)) for k in range(3)) + rivets(*M([(210, 150), (276, 148)], sd), 6, 1))

def leg(s, sd):
    s.plate(R(M([(176, 292), (210, 292), (218, 308), (170, 310)], sd), 5), 3)                       # flared greave
    s.plate(R(M([(172, 232), (212, 232), (214, 266), (178, 268)], sd), 6), 3)                       # thigh
    s.plate(R(M([(170, 260), (214, 260), (220, 278), (206, 296), (178, 296), (164, 278)], sd), 12), 4.4)  # knee guard
    s.detail(''.join(rib(*M([(176, 272 + k * 7), (208, 272 + k * 7)], sd)) for k in range(3)) + ''.join(rib(*M([(178, 297 + k * 4), (212, 297 + k * 4)], sd)) for k in range(2))
             + rivets(*M([(174, 238), (210, 238)], sd), 4, 0.9))

# ------------------------------------------------------------------ back pieces
def helmet_back(s):
    s.plate(R([(134, 58), (186, 58), (198, 74), (198, 104), (122, 104), (122, 74)], 15), 4)
    s.detail(seam((128, 80), (192, 80)) + ''.join(slot(140 + k * 10, 88, 144 + k * 10, 98) for k in range(4)))

def collar_back(s):
    s.plate(R([(114, 92), (206, 92), (214, 108), (200, 122), (120, 122), (106, 108)], 10), 3.6)

def pack(s):
    for sd in (-1, 1):                                                                              # low side canisters (horizontal)
        s.plate(R(M([(176, 184), (214, 184), (216, 200), (176, 200)], sd), 7), 2.6)
    s.plate(R([(118, 104), (202, 104), (212, 124), (208, 192), (112, 192), (108, 124)], 16), 5)       # reactor housing
    s.plate(V.circle(160, 146, 20, 32), 4)                                                           # reactor port ring
    det = (f'<circle cx="160" cy="146" r="11" fill="#1d1b1e" stroke="{OLC}" stroke-width="1.2"/>'
           f'<circle cx="160" cy="146" r="8" fill="#4aa8e8" filter="url(#GLOW)"/><circle cx="160" cy="146" r="5" fill="#bfe6ff"/>'
           + ''.join(rib((126, 110 + k * 5), (194, 110 + k * 5)) for k in range(3))
           + rivets((120, 120), (120, 184), 6, 1) + rivets((200, 120), (200, 184), 6, 1)
           + seam((116, 172), (204, 172)) + bolt(118, 128) + bolt(202, 128) + bolt(120, 184) + bolt(200, 184))
    s.detail(det)

def build(facing, prefix):
    s = Suit(prefix)
    if facing == 'south':
        for sd in (-1, 1): leg(s, sd)
        torso(s)
        for sd in (-1, 1): arm_low(s, sd)
        helmet(s); collar(s); face(s)
        for sd in (-1, 1): pauldron(s, sd)
    else:
        for sd in (-1, 1): leg(s, sd)
        for sd in (-1, 1): arm_low(s, sd)
        helmet_back(s); collar_back(s); pack(s)
        for sd in (-1, 1): pauldron(s, sd)
    return s.render()

def piece(fn, prefix):
    s = Suit(prefix); fn(s); return s.render()

CELLS = [('Helmet + collar', (100, 44, 120, 90), 'south', lambda: piece(lambda s: (helmet(s), collar(s), face(s)), 'h')),
         ('Chest, abdomen, hip skirt', (84, 104, 152, 146), 'south', lambda: piece(torso, 'c')),
         ('Pauldrons and forearm cuffs', (26, 80, 268, 176), 'south', lambda: piece(lambda s: [f(s, d) for d in (-1, 1) for f in (arm_low, pauldron)], 'a')),
         ('Legs', (96, 222, 128, 94), 'south', lambda: piece(lambda s: (leg(s, -1), leg(s, 1)), 'l')),
         ('Pack (reactor)', (96, 80, 128, 134), 'north', lambda: piece(pack, 'p'))]

if __name__ == '__main__':
    out = sys.argv[1]
    C, PAD = 230, 12
    Wd = PAD + 3 * C + 2 * 300 + PAD * 2; Hd = 60 + 2 * C + 40
    parts = [f'<rect width="{Wd}" height="{Hd}" fill="#ece6dc"/>',
             f'<text x="{PAD}" y="32" font-family="DejaVu Sans, sans-serif" font-size="18" fill="#222">Heavy (Bulwark) - warcasket-like, blended with T-51b-inspired elements (our designs; grey = takes the suit tint)</text>']
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
        parts.append(f'<svg x="{cx}" y="58" width="292" height="{2 * C - 40}" viewBox="14 26 292 296" preserveAspectRatio="xMidYMid meet">'
                     f'{frame(f, f"F{j}_")}{build(f, f"B{j}_")}</svg>')
        parts.append(f'<text x="{cx + 146}" y="{50 + 2 * C - 16}" font-family="DejaVu Sans, sans-serif" font-size="13" text-anchor="middle" fill="#eee">Assembled ({f})</text>')
    open(f'{out}/svg/armor_heavy_t51_blend.svg', 'w').write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {Wd} {Hd}" width="{Wd}" height="{Hd}"><title>Heavy, warcasket-like</title>{"".join(parts)}</svg>')
    for f in ('south', 'north'):
        open(f'{out}/svg/armor_heavy_t51_suit_{f}.svg', 'w').write(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 320" width="320" height="320"><title>Heavy suit, warcasket-like</title>'
            f'{frame(f, "G_")}{build(f, "W_")}</svg>')
    print(Wd, Hd)
