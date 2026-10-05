"""Power-armour frame v4: a solid, bulky frame (original design, inspired by heavy open-back power
armour frames) in a RimWorld-like style. Bone-coloured armour shells over dark metal, rust-red
cable bundles at the waist, brass details. It opens from behind: the back hood (with its twin
tanks and valve wheel) swings up over the head, and the calf plates fold down to the ground as steps.

    python3 frame4.py <out dir> <vanilla Pawn/Humanlike dir>
"""
import math, sys
from PIL import Image, ImageDraw, ImageFont
from draw3 import (C, K, W, RAISE, OL, OLW, BONE, BONE_HI, BONE_SH, MET, MET_HI, MET_DK, RUST, RUST_HI,
                   BRASS, BRASS_DK, HOLE, YEL, X, bez, poly, flat, plate, tube, ball, coil, cell, cables, _line, pawn)

def seam(d, pts, w=1.6):
    _line(d, pts, w, OL)

def rivet(d, x, y, r=1.6):
    d.ellipse(((x - r) * K, (y - r) * K, (x + r) * K, (y + r) * K), fill=OL)

def mirror(pts):                       # right-half outline (top to bottom) -> whole symmetric outline
    return pts + [(320 - x, y) for x, y in reversed(pts)]

def fist(d, cx, cy, s):
    """a big mechanical gauntlet seen from the front (s = side, for the thumb)"""
    poly(d, [(cx - 14, cy - 10), (cx + 14, cy - 10), (cx + 16, cy + 6), (cx + 12, cy + 20), (cx - 12, cy + 20), (cx - 16, cy + 6)], MET)
    flat(d, [(cx - 11, cy - 7), (cx + 9, cy - 7), (cx + 8, cy - 1), (cx - 11, cy - 1)], MET_HI)
    plate(d, [(cx - 13, cy - 12), (cx + 13, cy - 12), (cx + 12, cy - 3), (cx - 12, cy - 3)])      # knuckle guard
    for fx in (-7, -1, 5):
        seam(d, [(cx + fx, cy + 5), (cx + fx, cy + 18)], 1.8)
    poly(d, [(cx - s * 15, cy - 1), (cx - s * 22, cy + 3), (cx - s * 21, cy + 12), (cx - s * 14, cy + 11)], MET_DK)

def tank(d, x, y0, y1, w=13):
    """a vertical tank: dark body, bone end caps"""
    d.rounded_rectangle(((x - w / 2 - OLW) * K, (y0 - OLW) * K, (x + w / 2 + OLW) * K, (y1 + OLW) * K), radius=(w / 2 + OLW) * K, fill=OL)
    d.rounded_rectangle(((x - w / 2) * K, y0 * K, (x + w / 2) * K, y1 * K), radius=w / 2 * K, fill=MET)
    d.rectangle(((x - w / 2 + 2) * K, (y0 + 4) * K, (x - w / 2 + 4.5) * K, (y1 - 4) * K), fill=MET_HI)
    for yy in (y0 + 5, y1 - 7):
        d.rectangle(((x - w / 2) * K, yy * K, (x + w / 2) * K, (yy + 2) * K), fill=OL)
    d.rounded_rectangle(((x - w / 2) * K, y0 * K, (x + w / 2) * K, (y0 + 5) * K), radius=2 * K, fill=BONE)

def aux_tank(d, x0, x1, y, h=13):
    """a horizontal tank across the seat; its left end cap is the auxiliary cell port"""
    d.rounded_rectangle(((x0 - OLW) * K, (y - h / 2 - OLW) * K, (x1 + OLW) * K, (y + h / 2 + OLW) * K), radius=(h / 2 + OLW) * K, fill=OL)
    d.rounded_rectangle((x0 * K, (y - h / 2) * K, x1 * K, (y + h / 2) * K), radius=h / 2 * K, fill=MET)
    d.rectangle(((x0 + 5) * K, (y - h / 2 + 2) * K, (x1 - 5) * K, (y - h / 2 + 4) * K), fill=MET_HI)
    for xx in (x0 + 12, x1 - 12):
        d.rectangle((xx * K, (y - h / 2) * K, (xx + 2) * K, (y + h / 2) * K), fill=OL)
    d.rounded_rectangle((x0 * K, (y - h / 2) * K, (x0 + 9) * K, (y + h / 2) * K), radius=3 * K, fill=BONE)   # port cap
    aux_port(d, x0 + 4.5, y, 4)

