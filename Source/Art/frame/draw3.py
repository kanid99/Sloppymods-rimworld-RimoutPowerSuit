"""Power-armour frame v3 (original design inspired by open-lattice exoskeleton frames), RimWorld-like style:
bone-coloured lattice plates over a dark metal skeleton, rust-red cable bundles, brass joint coils."""
import math, sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, sys.argv[3] if len(sys.argv) > 3 else '.')
from draw2 import bez, pawn

C = 320; K = 4
RAISE = 26          # px the pilot sits higher than a bare pawn, so the head clears the collar
W = C * K
OL = (32, 28, 26, 255); OLW = 3.0
BONE = (222, 213, 194, 255); BONE_HI = (242, 236, 222, 255); BONE_SH = (184, 172, 150, 255)
MET = (78, 81, 88, 255); MET_HI = (122, 126, 134, 255); MET_DK = (52, 54, 60, 255)
RUST = (148, 62, 44, 255); RUST_HI = (190, 100, 72, 255); RUST_DK = (106, 40, 30, 255)
BRASS = (176, 144, 70, 255); BRASS_DK = (122, 96, 40, 255)
HOLE = (46, 44, 46, 255)
CELL = (66, 122, 170, 255); CELLHI = (108, 164, 208, 255); GREEN = (112, 222, 112, 255); AMBER = (240, 172, 52, 255); YEL = (226, 172, 56, 255)

def X(p, s):            # mirror helper: s=-1 left, +1 right, points given for the right side
    return [(160 + s * (x - 160), y) for x, y in p]

def poly(d, pts, fill):
    d.polygon([(x * K, y * K) for x, y in pts], fill=fill, outline=OL, width=int(OLW * K))

def flat(d, pts, fill):
    d.polygon([(x * K, y * K) for x, y in pts], fill=fill)

def _line(d, pts, w, fill):
    q = [(x * K, y * K) for x, y in pts]
    d.line(q, fill=fill, width=max(1, int(w * K)), joint='curve')
    r = w * K / 2
    for x, y in (q[0], q[-1]):
        d.ellipse((x - r, y - r, x + r, y + r), fill=fill)

def tube(d, pts, w, fill=MET, hi=MET_HI):
    _line(d, pts, w + 2 * OLW, OL); _line(d, pts, w, fill)
    _line(d, [(x - w * 0.2, y - w * 0.2) for x, y in pts], max(1, w * 0.25), hi)

def ball(d, cx, cy, r, fill=MET, hi=MET_HI, bolt=True):
    d.ellipse(((cx - r - OLW) * K, (cy - r - OLW) * K, (cx + r + OLW) * K, (cy + r + OLW) * K), fill=OL)
    d.ellipse(((cx - r) * K, (cy - r) * K, (cx + r) * K, (cy + r) * K), fill=fill)
    d.ellipse(((cx - r * 0.72) * K, (cy - r * 0.78) * K, (cx + r * 0.15) * K, (cy + r * 0.05) * K), fill=hi)
    if bolt:
        d.ellipse(((cx - r * 0.25) * K, (cy - r * 0.25) * K, (cx + r * 0.25) * K, (cy + r * 0.25) * K), fill=OL)

def coil(d, a, b, w, n=4):
    """a brass spring coil around a joint, from point a to b"""
    tube(d, [a, b], w * 0.7, MET_DK, MET)
    for i in range(n):
        t = (i + 0.5) / n
        x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy); nx, ny = -dy / L * w / 2, dx / L * w / 2
        _line(d, [(x - nx, y - ny), (x + nx, y + ny)], 3.2 + 2 * OLW, OL)
        _line(d, [(x - nx, y - ny), (x + nx, y + ny)], 3.2, BRASS)

def plate(d, pts, holes=(), hi=None, sh=None):
    """a bone-coloured lattice plate: body, lit and shaded faces, cut-out holes"""
    poly(d, pts, BONE)
    if hi:
        flat(d, hi, BONE_HI)
    if sh:
        flat(d, sh, BONE_SH)
    for h in holes:
        poly(d, h, HOLE)

def cables(d, pts_list, w=5):
    for pts in pts_list:
        tube(d, pts, w, RUST, RUST_HI)

