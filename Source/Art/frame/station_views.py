"""North and east views of the power armour station (south is station.py). The gantry posts stand at the
station's front corners; the pilot always enters from the open back.
North: rotated 180 - we see the frame's back; posts, hoist and clamps are behind it, the hazard edge is at
the far side of the deck, dock/monitor/cabinet mirrored. East: footprint 2 wide x 3 deep, posts along the
east edge (seen side-on: the near post hides the far one, the beam end-on on top), a hoist arm reaching
over the frame, which faces the posts in profile.
    python3 station_views.py <out dir>"""
import sys
import frame_svg as S
import station as T
from station import (YEL, YEL_HI, YEL_DK, STEEL, STEEL_HI, STEEL_DK, REDC, REDC_HI, REDC_DK, SCREEN, SCREEN_HI,
                     ibeam, hazard_band, chain, lamp, rect, TILE)
from frame4 import K, OL, OLW, poly, flat, plate, tube, ball, _line, seam, rivet, cell

def deck(d, x0, x1, ytop, yfront, ybot, band=None):
    poly(d, [(x0 + 6, ytop), (x1 - 6, ytop), (x1, yfront), (x0, yfront)], STEEL)
    flat(d, [(x0 + 10, ytop + 4), (x1 - 10, ytop + 4), (x1 - 10, ytop + 9), (x0 + 10, ytop + 9)], STEEL_HI)
    for y in range(int(ytop) + 24, int(yfront) - 6, 14):
        for x in range(int(x0) + 24, int(x1) - 18, 18):
            xx = x + (7 if (y // 14) % 2 else 0)
            _line(d, [(xx - 3, y + 2), (xx + 3, y - 2)], 1.6, STEEL_DK)
    poly(d, [(x0, yfront), (x1, yfront), (x1, ybot), (x0, ybot)], STEEL_DK)      # side face: plain steel
    flat(d, [(x0 + 3, yfront + 3), (x1 - 3, yfront + 3), (x1 - 3, yfront + 6), (x0 + 3, yfront + 6)], STEEL)

def dock(d, x0, y0):
    poly(d, [(x0, y0), (x0 + 52, y0), (x0 + 52, y0 + 62), (x0, y0 + 62)], STEEL_DK)
    flat(d, [(x0 + 3, y0 + 3), (x0 + 49, y0 + 3), (x0 + 49, y0 + 7), (x0 + 3, y0 + 7)], STEEL)
    for i, ch in enumerate((1.0, 1.0, 0.35)):
        cell(d, x0 + 5, y0 + 11 + i * 16, 36, 13, ch)
    d.ellipse(((x0 + 44) * K, (y0 + 54) * K, (x0 + 49) * K, (y0 + 59) * K), fill=SCREEN_HI)

def monitor(d, arm, x0, y0):
    tube(d, arm, 5, STEEL_DK, STEEL)
    poly(d, [(x0, y0 + 4), (x0 + 38, y0), (x0 + 40, y0 + 30), (x0 + 2, y0 + 34)], STEEL_DK)
    poly(d, [(x0 + 5, y0 + 8), (x0 + 34, y0 + 5), (x0 + 35, y0 + 25), (x0 + 6, y0 + 28)], SCREEN)
    for k, y in enumerate((y0 + 12, y0 + 17, y0 + 22)):
        _line(d, [(x0 + 9, y), (x0 + 9 + (20 if k != 1 else 12), y - 1)], 1.6, SCREEN_HI)

def cabinet(d, x0, y0, x1, y1):
    poly(d, [(x0, y0), (x1, y0), (x1 + 2, y1), (x0 - 2, y1)], REDC)
    flat(d, [(x0 + 3, y0 + 3), (x1 - 3, y0 + 3), (x1 - 3, y0 + 7), (x0 + 3, y0 + 7)], REDC_HI)
    flat(d, [(x1 - 4, y0 + 7), (x1, y0 + 7), (x1 + 1, y1 - 3), (x1 - 3, y1 - 3)], REDC_DK)
    n = max(2, int((y1 - y0 - 12) // 22))
    for i in range(n):
        y = y0 + 20 + i * (y1 - y0 - 20) / n
        seam(d, [(x0 + 2, y), (x1 - 2, y)], 2)
        mx = (x0 + x1) / 2
        _line(d, [(mx - 11, y + 9), (mx + 11, y + 9)], 3 + 2 * OLW, OL); _line(d, [(mx - 11, y + 9), (mx + 11, y + 9)], 3, STEEL_HI)

def boot_clamps(d, xs, y):
    for cx in xs:
        poly(d, [(cx - 27, y), (cx + 27, y), (cx + 29, y + 20), (cx - 29, y + 20)], YEL)
        flat(d, [(cx - 24, y + 3), (cx + 24, y + 3), (cx + 24, y + 6), (cx - 24, y + 6)], YEL_HI)
        for k in (-18, 18):
            ball(d, cx + k, y + 10, 3.5, STEEL, STEEL_HI)

def hook(d, x, y, s):
    _line(d, [(x, y), (x, y + 10), (x + 6 * s, y + 16)], 4 + 2 * OLW, OL)
    _line(d, [(x, y), (x, y + 10), (x + 6 * s, y + 16)], 4, STEEL)

# ------------------------------------------------------------------ NORTH (3 x 2, same canvas as south)
NW, NH = T.W, T.H
def north_back(d):
    deck(d, 2, 352, 268, 446, 466)
    hazard_band(d, 10, 268, 344, 282)                              # the station's front is the far edge now
    boot_clamps(d, (145, 209), 396)
    ibeam(d, 16, 46, 70, 300); ibeam(d, 308, 338, 70, 300)          # posts at the (far) front corners
    for x in (16, 308):
        poly(d, [(x - 8, 290), (x + 38, 290), (x + 40, 304), (x - 10, 304)], STEEL_DK)
    rect(d, 6, 52, 348, 82, YEL, hi=4)
    flat(d, [(10, 74), (344, 74), (344, 79), (10, 79)], YEL_DK)
    hazard_band(d, 120, 56, 234, 66, 10)
    poly(d, [(140, 80), (214, 80), (210, 98), (144, 98)], STEEL)
    for x in (152, 202):
        ball(d, x, 89, 5, STEEL_DK, STEEL)
    for x in (117, 237):
        chain(d, x, 82, 196)
    lamp(d, 30, 90, 1); lamp(d, 324, 90, -1)
    cabinet(d, 12, 300, 70, 392)                                    # front-right of the station = back-left here
    tube(d, [(56, 82), (50, 160), (44, 240), (40, 300)], 5, (60, 60, 64, 255), (100, 100, 104, 255))
    tube(d, [(64, 82), (60, 150), (64, 220)], 4, (120, 40, 34, 255), (170, 80, 64, 255))
    for s in (-1, 1):                                               # clamp arms, behind the frame
        x0, x1 = 177 + s * 146, 177 + s * 108
        poly(d, [(min(x0, x1), 222), (max(x0, x1), 222), (max(x0, x1), 236), (min(x0, x1), 236)], YEL)
        poly(d, [(x1 - 5, 216), (x1 + 5, 216), (x1 + 5, 242), (x1 - 5, 242)], STEEL_DK)
    dock(d, 296, 196)                                               # the station's left post = right here
    monitor(d, [(308, 176), (290, 176), (284, 162)], 262, 132)

def north_front(d):
    for x, s in ((117, -1), (237, 1)):
        hook(d, x, 190, s)

# ------------------------------------------------------------------ EAST (2 wide x 3 deep)
EW = round(2 * TILE)
DEPTH_PX = 89                                                       # a tile of depth on the deck, as in the south view
EH = 650
E_TOP, E_FRONT, E_BOT = 626 - 3 * DEPTH_PX, 626, 650
EFX, EFY = -60, 500 - 318                                           # the frame's canvas: hatch at x 40, toes at 148, feet at y 500
def clamp_arm(d, y, x_post=190, x_pad=98):
    """a clamp arm from the post to the frame's side, with its pad"""
    poly(d, [(x_pad, y), (x_post, y), (x_post, y + 14), (x_pad, y + 14)], YEL)
    flat(d, [(x_pad + 2, y + 2), (x_post - 2, y + 2), (x_post - 2, y + 5), (x_pad + 2, y + 5)], YEL_HI)
    poly(d, [(x_pad - 5, y - 6), (x_pad + 5, y - 6), (x_pad + 5, y + 20), (x_pad - 5, y + 20)], STEEL_DK)

def east_back(d):
    deck(d, 2, EW - 2, E_TOP, E_FRONT, E_BOT)
    hazard_band(d, EW - 18, E_TOP + 6, EW - 6, E_FRONT - 4, 10)      # front edge (east)
    boot_clamps(d, (102,), 486)
    # the far (north) post is hidden behind the near one; its dock and monitor face inward, beside it
    dock(d, 140, 150)
    monitor(d, [(190, 236), (176, 236), (172, 224)], 134, 220)
    # hoist arm over the frame, chain down to its shoulder
    poly(d, [(84, 112), (190, 112), (190, 130), (84, 130)], YEL)
    flat(d, [(86, 114), (188, 114), (188, 118), (86, 118)], YEL_HI)
    poly(d, [(84, 126), (120, 126), (116, 142), (88, 142)], STEEL)
    ball(d, 102, 134, 5, STEEL_DK, STEEL)
    chain(d, 102, 140, 286)
    tube(d, [(196, 262), (194, 330), (198, 420)], 5, (60, 60, 64, 255), (100, 100, 104, 255))
    clamp_arm(d, 298)                                               # the far arm, behind the frame (higher: further away)

def east_front(d):
    hook(d, 102, 280, 1)
    clamp_arm(d, 312)                                               # the near arm, across the frame's side
    cabinet(d, 128, 540, 182, 622)                                  # front-right of the station = south-east corner
    tube(d, [(198, 420), (196, 500), (186, 548)], 5, (60, 60, 64, 255), (100, 100, 104, 255))
    # the near (south) post, full height, the beam end-on on top of it with its lamp
    ibeam(d, 190, 218, 34, 620)
    poly(d, [(182, 608), (226, 608), (228, 622), (180, 622)], STEEL_DK)
    rivet(d, 186, 616); rivet(d, 222, 616)
    rect(d, 178, 4, 230, 40, YEL, hi=4)
    flat(d, [(182, 32), (226, 32), (226, 37), (182, 37)], YEL_DK)
    hazard_band(d, 184, 12, 224, 22, 8)
    lamp(d, 204, 48, -1)

def doc(els, w, h, title, bg=None):
    b = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w * 2}" height="{h * 2}">'
            f'<title>{title}</title>{b}{"".join(els)}</svg>')

if __name__ == '__main__':
    out = sys.argv[1]
    def build(back, front, frame_facing, fx, fy, w, h, name):
        d = S.SvgDraw([], [0]); back(d); front(d)
        open(f'{out}/svg/station_{name}.svg', 'w').write(doc(d.out, w, h, 'Power armour station'))
        p = S.SvgDraw([], [100000]); back(p)
        fr = ''.join(S.view(frame_facing, 0.0)).replace('id="c', 'id="f').replace('#c', '#f')
        p.out.append(f'<g transform="translate({fx},{fy})">{fr}</g>')
        front(p)
        open(f'{out}/svg/station_{name}_with_frame.svg', 'w').write(doc(p.out, w, h, 'Power armour station', '#605c62'))
    build(north_back, north_front, 'north', T.FX, T.FY, NW, NH, 'north')
    build(east_back, east_front, 'east', EFX, EFY, EW, EH, 'east')
    print(EW, EH)