def aux_port(d, cx, cy, r):
    """the auxiliary cell port: a yellow ring round the end of a seated cell"""
    d.ellipse(((cx - r - 1.5) * K, (cy - r - 1.5) * K, (cx + r + 1.5) * K, (cy + r + 1.5) * K), fill=OL)
    d.ellipse(((cx - r) * K, (cy - r) * K, (cx + r) * K, (cy + r) * K), fill=YEL)
    d.ellipse(((cx - r * 0.55) * K, (cy - r * 0.55) * K, (cx + r * 0.55) * K, (cy + r * 0.55) * K), fill=(66, 122, 170, 255))

def wheel(d, cx, cy, r=9):
    """a valve wheel: rim, hub, four spokes"""
    for a in range(4):
        t = a * math.pi / 2 + 0.4
        _line(d, [(cx, cy), (cx + r * math.cos(t), cy + r * math.sin(t))], 2.4 + 2 * OLW, OL)
        _line(d, [(cx, cy), (cx + r * math.cos(t), cy + r * math.sin(t))], 2.4, BRASS)
    d.ellipse(((cx - r - OLW) * K, (cy - r - OLW) * K, (cx + r + OLW) * K, (cy + r + OLW) * K), outline=OL, width=int((3 + 2 * OLW) * K))
    d.ellipse(((cx - r) * K, (cy - r) * K, (cx + r) * K, (cy + r) * K), outline=BRASS, width=int(3 * K))
    ball(d, cx, cy, 3, BRASS_DK, BRASS, bolt=False)

def boot(d, cx, top=294, toe=True):
    poly(d, [(cx - 19, top), (cx + 19, top), (cx + 23, top + 14), (cx + 23, 318), (cx - 23, 318), (cx - 23, top + 14)], MET)
    flat(d, [(cx - 17, top + 3), (cx + 15, top + 3), (cx + 16, top + 7), (cx - 18, top + 7)], MET_HI)
    if toe:
        plate(d, [(cx - 20, top + 12), (cx + 20, top + 12), (cx + 22, 316), (cx - 22, 316)], hi=[(cx - 17, top + 14), (cx + 17, top + 14), (cx + 18, top + 17), (cx - 18, top + 17)])
    seam(d, [(cx - 22, 317), (cx + 22, 317)], 2.4)

def heel_ring(d, cx, cy, r=10):
    d.ellipse(((cx - r - OLW) * K, (cy - r - OLW) * K, (cx + r + OLW) * K, (cy + r + OLW) * K), fill=OL)
    d.ellipse(((cx - r) * K, (cy - r) * K, (cx + r) * K, (cy + r) * K), fill=MET)
    d.ellipse(((cx - r * 0.55) * K, (cy - r * 0.55) * K, (cx + r * 0.55) * K, (cy + r * 0.55) * K), fill=OL)
    d.ellipse(((cx - r * 0.35) * K, (cy - r * 0.35) * K, (cx + r * 0.35) * K, (cy + r * 0.35) * K), fill=MET_DK)
    d.arc(((cx - r + 1.5) * K, (cy - r + 1.5) * K, (cx + r - 1.5) * K, (cy + r - 1.5) * K), 180, 290, fill=MET_HI, width=int(2 * K))

# ---------------------------------------------------------------- shared pieces (s = side, -1 left / +1 right)
def thigh(d, s, windows=True):
    plate(d, X([(174, 226), (206, 226), (213, 246), (208, 270), (180, 272), (172, 248)], s),
          holes=[X([(186, 240), (200, 240), (196, 258), (188, 258)], s)] if windows else [],
          hi=X([(177, 229), (204, 229), (206, 233), (176, 233)], s), sh=X([(206, 252), (211, 247), (207, 268), (203, 268)], s))
    if windows:
        _line(d, X([(193, 243), (192, 255)], s), 3, RUST)

def knee(d, s):
    hx = 160 + s * 32
    ball(d, hx, 274, 9)
    plate(d, [(hx - 11, 266), (hx + 11, 266), (hx + 9, 282), (hx - 9, 282)], hi=[(hx - 8, 268), (hx + 8, 268), (hx + 8, 271), (hx - 8, 271)])
    seam(d, [(hx - 5, 274), (hx + 5, 274)])

def shin_front(d, s):
    plate(d, X([(176, 280), (208, 280), (210, 296), (178, 298)], s), hi=X([(179, 283), (205, 283), (206, 286), (179, 286)], s))
    seam(d, X([(184, 290), (202, 289)], s))

def pauldron(d, s, back=False):
    pts = X([(204, 110), (234, 102), (258, 112), (264, 136), (250, 152), (218, 148), (206, 130)], s)
    plate(d, pts, hi=X([(208, 112), (234, 105), (252, 112), (232, 112)], s), sh=X([(250, 148), (260, 136), (262, 140), (252, 150)], s))
    for i in range(3):                                                               # ribbing
        seam(d, X([(222 + i * 9, 122 + i * 2), (226 + i * 9, 140 + i)], s), 2)
    rivet(d, 160 + s * 214, 118); rivet(d, 160 + s * 250, 124)