def boot_front(d, cx, y):
    poly(d, [(cx - 17, y - 18), (cx + 17, y - 18), (cx + 20, y - 4), (cx + 19, y + 3), (cx - 19, y + 3), (cx - 20, y - 4)], MET)
    plate(d, [(cx - 13, y - 14), (cx + 13, y - 14), (cx + 15, y - 5), (cx - 15, y - 5)], hi=[(cx - 10, y - 12), (cx + 10, y - 12), (cx + 11, y - 9), (cx - 11, y - 9)])
    d.line(((cx - 17) * K, (y + 1) * K, (cx + 17) * K, (y + 1) * K), fill=MET_DK, width=2 * K)

def knee_pad(d, cx, cy, w=12):
    plate(d, [(cx - w, cy - w + 2), (cx + w, cy - w + 2), (cx + w, cy + w - 2), (cx - w, cy + w - 2)],
          hi=[(cx - w + 3, cy - w + 5), (cx + w - 3, cy - w + 5), (cx + w - 3, cy - w + 8), (cx - w + 3, cy - w + 8)])
    _line(d, [(cx - w + 4, cy - w + 6), (cx + w - 4, cy + w - 6)], 3.5, OL)
    _line(d, [(cx + w - 4, cy - w + 6), (cx - w + 4, cy + w - 6)], 3.5, OL)

def gauntlet(d, cx, cy, s):
    poly(d, [(cx - 11, cy - 9), (cx + 11, cy - 9), (cx + 13, cy + 5), (cx + 9, cy + 16), (cx - 9, cy + 16), (cx - 13, cy + 5)], MET)
    flat(d, [(cx - 8, cy - 6), (cx + 6, cy - 6), (cx + 5, cy - 1), (cx - 8, cy - 1)], MET_HI)
    for fx in (-6, -1, 4):                                                   # finger joints
        _line(d, [(cx + fx, cy + 4), (cx + fx, cy + 14)], 1.6, OL)
    poly(d, [(cx - s * 12, cy - 2), (cx - s * 18, cy + 1), (cx - s * 17, cy + 9), (cx - s * 11, cy + 8)], MET_DK)   # thumb

def cell(d, x, y, w, h, charge):
    d.rounded_rectangle((x * K, y * K, (x + w) * K, (y + h) * K), radius=4 * K, fill=OL)
    d.rounded_rectangle(((x + 1.5) * K, (y + 1.5) * K, (x + w - 1.5) * K, (y + h - 1.5) * K), radius=3 * K, fill=CELL)
    d.rectangle(((x + 3) * K, (y + 3) * K, (x + w - 3) * K, (y + 5) * K), fill=CELLHI)
    d.rounded_rectangle(((x + w) * K - 2, (y + h * 0.3) * K, (x + w + 4) * K, (y + h * 0.7) * K), radius=K, fill=OL)   # terminal
    d.rectangle(((x + w * 0.2) * K, (y + 2) * K, (x + w * 0.2 + 2) * K, (y + h - 2) * K), fill=YEL)
    bx, bw = x + w * 0.45, w * 0.42
    d.rectangle((bx * K, (y + h * 0.3) * K, (bx + bw) * K, (y + h * 0.7) * K), fill=OL)
    d.rectangle(((bx + 1) * K, (y + h * 0.3 + 1) * K, (bx + 1 + (bw - 2) * charge) * K, (y + h * 0.7 - 1) * K), fill=GREEN if charge > 0.5 else AMBER)

# ============================================================== SOUTH
def legs_front(d):
    for s in (-1, 1):
        hx = 160 + s * 30
        tube(d, [(hx, 238), (hx + s * 5, 276)], 9)                               # thigh bone
        plate(d, X([(176, 240), (205, 240), (209, 256), (204, 272), (180, 272), (174, 256)], s),
              holes=[X([(182, 246), (196, 246), (189, 258)], s), X([(186, 262), (199, 262), (196, 268), (188, 268)], s)],
              hi=X([(179, 243), (202, 243), (203, 246), (178, 246)], s))
        coil(d, (hx + s * 5, 270), (hx + s * 5, 282), 12)
        knee_pad(d, hx + s * 5, 282)
        tube(d, [(hx + s * 5, 290), (hx + s * 3, 300)], 8)
        plate(d, X([(180, 290), (202, 290), (200, 300), (182, 300)], s), holes=[X([(186, 292), (196, 292), (191, 298)], s)])
        boot_front(d, hx + s * 3, 314)
        ball(d, hx, 240, 9)

