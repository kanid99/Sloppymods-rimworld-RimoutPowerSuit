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

def band(tl, tr, br, bl, sag=3.0, k=10):
    """a band round a cylinder seen from just above: its top and bottom edges bow down"""
    def curve(a, b):
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + sag * 2
        return [((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * mx + t * t * b[0],
                 (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * my + t * t * b[1]) for t in [i / k for i in range(k + 1)]]
    return curve(tl, tr) + curve(br, bl)

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

    # ---- waist (from the sample): a broad, heavy segmented abdomen, a thick belt with a buckle box,
    # a shield-shaped groin plate and big curved hip plates
    d.part([F([(116, 160), (204, 160), (208, 206), (190, 216), (130, 216), (112, 206)], (0, 0, 1), 'cyl_h', 'dark')], grime=False)
    for s_ in (-1, 1):
        d.tube(mirror([(118, 164), (112, 184), (116, 204)], s_), 2.8)
    for k in (2, 1, 0):                                        # three thick bands, each a front face and two angled sides
        y0 = 166 + k * 13; w = 44 - k * 3
        d.part([F([(160 - w + 10, y0), (160 + w - 10, y0), (160 + w - 9, y0 + 3), (160 - w + 9, y0 + 3)], (0, -0.85, 0.5)),
                F([(160 - w + 9, y0 + 3), (160 + w - 9, y0 + 3), (160 + w - 11, y0 + 13), (160 - w + 11, y0 + 13)], (0, 0.08, 1)),
                F([(160 + w - 10, y0), (160 + w, y0 + 4), (160 + w - 3, y0 + 12), (160 + w - 11, y0 + 13), (160 + w - 9, y0 + 3)], (0.75, 0, 0.66)),
                F([(160 - w + 10, y0), (160 - w, y0 + 4), (160 - w + 3, y0 + 12), (160 - w + 11, y0 + 13), (160 - w + 9, y0 + 3)], (-0.75, 0, 0.66))])
        d.part([F([(155, y0 + 2), (165, y0 + 2), (164, y0 + 12), (156, y0 + 12)], (0, -0.1, 1))], shadow=False, grime=False)
    # belt
    d.part([F([(114, 205), (206, 205), (208, 210), (112, 210)], (0, -0.8, 0.6), 'flat', 'metal'),
            F([(112, 210), (208, 210), (204, 217), (116, 217)], (0, 0.15, 1), 'cyl_h', 'metal')], grime=False)
    d.part([F([(150, 203), (170, 203), (172, 219), (148, 219)], (0, 0, 1))])                       # buckle box
    d.recess([(153, 207), (167, 207), (167, 215), (153, 215)], 'dark')
    d.light(156.5, 210, 7, 2.6, '#f2a83a', '#fff0c8')
    for s_ in (-1, 1):                                                                         # belt pouches
        d.part([Fs([(176, 207), (190, 207), (190, 220), (176, 220)], (0, 0.1, 1), s_)])
        d.groove(mirror([(176, 211), (190, 211)], s_), 0.7)
    # big shield-shaped groin plate
    d.part([F([(142, 218), (178, 218), (176, 222), (144, 222)], (0, -0.8, 0.6)),
            F([(144, 222), (160, 222), (160, 252), (150, 244), (142, 232)], (-0.25, 0.1, 0.96)),
            F([(160, 222), (176, 222), (178, 232), (170, 244), (160, 252)], (0.25, 0.1, 0.96))])
    d.bolt(160, 229, 1.3)
    # big curved hip plates
    for s_ in (-1, 1):
        d.part([Fs([(182, 210), (210, 212), (222, 224), (224, 244), (206, 252), (186, 244), (180, 226)], (0.35, 0.05, 0.94), s_),
                Fs([(210, 212), (216, 213), (230, 226), (232, 244), (224, 244), (222, 224)], (0.85, 0.05, 0.52), s_),
                Fs([(186, 244), (206, 252), (224, 244), (222, 250), (206, 258), (188, 250)], (0.15, 0.8, 0.58), s_)])
        d.groove(mirror([(186, 230), (206, 236), (222, 232)], s_))
        d.bolt(*mirror([(198, 222)], s_)[0])
        d.bolt(*mirror([(214, 240)], s_)[0])

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
        acx = 160 + s * 86
        d.add(f'<g transform="translate({acx} 0) scale(1.38 1) translate({-acx} 0)">')   # bulkier arms (sample ratio)
        d.part([F(mirror(band((230, 148), (262, 146), (262, 186), (231, 188), 1.8), s), (0, 0, 1), 'cyl_h')])
        ex = 160 + s * 86
        d.part([F(circle(ex, 189, 10.5), (0, 0, 1), 'dome', 'dark')], grime=False)
        d.bolt(ex, 188, 1.5)
        d.piston(mirror([(258, 158)], s)[0], mirror([(266, 204)], s)[0])
        lower = band((231, 212), (263, 211), (262, 238), (232, 240), 2.6)
        upper = band((230, 193), (262, 192), (263, 212), (231, 214), 2.6)
        ring = band((232, 237), (262, 236), (262, 244), (232, 246), 2.2)
        d.part([F(mirror(lower, s), (0, 0.1, 1), 'cyl_h')])
        d.part([F(mirror(upper, s), (0, -0.1, 1), 'cyl_h')])
        d.part([F(mirror(ring, s), (0, 0, 1), 'cyl_h', 'dark')], grime=False)
        for k in range(1, 4):
            x = 232 + k * 7.5
            d.groove(mirror([(x, 237.5 + 2.2 * 2 * 4 * ((x - 232) / 30) * (1 - (x - 232) / 30) * 0.5 + 0.2), (x, 244.5)], s), 0.7)
        mid = band((230, 202), (262, 201), (262, 201), (230, 202), 2.6)[:11]
        d.groove(mirror(mid, s))
        lowg = band((231, 224), (263, 223), (263, 223), (231, 224), 2.6)[:11]
        d.hazard(mirror([(252, 197), (261, 196), (262, 202), (253, 203)], s))
        d.groove(mirror(lowg, s)); d.bolt(*mirror([(236, 232)], s)[0])
        # an armoured gauntlet over the frame's fist: knuckle plate, back of hand, thumb, finger segments
        d.part([Fs([(234, 246), (260, 246), (262, 256), (232, 256)], (0, -0.4, 0.92), s, 'flat', 'metal'),
                Fs([(232, 256), (262, 256), (260, 266), (234, 266)], (0, 0.3, 0.95), s, 'flat', 'dark')], grime=False)
        for k in range(4):
            x = 235 + k * 6.5
            d.part([Fs([(x, 264), (x + 5.4, 264), (x + 5, 272), (x + 0.4, 272)], (0, 0.4, 0.9), s, 'flat', 'metal')], shadow=False, grime=False)
        d.part([Fs([(230, 250), (234, 250), (232, 262), (227, 260)], (-0.7, 0.2, 0.7), s, 'flat', 'metal')], shadow=False, grime=False)
        d.groove(mirror([(236, 251), (258, 251)], s), 0.7)
        d.add('</g>')

    # collar with a curved neck cutout: a dark recess where the helmet sits, two collar pieces either side
    neck = [(132, 110), (188, 110), (186, 122), (176, 131), (144, 131), (134, 122)]
    d.recess(neck, 'dark')
    for s_ in (-1, 1):
        inner = [(190, 126), (185, 121), (184, 116), (186, 112)]
        d.part([Fs([(186, 112), (202, 112), (210, 118), (190, 118)], (0, -0.8, 0.6), s_),
                Fs([(190, 118), (210, 118), (200, 126)] + inner[:1], (0, 0.15, 0.99), s_)])
        d.bolt(*mirror([(200, 121)], s_)[0], 1.1)
        d.groove(mirror([(188, 112), (184, 118), (186, 124), (192, 128)], s_), 0.8)
    # ---- helmet (from the owner's second reference): crested dome, wide tinted visor, gas-mask snout, hoses
    from armor_ws2 import rounded
    d.add('<g transform="translate(160 0) scale(0.85 1) translate(-160 0)">')
    for s_ in (-1, 1):                                                                             # ear housings
        d.part([Fs([(186, 80), (200, 78), (204, 98), (190, 102), (184, 94)], (0.6, 0, 0.8), s_)])
        d.bolt(*mirror([(195, 90)], s_)[0], 1.4)
    d.part([F(rounded([(134, 56), (186, 56), (198, 72), (198, 98), (122, 98), (122, 72)], 17), (0, -0.1, 1), 'dome')])
    d.part([F([(155, 50), (165, 50), (167, 72), (153, 72)], (0, -0.4, 0.92)),                      # raised crest ridge
            F([(165, 50), (169, 54), (170, 72), (167, 72)], (0.8, 0, 0.6))], shadow=True)
    d.part([F([(124, 70), (196, 70), (200, 75), (120, 75)], (0, -0.8, 0.6)),                        # brow
            F([(120, 75), (200, 75), (196, 80), (124, 80)], (0, 0.2, 0.98))])
    visor = [(126, 81), (194, 81), (190, 95), (130, 95)]
    d.recess(visor, 'dark')
    gid = d.id()
    d.defs.append(f'<linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f6d77a"/>'
                  f'<stop offset="0.5" stop-color="#c8923a"/><stop offset="1" stop-color="#6e4a1c"/></linearGradient>')
    d.add(f'<polygon points="{P([(128, 82.5), (192, 82.5), (188.8, 93.5), (131.2, 93.5)])}" fill="url(#{gid})" fill-opacity="0.92"/>'
          f'<polygon points="{P([(128, 82.5), (192, 82.5), (188.8, 93.5), (131.2, 93.5)])}" fill="#ffc860" fill-opacity="0.35" filter="url(#{d.glow})"/>'
          f'<polygon points="{P([(134, 83.5), (150, 83.5), (143, 92.5), (136, 92.5)])}" fill="#fff" fill-opacity="0.38"/>'
          f'<line x1="154" y1="83.5" x2="150" y2="92.5" stroke="#fff" stroke-opacity="0.25" stroke-width="1.6"/>')
    # gas-mask snout with a round filter, corrugated hoses down to the collar
    for s_ in (-1, 1):
        pts = mirror([(172, 108), (186, 112), (194, 104), (200, 110)], s_)
        d.tube(pts, 4.4, '#55575e', '#a8aab2')
        for k in range(1, 6):
            t = k / 6
            x = pts[0][0] + (pts[-1][0] - pts[0][0]) * t; y = pts[0][1] + (pts[-1][1] - pts[0][1]) * t + (-4 * t * (1 - t) * 1.2)
            d.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.3" fill="none" stroke="#1c1a19" stroke-width="0.7" stroke-opacity="0.7"/>')
    d.part([F([(146, 96), (174, 96), (180, 106), (174, 116), (146, 116), (140, 106)], (0, 0.05, 1)),
            F([(146, 116), (174, 116), (168, 122), (152, 122)], (0, 0.8, 0.6))])
    d.part([F(circle(160, 108, 7.5), (0, 0, 1), 'dome', 'metal')], grime=False)
    d.add(f'<circle cx="160" cy="108" r="4.6" fill="#1d1b1e"/>')
    for k in range(6):
        ang = k * math.pi / 3
        d.add(f'<line x1="160" y1="108" x2="{160 + 4.4 * math.cos(ang):.2f}" y2="{108 + 4.4 * math.sin(ang):.2f}" stroke="#8a8c94" stroke-width="0.8"/>')
    d.add('</g>')
    # a round pressure gauge on the chest
    d.part([F(circle(136, 136, 6.5), (0, 0, 1), 'dome', 'metal')], grime=False)
    d.add('<circle cx="136" cy="136" r="4.4" fill="#ece6d4" stroke="#1c1a19" stroke-width="0.6"/>'
          '<line x1="136" y1="136" x2="139" y2="133" stroke="#b02a1a" stroke-width="0.9"/><circle cx="136" cy="136" r="0.8" fill="#1c1a19"/>')

    # ---- pauldrons (90% about the shoulder): a concave curved cutout on the inner edge shows more chest plate
    SC = lambda p: [(246 + (x - 246) * 0.6, 122 + (y - 122) * 0.6) for x, y in p]   # smaller, per the sample's ratio
    def arc(a, c, b, k=8):
        return [((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * c[0] + t * t * b[0],
                 (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * c[1] + t * t * b[1]) for t in [i / k for i in range(1, k)]]
    for s in (-1, 1):
        G = lambda p, n, kind='flat', tone='light': Fs(SC(p), n, s, kind, tone)
        lame = [(216, 138), (272, 142), (290, 134), (288, 146), (272, 156), (220, 152)] + arc((220, 152), (229, 146), (216, 138))
        d.part([G(lame, (0.2, 0.35, 0.92)),
                G([(220, 152), (272, 156), (288, 146), (284, 152), (270, 160), (223, 156)], (0.1, 0.85, 0.5))])
        main = [(212, 100), (236, 92), (272, 100), (288, 126), (270, 142), (214, 140)] + arc((214, 140), (234, 120), (212, 100))
        d.part([G(main, (0.2, 0.05, 0.98)),
                G([(217, 94), (236, 84), (274, 94), (272, 100), (236, 92), (212, 100)], (0.15, -0.85, 0.5)),
                G([(272, 100), (274, 94), (294, 126), (288, 126)], (0.85, -0.2, 0.5)),
                G([(288, 126), (294, 126), (290, 136), (270, 142)], (0.7, 0.5, 0.5))])
        d.part([G([(224, 98), (240, 91), (264, 98), (262, 105), (240, 99), (227, 104)], (0.1, -0.5, 0.86))], shadow=True)
        v = mirror(SC([(250, 112), (270, 126)]), s)
        x0, x1 = sorted([v[0][0], v[1][0]])
        d.vent(x0, v[0][1], x1, v[1][1], 5)
        h = mirror(SC([(229, 113), (245, 113), (245, 126), (229, 126)]), s)
        d.recess(h)
        for p in mirror(SC([(231.5, 115.5), (242.5, 115.5), (242.5, 123.5), (231.5, 123.5)]), s):
            d.bolt(*p, 0.8)
        d.stencil(*mirror(SC([(238, 137)]), s)[0], '7A', 3.2)
        lx, ly = mirror(SC([(284, 132)]), s)[0]
        d.light(lx - 2, ly - 1.6, 4, 3.2, '#f2a83a', '#fff0c8')
        d.groove(mirror(SC([(226, 134), (270, 138)]), s))
    return d.svg()

if __name__ == '__main__':
    out = sys.argv[1]
    open(f'{out}/svg/armor_ref2_suit_south.svg', 'w').write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 320" width="320" height="320"><title>Heavy suit from the reference, faceted</title>'
        f'{frame("south", "G_")}{build("R_")}</svg>')
    print('ok')