def arm(d, s, back=False):
    sx = 160 + s * 80
    tube(d, [(sx, 146), (sx + s * 4, 188)], 18)                                       # upper arm
    plate(d, X([(232, 152), (250, 150), (252, 182), (236, 184)], s), hi=X([(235, 154), (248, 153), (249, 157), (235, 158)], s))
    ball(d, sx + s * 5, 194, 10)                                                      # elbow
    plate(d, X([(226, 196), (258, 194), (264, 216), (256, 236), (234, 238), (226, 216)], s),
          holes=[] if back else [X([(236, 204), (252, 203), (248, 220), (238, 220)], s)],
          hi=X([(229, 198), (256, 197), (257, 201), (229, 202)], s), sh=X([(256, 232), (262, 216), (264, 218), (258, 236)], s))
    if not back:
        _line(d, X([(244, 207), (243, 217)], s), 3, RUST)
    else:
        seam(d, X([(232, 214), (258, 213)], s))
    fist(d, sx + s * 6, 250, s if not back else -s)

def tanks(d, top=80):
    """the twin tanks on the frame's shoulders, flanking the head"""
    for s in (-1, 1):
        tank(d, 160 + s * 34, top, top + 50)

def pipe_wheel(d, top=80):
    """the pipe loop and valve wheel on the back hood"""
    tube(d, bez((126, top + 40), (126, top + 60), (194, top + 60), (194, top + 40)), 4, MET_DK, MET)   # pipe loop
    wheel(d, 160, top + 56, 9)

# ---------------------------------------------------------------- SOUTH
def south(d, part):
    if part == 'back':
        d.ellipse((128 * K, 100 * K, 192 * K, 124 * K), fill=OL)             # the neck opening and the collar's far half
        d.ellipse((130 * K, 102 * K, 190 * K, 122 * K), fill=BONE)
        d.ellipse((134 * K, 106 * K, 186 * K, 120 * K), fill=MET_DK)
        return
    for s in (-1, 1):
        thigh(d, s); knee(d, s); shin_front(d, s); boot(d, 160 + s * 32)
    # pelvis: belt, hip plates, codpiece
    tube(d, bez((110, 222), (130, 234), (190, 234), (210, 222)), 12)
    for s in (-1, 1):
        plate(d, X([(194, 214), (216, 216), (220, 236), (200, 240)], s), hi=X([(197, 217), (214, 218), (215, 221), (197, 221)], s))
    plate(d, [(146, 222), (174, 222), (178, 236), (166, 248), (154, 248), (142, 236)], hi=[(149, 225), (171, 225), (172, 229), (148, 229)])
    # waist: bellows core and rust cable bundles, side rib plates
    for s in (-1, 1):
        cables(d, [bez((160 + s * 20, 184), (160 + s * 32, 196), (160 + s * 30, 210), (160 + s * 22, 224)),
                   bez((160 + s * 28, 184), (160 + s * 40, 198), (160 + s * 38, 212), (160 + s * 30, 224))], 6)
        plate(d, X([(202, 182), (216, 184), (212, 214), (200, 214)], s))
    for i, y in enumerate((186, 194, 202, 210)):
        d.rounded_rectangle((145 * K, y * K, 175 * K, (y + 9) * K), radius=3 * K, fill=OL)
        d.rounded_rectangle((146.5 * K, (y + 1.5) * K, 173.5 * K, (y + 7.5) * K), radius=2 * K, fill=MET if i % 2 else MET_HI)
    # chest shell, two halves around a dark core with a status lamp
    poly(d, [(150, 116), (170, 116), (172, 186), (148, 186)], MET)
    flat(d, [(152, 119), (156, 119), (156, 183), (152, 183)], MET_HI)
    for s in (-1, 1):
        plate(d, X([(166, 112), (198, 110), (218, 122), (222, 150), (214, 176), (194, 190), (170, 188), (166, 150)], s),
              holes=[X([(186, 160), (206, 156), (204, 172), (190, 178)], s)],
              hi=X([(169, 115), (198, 113), (212, 121), (172, 121)], s), sh=X([(196, 186), (212, 174), (216, 178), (198, 190)], s))
        seam(d, X([(172, 140), (214, 134)], s))
        _line(d, X([(196, 163), (198, 172)], s), 3, RUST)
    ball(d, 160, 150, 5, (120, 210, 230, 255), (200, 245, 255, 255), bolt=False)
    # collar: the near half of the ring, over the chin (the far half is behind the head)
    d.arc((128 * K, 100 * K, 192 * K, 124 * K), 0, 180, fill=OL, width=int(10 * K))
    d.arc((130 * K, 102 * K, 190 * K, 122 * K), 0, 180, fill=BONE, width=int(5 * K))
    for s in (-1, 1):
        arm(d, s); pauldron(d, s)

