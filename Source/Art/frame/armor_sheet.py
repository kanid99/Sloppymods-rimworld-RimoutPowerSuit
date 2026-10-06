"""A sheet of armour pieces in five styles, drawn as SVG to fit the frame (option A: frame proportions win).
Rows: helmet, chest plate, arms, legs, pack (north, on the hatch), the assembled suit (south).
Columns: Heavy (Bulwark), Light (Bughunter), Industrial (Miner), Builder, Medic.
Pieces are drawn in the frame's canvas coordinates (320 = 2.717 tiles), south-facing except packs.
Colours here only tell the styles apart; in game the plates take the suit's tint.
    python3 armor_sheet.py <out dir>"""
import math, sys
import frame_svg as S
from frame4 import K, OL, OLW, X, MET, MET_HI, MET_DK, RUST, poly, flat, _line, ball, rivet, seam, tube, bez

def sh(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c[:3]) + (255,)

class St:
    def __init__(self, name, base, accent, glow):
        self.name, self.base, self.hi, self.sh, self.dk = name, base + (255,), sh(base, 1.22), sh(base, 0.78), sh(base, 0.55)
        self.acc, self.glow = accent + (255,), glow + (255,)

STYLES = [St('Heavy (Bulwark)', (118, 128, 140), (60, 64, 70), (230, 60, 44)),
          St('Light (Bughunter)', (122, 136, 84), (64, 70, 52), (130, 236, 120)),
          St('Industrial (Miner)', (212, 122, 46), (52, 50, 50), (255, 222, 120)),
          St('Builder', (222, 186, 64), (40, 36, 34), (255, 150, 40)),
          St('Medic', (230, 230, 222), (190, 44, 40), (90, 210, 220))]
HAZ = (34, 30, 28, 255)

def pl(d, pts, st, hi=None, shd=None, base=None):
    poly(d, pts, base or st.base)
    if hi: flat(d, hi, st.hi)
    if shd: flat(d, shd, st.sh)

def stripes(d, pts_box, col_a, col_b, step=8):
    """diagonal stripes clipped to a polygon"""
    g = d.group()
    xs = [x for x, _ in pts_box]; ys = [y for _, y in pts_box]
    flat(g, [(min(xs), min(ys)), (max(xs), min(ys)), (max(xs), max(ys)), (min(xs), max(ys))], col_a)
    h = max(ys) - min(ys); x = min(xs) - h
    while x < max(xs) + h:
        flat(g, [(x, max(ys)), (x + step / 2, max(ys)), (x + step / 2 + h, min(ys)), (x + h, min(ys))], col_b)
        x += step
    cid = d._id()
    d.out.append(f'<clipPath id="{cid}"><polygon points="' + ' '.join(f'{x:.2f},{y:.2f}' for x, y in pts_box) + '"/></clipPath>')
    d.place(g, f'clip-path="url(#{cid})"')
    _line(d, pts_box + pts_box[:1], OLW * 2, OL)

def lens(d, cx, cy, r, glow):
    ball(d, cx, cy, r, sh(glow, 0.55), glow, bolt=False)

def cross(d, cx, cy, s, col):
    flat(d, [(cx - s / 3, cy - s), (cx + s / 3, cy - s), (cx + s / 3, cy + s), (cx - s / 3, cy + s)], col)
    flat(d, [(cx - s, cy - s / 3), (cx + s, cy - s / 3), (cx + s, cy + s / 3), (cx - s, cy + s / 3)], col)

