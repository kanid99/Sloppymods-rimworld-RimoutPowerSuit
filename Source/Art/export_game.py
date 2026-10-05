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
    """args: Suit=dir (every piece, bare arms), Suit/L/weapon=dir, Suit/R/weapon=dir (one arm with a weapon)
    or Suit/Body/pack=dir (the body with a backpack fitted)"""
    root = sys.argv[1]
    layers = {}                                   # (suit, texture name, facing) -> (tex, mask)
    for arg in sys.argv[2:]:
        key, out = arg.split('=', 1)
        parts = key.split('/')
        if len(parts) == 1:
            for p in PIECES:
                for f in FACINGS:
                    layers[(parts[0], p, f)] = load(out, p, f)
        elif parts[1] == 'Body':                  # Suit/Body/key: the body with another backpack
            for f in FACINGS:
                layers[(parts[0], f'Body_{parts[2]}', f)] = load(out, 'Body', f)
        else:
            suit, side, weapon = parts
            for f in FACINGS:
                layers[(suit, f'Arm{side}_{weapon}', f)] = load(out, f'Arm{side}', f)
    # one square crop, centred on the canvas centre, holding every piece of every suit
    half = 0
    c = kit.C / 2
    for t, _ in layers.values():
        bb = t.getbbox()
        if bb:
            half = max(half, c - bb[0], bb[2] - c, c - bb[1], bb[3] - c)
    half = int(np.ceil(half / 8) * 8)
    box = (int(c - half), int(c - half), int(c + half), int(c + half))
    side = round(2 * half * SCALE)
    draw = kit.DRAW_SIZE * 2 * half / kit.C
    for (s, name, f), (t, m) in layers.items():
        pawn_dir = f'{root}/Textures/Things/Pawn/PowerSuit/{s}'
        os.makedirs(pawn_dir, exist_ok=True)
        t.crop(box).resize((side, side), Image.LANCZOS).save(f'{pawn_dir}/{name}_{f}.png')
        m.crop(box).resize((side, side), Image.LANCZOS).save(f'{pawn_dir}/{name}_{f}m.png')
    suits = sorted({s for s, _, _ in layers})
    for s in suits:
        if (s, 'Body', 'south') not in layers:
            continue
        # the standing suit's icon: the south pieces stacked in draw order (the game draws the pieces itself)
        tex = Image.new('RGBA', (kit.C, kit.C)); msk = Image.new('RGBA', (kit.C, kit.C))
        for p in kit.ORDER['south']:
            t, m = layers[(s, p, 'south')]
            tex.alpha_composite(t)
            a = np.array(t)[..., 3:4] / 255.0
            mm = np.array(msk).astype(float); mm[..., :3] = mm[..., :3] * (1 - a) + np.array(m)[..., :3] * a
            mm[..., 3] = np.maximum(mm[..., 3], np.array(t)[..., 3]); msk = Image.fromarray(mm.astype(np.uint8))
        item_dir = f'{root}/Textures/Things/Item/PowerSuit'
        os.makedirs(item_dir, exist_ok=True)
        tex.crop(box).resize((side, side), Image.LANCZOS).save(f'{item_dir}/{s}.png')
        msk.crop(box).resize((side, side), Image.LANCZOS).save(f'{item_dir}/{s}_m.png')
    # arm module items: the left arm facing south, cropped to itself
    for (s, name, f), (t, m) in layers.items():
        if f != 'south' or not name.startswith('ArmL_'):
            continue
        bb = t.getbbox(); w, h = bb[2] - bb[0], bb[3] - bb[1]; n = max(w, h) + 16
        icon = Image.new('RGBA', (n, n)); icon.alpha_composite(t.crop(bb), ((n - w) // 2, (n - h) // 2))
        arm_dir = f'{root}/Textures/Things/Item/PowerSuit/Arms'
        os.makedirs(arm_dir, exist_ok=True)
        icon.resize((128, 128), Image.LANCZOS).save(f'{arm_dir}/{s}_{name[5:]}.png')
    # backpack items: the body with that pack, from behind, cropped to itself
    for (s, name, f), (t, m) in layers.items():
        if f != 'north' or not name.startswith('Body_'):
            continue
        bb = t.getbbox(); w, h = bb[2] - bb[0], bb[3] - bb[1]; n = max(w, h) + 16
        icon = Image.new('RGBA', (n, n)); icon.alpha_composite(t.crop(bb), ((n - w) // 2, (n - h) // 2))
        pack_dir = f'{root}/Textures/Things/Item/PowerSuit/Packs'
        os.makedirs(pack_dir, exist_ok=True)
        icon.resize((128, 128), Image.LANCZOS).save(f'{pack_dir}/{s}_{name[5:]}.png')
    print(f'texture {side}px, drawSize ({draw:.3f},{draw:.3f})')


if __name__ == '__main__':
    main()