def south_hood(d, th):
    """from the front the shut hood hides behind the chest; swung past upright it rises above the
    shoulders, its outside (panels, pipe, wheel) now facing us"""
    if math.cos(th) >= -0.05:
        return
    f = lambda p: proj(HINGE_HOOD, th, p, -0.08)
    plate(d, f(HOOD), hi=f([(182, 107), (204, 113), (206, 116), (184, 110)]))
    for y in (140, 172):
        seam(d, f([(108, y), (212, y)]))
    tube(d, f([(138, 126), (138, 138), (182, 138), (182, 126)]), 4, MET_DK, MET)
    (cx, cy), = f([(160, 144)]); wheel(d, cx, cy, 9 * min(1, -math.cos(th) + 0.3))

# ---------------------------------------------------------------- EAST (facing right)
E_HINGE = (134, 100)
E_HOOD = [(142, 102), (134, 92), (122, 90), (110, 104), (104, 124), (100, 160), (104, 192), (118, 204), (138, 200)]
E_CAVITY = [(142, 104), (130, 96), (118, 102), (112, 128), (110, 160), (114, 188), (124, 198), (140, 196)]

def east_hood(d, a):
    """the back hood in profile, swung up and back about its hinge by a (0 = shut)"""
    hx, hy = E_HINGE; ca, sa = math.cos(a), math.sin(a)
    R = lambda pts: [(hx + (x - hx) * ca - (y - hy) * sa, hy + (x - hx) * sa + (y - hy) * ca) for x, y in pts]
    plate(d, R(E_HOOD), hi=R([(132, 94), (122, 93), (112, 106), (116, 108), (124, 97), (132, 97)]),
          sh=R([(104, 188), (118, 200), (126, 202), (110, 192)]))
    seam(d, R([(108, 150), (134, 150)])); seam(d, R([(106, 176), (134, 176)]))
    poly(d, R([(102, 156), (107, 156), (107, 160), (102, 160)]), OL)
    (wx, wy), = R([(110, 134)]); wheel(d, wx, wy, 6)
    ball(d, hx, hy, 4, MET, MET_HI, bolt=False)