# ------------------------------------------------------------------ helmets (the head zone: ~126-194, 50-114)
def helmet(d, st, i):
    if i == 0:      # heavy: a boxy helm, a single visor slit, cheek guards, a crest ridge
        pl(d, [(128, 56), (192, 56), (200, 74), (198, 104), (186, 116), (134, 116), (122, 104), (120, 74)], st,
           hi=[(132, 59), (188, 59), (192, 66), (128, 66)], shd=[(190, 104), (196, 80), (198, 100), (186, 114)])
        poly(d, [(130, 80), (190, 80), (188, 92), (132, 92)], st.acc)
        _line(d, [(136, 86), (184, 86)], 3, st.glow)
        pl(d, [(154, 48), (166, 48), (168, 60), (152, 60)], st)
        for x in (128, 192): rivet(d, x, 100, 2)
        seam(d, [(140, 104), (180, 104)], 2)
    elif i == 1:    # light: a rounded dome, two big bug-eye lenses, mandible vents
        d.ellipse((124 * K, 52 * K, 196 * K, 114 * K), fill=OL); d.ellipse((127 * K, 55 * K, 193 * K, 111 * K), fill=st.base)
        d.ellipse((134 * K, 58 * K, 176 * K, 72 * K), fill=st.hi)
        lens(d, 146, 84, 9, st.glow); lens(d, 174, 84, 9, st.glow)
        for x in (150, 160, 170): _line(d, [(x, 100), (x, 108)], 2.4, st.acc)
    elif i == 2:    # industrial: a round helmet with a brow, a headlamp and a mouth grille
        pl(d, [(126, 70), (138, 54), (182, 54), (194, 70), (196, 104), (184, 116), (136, 116), (124, 104)], st,
           hi=[(140, 57), (180, 57), (186, 64), (134, 64)])
        poly(d, [(122, 72), (198, 72), (198, 80), (122, 80)], st.sh)
        poly(d, [(132, 84), (188, 84), (186, 96), (134, 96)], st.acc)
        _line(d, [(138, 90), (182, 90)], 2.4, sh(st.glow, 0.8))
        poly(d, [(146, 100), (174, 100), (172, 114), (148, 114)], MET_DK)
        for x in (152, 158, 164, 170): _line(d, [(x, 102), (x, 112)], 1.8, MET)
        poly(d, [(150, 44), (170, 44), (172, 56), (148, 56)], MET_DK); d.ellipse((153 * K, 46 * K, 167 * K, 54 * K), fill=st.glow)
    elif i == 3:    # builder: a hard hat with a wide brim over an amber face visor
        d.ellipse((128 * K, 48 * K, 192 * K, 96 * K), fill=OL); d.ellipse((131 * K, 51 * K, 189 * K, 93 * K), fill=st.base)
        pl(d, [(112, 74), (208, 74), (204, 84), (116, 84)], st, hi=[(116, 76), (204, 76), (204, 78), (116, 78)])
        pl(d, [(156, 50), (164, 50), (164, 74), (156, 74)], st, base=st.sh)
        poly(d, [(132, 86), (188, 86), (184, 110), (136, 110)], (170, 110, 40, 255))
        flat(d, [(138, 89), (160, 89), (156, 96), (138, 96)], (230, 180, 90, 255))
    else:           # medic: a big round teal glass dome in a white ring, antenna with a green tip
        d.ellipse((124 * K, 50 * K, 196 * K, 116 * K), fill=OL); d.ellipse((127 * K, 53 * K, 193 * K, 113 * K), fill=st.base)
        d.ellipse((133 * K, 60 * K, 187 * K, 108 * K), fill=OL); d.ellipse((135 * K, 62 * K, 185 * K, 106 * K), fill=sh(st.glow, 0.7))
        d.ellipse((141 * K, 66 * K, 165 * K, 80 * K), fill=sh(st.glow, 1.25))
        _line(d, [(190, 64), (200, 44)], 2.6 + 2 * OLW, OL); _line(d, [(190, 64), (200, 44)], 2.6, MET)
        d.ellipse((197 * K, 39 * K, 205 * K, 47 * K), fill=(120, 230, 120, 255))
        cross(d, 160, 109, 3, st.acc)