def torso_front(d):
    # cable bundles (the frame's "muscles") either side of the bellows, from chest to belt
    for s in (-1, 1):
        cables(d, [bez((160 + s * 16, 196), (160 + s * 28, 206), (160 + s * 24, 220), (160 + s * 18, 232)),
                   bez((160 + s * 24, 194), (160 + s * 38, 206), (160 + s * 34, 222), (160 + s * 28, 232))], 6)
    # bellows stomach
    for i, y in enumerate((200, 207, 214, 221)):
        d.rounded_rectangle(((146) * K, y * K, 174 * K, (y + 8) * K), radius=3 * K, fill=OL)
        d.rounded_rectangle((147.5 * K, (y + 1.5) * K, 172.5 * K, (y + 6.5) * K), radius=2 * K, fill=MET if i % 2 else MET_HI)
    # pelvis: dark belt and a bone codpiece plate
    tube(d, bez((112, 230), (130, 240), (190, 240), (208, 230)), 11)
    plate(d, [(148, 226), (172, 226), (176, 238), (166, 250), (154, 250), (144, 238)], hi=[(151, 229), (169, 229), (171, 233), (149, 233)])
    # chest cage: a broad bone lattice over the pecs, open in the middle, sternum ridge
    for s in (-1, 1):
        plate(d, X([(164, 130), (196, 128), (220, 140), (226, 162), (216, 186), (196, 200), (170, 198), (166, 170)], s),
              holes=[X([(176, 140), (198, 138), (210, 150), (190, 156)], s), X([(178, 164), (204, 160), (210, 176), (186, 182)], s),
                     X([(214, 160), (220, 164), (214, 180)], s)],
              hi=X([(168, 133), (196, 131), (212, 138), (172, 140)], s),
              sh=X([(198, 196), (214, 184), (218, 188), (200, 198)], s))
    poly(d, [(156, 128), (164, 128), (166, 198), (154, 198)], MET)                       # sternum
    flat(d, [(157, 131), (160, 131), (160, 195), (157, 195)], MET_HI)
    # neck ring
    d.ellipse((134 * K, 114 * K, 186 * K, 136 * K), outline=OL, width=int(7 * K))
    d.ellipse((135.5 * K, 115.5 * K, 184.5 * K, 134.5 * K), outline=MET_HI, width=int(2.5 * K))
    # roll bars over the shoulders, two prongs each side
    for s in (-1, 1):
        tube(d, X(bez((176, 126), (186, 98), (206, 98), (214, 120)), s), 6, BONE, BONE_HI)
        tube(d, X(bez((196, 130), (212, 104), (232, 108), (236, 128)), s), 5, BONE, BONE_HI)

def arms_front(d):
    for s in (-1, 1):
        sx = 160 + s * 82
        tube(d, [(sx, 140), (sx + s * 6, 166)], 11)
        coil(d, (sx + s * 6, 166), (sx + s * 8, 184), 15)
        ball(d, sx + s * 8, 190, 8)
        tube(d, [(sx + s * 8, 192), (sx + s * 7, 226)], 9)
        plate(d, X([(229, 196), (258, 194), (256, 222), (235, 226)], s), holes=[X([(238, 202), (250, 201), (246, 214)], s)],
              hi=X([(232, 198), (255, 197), (255, 200), (232, 201)], s))
        gauntlet(d, sx + s * 7, 238, s)
        # shoulder: dark ball under a bone cap
        ball(d, sx, 140, 15)
        plate(d, X([(226, 124), (250, 122), (260, 134), (254, 140), (230, 138)], s), hi=X([(230, 126), (248, 124), (252, 128), (232, 129)], s))

def south(d, part):
    if part == 'back':
        tube(d, [(160, 122), (160, 228)], 9, MET_DK, MET)                        # spine, seen through the cage
        for s in (-1, 1):
            tube(d, X(bez((166, 128), (214, 134), (222, 186), (190, 214)), s), 6, MET_DK, MET)
        return
    legs_front(d); torso_front(d); arms_front(d)

