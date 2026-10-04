"""Export suit-kit output as the mod's game textures (run from Source/Art).

    python3 export_game.py <mod root> NAME=kit_out_dir [NAME=kit_out_dir ...]

For each suit NAME (e.g. Bulwark=kit/out_bulwark_bare) it writes
  Textures/Things/Pawn/PowerSuit/<NAME>/<Piece>_<south|east|north>.png (+ m masks)
      one render node per piece (Body, Legs, ArmL, ArmR, Helmet); the game mirrors east for west
  Textures/Things/Item/PowerSuit/<NAME>.png (+ _m): the standing suit, all pieces facing south

All textures share one canvas, cropped square around the kit canvas centre (the pawn's draw
position) to the area any suit uses, and scaled by SCALE. The helmet is stored where it is shown
(the kit keeps it HEAD px lower for a head-anchored node; the game draws it from the body node).
Prints the drawSize the defs need.
"""
import os
import sys

import numpy as np
from PIL import Image

import suit_kit as kit

SCALE = 0.5
PIECES = ('Legs', 'Body', 'ArmL', 'ArmR', 'Helmet')
FACINGS = ('south', 'east', 'north')


def paintable(t, m):
    """The side and back paintings are lilac-tinted, so the kit's mask (near-neutral greys only)
    misses their plates and they would stay purple while the front takes the suit's colour.
    Lilac plate pixels join the mask, and every masked pixel is made neutral grey so the colour
    tints it cleanly. Lamps, visors, glows, hazard bands and the dark frame keep their colour."""
    a = np.array(t).astype(float); mk = np.array(m).astype(float)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]; lum = a[..., :3].mean(2)
    lilac = (b >= g + 6) & (r >= g + 3) & (np.abs(r - b) < 45) & (lum > 72) & (a[..., 3] > 100)
    soft = np.clip((lum - 72) / 18, 0, 1) * lilac
    red = np.maximum(mk[..., 0] / 255, soft)
    from scipy import ndimage
    red = ndimage.median_filter(red, size=5)
    grey = lum[..., None] * np.ones(3)
    a[..., :3] = a[..., :3] * (1 - red[..., None]) + grey * red[..., None]
    mk[..., 0] = red * 255
    return Image.fromarray(a.astype(np.uint8), 'RGBA'), Image.fromarray(mk.astype(np.uint8), 'RGBA')


def load(out, piece, facing):
    t = Image.open(f'{out}/{piece}_{facing}.png').convert('RGBA')
    m = Image.open(f'{out}/{piece}_{facing}m.png').convert('RGBA')
    t, m = paintable(t, m)
    if piece == 'Helmet':                       # back to where it is shown
        for name in ('t', 'm'):
            im = t if name == 't' else m
            n = Image.new('RGBA', im.size); n.paste(im, (0, -kit.HEAD))
            if name == 't': t = n
            else: m = n
    return t, m


def main():
    root = sys.argv[1]
    suits = dict(a.split('=', 1) for a in sys.argv[2:])
    layers = {s: {(p, f): load(o, p, f) for p in PIECES for f in FACINGS} for s, o in suits.items()}
    # one square crop, centred on the canvas centre, holding every piece of every suit
    half = 0
    c = kit.C / 2
    for d in layers.values():
        for t, _ in d.values():
            bb = t.getbbox()
            if bb:
                half = max(half, c - bb[0], bb[2] - c, c - bb[1], bb[3] - c)
    half = int(np.ceil(half / 8) * 8)
    box = (int(c - half), int(c - half), int(c + half), int(c + half))
    side = round(2 * half * SCALE)
    draw = kit.DRAW_SIZE * 2 * half / kit.C
    for s, d in layers.items():
        pawn_dir = f'{root}/Textures/Things/Pawn/PowerSuit/{s}'
        os.makedirs(pawn_dir, exist_ok=True)
        for (p, f), (t, m) in d.items():
            t.crop(box).resize((side, side), Image.LANCZOS).save(f'{pawn_dir}/{p}_{f}.png')
            m.crop(box).resize((side, side), Image.LANCZOS).save(f'{pawn_dir}/{p}_{f}m.png')
        # the standing suit: the south pieces stacked in draw order
        tex = Image.new('RGBA', (kit.C, kit.C)); msk = Image.new('RGBA', (kit.C, kit.C))
        for p in kit.ORDER['south']:
            t, m = d[(p, 'south')]
            tex.alpha_composite(t)
            a = np.array(t)[..., 3:4] / 255.0
            mm = np.array(msk).astype(float); mm[..., :3] = mm[..., :3] * (1 - a) + np.array(m)[..., :3] * a
            mm[..., 3] = np.maximum(mm[..., 3], np.array(t)[..., 3]); msk = Image.fromarray(mm.astype(np.uint8))
        item_dir = f'{root}/Textures/Things/Item/PowerSuit'
        os.makedirs(item_dir, exist_ok=True)
        tex.crop(box).resize((side, side), Image.LANCZOS).save(f'{item_dir}/{s}.png')
        msk.crop(box).resize((side, side), Image.LANCZOS).save(f'{item_dir}/{s}_m.png')
    print(f'texture {side}px, drawSize ({draw:.3f},{draw:.3f})')


if __name__ == '__main__':
    main()