# ------------------------------------------------------------------ chest plates (the torso: ~98-222, 104-198)
def chest(d, st, i):
    if i == 0:      # heavy: a wide two-layer slab with a centre ridge
        pl(d, [(104, 108), (216, 108), (226, 128), (222, 176), (198, 194), (122, 194), (98, 176), (94, 128)], st,
           hi=[(108, 111), (212, 111), (216, 118), (104, 118)], shd=[(206, 186), (220, 172), (222, 176), (200, 192)])
        pl(d, [(114, 150), (206, 150), (210, 176), (190, 190), (130, 190), (110, 176)], st, base=st.sh)
        poly(d, [(154, 112), (166, 112), (168, 186), (152, 186)], st.hi)
        for x, y in ((110, 124), (210, 124), (118, 172), (202, 172)): rivet(d, x, y, 2.2)
    elif i == 1:    # light: a slim V plate with open cut-outs showing the frame, side vents
        pl(d, [(116, 108), (204, 108), (214, 126), (196, 176), (160, 192), (124, 176), (106, 126)], st,
           hi=[(120, 111), (200, 111), (204, 118), (116, 118)])
        for s in (-1, 1):
            poly(d, X([(170, 128), (196, 126), (186, 152), (170, 150)], s), MET_DK)
            for k in range(3): _line(d, X([(202, 140 + k * 8), (212, 138 + k * 8)], s), 2, st.acc)
        lens(d, 160, 166, 4, st.glow)
    elif i == 2:    # industrial: a barrel chest with a hazard band and intake grilles
        pl(d, [(106, 110), (214, 110), (224, 134), (220, 176), (196, 194), (124, 194), (100, 176), (96, 134)], st,
           hi=[(110, 113), (210, 113), (214, 120), (106, 120)])
        stripes(d, [(100, 150), (220, 150), (220, 164), (100, 164)], (240, 196, 60, 255), HAZ)
        for s in (-1, 1):
            poly(d, X([(176, 122), (206, 122), (206, 144), (176, 144)], s), MET_DK)
            for k in range(4): _line(d, X([(179, 126 + k * 5), (203, 126 + k * 5)], s), 1.6, MET)
    elif i == 3:    # builder: a plate with tool loops, a pocket and a chevron band
        pl(d, [(108, 110), (212, 110), (220, 130), (216, 178), (194, 194), (126, 194), (104, 178), (100, 130)], st,
           hi=[(112, 113), (208, 113), (212, 120), (108, 120)])
        stripes(d, [(108, 176), (212, 176), (196, 190), (124, 190)], (240, 196, 60, 255), HAZ, 10)
        for x in (124, 140): poly(d, [(x, 126), (x + 10, 126), (x + 10, 160), (x, 160)], st.acc)
        pl(d, [(176, 130), (204, 130), (204, 160), (176, 160)], st, base=st.sh)
        seam(d, [(176, 138), (204, 138)], 2)
    else:           # medic: a smooth rounded plate, a diagnostic screen and a red cross
        pl(d, [(110, 110), (210, 110), (220, 132), (214, 176), (188, 194), (132, 194), (106, 176), (100, 132)], st,
           hi=[(114, 113), (206, 113), (210, 120), (110, 120)])
        poly(d, [(130, 128), (176, 128), (176, 156), (130, 156)], (30, 50, 46, 255))
        _line(d, [(134, 144), (144, 144), (148, 134), (154, 152), (158, 144), (172, 144)], 1.8, (120, 236, 140, 255))
        cross(d, 196, 142, 8, st.acc)