# ============================================================== EAST (facing right)
def east(d, part):
    if part == 'back':                                                      # far arm and far leg in shadow
        tube(d, [(168, 140), (176, 186)], 9, MET_DK, MET); tube(d, [(176, 190), (188, 228)], 8, MET_DK, MET)
        gauntlet(d, 192, 238, 1)
        tube(d, [(162, 240), (170, 276)], 9, MET_DK, MET); tube(d, [(170, 284), (166, 300)], 8, MET_DK, MET)
        poly(d, [(152, 300), (186, 300), (196, 308), (196, 314), (148, 314)], MET_DK)
        return
    # the rear hatch seen edge-on: a shallow shell hugging the back, its hinge at the top, the cell port low
    poly(d, [(134, 124), (124, 130), (117, 156), (118, 200), (126, 214), (136, 212)], MET)
    flat(d, [(132, 128), (125, 134), (121, 156), (126, 156), (128, 136), (134, 131)], MET_HI)
    ball(d, 133, 126, 4, MET, MET_HI, bolt=False)
    d.ellipse((116 * K, 190 * K, 128 * K, 202 * K), fill=OL); d.ellipse((118 * K, 192 * K, 126 * K, 200 * K), fill=MET_DK)
    d.ellipse((120 * K, 194 * K, 124 * K, 198 * K), fill=CELL)
    # chest cage in profile, bulging forward, with holes
    plate(d, [(130, 126), (170, 122), (196, 134), (208, 158), (204, 184), (186, 200), (150, 204), (132, 196)],
          holes=[[(146, 136), (172, 134), (180, 150), (150, 154)], [(150, 164), (190, 160), (192, 176), (156, 184)], [(196, 150), (202, 160), (198, 176)]],
          hi=[(134, 129), (170, 125), (186, 132), (138, 134)], sh=[(150, 200), (184, 196), (188, 199), (152, 202)])
    # bellows and cables in profile
    cables(d, [bez((150, 200), (170, 210), (176, 222), (168, 232)), bez((140, 200), (152, 214), (156, 224), (150, 234))], 6)
    for y in (204, 211, 218):
        d.rounded_rectangle((160 * K, y * K, 186 * K, (y + 8) * K), radius=3 * K, fill=OL)
        d.rounded_rectangle((161.5 * K, (y + 1.5) * K, 184.5 * K, (y + 6.5) * K), radius=2 * K, fill=MET_HI)
    tube(d, bez((122, 228), (140, 238), (176, 238), (190, 230)), 11)                    # belt
    # near leg: thigh plate, coil, knee pad, shin, boot with the heel ring
    tube(d, [(156, 240), (162, 276)], 9)
    plate(d, [(146, 240), (172, 240), (178, 256), (172, 274), (152, 274), (144, 256)],
          holes=[[(154, 246), (168, 246), (161, 258)], [(156, 262), (168, 262), (166, 270), (158, 270)]], hi=[(148, 243), (170, 243), (171, 246), (148, 246)])
    coil(d, (162, 270), (164, 282), 12)
    knee_pad(d, 168, 282, 10)
    tube(d, [(164, 290), (160, 302)], 8)
    plate(d, [(150, 290), (172, 290), (170, 302), (152, 302)], holes=[[(156, 292), (166, 292), (161, 299)]])
    poly(d, [(140, 300), (176, 300), (188, 305), (200, 308), (200, 316), (138, 316)], MET)
    plate(d, [(172, 302), (190, 306), (198, 309), (198, 312), (172, 312)])
    d.ellipse((128 * K, 298 * K, 146 * K, 316 * K), outline=OL, width=int(6 * K))         # heel ring
    d.ellipse((129.5 * K, 299.5 * K, 144.5 * K, 314.5 * K), outline=MET_HI, width=int(2 * K))
    ball(d, 156, 240, 9)
    # roll bar, shoulder, near arm swinging slightly forward
    tube(d, bez((138, 128), (144, 100), (172, 98), (178, 122)), 6, BONE, BONE_HI)
    tube(d, [(156, 140), (162, 166)], 11)
    coil(d, (162, 166), (166, 184), 15)
    ball(d, 168, 190, 8)
    tube(d, [(168, 192), (180, 226)], 9)
    plate(d, [(164, 196), (184, 192), (192, 222), (178, 228)], holes=[[(172, 202), (182, 200), (182, 214)]], hi=[(167, 198), (182, 195), (183, 198), (168, 201)])
    gauntlet(d, 184, 238, 1)
    ball(d, 156, 140, 15)
    plate(d, [(140, 124), (166, 120), (176, 130), (170, 138), (144, 138)], hi=[(144, 126), (164, 123), (168, 127), (146, 129)])

