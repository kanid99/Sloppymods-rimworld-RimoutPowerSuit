"""Art for the power suit frame, drawn in code with Pillow and numpy.

    python3 Source/Art/make_suit_art.py

Writes the worn suit for every adult body type in three directions
(Textures/Things/Pawn/PowerSuit; the game mirrors east for west), the standing suit
(Textures/Things/Item/PowerSuit), the "Climb out" command icon and About/Preview.png.

Every part is a flat shape drawn at 4x size: filled with a top-left lit gradient, given a
rim light and a shadowed edge, outlined in near-black like vanilla art, then the whole
sheet is scaled down to 256px, which antialiases it. Shape coordinates below are in
256px units; (128, 128) is the centre of the pawn's body.
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
K = 4                 # supersampling
S = 256               # output size
N = S * K
CX = 128

# Palette: olive drab plate over a gunmetal frame, Fallout T-51 style.
OLIVE = (126, 124, 84)
OLIVE_DARK = (98, 96, 64)
GUN = (82, 88, 86)
GUN_DARK = (58, 62, 62)
RUBBER = (46, 48, 48)
EDGE = (24, 24, 22)
STRIPE = (190, 140, 48)
VISOR_ON = (255, 196, 84)
VISOR_OFF = (70, 64, 52)
CORE = (120, 226, 255)
LINE = (40, 42, 38)

OUTLINE = 4.0         # outline thickness, output pixels
BODY_WIDTH = {"Male": 1.0, "Female": 0.94, "Thin": 0.9, "Fat": 1.12, "Hulk": 1.16}


# --------------------------------------------------------------------- drawing core

def k(v):
    return v * K


def _shift(m, dx, dy):
    out = np.zeros_like(m)
    h, w = m.shape
    xs, xd = (slice(0, w - dx), slice(dx, w)) if dx >= 0 else (slice(-dx, w), slice(0, w + dx))
    ys, yd = (slice(0, h - dy), slice(dy, h)) if dy >= 0 else (slice(-dy, h), slice(0, h + dy))
    out[yd, xd] = m[ys, xs]
    return out


def _dilate(m, r):
    out = m.copy()
    for i in range(int(r)):
        grown = out.copy()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) + (((1, 1), (1, -1), (-1, 1), (-1, -1)) if i % 2 else ()):
            grown |= _shift(out, dx, dy)
        out = grown
    return out


class Sheet:
    def __init__(self):
        self.rgb = np.zeros((N, N, 3), np.float32)
        self.alpha = np.zeros((N, N), bool)
        self.yy, self.xx = np.mgrid[0:N, 0:N].astype(np.float32)

    def mask(self, draw_fn):
        img = Image.new("L", (N, N), 0)
        draw_fn(ImageDraw.Draw(img))
        return np.array(img) > 127

    def part(self, draw_fn, color, light=0.32, outline=True, rim=True):
        """A plate: gradient-filled, rim-lit, outlined."""
        m = self.mask(draw_fn)
        if not m.any():
            return m
        if outline:
            o = _dilate(m, OUTLINE * K / 2) & ~m
            self.rgb[o] = EDGE
            self.alpha |= o
        ys, xs = np.nonzero(m)
        y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
        ny = (self.yy - y0) / max(1, y1 - y0)
        nx = (self.xx - x0) / max(1, x1 - x0)
        f = 1 + light * (0.5 - ny) + light * 0.45 * (0.5 - nx)
        if rim:
            off = 3 * K
            f = f + 0.22 * (m & ~_shift(m, off, off))     # lit top-left edge
            f = f - 0.22 * (m & ~_shift(m, -off, -off))   # shaded bottom-right edge
        col = np.clip(np.array(color, np.float32)[None, None, :] * f[..., None], 0, 255)
        self.rgb[m] = col[m]
        self.alpha |= m
        return m

    def flat(self, draw_fn, color):
        """Unshaded detail painted only onto what is already drawn (panel lines, decals)."""
        m = self.mask(draw_fn) & self.alpha
        self.rgb[m] = color
        return m

    def glow(self, draw_fn, color, radius=3):
        m = self.mask(draw_fn)
        halo = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius * K))
        h = (np.array(halo, np.float32) / 255)[..., None] * self.alpha[..., None]
        self.rgb = self.rgb * (1 - 0.6 * h) + np.array(color, np.float32) * 0.6 * h
        core = np.clip(np.array(color, np.float32) + 40, 0, 255)
        self.rgb[m] = core
        self.alpha |= m

    def image(self):
        a = (self.alpha * 255).astype(np.uint8)
        img = Image.fromarray(np.dstack([self.rgb.astype(np.uint8), a]), "RGBA")
        return img.resize((S, S), Image.LANCZOS)


def rrect(box, r):
    return lambda d: d.rounded_rectangle([k(v) for v in box], k(r), fill=255)


def ellipse(box):
    return lambda d: d.ellipse([k(v) for v in box], fill=255)


def poly(points):
    return lambda d: d.polygon([(k(x), k(y)) for x, y in points], fill=255)


def line(points, width):
    return lambda d: d.line([(k(x), k(y)) for x, y in points], fill=255, width=int(k(width)), joint="curve")


def both(*fns):
    def draw(d):
        for fn in fns:
            fn(d)
    return draw


def rivets(sh, points, r=1.6):
    for x, y in points:
        sh.flat(ellipse((x - r, y - r, x + r, y + r)), LINE)
        sh.flat(ellipse((x - r * 0.5 - 0.4, y - r * 0.5 - 0.4, x - 0.2, y - 0.2)), (176, 172, 140))


# ----------------------------------------------------------------------- the suit

def front(sh, w, visor):
    """South: the suit facing the viewer."""
    def X(off):
        return CX + off * w

    # legs
    for s in (-1, 1):
        lx = X(s * 25)
        sh.part(rrect((lx - 18, 148, lx + 18, 196), 8), GUN)                       # thigh
        sh.part(rrect((lx - 19, 186, lx + 19, 224), 8), OLIVE)                     # shin plate
        sh.part(ellipse((lx - 13, 178, lx + 13, 200)), OLIVE_DARK)                 # knee cap
        sh.part(rrect((lx - 22, 214, lx + 22, 238), 7), RUBBER)                    # boot
        sh.flat(line([(lx - 20, 231), (lx + 20, 231)], 1.4), EDGE)                 # sole
        sh.flat(line([(lx - 12, 206), (lx + 12, 206)], 1.2), LINE)
    # hips and belt
    sh.part(rrect((X(-46), 136, X(46), 162), 9), GUN_DARK)
    sh.part(rrect((CX - 13, 140, CX + 13, 160), 4), OLIVE_DARK)                   # buckle plate
    for s in (-1, 1):
        sh.part(poly([(X(s * 30), 146), (X(s * 50), 146), (X(s * 48), 176), (X(s * 30), 172)]), OLIVE)  # tassets
    # upper arms
    for s in (-1, 1):
        sh.part(rrect((X(s * 78) - 15, 96, X(s * 78) + 15, 150), 9), GUN)
    # torso: gunmetal frame behind an olive chest plate
    sh.part(poly([(X(-58), 86), (X(58), 86), (X(48), 146), (X(-48), 146)]), GUN_DARK)
    sh.part(poly([(X(-52), 84), (X(52), 84), (X(44), 128), (X(14), 136), (X(-14), 136), (X(-44), 128)]), OLIVE)
    sh.flat(line([(CX, 88), (CX, 134)], 1.6), LINE)                                # chest ridge
    sh.flat(line([(X(-44), 108), (X(-14), 116)], 1.2), LINE)
    sh.flat(line([(X(44), 108), (X(14), 116)], 1.2), LINE)
    for i, y in enumerate((134, 141)):                                             # abdomen bands
        sh.flat(line([(X(-40 + i * 3), y), (X(40 - i * 3), y)], 1.2), LINE)
    rivets(sh, [(X(-40), 94), (X(40), 94), (X(-36), 122), (X(36), 122)])
    # forearm gauntlets and fists
    for s in (-1, 1):
        ax = X(s * 80)
        sh.part(ellipse((ax - 11, 140, ax + 11, 160)), GUN_DARK)                  # elbow
        sh.part(rrect((ax - 17, 150, ax + 17, 188), 9), OLIVE)
        sh.flat(line([(ax - 13, 168), (ax + 13, 168)], 1.2), LINE)
        sh.part(rrect((ax - 15, 184, ax + 15, 206), 8), RUBBER)                    # fist
        sh.flat(line([(ax - 9, 195), (ax + 9, 195)], 1.0), EDGE)
    # pauldrons, with a painted stripe
    for s in (-1, 1):
        px = X(s * 80)
        sh.part(rrect((px - 30, 68, px + 30, 112), 18), OLIVE)
        sh.flat(rrect((px - 30, 92, px + 30, 98), 0), STRIPE)
        sh.flat(line([(px - 26, 105), (px + 26, 105)], 1.2), LINE)
        rivets(sh, [(px - 18, 80), (px + 18, 80)])
    # gorget and helmet
    sh.part(rrect((CX - 30, 80, CX + 30, 100), 8), GUN_DARK)
    sh.part(rrect((CX - 34, 26, CX + 34, 94), 26), OLIVE)                          # dome
    sh.flat(line([(CX, 28), (CX, 46)], 2.0), OLIVE_DARK)                            # crest
    sh.part(rrect((CX - 27, 46, CX + 27, 66), 8), RUBBER, light=0.1)               # visor housing
    if visor:
        sh.glow(rrect((CX - 22, 52, CX + 22, 60), 3), VISOR_ON)
    else:
        sh.flat(rrect((CX - 22, 52, CX + 22, 60), 3), VISOR_OFF)
    sh.part(poly([(CX - 22, 68), (CX + 22, 68), (CX + 15, 92), (CX - 15, 92)]), GUN)  # jaw / breather
    for gx in (-8, -3, 2, 7):
        sh.flat(line([(CX + gx + 0.5, 72), (CX + gx * 0.8 + 0.5, 88)], 1.5), EDGE)
    for s in (-1, 1):
        sh.part(ellipse((CX + s * 31 - 7, 60, CX + s * 31 + 7, 76)), GUN_DARK)    # cheek vents


def back(sh, w):
    """North: the suit from behind, power cell housing in view."""
    def X(off):
        return CX + off * w

    for s in (-1, 1):
        lx = X(s * 25)
        sh.part(rrect((lx - 18, 148, lx + 18, 196), 8), GUN)
        sh.part(rrect((lx - 18, 188, lx + 18, 222), 8), OLIVE_DARK)              # calf
        sh.part(rrect((lx - 22, 214, lx + 22, 238), 7), RUBBER)
        sh.flat(line([(lx - 20, 231), (lx + 20, 231)], 1.4), EDGE)
    sh.part(rrect((X(-46), 136, X(46), 162), 9), GUN_DARK)
    for s in (-1, 1):
        sh.part(rrect((X(s * 78) - 15, 96, X(s * 78) + 15, 150), 9), GUN)
    sh.part(poly([(X(-58), 86), (X(58), 86), (X(48), 146), (X(-48), 146)]), OLIVE)
    sh.flat(line([(CX, 90), (CX, 144)], 1.4), LINE)
    for s in (-1, 1):
        ax = X(s * 80)
        sh.part(ellipse((ax - 11, 140, ax + 11, 160)), GUN_DARK)
        sh.part(rrect((ax - 17, 150, ax + 17, 188), 9), OLIVE)
        sh.part(rrect((ax - 15, 184, ax + 15, 206), 8), RUBBER)
    # power cell housing: a backpack with the cell port and two exhausts
    sh.part(rrect((X(-40), 84, X(40), 150), 12), GUN)
    sh.part(rrect((CX - 15, 96, CX + 15, 140), 7), RUBBER, light=0.1)
    sh.glow(rrect((CX - 8, 104, CX + 8, 132), 4), CORE, radius=4)
    sh.flat(line([(CX - 8, 113), (CX + 8, 113)], 1.0), (60, 120, 140))
    sh.flat(line([(CX - 8, 123), (CX + 8, 123)], 1.0), (60, 120, 140))
    for s in (-1, 1):
        sh.part(rrect((X(s * 28) - 7, 74, X(s * 28) + 7, 98), 5), GUN_DARK)     # exhaust stacks
        sh.part(ellipse((X(s * 28) - 6, 72, X(s * 28) + 6, 80)), RUBBER, outline=False)
    rivets(sh, [(X(-32), 140), (X(32), 140), (X(-32), 94), (X(32), 94)])
    for s in (-1, 1):
        px = X(s * 80)
        sh.part(rrect((px - 30, 68, px + 30, 112), 18), OLIVE)
        sh.flat(rrect((px - 30, 92, px + 30, 98), 0), STRIPE)
    sh.part(rrect((CX - 34, 26, CX + 34, 92), 26), OLIVE)
    sh.flat(line([(CX, 28), (CX, 84)], 2.0), OLIVE_DARK)
    for y in (66, 72, 78):                                                          # rear vents
        sh.flat(line([(CX - 16, y), (CX + 16, y)], 1.4), LINE)


def side(sh, w, visor):
    """East: the suit in profile, facing right."""
    d = 0.75 + 0.25 * w      # body types change depth less than width

    def X(off):
        return CX + off * d

    sh.part(rrect((X(-24), 150, X(8), 222), 8), GUN_DARK)                           # far leg
    sh.part(rrect((X(-26), 214, X(16), 238), 7), RUBBER)
    sh.part(rrect((X(-66), 82, X(-26), 152), 12), GUN)                              # backpack
    sh.part(rrect((X(-62), 96, X(-44), 140), 6), RUBBER, light=0.1)
    sh.glow(rrect((X(-58), 104, X(-48), 132), 3), CORE, radius=3)
    sh.part(rrect((X(-58), 70, X(-46), 96), 5), GUN_DARK)                          # exhaust stack
    sh.part(rrect((X(-34), 136, X(30), 162), 9), GUN_DARK)                          # hips
    sh.part(poly([(X(-36), 84), (X(34), 84), (X(40), 128), (X(28), 146), (X(-30), 146)]), OLIVE)  # torso
    sh.flat(line([(X(-24), 132), (X(30), 132)], 1.2), LINE)
    sh.flat(line([(X(-24), 140), (X(28), 140)], 1.2), LINE)
    sh.part(rrect((X(-6), 150, X(26), 196), 8), GUN)                                # near thigh
    sh.part(rrect((X(-6), 186, X(28), 224), 8), OLIVE)                              # near shin
    sh.part(ellipse((X(10), 176, X(32), 200)), OLIVE_DARK)                         # knee cap
    sh.part(rrect((X(-8), 214, X(40), 238), 7), RUBBER)                             # near boot
    sh.flat(line([(X(-6), 231), (X(38), 231)], 1.4), EDGE)
    # helmet in profile, the breather jutting forward
    sh.part(rrect((X(-22), 80, X(26), 100), 8), GUN_DARK)                           # gorget
    sh.part(rrect((X(-26), 26, X(34), 94), 26), OLIVE)
    sh.part(poly([(X(18), 66), (X(44), 70), (X(40), 90), (X(14), 92)]), GUN)       # breather
    for gx in (24, 30, 36):
        sh.flat(line([(X(gx), 72), (X(gx - 1), 88)], 1.5), EDGE)
    sh.part(rrect((X(16), 46, X(40), 64), 7), RUBBER, light=0.1)
    if visor:
        sh.glow(rrect((X(22), 51, X(40), 59), 3), VISOR_ON)
    else:
        sh.flat(rrect((X(22), 51, X(40), 59), 3), VISOR_OFF)
    sh.part(ellipse((X(-14), 56, X(4), 74)), GUN_DARK)                             # ear vent
    sh.flat(line([(X(-20), 32), (X(10), 28)], 2.0), OLIVE_DARK)
    # arm hangs in front of the torso
    sh.part(rrect((X(-12), 96, X(18), 150), 9), GUN)
    sh.part(ellipse((X(-8), 140, X(14), 160)), GUN_DARK)
    sh.part(rrect((X(-12), 150, X(22), 188), 9), OLIVE)
    sh.flat(line([(X(-8), 168), (X(18), 168)], 1.2), LINE)
    sh.part(rrect((X(-10), 184, X(24), 206), 8), RUBBER)
    sh.part(rrect((X(-28), 68, X(30), 112), 18), OLIVE)                             # pauldron
    sh.flat(rrect((X(-28), 92, X(30), 98), 0), STRIPE)
    rivets(sh, [(X(-16), 80), (X(18), 80)])


def suit(direction, w=1.0, visor=True):
    sh = Sheet()
    {"south": lambda: front(sh, w, visor),
     "north": lambda: back(sh, w),
     "east": lambda: side(sh, w, visor)}[direction]()
    return sh.image()


# ----------------------------------------------------------------------- outputs

def save(img, *parts):
    path = os.path.join(ROOT, *parts)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    print("wrote", os.path.relpath(path, ROOT))


def standing():
    """The empty suit as it stands on the map: visor dark, a shadow on the floor."""
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse((44, 220, 212, 248), fill=(0, 0, 0, 120))
    img = Image.alpha_composite(img, shadow.filter(ImageFilter.GaussianBlur(5)))
    return Image.alpha_composite(img, suit("south", visor=False))


def icon():
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    img.alpha_composite(suit("south", visor=False).resize((212, 212), Image.LANCZOS), (-14, 30))
    arrow = Sheet()
    arrow.part(poly([(150, 112), (206, 112), (206, 88), (248, 128), (206, 168), (206, 144), (150, 144)]),
               (236, 236, 228), light=0.2)
    img.alpha_composite(arrow.image())
    return img.resize((128, 128), Image.LANCZOS)


def preview():
    img = Image.new("RGBA", (640, 360), (40, 44, 42, 255))
    d = ImageDraw.Draw(img)
    for i in range(0, 640, 40):
        d.line((i, 0, i, 360), fill=(48, 52, 50, 255))
    for i in range(0, 360, 40):
        d.line((0, i, 640, i), fill=(48, 52, 50, 255))
    img.alpha_composite(standing().resize((300, 300), Image.LANCZOS), (40, 40))
    img.alpha_composite(suit("east").resize((300, 300), Image.LANCZOS), (300, 40))
    return img.convert("RGB")


def main():
    for body, w in BODY_WIDTH.items():
        for direction in ("south", "north", "east"):
            save(suit(direction, w), "Textures", "Things", "Pawn", "PowerSuit",
                 "PowerSuitFrame_%s_%s.png" % (body, direction))
    save(standing(), "Textures", "Things", "Item", "PowerSuit", "PowerSuitFrame.png")
    save(icon(), "Textures", "UI", "Commands", "RPS_ExitPowerSuit.png")
    save(preview(), "About", "Preview.png")


if __name__ == "__main__":
    main()