# ------------------------------------------------------------------ arms (pauldron ~204-266/100-150, forearm ~224-266/192-240)
def arm(d, st, i, s):
    Q = lambda p: X(p, s)
    if i == 0:      # heavy: a three-layer pauldron, a thick forearm guard
        for k, y in enumerate((96, 110, 124)):
            pl(d, Q([(200 + k * 4, y), (240, y - 6 + k * 2), (268, y + 4), (272, y + 22), (244, y + 26), (206 + k * 4, y + 20)]), st,
               hi=Q([(206 + k * 4, y + 3), (240, y - 3 + k * 2), (262, y + 6), (240, y + 6)]))
        pl(d, Q([(222, 192), (264, 190), (270, 214), (262, 240), (230, 242), (220, 216)]), st,
           hi=Q([(226, 195), (260, 193), (262, 198), (226, 200)]), shd=Q([(262, 236), (268, 214), (270, 218), (264, 240)]))
        for y in (204, 228): rivet(d, 160 + s * 72, y, 2)
    elif i == 1:    # light: a small round shoulder cap, a slim open bracer
        pl(d, Q([(212, 104), (240, 98), (262, 108), (264, 128), (246, 138), (218, 134)]), st,
           hi=Q([(216, 107), (240, 101), (256, 108), (238, 108)]))
        lens(d, 160 + s * 80, 120, 3, st.glow)
        pl(d, Q([(230, 196), (260, 194), (262, 236), (234, 238)]), st)
        poly(d, Q([(238, 204), (254, 203), (254, 226), (240, 227)]), MET_DK)
    elif i == 2:    # industrial: a rounded pauldron with a hazard edge, a vented forearm cowl
        pl(d, Q([(204, 102), (238, 94), (266, 104), (272, 134), (252, 148), (212, 144)]), st,
           hi=Q([(208, 105), (238, 97), (260, 104), (236, 104)]))
        stripes(d, Q([(212, 136), (252, 140), (250, 148), (212, 144)]), (240, 196, 60, 255), HAZ, 7)
        pl(d, Q([(224, 192), (264, 190), (268, 228), (256, 242), (230, 242), (222, 226)]), st)
        for k in range(3): _line(d, Q([(232, 204 + k * 7), (258, 203 + k * 7)]), 1.8, st.dk)
    elif i == 3:    # builder: a pauldron with a beacon light, a bracer with a tool clip
        pl(d, Q([(206, 104), (240, 96), (266, 106), (270, 132), (250, 144), (214, 140)]), st,
           hi=Q([(210, 107), (240, 99), (260, 106), (236, 106)]))
        poly(d, Q([(232, 88), (248, 88), (250, 100), (230, 100)]), MET_DK)
        d.ellipse(((160 + s * 80 - 6) * K, 84 * K, (160 + s * 80 + 6) * K, 96 * K), fill=st.glow)
        pl(d, Q([(226, 194), (262, 192), (266, 236), (230, 240)]), st)
        poly(d, Q([(236, 206), (256, 205), (256, 222), (236, 223)]), st.acc)
    else:           # medic: a smooth oval pauldron with a cross, a bracer with a small screen
        d.ellipse(((160 + s * 78 - 32) * K, 96 * K, (160 + s * 78 + 32) * K, 146 * K), fill=OL)
        d.ellipse(((160 + s * 78 - 29) * K, 99 * K, (160 + s * 78 + 29) * K, 143 * K), fill=st.base)
        d.ellipse(((160 + s * 78 - 22) * K, 102 * K, (160 + s * 78 + 10) * K, 114 * K), fill=st.hi)
        cross(d, 160 + s * 78, 124, 7, st.acc)
        pl(d, Q([(228, 194), (262, 192), (264, 236), (230, 238)]), st)
        poly(d, Q([(236, 204), (256, 203), (256, 218), (236, 219)]), (30, 50, 46, 255))
        _line(d, Q([(239, 211), (245, 211), (247, 207), (250, 214), (253, 211)]), 1.4, (120, 236, 140, 255))

# ------------------------------------------------------------------ legs (thigh ~172-214/224-274, knee ~266-284, shin ~176-210/280-298)
def leg(d, st, i, s):
    Q = lambda p: X(p, s)
    if i == 0:      # heavy: a thick thigh plate, a big knee guard, a greave
        pl(d, Q([(170, 224), (210, 224), (216, 248), (210, 270), (178, 272), (168, 248)]), st,
           hi=Q([(173, 227), (207, 227), (209, 232), (172, 232)]))
        pl(d, Q([(176, 262), (208, 262), (212, 284), (192, 292), (172, 284)]), st, base=st.sh)
        pl(d, Q([(174, 284), (210, 284), (212, 300), (176, 302)]), st)
        rivet(d, 160 + s * 32, 274, 2.2)
    elif i == 1:    # light: a thigh strip and a small knee cap
        pl(d, Q([(180, 228), (206, 228), (208, 262), (184, 264)]), st)
        poly(d, Q([(186, 236), (200, 236), (200, 254), (188, 254)]), MET_DK)
        pl(d, Q([(182, 266), (204, 266), (206, 282), (184, 282)]), st, hi=Q([(185, 268), (202, 268), (202, 271), (185, 271)]))
    elif i == 2:    # industrial: a thigh plate with a pouch, a chunky knee pad
        pl(d, Q([(172, 226), (212, 226), (214, 266), (176, 268)]), st)
        pl(d, Q([(190, 236), (210, 236), (210, 258), (190, 258)]), st, base=st.sh)
        seam(d, Q([(190, 242), (210, 242)]), 2)
        pl(d, Q([(174, 264), (210, 264), (214, 286), (172, 286)]), st, base=st.acc)
        stripes(d, Q([(176, 268), (208, 268), (210, 276), (176, 276)]), (240, 196, 60, 255), HAZ, 7)
    elif i == 3:    # builder: a big knee pad, a thigh strap with a holster
        _line(d, Q([(170, 240), (214, 240)]), 5 + 2 * OLW, OL); _line(d, Q([(170, 240), (214, 240)]), 5, st.acc)
        pl(d, Q([(192, 236), (212, 236), (214, 262), (194, 264)]), st, base=st.sh)
        pl(d, Q([(172, 262), (212, 262), (216, 290), (194, 296), (168, 290)]), st, hi=Q([(175, 265), (209, 265), (210, 270), (174, 270)]))
    else:           # medic: smooth thigh, knee and shin plates with a white trim line
        pl(d, Q([(174, 226), (210, 226), (214, 250), (208, 270), (180, 270), (170, 250)]), st)
        _line(d, Q([(178, 246), (206, 246)]), 2.4, st.acc)
        d.ellipse(((160 + s * 32 - 12) * K, 264 * K, (160 + s * 32 + 12) * K, 288 * K), fill=OL)
        d.ellipse(((160 + s * 32 - 9) * K, 267 * K, (160 + s * 32 + 9) * K, 285 * K), fill=st.base)
        pl(d, Q([(178, 286), (208, 286), (210, 300), (180, 302)]), st)