# ============================================================== NORTH
def cell_bay(d):
    """the cell port on the right hip, outside the back doors: a battery-like cell slots in from the top"""
    sub = Image.new('RGBA', (52 * K, 24 * K)); sd = ImageDraw.Draw(sub)
    sd.rounded_rectangle((0, 0, 52 * K - 1, 24 * K - 1), radius=4 * K, fill=OL)
    sd.rounded_rectangle((1.5 * K, 1.5 * K, 50.5 * K, 22.5 * K), radius=3 * K, fill=MET)
    sd.rectangle((3 * K, 3 * K, 49 * K, 5 * K), fill=MET_HI)
    sd.rounded_rectangle((4 * K, 6 * K, 44 * K, 19 * K), radius=2 * K, fill=MET_DK)
    cell(sd, 6, 5, 38, 15, 0.85)
    d._image.alpha_composite(sub.rotate(90, expand=True), (int(205 * K), int(186 * K)))

def north(d, part, closed=False, layer='all'):
    if part == 'back':
        if closed:
            return
        # the the rear hatch, swung UP over the head on its top hinge (we see its inside, foreshortened)
        plate(d, [(124, 104), (196, 104), (204, 82), (190, 70), (130, 70), (116, 82)],
              holes=[[(136, 78), (156, 76), (154, 92), (138, 94)], [(164, 76), (184, 78), (182, 94), (166, 92)]],
              hi=[(132, 72), (188, 72), (196, 78), (124, 78)])
        for s in (-1, 1):
            tube(d, X([(186, 104), (190, 124)], s), 5, MET, MET_HI)                              # the hatch's hinge arms
        return
    if layer in ('all', 'far'):
        # legs from behind: calf plates, boots with heel rings
        for s in (-1, 1):
            hx = 160 + s * 30
            tube(d, [(hx, 238), (hx + s * 5, 276)], 9)
            plate(d, X([(176, 240), (205, 240), (209, 256), (204, 272), (180, 272), (174, 256)], s),
                  holes=[X([(184, 248), (198, 248), (192, 264)], s)], hi=X([(179, 243), (202, 243), (203, 246), (178, 246)], s))
            coil(d, (hx + s * 5, 270), (hx + s * 5, 284), 12)
            tube(d, [(hx + s * 5, 284), (hx + s * 3, 300)], 9)
            plate(d, X([(178, 284), (204, 284), (202, 300), (180, 300)], s), holes=[X([(186, 288), (198, 288), (192, 296)], s)])
            poly(d, X([(172, 300), (206, 300), (208, 316), (170, 316)], s), MET)
            cx = hx + s * 3
            d.ellipse(((cx - 10) * K, 300 * K, (cx + 10) * K, 318 * K), outline=OL, width=int(6 * K))   # heel ring
            d.ellipse(((cx - 8.5) * K, 301.5 * K, (cx + 8.5) * K, 316.5 * K), outline=MET_HI, width=int(2 * K))
            ball(d, hx, 240, 9)
        cell_bay(d)
        # roll bars and shoulders, arms from behind
        for s in (-1, 1):
            tube(d, X(bez((176, 126), (186, 98), (206, 98), (214, 120)), s), 6, BONE, BONE_HI)
            tube(d, X(bez((196, 130), (212, 104), (232, 108), (236, 128)), s), 5, BONE, BONE_HI)
            sx = 160 + s * 82
            tube(d, [(sx, 140), (sx + s * 6, 166)], 11)
            coil(d, (sx + s * 6, 166), (sx + s * 8, 184), 15)
            ball(d, sx + s * 8, 190, 8)
            tube(d, [(sx + s * 8, 192), (sx + s * 7, 226)], 9)
            plate(d, X([(229, 196), (258, 194), (256, 222), (235, 226)], s), holes=[X([(238, 202), (250, 201), (246, 214)], s)])
            gauntlet(d, sx + s * 7, 238, -s)
            ball(d, sx, 140, 15)
            plate(d, X([(226, 124), (250, 122), (260, 134), (254, 140), (230, 138)], s))

    if layer in ('all', 'near'):
        tube(d, bez((112, 230), (130, 240), (190, 240), (208, 230)), 11)
        plate(d, [(146, 226), (174, 226), (178, 240), (142, 240)], hi=[(149, 228), (171, 228), (172, 231), (148, 231)])
        if closed:
            # the hatch shut over the opening: a bone shell the shape of the rim, hinges at the top
            rp = bez((166, 128), (216, 132), (222, 188), (186, 214))
            shell = rp + [(160 + (160 - x), y) for x, y in reversed(rp)]
            plate(d, shell, holes=[X([(x, 146 + (x - 172) // 3), (x + 4, 146 + (x - 172) // 3), (x + 4, 178 - (x - 172) // 2), (x, 178 - (x - 172) // 2)], s)
                                  for s in (-1, 1) for x in (172, 182, 192)],
                  hi=[(150, 132), (170, 132), (190, 136), (150, 138)])
            for s_ in (-1, 1):
                hx = 160 + s_ * 20
                d.rounded_rectangle(((hx - 6) * K, 124 * K, (hx + 6) * K, 132 * K), radius=2 * K, fill=OL)   # top hinges
                d.rounded_rectangle(((hx - 4.5) * K, 125.5 * K, (hx + 4.5) * K, 130.5 * K), radius=K, fill=YEL)
            tube(d, [(148, 186), (172, 186)], 4, MET_DK, MET)                                      # grab handle
        else:
            # the open back: the rim of the cage's rear opening around the pilot's back...
            for s in (-1, 1):
                tube(d, X(bez((166, 130), (214, 134), (220, 186), (186, 212)), s), 7, BONE, BONE_HI)

VIEWS = {'south': south, 'east': east, 'north': north, 'north_closed': lambda d, p: north(d, p, True)}

def render(art, facing, frame=True, with_pawn=True):
    out = Image.new('RGBA', (C, C))
    if frame:
        im = Image.new('RGBA', (W, W)); VIEWS[facing](ImageDraw.Draw(im), 'back'); out.alpha_composite(im.resize((C, C), Image.LANCZOS))
    if with_pawn:
        p = pawn(art, facing.split('_')[0]); up = Image.new('RGBA', (C, C)); up.alpha_composite(p, (0, -RAISE)); out.alpha_composite(up)
    if frame:
        im = Image.new('RGBA', (W, W)); VIEWS[facing](ImageDraw.Draw(im), 'front'); out.alpha_composite(im.resize((C, C), Image.LANCZOS))
    return out

if __name__ == '__main__':
    out, art = sys.argv[1], sys.argv[2]
    rows = [('frame', True, False), ('frame + pawn', True, True), ('pawn (game art)', False, True)]
    Z = 2
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 22)
    sheet = Image.new('RGB', (190 + 4 * C * Z, 50 + len(rows) * C * Z), (236, 230, 220)); sd = ImageDraw.Draw(sheet)
    for i, f in enumerate(('south', 'east', 'north', 'north_closed')):
        sd.text((190 + i * C * Z + 20, 14), f, fill=(20, 20, 20), font=font)
    for j, (lab, fr, pw) in enumerate(rows):
        sd.text((10, 50 + j * C * Z + C * Z // 2 - 10), lab, fill=(20, 20, 20), font=font)
        for i, f in enumerate(('south', 'east', 'north', 'north_closed')):
            im = render(art, f, fr, pw)
            im.save(f'{out}/v3c_{lab.split()[0]}{"_pawn" if pw and fr else ""}_{f}.png')
            bg = Image.new('RGBA', (C, C), (96, 92, 98, 255)); bg.alpha_composite(im)
            sheet.paste(bg.resize((C * Z, C * Z), Image.LANCZOS), (190 + i * C * Z, 50 + j * C * Z))
    sheet.save(f'{out}/frame_sheet_v3c.png')
