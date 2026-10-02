"""Turns the Nano Banana suit paintings into RimWorld textures.

    python3 Source/Art/process_nano.py

Source/Art/nano/{south,east,north}.png are the paintings (made with Source/Art/nano.py:
Nano Banana Pro, an original design - a diving-helmet industrial suit - with the VFE
Pirates warcasket sprites given only for format and style), on white. This script:

- cuts each one out of its white background,
- scales each so the figure is the same height, feet - well, hip plates - on the same
  line, centred, on the 256px canvas of the pawn's 1.5-tile body mesh,
- writes a colour mask beside it (_southm / _eastm / _northm, and _m for the standing
  suit) whose red channel marks the light-grey armour plates: with the CutoutComplex
  shader the game tints only those with the suit's colour, and the gunmetal frame, brown
  hoses, lamp and lenses keep their own colours,
- writes the standing suit, the "Climb out" icon and the mod preview from them.
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = os.path.join(ROOT, "Source", "Art", "nano")
S = 256
FIG_H = 244          # figure height on the canvas, helmet top to the bottom of the hip plates
BOTTOM = 252         # where the hip plates end
MAX_W = 250
OUTER = 1.5        # extra silhouette outline, output pixels

OLIVE = (0.58, 0.60, 0.42)
DESERT = (0.78, 0.68, 0.50)
GUNMETAL = (0.56, 0.58, 0.60)


def cut_out(rgb):
    """Alpha for the figure: everything but the white background (white regions touching
    the border, or large pure-white pockets enclosed by the figure)."""
    lum = rgb.mean(2)
    spread = rgb.max(2) - rgb.min(2)
    white = (rgb.min(2) > 226) & (spread < 22)
    labels, n = ndimage.label(white)
    border = set(np.unique(np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]])))
    sizes = ndimage.sum(np.ones_like(lum), labels, range(n + 1))
    bg = np.zeros_like(white)
    for i in range(1, n + 1):
        if i in border or sizes[i] > 0.002 * white.size:
            bg |= labels == i
    # keep the black outline: grow the background by nothing, but drop stray specks
    fig = ~bg
    fig = ndimage.binary_opening(fig, iterations=1)
    return fig


def plate_mask(rgb):
    """1 on the light grey armour plates, 0 on the dark frame, the coloured parts (visor,
    lamp, hazard stripes, cells) and the black lines. Thresholds are soft and the result is
    median-filtered, so compression noise in the painting doesn't speckle the paint job."""
    lum = rgb.mean(2)
    spread = rgb.max(2) - rgb.min(2)
    neutral = np.clip((48 - spread) / 14, 0, 1)
    light = np.clip((lum - 118) / 20, 0, 1)
    m = neutral * light
    return ndimage.median_filter(m, size=7)


def fit(name):
    rgb = np.array(Image.open(os.path.join(SRC, name + ".png")).convert("RGB")).astype(np.float32)
    fig = cut_out(rgb)
    mask = plate_mask(rgb) * fig
    ys, xs = np.nonzero(fig)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    scale = min(FIG_H / (y1 - y0), MAX_W / (x1 - x0))
    # a heavier silhouette outline, as the warcaskets have: grow the figure by a couple of
    # output pixels of black
    ring = ndimage.binary_dilation(fig, iterations=max(1, round(OUTER / scale))) & ~fig
    rgb[ring] = 8
    fig = fig | ring
    ys, xs = np.nonzero(fig)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    scale = min(FIG_H / (y1 - y0), MAX_W / (x1 - x0))
    w, h = max(1, round((x1 - x0) * scale)), max(1, round((y1 - y0) * scale))
    # black under the background, so scaling down blends edges into the outline, not white
    rgb[~fig] = 0
    a = (fig * 255).astype(np.uint8)
    crop = lambda arr: arr[y0:y1, x0:x1]
    body = Image.fromarray(np.dstack([crop(rgb).astype(np.uint8), crop(a)]), "RGBA").resize((w, h), Image.LANCZOS)
    m = Image.fromarray(crop((mask * 255).astype(np.uint8)), "L").resize((w, h), Image.LANCZOS)
    left, top = (S - w) // 2, BOTTOM - h
    tex = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    tex.alpha_composite(body, (left, top))
    red = Image.new("L", (S, S), 0)
    red.paste(m, (left, top))
    alpha = tex.split()[3]
    zero = Image.new("L", (S, S), 0)
    return tex, Image.merge("RGBA", (red, zero, zero, alpha))


def tint(tex, mask, color):
    """What CutoutComplex does: plates multiplied by the colour, the rest left alone."""
    t = np.array(tex, np.float32)
    m = np.array(mask, np.float32)[..., :1] / 255
    t[..., :3] *= (1 - m) + m * np.array(color, np.float32)
    return Image.fromarray(t.astype(np.uint8), "RGBA")


def save(img, *parts):
    path = os.path.join(ROOT, *parts)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, optimize=True)
    print("wrote", os.path.relpath(path, ROOT))


def main():
    views = {d: fit(d) for d in ("south", "east", "north")}
    for d, (tex, mask) in views.items():
        save(tex, "Textures", "Things", "Pawn", "PowerSuit", "PowerSuitFrame_%s.png" % d)
        save(mask, "Textures", "Things", "Pawn", "PowerSuit", "PowerSuitFrame_%sm.png" % d)

    # the standing suit: the front view with a shadow on the floor (the shadow is black in
    # the mask, so it never takes the paint)
    tex, mask = views["south"]
    shadow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse((40, 232, 216, 256), fill=(0, 0, 0, 110))
    standing = Image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(5)), tex)
    r, g, b, _ = mask.split()
    save(standing, "Textures", "Things", "Item", "PowerSuit", "PowerSuitFrame.png")
    save(Image.merge("RGBA", (r, g, b, standing.split()[3])), "Textures", "Things", "Item", "PowerSuit",
         "PowerSuitFrame_m.png")

    icon = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    icon.alpha_composite(tint(tex, mask, OLIVE).resize((210, 210), Image.LANCZOS), (-8, 30))
    d = ImageDraw.Draw(icon)
    arrow = [(156, 112), (206, 112), (206, 86), (250, 128), (206, 170), (206, 144), (156, 144)]
    d.polygon(arrow, fill=(236, 236, 228, 255), outline=(10, 10, 10, 255), width=5)
    save(icon.resize((128, 128), Image.LANCZOS), "Textures", "UI", "Commands", "RPS_ExitPowerSuit.png")

    preview = Image.new("RGBA", (640, 360), (40, 44, 42, 255))
    d = ImageDraw.Draw(preview)
    for i in range(0, 640, 40):
        d.line((i, 0, i, 360), fill=(48, 52, 50, 255))
    for i in range(0, 360, 40):
        d.line((0, i, 640, i), fill=(48, 52, 50, 255))
    east_tex, east_mask = views["east"]
    north_tex, north_mask = views["north"]
    preview.alpha_composite(tint(north_tex, north_mask, DESERT).resize((220, 220), Image.LANCZOS), (0, 120))
    preview.alpha_composite(tint(tex, mask, OLIVE).resize((300, 300), Image.LANCZOS), (170, 40))
    preview.alpha_composite(tint(east_tex, east_mask, GUNMETAL).resize((220, 220), Image.LANCZOS), (430, 120))
    save(preview.convert("RGB"), "About", "Preview.png")


if __name__ == "__main__":
    main()
