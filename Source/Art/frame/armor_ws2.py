"""Heavy (Bulwark) pieces that *resemble* the warcasket design language (not copies): a massive top-heavy
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

# ------------------------------------------------------------------ front pieces
def helmet(s):
    s.plate(R([(134, 60), (186, 60), (198, 76), (198, 106), (122, 106), (122, 76)], 15), 4)       # dome
    for sd in (-1, 1):                                                                             # ear pods
        s.plate(R(M([(192, 76), (204, 78), (206, 98), (194, 100)], sd), 5), 2.4)
    s.detail(f'<path d="M131,82 Q160,78 189,82 L188,93 Q160,96 132,93 Z" fill="#1d1b1e" stroke="{OLC}" stroke-width="1.3"/>'
             f'<path d="M136,86.5 Q160,83.5 184,86.5" stroke="{ACC}" stroke-width="3" fill="none" filter="url(#GLOW)"/>'
             f'<path d="M137,86.5 Q160,84 183,86.5" stroke="#ffd7c4" stroke-width="1.4" fill="none"/>'
             + seam((140, 70), (180, 70)) + bolt(127, 98) + bolt(193, 98))

def collar(s):
    s.plate(R([(116, 96), (204, 96), (212, 110), (198, 124), (122, 124), (108, 110)], 8), 3.6)
    s.detail(seam((128, 116), (192, 116)))

def torso(s):
    for k, (y, w) in enumerate(((196, 30), (186, 34))):                                            # abdomen bands
        s.plate(R([(160 - w, y), (160 + w, y), (160 + w - 3, y + 12), (160 - w + 3, y + 12)], 4), 2.4)
    s.plate(R([(140, 204), (180, 204), (184, 232), (160, 242), (136, 232)], 6), 3)                   # hip skirt
    for sd in (-1, 1):
        s.plate(R(M([(180, 200), (220, 204), (232, 236), (198, 242), (182, 226)], sd), 7), 3.4)
    s.plate(R([(110, 116), (210, 116), (228, 134), (226, 168), (206, 188), (114, 188), (94, 168), (92, 134)], 18), 5)   # barrel chest
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
    s.detail(seam((160, 166), (160, 184))                                                          # the sternum channel below them
             + f'<rect x="184" y="172" width="14" height="3.6" rx="1" fill="#1d1b1e"/><rect x="186" y="173" width="10" height="1.6" fill="#8ef08a" filter="url(#GLOW)"/>'
             + bolt(104, 140) + bolt(216, 140))

def arm_low(s, sd):
    s.plate(R(M([(234, 150), (254, 148), (256, 184), (236, 186)], sd), 4), 2.4)                    # upper arm
    s.plate(R(M([(224, 198), (264, 196), (266, 234), (226, 236)], sd), 4), 3.6)                     # forearm cuff: smaller, squarer
    s.plate(R(M([(226, 232), (266, 231), (267, 243), (227, 244)], sd), 3), 2.2)                     # wrist lip
    a, b = M([(234, 208)], sd)[0], M([(254, 207)], sd)[0]
    s.detail(slot(min(a[0], b[0]), 205, max(a[0], b[0]), 210) + bolt(*M([(256, 224)], sd)[0]))

def pauldron(s, sd):
    """angular, armoured: tilted down and outward, flat faceted planes, tight corners, a sharp outer point"""
    s.plate(R(M([(204, 138), (274, 142), (294, 132), (292, 148), (274, 160), (208, 154)], sd), 2), 2.4)      # angled lower lame
    s.plate(R(M([(198, 102), (236, 88), (274, 98), (294, 130), (272, 146), (208, 142), (194, 124)], sd), 3), 4.4)   # main plate
    s.plate(R(M([(214, 100), (238, 92), (270, 104), (268, 110), (238, 99), (216, 106)], sd), 2), 1.6)     # raised ridge along the top
    s.detail(seam(*M([(214, 120), (276, 128)], sd)) + bolt(*M([(216, 134)], sd)[0]) + bolt(*M([(276, 136)], sd)[0]))

def leg(s, sd):
    s.plate(R(M([(176, 292), (210, 292), (218, 308), (170, 310)], sd), 5), 3)                       # flared greave
    s.plate(R(M([(172, 232), (212, 232), (214, 266), (178, 268)], sd), 6), 3)                       # thigh
    s.plate(R(M([(170, 260), (214, 260), (220, 278), (206, 296), (178, 296), (164, 278)], sd), 12), 4.4)  # knee guard
    s.detail(bolt(*M([(192, 278)], sd)[0], 2))

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
           + ''.join(slot(132 + k * 12, 112, 140 + k * 12, 118) for k in range(5))
           + seam((116, 172), (204, 172)) + bolt(118, 128) + bolt(202, 128) + bolt(120, 184) + bolt(200, 184))
    s.detail(det)

def build(facing, prefix):
    s = Suit(prefix)
    if facing == 'south':
        for sd in (-1, 1): leg(s, sd)
        torso(s)
        for sd in (-1, 1): arm_low(s, sd)
        helmet(s); collar(s)
        for sd in (-1, 1): pauldron(s, sd)
    else:
        for sd in (-1, 1): leg(s, sd)
        for sd in (-1, 1): arm_low(s, sd)
        helmet_back(s); collar_back(s); pack(s)
        for sd in (-1, 1): pauldron(s, sd)
    return s.render()

def piece(fn, prefix):
    s = Suit(prefix); fn(s); return s.render()

CELLS = [('Helmet + collar', (100, 44, 120, 90), 'south', lambda: piece(lambda s: (helmet(s), collar(s)), 'h')),
         ('Chest, abdomen, hip skirt', (84, 104, 152, 146), 'south', lambda: piece(torso, 'c')),
         ('Pauldrons and forearm cuffs', (16, 80, 288, 180), 'south', lambda: piece(lambda s: [f(s, d) for d in (-1, 1) for f in (arm_low, pauldron)], 'a')),
         ('Legs', (96, 222, 128, 94), 'south', lambda: piece(lambda s: (leg(s, -1), leg(s, 1)), 'l')),
         ('Pack (reactor)', (96, 80, 128, 134), 'north', lambda: piece(pack, 'p'))]

if __name__ == '__main__':
    out = sys.argv[1]
    C, PAD = 230, 12
    Wd = PAD + 3 * C + 2 * 300 + PAD * 2; Hd = 60 + 2 * C + 40
    parts = [f'<rect width="{Wd}" height="{Hd}" fill="#ece6dc"/>',
             f'<text x="{PAD}" y="32" font-family="DejaVu Sans, sans-serif" font-size="18" fill="#222">Heavy (Bulwark) - resembling the warcasket design language, our own designs (grey = takes the suit tint)</text>']
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
    open(f'{out}/svg/armor_heavy_warcasket_like.svg', 'w').write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {Wd} {Hd}" width="{Wd}" height="{Hd}"><title>Heavy, warcasket-like</title>{"".join(parts)}</svg>')
    for f in ('south', 'north'):
        open(f'{out}/svg/armor_heavy_wl_suit_{f}.svg', 'w').write(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 320" width="320" height="320"><title>Heavy suit, warcasket-like</title>'
            f'{frame(f, "G_")}{build(f, "W_")}</svg>')
    print(Wd, Hd)
