"""Art for the power suit frame, drawn in code with Pillow and numpy.

    python3 Source/Art/make_suit_art.py

Writes the worn suit in three directions (Textures/Things/Pawn/PowerSuit; the game mirrors
east for west), the standing suit (Textures/Things/Item/PowerSuit), the "Climb out" command
icon and About/Preview.png.

Style follows the warcaskets of Vanilla Factions Expanded - Pirates, so the suits sit
beside them: chunky plates with heavy black outlines, a few flat grey tones with a soft
top-down gradient, dark vent slots and round ports rather than fine detail. The textures
are greyscale - the game tints them with the suit's colour (CompColorable), so one drawing
serves every paint job. One drawing also serves every body type (VEF's isUnifiedApparel),
as the warcaskets' do.

Each view is built from named pieces (shell, chest, helmet, ...) so later work - the suit
opening around its pilot - can draw them separately. Shape coordinates are in 256px units
on the body's 1.5-tile mesh; (128, 128) is the centre of the pawn's body and the head sits
about 58px above it.
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
K = 4                 # supersampling
S = 256               # output size
N = S * K
CX = 128

# Greyscale tones, matched to the warcasket textures (their plates sit at ~205-255, mid
# panels ~150, recesses ~50). The game multiplies these by the suit's colour.
WHITE = (240, 240, 240)
LIGHT = (208, 208, 208)
MID = (164, 164, 164)
DARK = (104, 104, 104)
RECESS = (54, 54, 54)
EDGE = (12, 12, 12)

OUTLINE = 4.5         # outline thickness, output pixels

# Paint jobs for previews; the same colours seed the def's colorGenerator.
OLIVE = (0.58, 0.60, 0.42)
DESERT = (0.78, 0.68, 0.50)
GUNMETAL = (0.56, 0.58, 0.60)
RUST = (0.66, 0.40, 0.32)


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

    def part(self, draw_fn, tone, light=0.16, outline=True, rim=True, weight=OUTLINE):
        """A plate: soft top-down gradient, rim-lit top edge, shaded lower edge, outlined."""
        m = self.mask(draw_fn)
        if not m.any():
            return m
        if outline:
            o = _dilate(m, weight * K / 2) & ~m
            self.rgb[o] = EDGE
            self.alpha |= o
        ys, xs = np.nonzero(m)
        y0, y1 = ys.min(), ys.max()
        ny = (self.yy - y0) / max(1, y1 - y0)
        f = 1 + light * (0.5 - ny)
        if rim:
            off = 4 * K
            f = f + 0.08 * (m & ~_shift(m, off // 2, off))      # lit upper edge
            f = f - 0.14 * (m & ~_shift(m, 0, -off))            # shaded lower edge
        col = np.clip(np.array(tone, np.float32)[None, None, :] * f[..., None], 0, 255)
        self.rgb[m] = col[m]
        self.alpha |= m
        return m

    def flat(self, draw_fn, tone):
        """Unshaded detail painted only onto what is already drawn (slots, seams)."""
        m = self.mask(draw_fn) & self.alpha
        self.rgb[m] = tone
        return m

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


def chord(box, start, end):
    return lambda d: d.chord([k(v) for v in box], start, end, fill=255)


def slot(sh, x0, y0, x1, y1):
    """A dark vent slot, as on the warcaskets."""
    sh.flat(rrect((x0, y0, x1, y1), (y1 - y0) / 2), RECESS)


def port(sh, cx, cy, r, tone=MID):
    """A round port: a ring around a dark centre."""
    sh.part(ellipse((cx - r, cy - r, cx + r, cy + r)), tone, rim=False)
    sh.flat(ellipse((cx - r * 0.55, cy - r * 0.55, cx + r * 0.55, cy + r * 0.55)), RECESS)


def both(*fns):
    def draw(d):
        for fn in fns:
            fn(d)
    return draw


def dome(x0, x1, top, bottom, chin):
    """A helmet: round crown, sides tapering in to the chin."""
    w = x1 - x0
    return both(ellipse((x0, top, x1, top + w)),
                poly([(x0, top + w * 0.5), (x1, top + w * 0.5), (x1 - chin, bottom), (x0 + chin, bottom)]),
                rrect((x0 + chin - 4, bottom - 24, x1 - chin + 4, bottom), 12))


def torso(x0, x1, top, waist_in):
    """A chest shell: broad shoulders, tapering to the waist."""
    return both(rrect((x0, top, x1, top + 64), 40),
                poly([(x0, top + 30), (x1, top + 30), (x1 - waist_in, 206), (x0 + waist_in, 206)]),
                rrect((x0 + waist_in - 6, 180, x1 - waist_in + 6, 210), 14))


HELMET_WEIGHT = 6.0   # the helmet's outline is heavier, as on the warcaskets


# ----------------------------------------------------------------------- the suit

def skirt(sh, x_of, back=False):
    """Hip plates hanging from the waist - the bottom of the silhouette."""
    sh.part(rrect((x_of(-44), 196, x_of(44), 222), 8), RECESS, light=0)        # thigh gap
    for s in (-1, 1):
        sh.part(poly([(x_of(s * 30), 198), (x_of(s * 74), 192), (x_of(s * 70), 244), (x_of(s * 34), 250)]),
                MID if back else LIGHT)
    sh.part(poly([(x_of(-24), 202), (x_of(24), 202), (x_of(20), 246), (x_of(-20), 246)]), MID if back else WHITE)


def pauldron(sh, cx, back=False):
    """A big rounded shoulder plate with a trim band round its lower edge and a bolt."""
    sh.part(rrect((cx - 37, 64, cx + 37, 152), 30), WHITE)
    sh.part(chord((cx - 37, 92, cx + 37, 160), 0, 180), MID, rim=False)         # lower trim band
    sh.flat(rrect((cx - 37, 124, cx + 37, 129), 2), DARK)
    if not back:
        port(sh, cx, 100, 10, LIGHT)


def helmet_front(sh):
    """The T-51 style helmet: dome, two round eye lenses, a breather snout, cheek filters."""
    sh.part(dome(CX - 52, CX + 52, 8, 128, 14), WHITE, weight=HELMET_WEIGHT)     # dome
    sh.part(rrect((CX - 8, 6, CX + 8, 40), 6), LIGHT)                             # crest
    sh.part(poly([(CX - 42, 48), (CX + 42, 48), (CX + 38, 76), (CX - 38, 76)]), DARK, light=0)  # brow
    for s in (-1, 1):                                                             # eye lenses
        ex = CX + s * 21
        sh.part(ellipse((ex - 15, 50, ex + 15, 80)), RECESS, light=0, rim=False)
        sh.flat(ellipse((ex - 8, 56, ex - 1, 63)), (120, 120, 120))              # glint
    for s in (-1, 1):                                                             # cheek filters
        port(sh, CX + s * 44, 98, 15, MID)
    sh.part(poly([(CX - 26, 82), (CX + 26, 82), (CX + 20, 124), (CX - 20, 124)]), MID)  # snout
    for gx in (-12, -4, 4, 12):
        slot(sh, CX + gx - 2, 90, CX + gx + 2, 116)


def helmet_back(sh):
    sh.part(dome(CX - 52, CX + 52, 8, 128, 14), WHITE, weight=HELMET_WEIGHT)
    sh.part(rrect((CX - 8, 6, CX + 8, 100), 6), LIGHT)                            # crest runs back
    sh.part(poly([(CX - 50, 96), (CX + 50, 96), (CX + 38, 126), (CX - 38, 126)]), MID)  # neck guard
    for y in (104, 114):
        slot(sh, CX - 26, y, CX + 26, y + 5)


def south(sh, pieces=("shell", "chest", "pauldrons", "helmet")):
    x = lambda off: CX + off
    if "shell" in pieces:
        skirt(sh, x)
        sh.part(rrect((CX - 34, 98, CX + 34, 132), 10), RECESS, light=0)            # collar
        sh.part(torso(CX - 78, CX + 78, 92, 22), LIGHT)                             # torso shell
        sh.part(rrect((CX - 50, 180, CX + 50, 200), 9), MID)                        # abdomen band
    if "chest" in pieces:
        sh.part(poly([(CX - 70, 110), (CX + 70, 110), (CX + 56, 162), (CX, 176), (CX - 56, 162)]), WHITE)
        sh.flat(rrect((CX - 3, 114, CX + 3, 170), 2), LIGHT)                        # centre ridge
        for s in (-1, 1):
            for i in range(2):
                slot(sh, CX + s * 30 - 14, 132 + i * 12, CX + s * 30 + 14, 137 + i * 12)
    if "pauldrons" in pieces:
        for cx in (CX - 82, CX + 82):
            pauldron(sh, cx)
    if "helmet" in pieces:
        helmet_front(sh)


def north(sh):
    x = lambda off: CX + off
    skirt(sh, x, back=True)
    sh.part(torso(CX - 78, CX + 78, 92, 22), LIGHT)
    sh.part(rrect((CX - 50, 184, CX + 50, 202), 8), MID)
    # power cell housing: a backpack with the cell's end cap and two exhaust stacks
    sh.part(rrect((CX - 48, 110, CX + 48, 192), 18), MID)
    for s in (-1, 1):
        sh.part(rrect((CX + s * 34 - 9, 92, CX + s * 34 + 9, 132), 6), DARK)
        sh.flat(ellipse((CX + s * 34 - 6, 94, CX + s * 34 + 6, 102)), RECESS)
    sh.part(ellipse((CX - 26, 126, CX + 26, 178)), LIGHT)
    sh.part(ellipse((CX - 17, 135, CX + 17, 169)), RECESS, light=0, rim=False)
    sh.flat(ellipse((CX - 7, 145, CX + 7, 159)), DARK)
    for cx in (CX - 82, CX + 82):
        pauldron(sh, cx, back=True)
    helmet_back(sh)


def east(sh):
    """Facing right. The pilot's back - and the power cell housing - is to the left."""
    # backpack, behind everything
    sh.part(rrect((CX - 84, 104, CX - 30, 196), 16), MID)
    sh.part(rrect((CX - 72, 88, CX - 52, 128), 6), DARK)                           # exhaust stack
    sh.part(ellipse((CX - 94, 128, CX - 62, 172)), LIGHT)                         # cell end cap
    sh.part(ellipse((CX - 88, 136, CX - 68, 164)), RECESS, light=0, rim=False)
    # hips and torso in profile
    sh.part(rrect((CX - 44, 196, CX + 40, 222), 8), RECESS, light=0)
    sh.part(poly([(CX - 46, 198), (CX + 6, 196), (CX + 4, 248), (CX - 40, 250)]), MID)
    sh.part(poly([(CX - 6, 198), (CX + 50, 194), (CX + 48, 244), (CX - 2, 248)]), LIGHT)
    sh.part(both(rrect((CX - 58, 92, CX + 66, 156), 40),
                 poly([(CX - 58, 122), (CX + 66, 122), (CX + 50, 206), (CX - 44, 206)]),
                 rrect((CX - 50, 178, CX + 56, 210), 14)), LIGHT)
    sh.part(poly([(CX + 8, 108), (CX + 70, 112), (CX + 64, 170), (CX + 14, 178)]), WHITE)  # chest plate
    for i in range(3):
        slot(sh, CX + 30, 126 + i * 11, CX + 58, 131 + i * 11)
    sh.part(rrect((CX - 36, 182, CX + 50, 200), 8), MID)
    # helmet in profile: the snout juts forward
    sh.part(dome(CX - 46, CX + 54, 8, 128, 10), WHITE, weight=HELMET_WEIGHT)
    sh.part(rrect((CX - 40, 6, CX + 20, 22), 8), LIGHT)                          # crest
    sh.part(poly([(CX + 20, 48), (CX + 56, 52), (CX + 54, 78), (CX + 18, 76)]), DARK, light=0)  # brow
    sh.part(ellipse((CX + 30, 52, CX + 56, 80)), RECESS, light=0, rim=False)      # eye lens
    sh.flat(ellipse((CX + 36, 57, CX + 43, 64)), (120, 120, 120))
    sh.part(poly([(CX + 24, 84), (CX + 70, 92), (CX + 64, 124), (CX + 20, 124)]), MID)  # snout
    for gx in (34, 44, 54):
        slot(sh, gx + CX - 2, 96, gx + CX + 2, 118)
    port(sh, CX - 6, 92, 17, MID)                                                 # cheek filter
    # near pauldron over the shoulder
    pauldron(sh, CX - 3)


