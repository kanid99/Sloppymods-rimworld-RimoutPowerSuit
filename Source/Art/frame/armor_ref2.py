"""The owner's reference (heavy power armour) translated into our asset style with renderer v2: faceted plates lit by
their angle, cylinder/dome shading, glints, lit edges, grime, carbon undersuit, recessed vents, pistons, cables.
South view, fitted to the frame. Grey plates take the suit tint.
    python3 armor_ref2.py <out dir>"""
import math, sys
from render2 import Doc, mirror, mn, P, col
from armor_vfe import frame

def F(pts, n, kind='flat', tone='light'):
    return (pts, n, kind, tone)

def Fs(pts, n, s, kind='flat', tone='light'):
    return (mirror(pts, s), mn(n, s), kind, tone)

def circle(cx, cy, r, k=24):
    return [(cx + r * math.cos(2 * math.pi * i / k), cy + r * math.sin(2 * math.pi * i / k)) for i in range(k)]

def rect_x(d, x0, x1):
    return (min(x0, x1), max(x0, x1))

def build(prefix):
    d = Doc(prefix)
    # ---- thruster behind the right shoulder (viewer's right)
    ax, ay, bx, by, w = 212, 100, 236, 62, 6.5
    L = math.hypot(bx - ax, by - ay); ux, uy = (bx - ax) / L, (by - ay) / L; px, py = -uy * w, ux * w
    body = [(ax + px, ay + py), (bx + px, by + py), (bx - px, by - py), (ax - px, ay - py)]
    d.part([F(body, (0.6, 0, 0.8), 'cyl_h', 'metal')])
    d.add(f'<ellipse cx="{bx}" cy="{by}" rx="7" ry="4" transform="rotate({math.degrees(math.atan2(by - ay, bx - ax)) + 90:.1f} {bx} {by})" fill="#1c1a19"/>'
          f'<ellipse cx="{bx}" cy="{by}" rx="5" ry="2.6" transform="rotate({math.degrees(math.atan2(by - ay, bx - ax)) + 90:.1f} {bx} {by})" fill="#ff8a3a" fill-opacity="0.55" filter="url(#{d.glow})"/>')
    for t in (0.35, 0.6):
        d.groove([(ax + (bx - ax) * t + px, ay + (by - ay) * t + py), (ax + (bx - ax) * t - px, ay + (by - ay) * t - py)])

    # ---- legs
    for s in (-1, 1):
        d.part([Fs([(170, 226), (212, 226), (214, 264), (176, 266)], (0, 0, 1), s, 'cyl_h', 'dark')], grime=False)
        d.part([Fs([(178, 228), (208, 228), (206, 232), (180, 232)], (0, -0.8, 0.6), s),
                Fs([(180, 232), (206, 232), (206, 254), (184, 256)], (0.1, -0.05, 1), s),
                Fs([(206, 232), (210, 234), (210, 252), (206, 254)], (0.8, 0, 0.6), s)])
        d.groove(mirror([(184, 244), (205, 243)], s))
        d.part([Fs([(170, 304), (214, 304), (218, 310), (166, 310)], (0, -0.7, 0.7), s),
                Fs([(166, 310), (218, 310), (220, 318), (164, 318)], (0, 0.2, 0.98), s)])
        d.part([Fs([(180, 290), (206, 290), (208, 306), (182, 308)], (0, 0, 1), s),
                Fs([(206, 290), (214, 288), (216, 302), (208, 306)], (0.8, 0, 0.6), s),
                Fs([(180, 290), (174, 288), (172, 302), (182, 308)], (-0.8, 0, 0.6), s)])
        d.groove(mirror([(194, 292), (195, 304)], s))
        d.hazard(mirror([(182, 292), (198, 292), (198, 296), (182, 296)], s))
        d.part([Fs([(172, 256), (212, 256), (206, 262), (178, 262)], (0, -0.75, 0.66), s),
                Fs([(178, 262), (206, 262), (210, 278), (202, 290), (184, 290), (174, 278)], (0, 0.05, 1), s),
                Fs([(206, 262), (212, 256), (220, 272), (210, 278)], (0.75, -0.2, 0.6), s),
                Fs([(178, 262), (172, 256), (166, 272), (174, 278)], (-0.75, -0.2, 0.6), s),
                Fs([(210, 278), (220, 272), (214, 286), (202, 290)], (0.6, 0.5, 0.6), s),
                Fs([(174, 278), (166, 272), (172, 286), (184, 290)], (-0.6, 0.5, 0.6), s)])
        jx = 160 + s * 61
        d.part([F(circle(jx, 276, 6.5), (0, 0, 1), 'dome', 'dark')], grime=False)
        d.bolt(jx, 276, 1.6)
        kx = 160 + s * 32
        d.light(kx - 3.5, 280, 7, 3, '#4aa8ff', '#e2f2ff')

    # ---- waist: dark undersuit, cables, chevron abdomen, groin plate, hip tassets
    d.part([F([(118, 160), (202, 160), (206, 200), (188, 214), (132, 214), (114, 200)], (0, 0, 1), 'cyl_h', 'dark')], grime=False)
    for s in (-1, 1):
        for k in range(2):
            d.tube(mirror([(114 + k * 6, 162), (110 + k * 6, 180), (116 + k * 6, 196), (126 + k * 5, 208)], s), 2.8)
    d.part([F([(152, 210), (168, 210), (170, 214), (150, 214)], (0, -0.8, 0.6)),
            F([(150, 214), (170, 214), (168, 228), (160, 234), (152, 228)], (0, 0.05, 1))])
    for k in (3, 2, 1, 0):
        y0 = 164 + k * 11
        d.part([F([(130 + k * 3, y0), (190 - k * 3, y0), (192 - k * 3, y0 + 3), (128 + k * 3, y0 + 3)], (0, -0.85, 0.5)),
                F([(128 + k * 3, y0 + 3), (192 - k * 3, y0 + 3), (186 - k * 3, y0 + 10), (160, y0 + 14), (134 + k * 3, y0 + 10)], (0, 0.1, 1))])
    for s in (-1, 1):
        d.part([Fs([(186, 200), (212, 204), (220, 224), (200, 232), (190, 220)], (0.35, 0.1, 0.93), s),
                Fs([(212, 204), (218, 206), (226, 226), (220, 224)], (0.85, 0.1, 0.5), s)])
        d.bolt(*mirror([(200, 214)], s)[0])

    # ---- breastplate
    facets = [F([(118, 110), (202, 110), (212, 122), (160, 128), (108, 122)], (0, -0.55, 0.83)),
              F([(126, 162), (194, 162), (190, 172), (130, 172)], (0, 0.7, 0.7))]
    for s in (-1, 1):
        facets += [Fs([(160, 128), (212, 122), (224, 128), (220, 150), (200, 164), (162, 166)], (0.32, 0.08, 0.94), s),
                   Fs([(212, 122), (222, 124), (230, 132), (228, 152), (220, 150), (224, 128)], (0.85, 0, 0.52), s),
                   Fs([(160, 126), (165, 128), (165, 162), (160, 168)], (0.6, 0, 0.8), s)]
    d.part(facets)
    for s in (-1, 1):
        d.groove(mirror([(176, 154), (196, 150), (214, 140)], s))
        d.bolt(*mirror([(218, 132)], s)[0])
    d.vent(152, 113, 168, 122, 3)
    d.light(132, 116, 8, 3.4, '#f2a83a', '#fff0c8'); d.light(180, 116, 8, 3.4, '#f2a83a', '#fff0c8')
    d.light(124, 146, 7, 3.2, '#4aa8ff', '#e2f2ff'); d.light(189, 146, 7, 3.2, '#3ad6c4', '#d8fff8')
    d.stencil(190, 160, 'SM-07', 3.2)

    # ---- arms
    for s in (-1, 1):
        d.part([Fs([(234, 150), (254, 148), (256, 182), (236, 184)], (0, 0, 1), s, 'cyl_h')])
        ex = 160 + s * 86
        d.part([F(circle(ex, 188, 7.5), (0, 0, 1), 'dome', 'dark')], grime=False)
        d.bolt(ex, 188, 1.5)
        d.piston(mirror([(258, 158)], s)[0], mirror([(266, 204)], s)[0])
        d.part([Fs([(228, 212), (266, 210), (268, 230), (260, 240), (232, 242)], (0, 0.1, 1), s, 'cyl_h')])
        d.part([Fs([(226, 194), (262, 192), (266, 206), (264, 212), (228, 214)], (0, -0.1, 1), s, 'cyl_h')])
        d.part([Fs([(232, 238), (262, 236), (262, 245), (232, 247)], (0, 0, 1), s, 'cyl_h', 'dark')], grime=False)
        for k in range(3):
            d.groove(mirror([(234 + k * 9, 238), (234 + k * 9, 246)], s), 0.7)
        d.hazard(mirror([(254, 197), (263, 196), (264, 202), (255, 203)], s))
        d.groove(mirror([(230, 224), (266, 222)], s)); d.bolt(*mirror([(236, 232)], s)[0])

    # ---- neck cables, helmet, collar, respirator
    for s in (-1, 1):
        d.tube(mirror([(178, 102), (186, 94), (190, 86)], s), 2.6)
    for s in (-1, 1):
        d.part([Fs([(186, 84), (200, 82), (204, 104), (190, 108), (184, 98)], (0.55, 0, 0.83), s)])
    from armor_ws2 import rounded
    d.part([F(rounded([(134, 58), (186, 58), (198, 74), (198, 100), (122, 100), (122, 74)], 16), (0, -0.1, 1), 'dome')])
    d.part([F([(146, 56), (174, 56), (178, 70), (142, 70)], (0, -0.5, 0.86)),
            F([(126, 72), (194, 72), (198, 76), (122, 76)], (0, -0.8, 0.6)),
            F([(122, 76), (198, 76), (194, 84), (126, 84)], (0, 0.1, 1))], shadow=True)
    for k in range(3):
        d.groove([(148, 60 + k * 3.5), (172, 60 + k * 3.5)], 0.7)
    visor = [(126, 85), (148, 87), (160, 93), (172, 87), (194, 85), (192, 93), (172, 97), (160, 102), (148, 97), (128, 93)]
    d.recess(visor, 'dark')
    d.add(f'<polyline points="{P([(131, 89), (149, 91), (160, 97.5), (171, 91), (189, 89)])}" fill="none" stroke="#ff3a22" stroke-width="3.4" filter="url(#{d.glow})"/>'
          f'<polyline points="{P([(132, 89), (149, 91.2), (160, 97.4), (171, 91.2), (188, 89)])}" fill="none" stroke="#ffd0bf" stroke-width="1.1"/>'
          f'<polyline points="{P([(136, 87.6), (146, 88.4)])}" stroke="#ffffff" stroke-width="0.9" stroke-opacity="0.7"/>')
    d.part([F([(118, 96), (202, 96), (210, 104), (110, 104)], (0, -0.8, 0.6)),
            F([(110, 104), (210, 104), (200, 122), (120, 122)], (0, 0.15, 0.99))])
    for x in (118, 140, 180, 202):
        d.bolt(x, 113, 1.1)
    d.part([F([(144, 100), (176, 100), (180, 112), (172, 120), (148, 120), (140, 112)], (0, 0.05, 1)),
            F([(148, 120), (172, 120), (168, 125), (152, 125)], (0, 0.8, 0.6))])
    d.vent(146, 104, 174, 117, 5)

    # ---- pauldrons (90% about the shoulder)
    SC = lambda p: [(236 + (x - 236) * 0.9, 120 + (y - 120) * 0.9) for x, y in p]
    for s in (-1, 1):
        G = lambda p, n, kind='flat', tone='light': Fs(SC(p), n, s, kind, tone)
        d.part([G([(202, 138), (272, 142), (290, 134), (288, 146), (272, 156), (206, 152)], (0.2, 0.35, 0.92)),
                G([(206, 152), (272, 156), (288, 146), (284, 152), (270, 160), (208, 156)], (0.1, 0.85, 0.5))])
        d.part([G([(196, 104), (236, 92), (272, 100), (288, 126), (270, 142), (206, 138), (192, 122)], (0.2, 0.05, 0.98)),
                G([(200, 98), (236, 84), (274, 94), (272, 100), (236, 92), (196, 104)], (0.15, -0.85, 0.5)),
                G([(272, 100), (274, 94), (294, 126), (288, 126)], (0.85, -0.2, 0.5)),
                G([(288, 126), (294, 126), (290, 136), (270, 142)], (0.7, 0.5, 0.5))])
        d.part([G([(210, 100), (238, 91), (264, 98), (262, 105), (238, 99), (213, 106)], (0.1, -0.5, 0.86))], shadow=True)
        v = mirror(SC([(244, 112), (268, 126)]), s)
        x0, x1 = sorted([v[0][0], v[1][0]])
        d.vent(x0, v[0][1], x1, v[1][1], 5)
        h = mirror(SC([(208, 116), (232, 116), (232, 130), (208, 130)]), s)
        d.recess(h)
        for p in mirror(SC([(211, 119), (229, 119), (229, 127), (211, 127)]), s):
            d.bolt(*p, 0.8)
        d.stencil(*mirror(SC([(222, 138)]), s)[0], '7A', 3.2)
        lx, ly = mirror(SC([(284, 132)]), s)[0]
        d.light(lx - 2, ly - 1.6, 4, 3.2, '#f2a83a', '#fff0c8')
        d.groove(mirror(SC([(206, 134), (270, 138)]), s))
    return d.svg()

if __name__ == '__main__':
    out = sys.argv[1]
    open(f'{out}/svg/armor_ref2_suit_south.svg', 'w').write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 320" width="320" height="320"><title>Heavy suit from the reference, faceted</title>'
        f'{frame("south", "G_")}{build("R_")}</svg>')
    print('ok')
