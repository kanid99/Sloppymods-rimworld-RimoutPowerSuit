"""Power armour station (original design, inspired by power-armour workstations): a yellow industrial
gantry over a steel deck, chain hoist, work lamps, cell charging dock, monitor and tool cabinet.
Footprint 3x2 tiles, drawn at the suit's scale (117.8 px per tile), south view, as SVG first.
    python3 station.py <out dir>"""
import math, sys
import frame_svg as S
from frame4 import (K, OL, OLW, BONE, MET, MET_HI, MET_DK, RUST, RUST_HI, BRASS, X,
                    poly, flat, plate, tube, ball, _line, seam, rivet, cell)

TILE = 320 / 2.717
W, H = round(3 * TILE), round(4 * TILE)          # 3 tiles wide; the gantry rises above the 2-tile-deep footprint
YEL, YEL_HI, YEL_DK = (214, 168, 52, 255), (242, 206, 112, 255), (158, 116, 30, 255)
STEEL, STEEL_HI, STEEL_DK = (112, 116, 122, 255), (152, 156, 162, 255), (72, 74, 80, 255)
HAZ = (34, 30, 28, 255)
REDC, REDC_HI, REDC_DK = (156, 54, 42, 255), (196, 92, 70, 255), (108, 34, 28, 255)
SCREEN, SCREEN_HI = (40, 86, 56, 255), (130, 230, 140, 255)
LAMP = (255, 236, 170, 255)
FX, FY = 177 - 160, 410 - 318                      # where the frame's canvas sits (its feet on the deck)

def rect(d, x0, y0, x1, y1, fill, hi=None, sh=None):
    poly(d, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], fill)
    if hi: flat(d, [(x0 + 3, y0 + 3), (x1 - 3, y0 + 3), (x1 - 3, y0 + 3 + hi), (x0 + 3, y0 + 3 + hi)], YEL_HI if fill == YEL else STEEL_HI)
    if sh: flat(d, [(x1 - 3 - sh, y0 + 3), (x1 - 3, y0 + 3), (x1 - 3, y1 - 3), (x1 - 3 - sh, y1 - 3)], YEL_DK if fill == YEL else STEEL_DK)

def ibeam(d, x0, x1, y0, y1):
    """an upright I-beam post: flanges and a recessed web, rivets down it"""
    rect(d, x0, y0, x1, y1, YEL)
    m = (x0 + x1) / 2
    flat(d, [(m - 5, y0 + 6), (m + 5, y0 + 6), (m + 5, y1 - 6), (m - 5, y1 - 6)], YEL_DK)
    flat(d, [(x0 + 3, y0 + 3), (x0 + 6, y0 + 3), (x0 + 6, y1 - 3), (x0 + 3, y1 - 3)], YEL_HI)
    for y in range(int(y0) + 14, int(y1) - 8, 26):
        rivet(d, x0 + 4.5, y, 1.4); rivet(d, x1 - 4.5, y, 1.4)

def hazard_band(d, x0, y0, x1, y1, step=14):
    """yellow and black chevrons, clipped to the band"""
    g = d.group()
    flat(g, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], YEL)
    h = y1 - y0
    x = x0 - h
    while x < x1 + h:
        flat(g, [(x, y1), (x + step / 2, y1), (x + step / 2 + h, y0), (x + h, y0)], HAZ)
        x += step
    cid = d._id()
    d.out.append(f'<clipPath id="{cid}"><rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}"/></clipPath>')
    d.place(g, f'clip-path="url(#{cid})"')
    _line(d, [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)], OLW * 2, OL)

def chain(d, x, y0, y1):
    y = y0
    while y < y1 - 4:
        d.ellipse(((x - 3) * K, y * K, (x + 3) * K, (y + 8) * K), outline=OL, width=int(2.4 * K))
        y += 6

def lamp(d, x, y, s):
    """a work lamp hung from the beam end, angled in, with its light pool"""
    _line(d, [(x, y - 8), (x, y)], 3 + 2 * OLW, OL); _line(d, [(x, y - 8), (x, y)], 3, STEEL)
    pts = [(x - 9, y), (x + 9, y), (x + 12 * s + 4, y + 14), (x + 12 * s - 8 * s - 12, y + 14)]
    poly(d, [(x - 10, y), (x + 10, y), (x + 13, y + 13), (x - 13, y + 13)], STEEL_DK)
    flat(d, [(x - 10, y + 10), (x + 10, y + 10), (x + 11, y + 12), (x - 11, y + 12)], LAMP)