# ------------------------------------------------------------------ packs (north view, on the hatch: ~112-208, 96-204)
def pack(d, st, i):
    if i == 0:      # heavy: three cell caps in a column and a shield emitter dish on top
        pl(d, [(128, 104), (192, 104), (198, 196), (122, 196)], st, hi=[(132, 107), (188, 107), (190, 112), (130, 112)])
        for y in (128, 154, 180):
            ball(d, 160, y, 10, st.sh, st.hi, bolt=False); ball(d, 160, y, 5, MET_DK, MET)
        d.ellipse((136 * K, 84 * K, 184 * K, 100 * K), fill=OL); d.ellipse((139 * K, 86 * K, 181 * K, 98 * K), fill=sh(st.glow, 0.8))
        _line(d, [(160, 100), (160, 106)], 4 + 2 * OLW, OL)
    elif i == 1:    # light: a slim pack with twin jump-jet nozzles
        pl(d, [(136, 106), (184, 106), (188, 176), (132, 176)], st, hi=[(140, 109), (180, 109), (182, 114), (138, 114)])
        for s in (-1, 1):
            poly(d, X([(176, 120), (200, 118), (204, 190), (180, 192)], s), st.sh)
            poly(d, X([(178, 190), (204, 188), (208, 206), (176, 208)], s), MET_DK)
            d.ellipse(((160 + s * 30 - 9) * K, 200 * K, (160 + s * 30 + 9) * K, 210 * K), fill=sh(st.glow, 0.9))
    elif i == 2:    # industrial: a radiator fan between exhaust stacks
        pl(d, [(124, 108), (196, 108), (200, 196), (120, 196)], st)
        d.ellipse((136 * K, 124 * K, 184 * K, 172 * K), fill=OL); d.ellipse((139 * K, 127 * K, 181 * K, 169 * K), fill=MET_DK)
        for a in range(4):
            t = a * math.pi / 2 + 0.5
            _line(d, [(160, 148), (160 + 18 * math.cos(t), 148 + 18 * math.sin(t))], 6, MET)
        ball(d, 160, 148, 5, MET, MET_HI, bolt=False)
        for s in (-1, 1):
            tube(d, X([(204, 168), (204, 92)], s), 8, MET, MET_HI)
            d.ellipse(((160 + s * 44 - 5) * K, 86 * K, (160 + s * 44 + 5) * K, 96 * K), fill=OL)
    elif i == 3:    # builder: a cable spool and a gas tank
        pl(d, [(126, 106), (194, 106), (198, 196), (122, 196)], st)
        d.ellipse((132 * K, 114 * K, 170 * K, 152 * K), fill=OL); d.ellipse((135 * K, 117 * K, 167 * K, 149 * K), fill=st.acc)
        for r in (12, 7): d.ellipse(((151 - r) * K, (133 - r) * K, (151 + r) * K, (133 + r) * K), outline=(200, 80, 50, 255), width=int(2 * K))
        tube(d, [(182, 120), (182, 186)], 16, (150, 60, 50, 255), (196, 100, 80, 255))
        stripes(d, [(128, 170), (172, 170), (172, 186), (128, 186)], (240, 196, 60, 255), HAZ, 8)
    else:           # medic: a medical case with a red cross and two canisters of green fluid
        pl(d, [(130, 106), (190, 106), (194, 194), (126, 194)], st, hi=[(134, 109), (186, 109), (188, 114), (132, 114)])
        cross(d, 160, 136, 12, st.acc)
        for s in (-1, 1):
            d.rounded_rectangle(((160 + s * 40 - 9) * K, 120 * K, (160 + s * 40 + 9) * K, 186 * K), radius=8 * K, fill=OL)
            d.rounded_rectangle(((160 + s * 40 - 6.5) * K, 123 * K, (160 + s * 40 + 6.5) * K, 183 * K), radius=6 * K, fill=(200, 220, 220, 255))
            d.rounded_rectangle(((160 + s * 40 - 6.5) * K, 146 * K, (160 + s * 40 + 6.5) * K, 183 * K), radius=6 * K, fill=(110, 210, 110, 255))
        _line(d, [(160, 106), (160, 92)], 2.4 + 2 * OLW, OL); _line(d, [(160, 106), (160, 92)], 2.4, MET)
        d.ellipse((157 * K, 87 * K, 163 * K, 93 * K), fill=(120, 230, 120, 255))

