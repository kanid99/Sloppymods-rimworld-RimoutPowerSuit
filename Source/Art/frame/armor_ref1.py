"""The owner's reference render (heavy power armour on a platform) translated into our asset style, fitted to the
frame: light grey plates that take the suit tint, dark undersuit plates, soft shading and light lines (armor_vfe.Suit).
South view. From the reference: a ribbed dome helmet with a winged red visor, a slatted respirator and cheek pods;
big angular layered pauldrons with vent grilles and stencils; an angular breastplate with small amber/blue/teal
lights; a stacked chevron abdomen with dark cables at the sides; angular hip plates; dark armoured thighs under a
light front plate; large knee guards with round side joints and a blue light; angular greaves over boot caps;
rounded segmented forearms with a hazard stripe; a thruster cylinder rising behind one shoulder.
    python3 armor_ref1.py <out dir>"""
import math, sys
import armor_vfe as V
from armor_vfe import Suit, seam, bolt, slot, OLC, frame
from armor_ws2 import rounded as R
from armor_t51 import rib, rivets
from frame4 import X

M = X

def light(x, y, w, h, col, core):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{min(w, h) / 2}" fill="#1d1b1e"/>'
            f'<rect x="{x + 0.8}" y="{y + 0.8}" width="{w - 1.6}" height="{h - 1.6}" rx="{min(w, h) / 2 - 0.8}" fill="{col}" filter="url(#GLOW)"/>'
            f'<rect x="{x + 1.2}" y="{y + 1.2}" width="{w - 2.4}" height="{h - 2.4}" rx="{min(w, h) / 2 - 1.2}" fill="{core}"/>')

def chevrons(pts, step=4.5):
    """a small yellow-and-black warning stripe clipped to a quad"""
    xs = [x for x, _ in pts]; ys = [y for _, y in pts]; h = max(ys) - min(ys)
    cid = f'hz{abs(hash(tuple(pts))) % 100000}'
    s = f'<clipPath id="{cid}"><polygon points="{V.P(pts)}"/></clipPath><g clip-path="url(#{cid})"><rect x="{min(xs)}" y="{min(ys)}" width="{max(xs) - min(xs)}" height="{h}" fill="#e2b03c"/>'
    x = min(xs) - h
    while x < max(xs) + h:
        s += f'<polygon points="{V.P([(x, max(ys)), (x + step / 2, max(ys)), (x + step / 2 + h, min(ys)), (x + h, min(ys))])}" fill="#262220"/>'
        x += step
    return s + '</g>'

def stencil(x, y, t, size=3.6, anchor='middle'):
    return (f'<text x="{x}" y="{y}" font-family="DejaVu Sans Mono, monospace" font-weight="bold" font-size="{size}" '
            f'fill="#3a383c" fill-opacity="0.65" text-anchor="{anchor}">{t}</text>')

def thruster(s):
    """behind the right shoulder (viewer's right), rising up and out"""
    s.plate([(206, 98), (216, 102), (240, 66), (230, 62)], 2.4)
    s.plate(R([(226, 60), (240, 66), (244, 58), (230, 52)], 2), 1.6, tone='dark')
    s.detail(rib((212, 92), (222, 96)) + rib((218, 82), (228, 86)))

def helmet(s):
    for sd in (-1, 1):                                                                             # cheek pods
        s.plate(R(M([(190, 82), (202, 84), (204, 104), (192, 106)], sd), 4), 2)
    s.plate(R([(134, 58), (186, 58), (198, 74), (198, 104), (122, 104), (122, 74)], 16), 4)       # dome
    visor = [(126, 78), (148, 82), (160, 89), (172, 82), (194, 78), (192, 88), (172, 93), (160, 99), (148, 93), (128, 88)]
    s.detail(''.join(rib((138, 62 + k * 4), (182, 62 + k * 4)) for k in range(3))
             + f'<polygon points="{V.P(visor)}" fill="#1d1b1e" stroke="{OLC}" stroke-width="1.2" stroke-linejoin="round"/>'
             + f'<polyline points="{V.P([(131, 84), (149, 87), (160, 93.5), (171, 87), (189, 84)])}" fill="none" stroke="#ff4a2e" stroke-width="3" filter="url(#GLOW)"/>'
             + f'<polyline points="{V.P([(132, 84), (149, 87.2), (160, 93.4), (171, 87.2), (188, 84)])}" fill="none" stroke="#ffc4b0" stroke-width="1.1"/>')

def collar(s):
    s.plate(R([(116, 98), (204, 98), (212, 110), (198, 124), (122, 124), (108, 110)], 8), 3.4)

def face(s):
    s.plate(R([(142, 98), (178, 98), (182, 112), (172, 122), (148, 122), (138, 112)], 8), 2.8)      # slatted respirator
    s.detail(''.join(slot(146, 103 + k * 4.4, 174, 105.4 + k * 4.4) for k in range(4)))