def suit(direction):
    sh = Sheet()
    {"south": lambda: south(sh), "north": lambda: north(sh), "east": lambda: east(sh)}[direction]()
    return sh.image()


# ----------------------------------------------------------------------- outputs

def tint(img, color):
    """What the game does with the greyscale texture: multiply by the suit's colour."""
    arr = np.array(img, np.float32)
    arr[..., :3] *= np.array(color, np.float32)
    return Image.fromarray(arr.astype(np.uint8), "RGBA")


def save(img, *parts):
    path = os.path.join(ROOT, *parts)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    print("wrote", os.path.relpath(path, ROOT))


def standing():
    """The empty suit as it stands on the map, with a shadow on the floor."""
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse((36, 222, 220, 254), fill=(0, 0, 0, 120))
    img = Image.alpha_composite(img, shadow.filter(ImageFilter.GaussianBlur(5)))
    return Image.alpha_composite(img, suit("south"))


def icon():
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    img.alpha_composite(tint(suit("south"), OLIVE).resize((220, 220), Image.LANCZOS), (-16, 24))
    arrow = Sheet()
    arrow.part(poly([(150, 112), (206, 112), (206, 88), (248, 128), (206, 168), (206, 144), (150, 144)]),
               (236, 236, 228), light=0.1)
    img.alpha_composite(arrow.image())
    return img.resize((128, 128), Image.LANCZOS)


def preview():
    img = Image.new("RGBA", (640, 360), (40, 44, 42, 255))
    d = ImageDraw.Draw(img)
    for i in range(0, 640, 40):
        d.line((i, 0, i, 360), fill=(48, 52, 50, 255))
    for i in range(0, 360, 40):
        d.line((0, i, 640, i), fill=(48, 52, 50, 255))
    img.alpha_composite(tint(standing(), DESERT).resize((230, 230), Image.LANCZOS), (-10, 110))
    img.alpha_composite(tint(standing(), OLIVE).resize((300, 300), Image.LANCZOS), (170, 40))
    img.alpha_composite(tint(suit("east"), GUNMETAL).resize((230, 230), Image.LANCZOS), (420, 110))
    return img.convert("RGB")


def main():
    for direction in ("south", "north", "east"):
        save(suit(direction), "Textures", "Things", "Pawn", "PowerSuit", "PowerSuitFrame_%s.png" % direction)
    save(standing(), "Textures", "Things", "Item", "PowerSuit", "PowerSuitFrame.png")
    save(icon(), "Textures", "UI", "Commands", "RPS_ExitPowerSuit.png")
    save(preview(), "About", "Preview.png")


if __name__ == "__main__":
    main()
