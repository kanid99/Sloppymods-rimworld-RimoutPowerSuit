"""Suit kit: turn a suit's parts into game textures for every piece and facing, with paint masks and a preview.

Reusable for every suit: a suit is a SPEC (below) naming its part images; the rig places them on one shared
canvas so the separate pieces line up when the game stacks them.

Canvas: 768 x 768 per texture. 2 canvas px = 1 px of the assembly coordinates used by the front-view
assembly (`bulwark_assemble.py`, 328 x 256, the vanilla 256 body canvas widened for the arms). The suit is
drawn 1.45x the vanilla body, so in game the textures use drawSize 3.26 (768 px = 3.26 world units).

The game draws the helmet at the head position, 0.34 world units (= 80 canvas px) above the body. So the
helmet texture is stored 80 px LOWER than where it shows, and the preview lifts it back up.

Pieces (each its own apparel, so each can be damaged and lost on its own):
  Body, Legs, ArmL, ArmR (shoulder plate + joint + weapon), Helmet.
Facings: south, east, north (the game mirrors east for west). In the east view only the near arm (ArmR) is
drawn; ArmL is empty there.

Usage: python3 suit_kit.py SPEC_NAME OUT_DIR  (see SPECS at the bottom)
Writes OUT_DIR/<Piece>_<facing>.png and OUT_DIR/<Piece>_<facing>m.png (red = takes the suit colour),
plus OUT_DIR/preview.png.
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
sys.path.insert(0, os.path.dirname(__file__))
from parts_lib import load
from process_nano import cut_out, plate_mask, tint

C = 768                 # texture size
K = 2                   # canvas px per assembly px
OX, OY = (C - 328 * K) // 2, 60
HEAD = 80               # helmet drawn this many canvas px above its texture position
DRAW_SIZE = 3.26
INK = (14, 14, 18, 255)


def A(x, y):
    """assembly coordinates -> canvas"""
    return OX + x * K, OY + y * K


def part(path, outline=1.5):
    """A painted part on white -> (RGBA, mask L) cropped to the part, with a thin outline added."""
    rgb = load(path); fg = cut_out(rgb)
    ring = ndimage.binary_dilation(fg, iterations=max(1, round(outline))) & ~fg
    rgb = rgb.copy(); rgb[ring] = 12; fg = fg | ring
    m = plate_mask(rgb) * fg
    ys, xs = np.nonzero(fg); bb = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    rgb[~fg] = 0
    tex = Image.fromarray(np.dstack([rgb.astype(np.uint8), (fg * 255).astype(np.uint8)]), 'RGBA').crop(bb)
    mask = Image.fromarray((m * 255).astype(np.uint8), 'L').crop(bb)
    return tex, mask


def legs_stub(path):
    """leg stubs: only the knee and foot of a generated pair of legs"""
    tex, mask = part(path)
    y = int(tex.height * 0.45)
    return tex.crop((0, y, tex.width, tex.height)), mask.crop((0, y, mask.width, mask.height))


class Layer:
    def __init__(self):
        self.tex = Image.new('RGBA', (C, C)); self.mask = Image.new('L', (C, C), 0)

    def put(self, pm, cx, top=None, bottom=None, h=None, w=None, flip=False, behind=False):
        """place part pm=(tex,mask) by its centre x and top or bottom (canvas px), sized to h or w"""
        tex, mask = pm
        if flip: tex, mask = tex.transpose(Image.FLIP_LEFT_RIGHT), mask.transpose(Image.FLIP_LEFT_RIGHT)
        if h: k = h / tex.height
        elif w: k = w / tex.width
        else: k = 1
        tw, th = max(1, round(tex.width * k)), max(1, round(tex.height * k))
        tex, mask = tex.resize((tw, th), Image.LANCZOS), mask.resize((tw, th), Image.LANCZOS)
        x = int(cx - tw / 2); y = int(top if top is not None else bottom - th)
        if behind:
            t = Image.new('RGBA', (C, C)); t.alpha_composite(tex, (x, y)); t.alpha_composite(self.tex); self.tex = t
            m = Image.new('L', (C, C), 0); m.paste(mask, (x, y)); m.paste(self.mask, (0, 0), self.mask); self.mask = m
        else:
            self.tex.alpha_composite(tex, (x, y))
            self.mask.paste(mask, (x, y), tex.split()[3])
        return (x, y, x + tw, y + th)

    def put_assembly(self, tex_path, mask_path):
        """a layer exported from the front-view assembly (assembly coordinates)"""
        t = Image.open(tex_path).convert('RGBA'); m = Image.open(mask_path).convert('RGBA')
        t = t.resize((t.width * K, t.height * K), Image.LANCZOS); m = m.resize((m.width * K, m.height * K), Image.LANCZOS)
        self.tex.alpha_composite(t, (OX, OY))
        mm = Image.new('L', (C, C), 0); mm.paste(m.split()[0], (OX, OY), m.split()[3]); self.mask = Image.fromarray(np.maximum(np.array(self.mask), np.array(mm)))

    def shift(self, dy):
        for attr in ('tex', 'mask'):
            im = getattr(self, attr); n = Image.new(im.mode, im.size); n.paste(im, (0, dy)); setattr(self, attr, n)

    def joint(self, cx, top, w=44, h=36):
        """ribbed square swivel between a shoulder plate and its weapon"""
        d = ImageDraw.Draw(self.tex)
        x0, y0, x1, y1 = cx - w / 2, top, cx + w / 2, top + h
        d.rounded_rectangle((x0 - 3, y0 - 3, x1 + 3, y1 + 3), radius=6, fill=INK)
        for i in range(int(y1 - y0)):
            v = int(150 - 50 * i / (y1 - y0)); d.line((x0, y0 + i, x1, y0 + i), fill=(v, v + 2, v + 8, 255))
        for k in (1, 2, 3):
            yy = y0 + (y1 - y0) * k / 4; d.line((x0, yy, x1, yy), fill=(30, 30, 36, 255), width=3)
        d.line((x0 + 4, y0 + 3, x1 - 4, y0 + 3), fill=(190, 192, 200, 255), width=2)

    def save(self, out, name):
        self.tex.save(f'{out}/{name}.png')
        a = np.array(self.tex)[..., 3]; m = np.array(self.mask)
        Image.fromarray(np.dstack([m, np.zeros_like(m), np.zeros_like(m), a]), 'RGBA').save(f'{out}/{name}m.png')


def bbox(im):
    a = np.array(im)[..., 3] > 100; ys, xs = np.nonzero(a)
    return xs.min(), ys.min(), xs.max(), ys.max()


def build(spec, out):
    os.makedirs(out, exist_ok=True)
    src = spec['assembly']                       # front-view layers exported by the assembly
    pieces = {}
    # ---------------- south: straight from the front-view assembly (keeps the nesting into the shoulders)
    for p, f in (('Body', 'body'), ('Helmet', 'helmet'), ('ArmL', f"armL_{spec['weapon_l']}"), ('ArmR', f"armR_{spec['weapon_r']}")):
        L = Layer(); L.put_assembly(f'{src}/south_{f}.png', f'{src}/south_{f}_m.png'); pieces[(p, 'south')] = L
    body_bb = bbox(pieces[('Body', 'south')].tex); helm_bb = bbox(pieces[('Helmet', 'south')].tex)
    armL_bb = bbox(pieces[('ArmL', 'south')].tex)
    body_h = body_bb[3] - body_bb[1]; helm_h = helm_bb[3] - helm_bb[1]; cx = (body_bb[0] + body_bb[2]) / 2
    plate_h = int(body_h * 0.62); plate_top = armL_bb[1]
    # legs (south) under the hips
    L = Layer(); L.put(legs_stub(spec['legs']['south']), cx, top=body_bb[3] - int(body_h * 0.12), w=int((body_bb[2] - body_bb[0]) * 0.72), behind=True)
    pieces[('Legs', 'south')] = L
    # ---------------- east (side view): body, near arm, helmet, legs
    L = Layer(); L.put(part(spec['body']['east']), cx, bottom=body_bb[3], h=body_h); pieces[('Body', 'east')] = L
    eb = bbox(L.tex)
    L = Layer(); L.put(legs_stub(spec['legs']['east']), cx, top=eb[3] - int(body_h * 0.12), h=int(body_h * 0.42)); pieces[('Legs', 'east')] = L
    L = Layer(); L.put(part(spec['helmet']['east']), cx + 4, bottom=helm_bb[3] - int(helm_h * 0.06), h=int(helm_h * 0.92)); pieces[('Helmet', 'east')] = L
    L = Layer()
    pb = L.put(part(spec['plate']['east']), cx - 4, top=eb[1] + int(body_h * 0.16), h=int(plate_h * 0.85))
    wh = int(spec['weapon_h'][spec['weapon_r']] * K)
    L.put(part(spec['weapons_east'][spec['weapon_r']]), cx, top=pb[3] - 18, h=wh, behind=True)
    L.joint(cx, pb[3] - 22)
    pieces[('ArmR', 'east')] = L; pieces[('ArmL', 'east')] = Layer()
    # ---------------- north (back view): mirrored arm sides, back panel with the cell caps
    L = Layer(); L.put(part(spec['body']['north']), cx, bottom=body_bb[3], h=body_h); pieces[('Body', 'north')] = L
    nb = bbox(L.tex)
    L = Layer(); L.put(legs_stub(spec['legs']['north']), cx, top=nb[3] - int(body_h * 0.12), w=int((body_bb[2] - body_bb[0]) * 0.72)); pieces[('Legs', 'north')] = L
    L = Layer(); L.put(part(spec['helmet']['north']), cx, bottom=helm_bb[3], h=helm_h); pieces[('Helmet', 'north')] = L
    armR_bb = bbox(pieces[('ArmR', 'south')].tex)
    for p, sbb, wname in (('ArmL', armR_bb, spec['weapon_l']), ('ArmR', armL_bb, spec['weapon_r'])):
        # seen from behind the arm that was on the left is on the right
        acx = (sbb[0] + sbb[2]) / 2; flip = p == 'ArmR'
        L = Layer()
        pb = L.put(part(spec['plate']['north']), acx, top=plate_top, h=plate_h, flip=flip)
        L.put(part(spec['weapons_south'][wname]), acx, top=pb[3] - 18, h=int(spec['weapon_h'][wname] * K), flip=True, behind=True)
        L.joint(acx, pb[3] - 22)
        pieces[(p, 'north')] = L
    # ---------------- save: helmet stored HEAD px lower (the game lifts it to the head)
    for (p, f), L in pieces.items():
        if p == 'Helmet': L.shift(HEAD)
        L.save(out, f'{p}_{f}')
    preview(out, spec.get('colors', [(0.56, 0.58, 0.60), (0.58, 0.60, 0.42)]))


ORDER = {'south': ['Legs', 'Body', 'ArmL', 'ArmR', 'Helmet'], 'east': ['ArmL', 'Legs', 'Body', 'ArmR', 'Helmet'],
         'north': ['Legs', 'Helmet', 'ArmL', 'ArmR', 'Body']}


def stack(out, facing, color=None):
    c = Image.new('RGBA', (C, C))
    for p in ORDER[facing]:
        t = Image.open(f'{out}/{p}_{facing}.png').convert('RGBA'); m = Image.open(f'{out}/{p}_{facing}m.png').convert('RGBA')
        if color: t = tint(t, Image.merge('RGBA', (m.split()[0],) * 3 + (m.split()[3],)), color)
        c.alpha_composite(t, (0, -HEAD if p == 'Helmet' else 0))
    return c


def preview(out, colors):
    rows = [None] + list(colors)
    W = 300; sheet = Image.new('RGB', (3 * W, len(rows) * W + 20), (92, 84, 70)); d = ImageDraw.Draw(sheet)
    for j, col in enumerate(rows):
        for i, f in enumerate(('south', 'east', 'north')):
            im = stack(out, f, col); im = im.crop(im.getbbox()); im.thumbnail((W - 20, W - 20), Image.LANCZOS)
            sheet.paste(im, (i * W + 10, 20 + j * W), im)
            if j == 0: d.text((i * W + 8, 4), f, fill=(255, 255, 255))
    sheet.save(f'{out}/preview.png')


def bulwark_spec(sp):
    """the Bulwark; sp = folder with the source paintings (scratchpad or Source/Art/nano/modular)"""
    ws = ['minigun', 'rockets', 'chainsaw', 'laser', 'flamer', 'hammer', 'autocannon', 'grenade', 'arc', 'towershield']
    return dict(
        assembly=f'{sp}/kit_src', weapon_l='minigun', weapon_r='rockets',
        body=dict(east=f'{sp}/views/chassis_east_caps.png', north=f'{sp}/views/chassis_north_caps.png'),
        helmet=dict(east=f'{sp}/views/helmet_east.png', north=f'{sp}/views/helmet_north.png'),
        plate=dict(east=f'{sp}/views/plate_east.png', north=f'{sp}/views/plate_north.png'),
        legs=dict(south=f'{sp}/views/legs_south.png', east=f'{sp}/views/legs_east2.png', north=f'{sp}/views/legs_north.png'),
        weapons_south={w: f'{sp}/weap/{w}.png' for w in ws},
        weapons_east={w: f'{sp}/weap_east/{w}.png' for w in ws},
        weapon_h={'minigun': 118, 'rockets': 104, 'chainsaw': 124, 'laser': 118, 'flamer': 112, 'hammer': 112,
                  'autocannon': 150, 'grenade': 104, 'arc': 134, 'towershield': 136})


if __name__ == '__main__':
    sp, out = sys.argv[1], sys.argv[2]
    spec = bulwark_spec(sp)
    for k in ('weapon_l', 'weapon_r'):
        if os.environ.get(k.upper()): spec[k] = os.environ[k.upper()]
    build(spec, out)