def back(d):
    # the deck: top surface and front face, 3/4 view
    poly(d, [(8, 268), (346, 268), (352, 446), (2, 446)], STEEL)
    flat(d, [(12, 272), (342, 272), (342, 277), (12, 277)], STEEL_HI)
    for y in range(292, 440, 14):                                  # tread plate
        for x in range(26, 336, 18):
            xx = x + (7 if (y // 14) % 2 else 0)
            _line(d, [(xx - 3, y + 2), (xx + 3, y - 2)], 1.6, STEEL_DK)
    hazard_band(d, 2, 446, 352, 466)
    poly(d, [(2, 466), (352, 466), (352, 470), (2, 470)], STEEL_DK)
    # boot clamps where the frame's feet lock in
    for s in (-1, 1):
        cx = 177 + s * 32
        poly(d, [(cx - 27, 396), (cx + 27, 396), (cx + 29, 416), (cx - 29, 416)], YEL)
        flat(d, [(cx - 24, 399), (cx + 24, 399), (cx + 24, 402), (cx - 24, 402)], YEL_HI)
        for k in (-18, 18):
            ball(d, cx + k, 406, 3.5, STEEL, STEEL_HI)
    # posts and the crossbeam, with the hoist trolley
    ibeam(d, 16, 46, 70, 440); ibeam(d, 308, 338, 70, 440)
    for x in (16, 308):                                            # post feet
        poly(d, [(x - 8, 428), (x + 38, 428), (x + 40, 442), (x - 10, 442)], STEEL_DK)
        rivet(d, x - 2, 436); rivet(d, x + 32, 436)
    rect(d, 6, 52, 348, 82, YEL, hi=4)
    flat(d, [(10, 74), (344, 74), (344, 79), (10, 79)], YEL_DK)
    hazard_band(d, 120, 56, 234, 66, 10)                           # the beam's warning band
    poly(d, [(140, 80), (214, 80), (210, 98), (144, 98)], STEEL)     # hoist trolley
    for x in (152, 202):
        ball(d, x, 89, 5, STEEL_DK, STEEL)
    for x in (117, 237):                                           # chains down to the frame's shoulders
        chain(d, x, 82, 196)
    # cables from the beam down the right post
    tube(d, [(300, 82), (296, 120), (300, 160), (298, 240)], 5, (60, 60, 64, 255), (100, 100, 104, 255))
    tube(d, [(290, 82), (284, 130), (290, 200)], 4, (120, 40, 34, 255), (170, 80, 64, 255))

def front(d):
    # hooks on the chains, gripping the shoulders
    for x in (117, 237):
        _line(d, [(x, 190), (x, 200), (x + (6 if x > 177 else -6), 206)], 4 + 2 * OLW, OL)
        _line(d, [(x, 190), (x, 200), (x + (6 if x > 177 else -6), 206)], 4, STEEL)
    # clamp arms from the posts to the frame's sides
    for s in (-1, 1):
        x0 = 177 + s * 146
        x1 = 177 + s * 108
        poly(d, [(min(x0, x1), 222), (max(x0, x1), 222), (max(x0, x1), 236), (min(x0, x1), 236)], YEL)
        flat(d, [(min(x0, x1) + 2, 224), (max(x0, x1) - 2, 224), (max(x0, x1) - 2, 227), (min(x0, x1) + 2, 227)], YEL_HI)
        poly(d, [(x1 - 5, 216), (x1 + 5, 216), (x1 + 5, 242), (x1 - 5, 242)], STEEL_DK)   # clamp pad
    # work lamps on the beam ends
    lamp(d, 30, 90, 1); lamp(d, 324, 90, -1)
    # the cell charging dock on the left post: three cells, two charged
    poly(d, [(6, 252), (58, 252), (58, 314), (6, 314)], STEEL_DK)
    flat(d, [(9, 255), (55, 255), (55, 259), (9, 259)], STEEL)
    for i, ch in enumerate((1.0, 1.0, 0.35)):
        cell(d, 11, 263 + i * 16, 36, 13, ch)
    d.ellipse((50 * K, 306 * K, 55 * K, 311 * K), fill=SCREEN_HI)          # status light
    # monitor on an arm off the left post
    tube(d, [(46, 190), (64, 190), (70, 176)], 5, STEEL_DK, STEEL)
    poly(d, [(54, 150), (92, 146), (94, 176), (56, 180)], STEEL_DK)
    poly(d, [(59, 154), (88, 151), (89, 171), (60, 174)], SCREEN)
    for k, y in enumerate((158, 163, 168)):
        _line(d, [(63, y), (63 + (20 if k != 1 else 12), y - 1)], 1.6, SCREEN_HI)
    # tool cabinet at the front right of the deck
    poly(d, [(282, 330), (344, 330), (346, 438), (280, 438)], REDC)
    flat(d, [(285, 333), (341, 333), (341, 337), (285, 337)], REDC_HI)
    flat(d, [(338, 337), (342, 337), (343, 435), (339, 435)], REDC_DK)
    for y in (350, 372, 394, 416):
        seam(d, [(284, y), (342, y)], 2)
        _line(d, [(302, y + 9), (324, y + 9)], 3 + 2 * OLW, OL); _line(d, [(302, y + 9), (324, y + 9)], 3, STEEL_HI)
    poly(d, [(288, 318), (338, 318), (340, 330), (286, 330)], STEEL)          # a wrench and parts on top
    _line(d, [(294, 322), (318, 324)], 3 + 2 * OLW, OL); _line(d, [(294, 322), (318, 324)], 3, STEEL_HI)
    tube(d, [(298, 240), (300, 300), (312, 318)], 5, (60, 60, 64, 255), (100, 100, 104, 255))

def doc(els, bg=None):
    b = f'<rect width="{W}" height="{H}" fill="{bg}"/>' if bg else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W * 2}" height="{H * 2}">'
            f'<title>Power armour station</title>{b}{"".join(els)}</svg>')

if __name__ == '__main__':
    out = sys.argv[1]
    d = S.SvgDraw([], [0]); back(d); front(d)
    open(f'{out}/svg/station_south.svg', 'w').write(doc(d.out))
    p = S.SvgDraw([], [100000]); back(p)
    fr = ''.join(S.view('south', 0.0)).replace('id="c', 'id="f').replace('#c', '#f')
    p.out.append(f'<g transform="translate({FX},{FY})">{fr}</g>')
    front(p)
    open(f'{out}/svg/station_south_with_frame.svg', 'w').write(doc(p.out, '#605c62'))
    print(W, H)
