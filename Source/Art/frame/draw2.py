"""A human-shaped power-armour frame (original design), RimWorld-like style, ~2x a pawn's size.
The pawn is the game's own naked body and head (reference art from the owner's game art; never shipped)."""
import math, sys
from PIL import Image, ImageDraw, ImageFont

C = 320; K = 4; W = C * K
OL = (30, 27, 26, 255); OLW = 3.2                    # outline colour / width (canvas px)
MET = (132, 136, 142, 255); HI = (178, 182, 188, 255); DK = (84, 88, 95, 255); DDK = (58, 61, 67, 255)
JNT = (74, 78, 86, 255); JHI = (118, 122, 130, 255)
YEL = (226, 172, 56, 255); YDK = (172, 122, 32, 255)
CELL = (66, 122, 170, 255); CELLHI = (108, 164, 208, 255); GREEN = (112, 222, 112, 255); AMBER = (240, 172, 52, 255)
GA = SP_GAME = None

def bez(p0, p1, p2, p3=None, n=24):
    pts = []
    for i in range(n + 1):
        t = i / n
        if p3 is None:
            x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]; y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
        else:
            x = (1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t * t * p2[0] + t ** 3 * p3[0]
            y = (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t * t * p2[1] + t ** 3 * p3[1]
        pts.append((x, y))
    return pts

def _line(d, pts, w, fill):
    q = [(x * K, y * K) for x, y in pts]
    d.line(q, fill=fill, width=max(1, int(w * K)), joint='curve')
    r = w * K / 2
    for x, y in (q[0], q[-1]):
        d.ellipse((x - r, y - r, x + r, y + r), fill=fill)

def tube(d, pts, w, fill=MET, hi=HI, taper=None):
    """a round metal tube along pts: outline, body, a lit stripe along its upper-left side"""
    if taper:                                  # draw as segments of changing width
        n = len(pts) - 1
        for pass_, col, extra in ((0, OL, 2 * OLW), (1, fill, 0)):
            for i in range(n):
                ww = w + (taper - w) * (i / n)
                _line(d, pts[i:i + 2], ww + extra, col)
        for i in range(n):
            ww = w + (taper - w) * (i / n)
            a, b = pts[i], pts[i + 1]
            _line(d, [(a[0] - ww * 0.18, a[1] - ww * 0.18), (b[0] - ww * 0.18, b[1] - ww * 0.18)], ww * 0.28, hi)
        return
    _line(d, pts, w + 2 * OLW, OL); _line(d, pts, w, fill)
    _line(d, [(x - w * 0.18, y - w * 0.18) for x, y in pts], w * 0.28, hi)

def ball(d, cx, cy, r, fill=JNT, hi=JHI, bolt=True):
    d.ellipse(((cx - r - OLW) * K, (cy - r - OLW) * K, (cx + r + OLW) * K, (cy + r + OLW) * K), fill=OL)
    d.ellipse(((cx - r) * K, (cy - r) * K, (cx + r) * K, (cy + r) * K), fill=fill)
    d.ellipse(((cx - r * 0.7) * K, (cy - r * 0.75) * K, (cx + r * 0.2) * K, (cy + r * 0.1) * K), fill=hi)
    if bolt:
        d.ellipse(((cx - r * 0.28) * K, (cy - r * 0.28) * K, (cx + r * 0.28) * K, (cy + r * 0.28) * K), fill=OL)

def blob(d, pts, fill, hi=None, hi_pts=None):
    q = [(x * K, y * K) for x, y in pts]
    d.polygon(q, fill=OL)
    # inset by drawing the outline ring thick over the edge
    d.polygon(q, fill=fill, outline=OL, width=int(OLW * K))
    if hi_pts:
        d.polygon([(x * K, y * K) for x, y in hi_pts], fill=hi)

def gauntlet(d, cx, cy, s, facing):
    """a chunky mitten hand: rounded block, knuckle ridge, thumb"""
    if facing == 'east':
        blob(d, [(cx - 9, cy - 8), (cx + 9, cy - 9), (cx + 13, cy), (cx + 10, cy + 13), (cx - 6, cy + 14), (cx - 11, cy + 4)], MET, HI,
             [(cx - 6, cy - 5), (cx + 6, cy - 6), (cx + 8, cy - 2), (cx - 6, cy - 1)])
    else:
        blob(d, [(cx - 11, cy - 8), (cx + 11, cy - 8), (cx + 13, cy + 6), (cx + 8, cy + 15), (cx - 8, cy + 15), (cx - 13, cy + 6)], MET, HI,
             [(cx - 8, cy - 5), (cx + 4, cy - 5), (cx + 2, cy), (cx - 8, cy)])
        d.line(((cx - 8) * K, (cy + 7) * K, (cx + 8) * K, (cy + 7) * K), fill=OL, width=int(2 * K))
        tx = cx - s * 12
        blob(d, [(tx - 4, cy - 2), (tx + 3, cy - 3), (tx + 4, cy + 8), (tx - 3, cy + 9)], DK)

def boot(d, cx, y, facing, s=1):
    if facing == 'east':
        blob(d, [(cx - 14, y - 16), (cx + 6, y - 16), (cx + 10, y - 9), (cx + 24, y - 6), (cx + 26, y + 2), (cx - 14, y + 2)], DK, MET,
             [(cx - 11, y - 13), (cx + 4, y - 13), (cx + 6, y - 9), (cx - 11, y - 9)])
    else:
        blob(d, [(cx - 15, y - 16), (cx + 15, y - 16), (cx + 18, y - 4), (cx + 17, y + 2), (cx - 17, y + 2), (cx - 18, y - 4)], DK, MET,
             [(cx - 12, y - 13), (cx + 12, y - 13), (cx + 14, y - 8), (cx - 13, y - 8)])

def cell(d, x, y, w, h, charge, out=0):
    y -= out
    d.rounded_rectangle((x * K, y * K, (x + w) * K, (y + h) * K), radius=4 * K, fill=OL)
    d.rounded_rectangle(((x + 1.5) * K, (y + 1.5) * K, (x + w - 1.5) * K, (y + h - 1.5) * K), radius=3 * K, fill=CELL)
    d.rectangle(((x + 3) * K, (y + 4) * K, (x + 5) * K, (y + h - 4) * K), fill=CELLHI)
    d.rounded_rectangle(((x + w * 0.3) * K, (y - 4) * K, (x + w * 0.7) * K, (y + 1) * K), radius=K, fill=OL)
    d.rectangle(((x + 2) * K, (y + h * 0.22) * K, (x + w - 2) * K, (y + h * 0.22 + 2) * K), fill=YEL)
    wy, wh = y + h * 0.42, h * 0.42
    d.rectangle(((x + w * 0.32) * K, wy * K, (x + w * 0.68) * K, (wy + wh) * K), fill=OL)
    d.rectangle(((x + w * 0.32 + 1) * K, (wy + wh * (1 - charge) + 1) * K, (x + w * 0.68 - 1) * K, (wy + wh - 1) * K), fill=GREEN if charge > 0.5 else AMBER)

# ---------------------------------------------------------------------------- views
# key heights (canvas px): the pawn's head 85-125, body 131-221
SH_Y, ELB_Y, HAND_Y, WAIST_Y, HIP_Y, KNEE_Y, FOOT_Y = 128, 188, 236, 214, 232, 268, 306

def south(d, part):
    if part == 'back':
        # the back half of the torso cage, seen through the open front
        for s in (-1, 1):
            tube(d, bez((160, 126), (160 + s * 66, 130), (160 + s * 56, 200), (160 + s * 40, WAIST_Y)), 6, DK, MET)
        tube(d, [(160, 122), (160, WAIST_Y + 4)], 9, DK, MET)                                   # spine behind
        return
    # legs: hip ball, tapered thigh, knee, tapered shin, boot
    for s in (-1, 1):
        hx = 160 + s * 32
        tube(d, bez((hx, HIP_Y), (hx + s * 9, 248), (hx + s * 8, KNEE_Y)), 13, taper=10)
        tube(d, bez((hx + s * 8, KNEE_Y), (hx + s * 11, 286), (hx + s * 5, FOOT_Y - 14)), 11, taper=8)
        ball(d, hx + s * 8, KNEE_Y, 8)
        boot(d, hx + s * 5, FOOT_Y, 'south')
    # pelvis girdle: a curved belt under the pawn, hip balls
    tube(d, bez((112, 222), (130, 240), (190, 240), (208, 222)), 11)
    d.rounded_rectangle(((152) * K, 228 * K, 168 * K, 238 * K), radius=2 * K, fill=YEL)
    for s in (-1, 1):
        ball(d, 160 + s * 32, HIP_Y, 10)
    # front torso cage: two side ribs bowing out round the chest and in at the waist, two chest bands
    for s in (-1, 1):
        tube(d, bez((160 + s * 30, 128), (160 + s * 80, 140), (160 + s * 66, 196), (160 + s * 46, WAIST_Y + 6)), 8)
    tube(d, bez((106, 162), (132, 172), (188, 172), (214, 162)), 6)
    tube(d, bez((112, 192), (136, 200), (184, 200), (208, 192)), 6)
    d.rounded_rectangle((152 * K, 160 * K, 168 * K, 204 * K), radius=4 * K, fill=OL)
    d.rounded_rectangle((153.5 * K, 161.5 * K, 166.5 * K, 202.5 * K), radius=3 * K, fill=YEL)
    for y in (172, 190):
        d.line((156 * K, y * K, 164 * K, y * K), fill=YDK, width=2 * K)
    # shoulder yoke: a curved collar sweeping out to the shoulders
    tube(d, bez((84, SH_Y + 6), (110, 116), (210, 116), (236, SH_Y + 6)), 11)
    d.arc((130 * K, 112 * K, 190 * K, 140 * K), 200, 340, fill=OL, width=int(7 * K))
    d.arc((131 * K, 113 * K, 189 * K, 139 * K), 205, 335, fill=HI, width=int(2.5 * K))
    # arms: shoulder ball, upper arm, elbow, forearm, gauntlet
    for s in (-1, 1):
        sx = 160 + s * 78
        tube(d, bez((sx, SH_Y), (sx + s * 10, 158), (sx + s * 8, ELB_Y)), 12, taper=10)
        tube(d, bez((sx + s * 8, ELB_Y), (sx + s * 9, 210), (sx + s * 5, HAND_Y - 10)), 10, taper=8)
        ball(d, sx + s * 8, ELB_Y, 8)
        gauntlet(d, sx + s * 5, HAND_Y, s, 'south')
        ball(d, sx, SH_Y, 15)

def east(d, part):
    if part == 'back':
        # far arm and far leg, in shadow
        tube(d, bez((170, SH_Y), (176, 160), (178, ELB_Y)), 10, DK, MET); ball(d, 178, ELB_Y, 7, DDK, JNT)
        tube(d, bez((178, ELB_Y), (184, 214), (190, HAND_Y - 8)), 8, DK, MET)
        gauntlet(d, 192, HAND_Y, 1, 'east')
        tube(d, bez((166, HIP_Y), (172, 250), (170, KNEE_Y)), 11, DK, MET); ball(d, 170, KNEE_Y, 7, DDK, JNT)
        tube(d, bez((170, KNEE_Y), (164, 288), (162, FOOT_Y - 14)), 9, DK, MET)
        boot(d, 166, FOOT_Y - 2, 'east')
        return
    # spine: an S-curve down the back, with the cell bay on it
    tube(d, bez((134, 120), (112, 150), (120, 196), (130, WAIST_Y + 10)), 11)
    blob(d, [(98, 158), (118, 154), (122, 206), (102, 210)], DK, MET, [(101, 161), (115, 158), (116, 172), (102, 175)])
    for y in (168, 186):
        d.rounded_rectangle((100 * K, y * K, 108 * K, (y + 14) * K), radius=K, fill=CELL)
    # ribs from the spine round the chest, bowing forward
    for y0, depth in ((140, 44), (168, 46), (196, 38)):
        tube(d, bez((124, y0 - 4), (150, y0 - 18), (160 + depth, y0 - 6), (160 + depth - 6, y0 + 14)), 6)
    # pelvis and near leg
    tube(d, bez((128, WAIST_Y + 8), (140, 236), (172, 236), (184, 226)), 11)
    ball(d, 156, HIP_Y, 10)
    tube(d, bez((156, HIP_Y), (166, 248), (162, KNEE_Y)), 13, taper=10)
    tube(d, bez((162, KNEE_Y), (154, 288), (152, FOOT_Y - 14)), 11, taper=8)
    ball(d, 162, KNEE_Y, 8)
    boot(d, 154, FOOT_Y, 'east')
    # shoulder, near arm swinging slightly forward
    tube(d, bez((130, SH_Y - 4), (150, 118), (176, 124)), 10)
    tube(d, bez((160, SH_Y), (170, 160), (170, ELB_Y)), 12, taper=10)
    tube(d, bez((170, ELB_Y), (178, 212), (184, HAND_Y - 10)), 10, taper=8)
    ball(d, 170, ELB_Y, 8)
    gauntlet(d, 186, HAND_Y, 1, 'east')
    ball(d, 160, SH_Y, 15)

def north(d, part):
    if part == 'back':
        return
    # legs and boots from behind, rear step bar between them
    for s in (-1, 1):
        hx = 160 + s * 32
        tube(d, bez((hx, HIP_Y), (hx + s * 9, 248), (hx + s * 8, KNEE_Y)), 13, taper=10)
        tube(d, bez((hx + s * 8, KNEE_Y), (hx + s * 11, 286), (hx + s * 5, FOOT_Y - 14)), 11, taper=8)
        ball(d, hx + s * 8, KNEE_Y, 8)
        boot(d, hx + s * 5, FOOT_Y, 'north')
    tube(d, [(140, 292), (180, 292)], 6, YEL, (246, 208, 112, 255))
    tube(d, bez((112, 222), (130, 240), (190, 240), (208, 222)), 11)
    for s in (-1, 1):
        ball(d, 160 + s * 32, HIP_Y, 10)
    # REAR ENTRY: the back cage is split down the spine; each half swings open on hinges at the
    # side ribs, like a pair of doors seen edge-on
    for s in (-1, 1):
        tube(d, bez((160 + s * 30, 128), (160 + s * 80, 140), (160 + s * 66, 196), (160 + s * 46, WAIST_Y + 6)), 8)
        for hy in (152, 196):
            hx = 160 + s * (74 if hy < 170 else 60)
            d.rounded_rectangle(((hx - 5) * K, hy * K, (hx + 5) * K, (hy + 11) * K), radius=2 * K, fill=OL)
            d.rounded_rectangle(((hx - 3.5) * K, (hy + 1.5) * K, (hx + 3.5) * K, (hy + 9.5) * K), radius=K, fill=YEL)
        # the swung-open half: its own curved ribs, foreshortened, out past the side
        ox = 160 + s * 74
        tube(d, bez((ox, 146), (ox + s * 22, 140), (ox + s * 32, 160), (ox + s * 30, 176)), 6, DK, MET)
        tube(d, bez((160 + s * 60, 204), (160 + s * 80, 200), (160 + s * 90, 210), (160 + s * 86, 222)), 6, DK, MET)
        tube(d, bez((ox + s * 30, 176), (ox + s * 34, 190), (160 + s * 90, 200), (160 + s * 86, 222)), 6, DK, MET)
    # spine with the power-cell bay: two battery cells drop in from the top
    tube(d, [(160, 120), (160, WAIST_Y + 6)], 10)
    blob(d, [(132, 168), (188, 168), (190, 224), (130, 224)], DK, MET, [(135, 171), (185, 171), (184, 177), (136, 177)])
    for x in (136, 162):
        d.rounded_rectangle((x * K, 178 * K, (x + 22) * K, 220 * K), radius=3 * K, fill=(38, 40, 44, 255))
    cell(d, 138, 180, 18, 38, 0.9)
    cell(d, 164, 180, 18, 38, 0.3, out=24)
    d.rounded_rectangle((140 * K, 220 * K, 180 * K, 226 * K), radius=K, fill=YEL)
    # yoke and arms from behind
    tube(d, bez((84, SH_Y + 6), (110, 116), (210, 116), (236, SH_Y + 6)), 11)
    for s in (-1, 1):
        sx = 160 + s * 78
        tube(d, bez((sx, SH_Y), (sx + s * 10, 158), (sx + s * 8, ELB_Y)), 12, taper=10)
        tube(d, bez((sx + s * 8, ELB_Y), (sx + s * 9, 210), (sx + s * 5, HAND_Y - 10)), 10, taper=8)
        ball(d, sx + s * 8, ELB_Y, 8)
        gauntlet(d, sx + s * 5, HAND_Y, -s, 'south')
        ball(d, sx, SH_Y, 15)

VIEWS = {'south': south, 'east': east, 'north': north}

def pawn(art, facing, skin=(0.98, 0.80, 0.66)):
    """the game's naked male body + average head, tinted like the game does, at the mod's scale"""
    import numpy as np
    S = round(1.5 * C / 2.717)                     # a pawn texture's size on our canvas (1.5 tiles)
    out = Image.new('RGBA', (C, C))
    b = Image.open(f'{art}/Bodies/Naked_Male_{facing}.png').convert('RGBA')
    h = Image.open(f'{art}/Heads/Male/Male_Average_Normal_{facing}.png').convert('RGBA')
    for im, dy in ((b, 0), (h, -round(0.34 * C / 2.717))):
        a = np.array(im).astype(float); a[..., :3] *= np.array(skin); im = Image.fromarray(a.astype('uint8'))
        im = im.resize((S, S), Image.LANCZOS)
        out.alpha_composite(im, ((C - S) // 2, (C - S) // 2 + dy))
    return out

def render(art, facing, frame=True, with_pawn=True):
    out = Image.new('RGBA', (C, C))
    if frame:
        im = Image.new('RGBA', (W, W)); VIEWS[facing](ImageDraw.Draw(im), 'back'); out.alpha_composite(im.resize((C, C), Image.LANCZOS))
    if with_pawn:
        out.alpha_composite(pawn(art, facing))
    if frame:
        im = Image.new('RGBA', (W, W)); VIEWS[facing](ImageDraw.Draw(im), 'front'); out.alpha_composite(im.resize((C, C), Image.LANCZOS))
    return out

if __name__ == '__main__':
    out, art = sys.argv[1], sys.argv[2]
    rows = [('frame', True, False), ('frame + pawn', True, True), ('pawn (game art)', False, True)]
    Z = 2
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 22)
    except Exception:
        font = ImageFont.load_default()
    sheet = Image.new('RGB', (190 + 3 * C * Z, 50 + len(rows) * C * Z), (236, 230, 220)); sd = ImageDraw.Draw(sheet)
    for i, f in enumerate(('south', 'east', 'north')):
        sd.text((190 + i * C * Z + 20, 14), f, fill=(20, 20, 20), font=font)
    for j, (lab, fr, pw) in enumerate(rows):
        sd.text((10, 50 + j * C * Z + C * Z // 2 - 10), lab, fill=(20, 20, 20), font=font)
        for i, f in enumerate(('south', 'east', 'north')):
            im = render(art, f, fr, pw)
            im.save(f'{out}/v2_{lab.split()[0]}{"_pawn" if pw and fr else ""}_{f}.png')
            bg = Image.new('RGBA', (C, C), (200, 190, 172, 255)); bg.alpha_composite(im)
            sheet.paste(bg.resize((C * Z, C * Z), Image.LANCZOS), (190 + i * C * Z, 50 + j * C * Z))
    sheet.save(f'{out}/frame_sheet_v2.png')