def east(d, part):
    if part == 'back':                                       # far arm and far leg, in shadow
        poly(d, E_CAVITY, MET_DK)                            # the inside of the back, shown while the hood is open
        tube(d, [(170, 146), (176, 190)], 16, MET_DK, MET); tube(d, [(176, 196), (190, 230)], 14, MET_DK, MET)
        poly(d, [(184, 236), (204, 236), (206, 256), (186, 258)], MET_DK)
        tube(d, [(166, 236), (172, 276)], 16, MET_DK, MET); tube(d, [(172, 280), (168, 300)], 14, MET_DK, MET)
        poly(d, [(150, 298), (190, 298), (206, 310), (206, 318), (146, 318)], MET_DK)
        return
    # chest in profile
    plate(d, [(134, 108), (172, 106), (198, 118), (210, 144), (206, 174), (190, 190), (150, 194), (134, 190)],
          holes=[[(178, 156), (198, 150), (198, 168), (182, 176)]],
          hi=[(138, 111), (172, 109), (190, 116), (140, 116)], sh=[(150, 190), (188, 186), (190, 190), (152, 192)])
    seam(d, [(140, 140), (204, 136)])
    _line(d, [(188, 158), (190, 168)], 3, RUST)
    cables(d, [bez((150, 192), (168, 202), (174, 214), (166, 226)), bez((140, 194), (150, 208), (154, 218), (148, 228))], 6)
    for y in (196, 204, 212):
        d.rounded_rectangle((164 * K, y * K, 190 * K, (y + 9) * K), radius=3 * K, fill=OL)
        d.rounded_rectangle((165.5 * K, (y + 1.5) * K, 188.5 * K, (y + 7.5) * K), radius=2 * K, fill=MET_HI)
    tube(d, bez((122, 222), (140, 234), (178, 234), (194, 224)), 12)
    d.ellipse((120 * K, 200 * K, 142 * K, 222 * K), fill=OL)                      # the auxiliary tank, end-on
    d.ellipse((122.5 * K, 202.5 * K, 139.5 * K, 219.5 * K), fill=BONE)
    aux_port(d, 131, 211, 4.5)
    plate(d, [(150, 214), (178, 216), (182, 236), (154, 240)], hi=[(153, 217), (176, 218), (177, 221), (153, 221)])
    # near leg: thigh, knee, shin with its calf plate behind, boot with the heel ring
    plate(d, [(144, 230), (176, 230), (184, 250), (178, 272), (150, 274), (142, 250)],
          holes=[[(156, 242), (170, 242), (168, 258), (158, 258)]], hi=[(147, 233), (174, 233), (176, 237), (146, 237)])
    _line(d, [(163, 245), (163, 255)], 3, RUST)
    ball(d, 166, 276, 9)
    plate(d, [(172, 266), (186, 268), (184, 284), (170, 284)])                         # knee cap
    plate(d, [(150, 280), (178, 280), (180, 298), (152, 300)], hi=[(153, 283), (175, 283), (176, 286), (153, 286)])
    plate(d, [(138, 278), (152, 278), (154, 300), (140, 300)], sh=[(138, 292), (152, 292), (153, 300), (140, 300)])   # calf plate
    poly(d, [(142, 296), (182, 296), (204, 306), (208, 312), (208, 318), (140, 318)], MET)
    plate(d, [(178, 300), (200, 306), (206, 312), (180, 314)])
    seam(d, [(140, 317), (208, 317)], 2.4)
    heel_ring(d, 138, 306, 10)
    # near arm: pauldron, upper arm, elbow, forearm, gauntlet
    tube(d, [(158, 146), (164, 188)], 18)
    ball(d, 166, 194, 10)
    plate(d, [(158, 198), (184, 194), (196, 222), (186, 240), (166, 236)],
          holes=[[(168, 206), (182, 203), (184, 220), (172, 224)]], hi=[(161, 200), (182, 197), (184, 201), (162, 203)])
    _line(d, [(176, 208), (178, 218)], 3, RUST)
    poly(d, [(176, 238), (198, 236), (204, 252), (196, 262), (178, 260)], MET)
    flat(d, [(179, 240), (196, 238), (197, 243), (180, 245)], MET_HI)
    plate(d, [(134, 112), (164, 104), (186, 114), (190, 138), (176, 152), (144, 150), (136, 134)],
          hi=[(138, 115), (164, 107), (180, 113), (160, 114)], sh=[(176, 148), (188, 138), (190, 142), (178, 152)])
    for i in range(3):
        seam(d, [(150 + i * 10, 122), (152 + i * 10, 142)], 2)

# ---------------------------------------------------------------- NORTH: fixed parts and the opening doors
HINGE_HOOD, HINGE_CALF = 104, 300
NECK = (160, 106, 27, 8)                                                   # the neck hole: centre and radii
HOOD = mirror([(160, 98), (176, 99), (186, 102), (196, 97), (206, 100), (210, 110), (218, 128), (216, 160), (206, 186), (188, 200), (160, 202)])
CAVITY = mirror([(160, 94), (184, 94), (200, 102), (206, 116), (212, 132), (210, 160), (200, 184), (184, 196), (160, 198)])
CALF = [(-15, 276), (15, 276), (16, 299), (-16, 299)]                      # relative to the leg's x

def proj(hinge, th, pts, grow=0.12, cx=160):
    """a door hinged on a horizontal line at y=hinge, swung by th (0 = shut, pi = folded flat toward us):
    heights foreshorten by cos(th) and it grows a little as it swings toward us"""
    c, sn = math.cos(th), math.sin(th)
    return [(cx + (x - cx) * (1 + grow * sn), hinge + (y - hinge) * c) for x, y in pts]