def torso(s):
    for sd in (-1, 1):                                                                             # dark cables at the waist
        for k in range(2):
            pts = M([(110 + k * 6, 158), (106 + k * 6, 178), (112 + k * 6, 196), (122 + k * 5, 208)], sd)
            s.detail(f'<polyline points="{V.P(pts)}" fill="none" stroke="{OLC}" stroke-width="4.6" stroke-linecap="round"/>'
                     f'<polyline points="{V.P(pts)}" fill="none" stroke="#4a4b52" stroke-width="3" stroke-linecap="round"/>'
                     f'<polyline points="{V.P([(x - 0.6, y) for x, y in pts])}" fill="none" stroke="#8c8e96" stroke-width="0.8" stroke-linecap="round"/>')
    s.plate(R([(150, 210), (170, 210), (168, 228), (160, 233), (152, 228)], 3), 2)                  # groin plate
    for k in range(4):                                                                             # stacked chevron abdomen
        y0 = 166 + k * 11
        s.plate(R([(128 + k * 3, y0), (192 - k * 3, y0), (186 - k * 3, y0 + 9), (160, y0 + 13), (134 + k * 3, y0 + 9)], 3), 2.2)
    s.plate(R([(112, 112), (208, 112), (226, 126), (222, 152), (200, 168), (120, 168), (98, 152), (94, 126)], 6), 4.6)   # breastplate
    for sd in (-1, 1):
        pec = R(M([(163, 120), (206, 118), (222, 128), (218, 142), (200, 156), (180, 162), (164, 164)], sd), 9)
        edge = R(M([(218, 142), (200, 156), (180, 162), (164, 163), (163, 124)], sd), 8)[3:-3]
        s.detail(f'<polygon points="{V.P(pec)}" fill="#ffffff" fill-opacity="0.14" filter="url(#SOFT)"/>'
                 f'<polyline points="{V.P(edge)}" fill="none" stroke="#3c3a40" stroke-width="0.9" stroke-opacity="0.45" stroke-linecap="round"/>')
    s.detail(light(132, 116, 8, 3.6, '#f2a83a', '#ffe2a8') + light(180, 116, 8, 3.6, '#f2a83a', '#ffe2a8')
             + light(124, 148, 7, 3.4, '#4aa8ff', '#cfe8ff') + light(189, 148, 7, 3.4, '#3ad6c4', '#c8fff6')
             + stencil(190, 162, 'SM-07') + bolt(104, 136) + bolt(216, 136))

def hips(s):
    for sd in (-1, 1):
        s.plate(R(M([(184, 198), (214, 202), (224, 226), (200, 234), (186, 220)], sd), 4), 3)

def arm(s, sd):
    s.plate(R(M([(234, 150), (254, 148), (256, 182), (236, 184)], sd), 4), 2.4)                    # upper arm
    jx = 160 + sd * 86
    s.plate(V.circle(jx, 188, 7, 18), 2, tone='dark')                                                 # elbow joint
    s.plate(R(M([(226, 216), (266, 214), (270, 230), (262, 242), (230, 244)], sd), 7), 3)            # lower forearm segment
    s.plate(R(M([(224, 192), (264, 190), (270, 206), (266, 218), (226, 220)], sd), 7), 3.4)           # upper forearm segment
    hz = M([(254, 196), (264, 195), (266, 201), (256, 202)], sd)
    s.detail(chevrons(hz) + bolt(*M([(232, 230)], sd)[0]) + seam(*M([(230, 208), (264, 206)], sd)))

def pauldron(s, sd):
    SC = lambda p: [(236 + (x - 236) * 0.9, 120 + (y - 120) * 0.9) for x, y in p]
    s.plate(R(M(SC([(200, 136), (272, 140), (292, 130), (290, 146), (272, 158), (204, 152)]), sd), 2), 2.2)      # lower lame
    s.plate(R(M(SC([(196, 100), (236, 86), (274, 96), (294, 128), (272, 144), (206, 140), (192, 122)]), sd), 3), 4)     # main plate
    s.plate(R(M(SC([(206, 96), (238, 86), (268, 96), (264, 108), (238, 100), (210, 108)]), sd), 2), 2)          # stepped top plate
    vx = [M(SC([(244 + k * 6, 0)]), sd)[0][0] for k in range(5)]
    s.detail(''.join(slot(min(x, x + sd * 3.2), 115, max(x, x + sd * 3.2), 129) for x in vx)
             + stencil(*M(SC([(220, 130)]), sd)[0], '7A', 3.4) + bolt(*M(SC([(212, 120)]), sd)[0]) + bolt(*M(SC([(284, 134)]), sd)[0]))

def leg(s, sd):
    s.plate(R(M([(170, 228), (212, 228), (214, 264), (176, 266)], sd), 6), 2.6, tone='dark')        # dark armoured thigh
    s.plate(R(M([(178, 234), (206, 234), (206, 256), (182, 258)], sd), 5), 2.4)                      # light front plate
    s.plate(R(M([(168, 304), (216, 304), (220, 318), (166, 318)], sd), 3), 2.4)                      # boot cap
    s.plate(R(M([(172, 286), (214, 286), (218, 300), (208, 310), (178, 310), (170, 300)], sd), 4), 3.2)    # greave
    s.plate(R(M([(170, 258), (214, 258), (220, 274), (208, 290), (180, 290), (166, 274)], sd), 8), 4)       # knee guard
    jx, jy = M([(220, 276)], sd)[0]
    s.plate(V.circle(jx, jy, 6, 16), 1.8, tone='dark')                                                   # round side joint
    kx, ky = M([(192, 280)], sd)[0]
    s.detail(light(kx - 3.5, ky - 1.7, 7, 3.4, '#4aa8ff', '#cfe8ff') + chevrons(M([(176, 292), (190, 292), (190, 296), (176, 296)], sd)))

def build(prefix):
    s = Suit(prefix)
    thruster(s)
    for sd in (-1, 1): leg(s, sd)
    hips(s); torso(s)
    for sd in (-1, 1): arm(s, sd)
    helmet(s); collar(s); face(s)
    for sd in (-1, 1): pauldron(s, sd)
    return s.render()

if __name__ == '__main__':
    out = sys.argv[1]
    body = build('R_')
    open(f'{out}/svg/armor_ref1_suit_south.svg', 'w').write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 320" width="320" height="320"><title>Heavy suit from the reference</title>'
        f'{frame("south", "G_")}{body}</svg>')
    print('ok')