# ------------------------------------------------------------------ the sheet
ROWS = [('Helmet', (106, 30, 108, 96), 'south'), ('Chest plate', (86, 98, 148, 104), 'south'),
        ('Arms', (34, 80, 252, 170), 'south'), ('Legs', (96, 218, 128, 92), 'south'),
        ('Pack (back, on the hatch)', (96, 78, 128, 140), 'north'), ('Assembled', (24, 26, 272, 294), 'south')]
CELL, PADL, PADT = 220, 150, 50
_ghosts = {}
def ghost(f):
    if f not in _ghosts:
        _ghosts[f] = ''.join(S.view(f if f == 'south' else 'north', 0.0))
    return _ghosts[f]

def cell_svg(row, si, st, uid):
    name, box, f = row
    d = S.SvgDraw([], [100000])                                    # its own clip ids, apart from the frame's
    if name == 'Helmet': helmet(d, st, si)
    elif name == 'Chest plate': chest(d, st, si)
    elif name == 'Arms': arm(d, st, si, 1); arm(d, st, si, -1)
    elif name == 'Legs': leg(d, st, si, 1); leg(d, st, si, -1)
    elif name.startswith('Pack'): pack(d, st, si)
    else:
        for s in (1, -1): leg(d, st, si, s)
        chest(d, st, si)
        for s in (1, -1): arm(d, st, si, s)
        helmet(d, st, si)
    body = ''.join(d.out)
    if name == 'Assembled':
        under = f'<g>{ghost(f)}</g>'
    else:
        under = f'<g opacity="0.22">{ghost(f)}</g>'
    inner = (under + body).replace('id="c', f'id="u{uid}c').replace('#c', f'#u{uid}c')
    x, y, w, h = box
    return f'<svg x="{{X}}" y="{{Y}}" width="{CELL - 12}" height="{CELL - 12}" viewBox="{x} {y} {w} {h}" preserveAspectRatio="xMidYMid meet">{inner}</svg>'

if __name__ == '__main__':
    out = sys.argv[1]
    Wd, Hd = PADL + len(STYLES) * CELL, PADT + len(ROWS) * CELL + 20
    parts = [f'<rect width="{Wd}" height="{Hd}" fill="#ece6dc"/>']
    uid = 0
    for si, st in enumerate(STYLES):
        parts.append(f'<text x="{PADL + si * CELL + CELL / 2}" y="32" font-family="DejaVu Sans, sans-serif" font-size="15" text-anchor="middle" fill="#222">{st.name}</text>')
    for ri, row in enumerate(ROWS):
        y0 = PADT + ri * CELL
        parts.append(f'<text x="12" y="{y0 + CELL / 2}" font-family="DejaVu Sans, sans-serif" font-size="15" fill="#222">{row[0].split(" (")[0]}</text>')
        if '(' in row[0]:
            parts.append(f'<text x="12" y="{y0 + CELL / 2 + 18}" font-family="DejaVu Sans, sans-serif" font-size="11" fill="#555">({row[0].split(" (")[1]}</text>')
        for si, st in enumerate(STYLES):
            x0 = PADL + si * CELL
            parts.append(f'<rect x="{x0 + 4}" y="{y0 + 4}" width="{CELL - 8}" height="{CELL - 8}" rx="6" fill="#605c62"/>')
            uid += 1
            parts.append(cell_svg(row, si, st, uid).replace('{X}', str(x0 + 6)).replace('{Y}', str(y0 + 6)))
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {Wd} {Hd}" width="{Wd}" height="{Hd}">'
           f'<title>Armour pieces</title>{"".join(parts)}</svg>')
    open(f'{out}/svg/armor_pieces.svg', 'w').write(svg)
    print(Wd, Hd)