def hood(d, th):
    c = math.cos(th); f = lambda p: proj(HINGE_HOOD, th, p)
    if abs(c) < 0.1:
        xs = [x for x, _ in f(HOOD)]
        tube(d, [(min(xs) + 4, HINGE_HOOD), (max(xs) - 4, HINGE_HOOD)], 9, BONE, BONE)
    elif c > 0:                                                          # outside: armour shell, panels
        plate(d, f(HOOD), hi=f([(188, 91), (204, 99), (206, 103), (190, 95)]),
              sh=f([(206, 182), (214, 160), (216, 164), (208, 186)]))
        for y in (150, 176):
            seam(d, f([(108, y), (212, y)]))
        for x, y in ((122, 128), (198, 128), (124, 186), (196, 186)):
            rivet(d, *f([(x, y)])[0])
        tube(d, f([(146, 188), (174, 188)]), 4, MET_DK, MET)            # grab handle
    else:                                                                # inside: padded lining, straps
        poly(d, f(HOOD), BONE_SH)
        poly(d, f(CAVITY), MET_DK)
        for y in (136, 168):
            tube(d, f([(126, y), (194, y)]), 6, RUST, RUST_HI)
    if abs(c) >= 0.1:                                                    # the neck hole, rimmed
        cx, cy, rx, ry = NECK
        ring = [(cx + rx * math.cos(a * math.pi / 16), cy + ry * math.sin(a * math.pi / 16)) for a in range(32)]
        d.polygon([(x * K, y * K) for x, y in f(ring)], fill=(0, 0, 0, 0))
        near = ring[:17]                                                 # the half nearer to us, over the chin
        _line(d, f(near), 5 + 2 * OLW, OL)
        _line(d, f(near), 3.5, BONE_SH if c > 0 else MET)
    for s in (-1, 1):
        hx = 160 + s * 42
        d.rounded_rectangle(((hx - 7) * K, (HINGE_HOOD - 4) * K, (hx + 7) * K, (HINGE_HOOD + 4) * K), radius=2 * K, fill=OL)
        d.rounded_rectangle(((hx - 5.5) * K, (HINGE_HOOD - 2.5) * K, (hx + 5.5) * K, (HINGE_HOOD + 2.5) * K), radius=K, fill=YEL)

def hood_wheel(d, th):
    """the pipe and wheel ride on the hood's outside, swinging with it"""
    if math.cos(th) > 0.1:
        f = lambda p: proj(HINGE_HOOD, th, p)
        c = math.cos(th)
        tube(d, f([(138, 126), (138, 138), (182, 138), (182, 126)]), 4, MET_DK, MET)
        (cx, cy), = f([(160, 144)])
        wheel(d, cx, cy, 9 * max(c, 0.3))

def calves(d, th):
    c = math.cos(th)
    for s in (-1, 1):
        cx = 160 + s * 32
        pts = [(cx + x, y) for x, y in CALF]
        f = lambda p: proj(HINGE_CALF, th, p, 0.1, cx)
        if abs(c) < 0.1:
            tube(d, [(cx - 14, HINGE_CALF), (cx + 14, HINGE_CALF)], 6, BONE, BONE)
        elif c > 0:
            plate(d, f(pts), hi=f([(cx - 12, 279), (cx + 12, 279), (cx + 12, 282), (cx - 12, 282)]))
            seam(d, f([(cx - 10, 290), (cx + 10, 290)]))
        else:                                                            # its inside: the step
            poly(d, f(pts), BONE_SH)
            for y in (281, 287, 293):
                tube(d, f([(cx - 10, y), (cx + 10, y)]), 2.2, MET, MET_HI)

def north_far(d):
    for s in (-1, 1):
        cx = 160 + s * 32
        thigh(d, s, windows=False)
        seam(d, X([(180, 248), (208, 246)], s))
        ball(d, cx, 274, 9)
        tube(d, [(cx, 278), (cx, 298)], 16, MET_DK, MET)                # shin, behind the calf plate
        boot(d, cx, toe=False)
        heel_ring(d, cx, 306, 10)
    # the torso's open back: dark padded cavity
    poly(d, CAVITY, MET_DK)
    for y in (140, 172):
        tube(d, [(128, y), (192, y)], 5, RUST, RUST_HI)

def north_near(d):
    # torso side walls and the rim of the opening
    for s in (-1, 1):
        plate(d, X([(206, 106), (226, 116), (230, 150), (222, 186), (204, 204), (210, 176), (216, 146), (214, 118)], s),
              sh=X([(214, 182), (226, 160), (228, 166), (216, 190)], s))
    # lumbar plate with the cell slot, belt, hip plates
    tube(d, bez((110, 222), (130, 234), (190, 234), (210, 222)), 12)
    plate(d, [(128, 196), (192, 196), (196, 222), (124, 222)], hi=[(131, 199), (189, 199), (190, 202), (130, 202)])
    aux_tank(d, 132, 188, 209, 15)                                      # the auxiliary tank, across the small of the back
    for s in (-1, 1):
        plate(d, X([(194, 214), (216, 216), (220, 236), (200, 240)], s))
    for s in (-1, 1):
        arm(d, s, back=True); pauldron(d, s, back=True)

def pawn_parts(art, facing, skin=(0.98, 0.80, 0.66)):
    """the vanilla pawn as (body, head) layers at the mod's scale"""
    import numpy as np
    S = round(1.5 * C / 2.717)
    parts = []
    for path, dy in ((f'{art}/Bodies/Naked_Male_{facing}.png', 0), (f'{art}/Heads/Male/Male_Average_Normal_{facing}.png', -round(0.34 * C / 2.717))):
        im = Image.open(path).convert('RGBA')
        a = np.array(im).astype(float); a[..., :3] *= np.array(skin); im = Image.fromarray(a.astype('uint8')).resize((S, S), Image.LANCZOS)
        out = Image.new('RGBA', (C, C)); out.alpha_composite(im, ((C - S) // 2, (C - S) // 2 + dy)); parts.append(out)
    return parts

def layer(fn, h=C):
    im = Image.new('RGBA', (W, h * K)); fn(ImageDraw.Draw(im)); return im.resize((C, h), Image.LANCZOS)

def north_frame(art, th_hood, th_calf, pilot=None, h=C):
    """compose the north view. pilot: None, ('out', dy) behind the frame, or ('in', dy) inside it.
    The hood is drawn in front of the pilot (head included: it shows through the neck hole) until it
    has swung up past ~100 degrees; beyond that it leans back behind them."""
    img = Image.new('RGBA', (C, h))
    front = th_hood < 0.56 * math.pi
    hood_l = layer(lambda d: (hood(d, th_hood), hood_wheel(d, th_hood)), h)
    if not front:
        img.alpha_composite(hood_l)
    img.alpha_composite(layer(north_far, h))
    body, head = pawn_parts(art, 'north') if pilot else (None, None)
    if pilot and pilot[0] == 'in':
        img.alpha_composite(body, (0, pilot[1]))
    img.alpha_composite(layer(north_near, h))
    if pilot and pilot[0] == 'in':
        img.alpha_composite(head, (0, pilot[1]))
    if front:
        img.alpha_composite(hood_l)
    if pilot and pilot[0] == 'out':
        img.alpha_composite(body, (0, pilot[1])); img.alpha_composite(head, (0, pilot[1]))
    return img

def view(art, facing, with_pawn):
    if facing.startswith('north'):
        o = 'open' in facing
        return north_frame(art, 0.75 * math.pi if o else 0, 0, ('in', -RAISE) if with_pawn else None)
    fn = {'south': south, 'east': east}[facing]
    img = Image.new('RGBA', (C, C))
    img.alpha_composite(layer(lambda d: fn(d, 'back')))
    if with_pawn:
        img.alpha_composite(pawn(art, facing), (0, -RAISE))
    img.alpha_composite(layer(lambda d: fn(d, 'front')))
    if facing == 'east':
        img.alpha_composite(layer(lambda d: east_hood(d, 0)))
    return img

def ease(t):
    t = min(1, max(0, t)); return t * t * (3 - 2 * t)

def animate(out, art):
    H = C + 110
    HO, CO = 0.9 * math.pi, 0
    STAND = 40
    seq = []
    for i in range(8): seq.append((0, 0, None))
    for i in range(20): seq.append((ease(i / 19) * HO, ease((i - 4) / 15) * CO, None))
    for i in range(24):
        t = i / 23; seq.append((HO, CO, ('out', round(110 + (STAND - 110) * t - 3 * abs(math.sin(t * math.pi * 3))))))
    for i in range(14):
        t = ease(i / 13); dy = round(STAND + (-RAISE - STAND) * t - 10 * math.sin(t * math.pi))
        seq.append((HO, CO, ('in' if dy <= -RAISE * 0.5 else 'out', dy)))
    for i in range(20): seq.append(((1 - ease(i / 19)) * HO, (1 - ease((i - 4) / 15)) * CO, ('in', -RAISE)))
    for i in range(14): seq.append((0, 0, ('in', -RAISE)))
    frames = []
    for th, tc, p in seq:
        bg = Image.new('RGBA', (C, H), (96, 92, 98, 255))
        bg.alpha_composite(north_frame(art, th, tc, p, H))
        frames.append(bg.convert('RGB').resize((C * 2, H * 2), Image.LANCZOS))
    frames[0].save(f'{out}/frame4b_climb_in.gif', save_all=True, append_images=frames[1:], duration=70, loop=0)

def pilot_path(facing, phase, t):
    """(state, dx, dy) of the pilot: walking up to the frame's back, then stepping up into it.
    north: from below (toward us); south: from above (behind the frame); east: from the left"""
    lift = -10 * math.sin(t * math.pi)
    if facing == 'north':
        return ('out', 0, round(110 + (40 - 110) * t)) if phase == 'walk' else \
               ('in' if t > 0.55 else 'out', 0, round(40 + (-RAISE - 40) * t + lift))
    if facing == 'south':
        return ('out', 0, round(-150 + (-70 + 150) * t)) if phase == 'walk' else \
               ('in' if t > 0.55 else 'out', 0, round(-70 + (-RAISE + 70) * t + lift))
    return ('out', round(-150 + (-60 + 150) * t), 0) if phase == 'walk' else \
           ('in' if t > 0.55 else 'out', round(-60 * (1 - t)), round(-RAISE * t + lift))

def view_frame(art, facing, th, pilot, h, top, left=0):
    """one facing at hood angle th, on a canvas of height h with the frame drawn at (left, top)"""
    w = C + left
    img = Image.new('RGBA', (w, h))
    def put(im, dx=0, dy=0):
        img.alpha_composite(im, (left + dx, top + dy))
    body, head = pawn_parts(art, facing) if pilot else (None, None)
    st, px, py = pilot if pilot else (None, 0, 0)
    if facing == 'north':
        fr = north_frame(art, th, 0, (st, py) if pilot else None, h - top)
        put(fr); return img
    if facing == 'south':
        put(layer(lambda d: south_hood(d, th)))                     # the raised hood stands behind the pilot
        if st == 'out':                                               # behind the frame: its tanks are nearer
            put(body, px, py); put(head, px, py)
        put(layer(lambda d: south(d, 'back')))
        if st == 'in':
            put(body, px, py); put(head, px, py)
        put(layer(lambda d: south(d, 'front')))
        return img
    # east
    hood_l = layer(lambda d: east_hood(d, th))
    put(layer(lambda d: east(d, 'back')))
    if st == 'out':
        put(hood_l); put(body, px, py); put(head, px, py)
    else:                                                              # inside: the hood's collar wraps behind the head
        if st == 'in':
            put(body, px, py); put(head, px, py)
        put(hood_l)
    put(layer(lambda d: east(d, 'front')))
    return img

def animate_all(out, art):
    HO = 0.75 * math.pi
    seq = []
    for i in range(8): seq.append((0, None, 0))
    for i in range(20): seq.append((ease(i / 19) * HO, None, 0))
    for i in range(24): seq.append((HO, 'walk', i / 23))
    for i in range(14): seq.append((HO, 'step', ease(i / 13)))
    for i in range(20): seq.append(((1 - ease(i / 19)) * HO, 'in', 1))
    for i in range(14): seq.append((0, 'in', 1))
    TOP, H, LEFT = 100, C + 200, 140
    frames = []
    for th, phase, t in seq:
        row = Image.new('RGBA', (3 * C + LEFT, H), (96, 92, 98, 255))
        x = 0
        for f in ('south', 'east', 'north'):
            p = None if phase is None else (('in', 0, -RAISE) if phase == 'in' else pilot_path(f, phase, t))
            lft = LEFT if f == 'east' else 0
            row.alpha_composite(view_frame(art, f, th, p, H, TOP, lft), (x, 0))
            x += C + lft
        frames.append(row.convert('RGB'))
    frames[0].save(f'{out}/frame4f_climb_in_3views.gif', save_all=True, append_images=frames[1:], duration=70, loop=0)
    keys = [0, 22, 34, 46, 54, 60, 70, len(frames) - 1]
    sh = Image.new('RGB', (frames[0].width // 2, H // 2 * len(keys)))
    for j, k in enumerate(keys):
        sh.paste(frames[k].resize((frames[0].width // 2, H // 2)), (0, j * H // 2))
    sh.save(f'{out}/frame4f_keys.png')

def sheet(out, art):
    cols = ('south', 'east', 'north', 'north_open')
    rows = (('frame', False), ('frame + pawn', True))
    Z = 2
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 22)
    sh = Image.new('RGB', (190 + len(cols) * C * Z, 50 + len(rows) * C * Z), (236, 230, 220)); sd = ImageDraw.Draw(sh)
    for i, f in enumerate(cols):
        sd.text((190 + i * C * Z + 20, 14), f, fill=(20, 20, 20), font=font)
    for j, (lab, pw) in enumerate(rows):
        sd.text((10, 50 + j * C * Z + C * Z // 2 - 10), lab, fill=(20, 20, 20), font=font)
        for i, f in enumerate(cols):
            im = view(art, f, pw)
            im.save(f'{out}/v4f_{f}{"_pawn" if pw else ""}.png')
            bg = Image.new('RGBA', (C, C), (96, 92, 98, 255)); bg.alpha_composite(im)
            sh.paste(bg.resize((C * Z, C * Z), Image.LANCZOS), (190 + i * C * Z, 50 + j * C * Z))
    sh.save(f'{out}/frame_sheet_v4f.png')

if __name__ == '__main__':
    sheet(sys.argv[1], sys.argv[2])
    if '--anim' in sys.argv:
        animate_all(sys.argv[1], sys.argv[2])
