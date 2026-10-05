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
Facings: south, east (a side view, the owner's pick; guns aimed forward), north (the game mirrors east for west).
ArmL is the arm on the left of the front view (the pawn's right arm): nearest the viewer facing east, on the
right from behind.

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


def src_bbox(path):
    """the painted part's box in its own painting (paintings repainted from one another share a frame)"""
    fg = cut_out(load(path)); ys, xs = np.nonzero(fg); return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def put_like(L, path, ref, cx, top, h):
    """place a repaint (e.g. a backpack with pylons sticking up) at the scale and spot its reference would take"""
    if not ref: return L.put(part(path), cx, top=top, h=h)
    r0, r1, r2, r3 = src_bbox(ref); v0, v1, v2, v3 = src_bbox(path); k = h / (r3 - r1)
    return L.put(part(path), cx + ((v0 + v2) - (r0 + r2)) / 2 * k, top=top - (r1 - v1) * k, h=(v3 - v1) * k)


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

    def collar(self, cx, cy, w, h, t=None, col=(150, 146, 158)):
        """front half of a collar ring (thickness t) centred on (cx, cy): drawn over what is behind it, painted"""
        t = t or max(10, h // 3)
        K4 = 4; W, H = self.tex.size
        m = Image.new('L', (W * K4, H * K4), 0); d = ImageDraw.Draw(m)
        box = lambda r: ((cx - w / 2 - r) * K4, (cy - h / 2 - r) * K4, (cx + w / 2 + r) * K4, (cy + h / 2 + r) * K4)
        d.ellipse(box(0), fill=255); d.ellipse(box(-t), fill=0)
        ring = np.array(m.resize((W, H), Image.LANCZOS)) > 127
        ring[:int(cy)] = False                                      # only the near (lower) half
        yy = np.arange(H)[:, None] * np.ones((1, W)); shade = np.clip(1.08 - (yy - cy) / (h / 2 + t) * 0.35, 0.7, 1.1)
        line = ndimage.binary_dilation(ring, iterations=3) & ~ring
        line[:int(cy)] = False
        a = np.array(self.tex); mk = np.array(self.mask)
        for c in range(3): a[..., c][ring] = np.clip(col[c] * shade[ring], 0, 255)
        a[..., 3][ring] = 255; a[line] = INK; mk[ring] = 255
        self.tex = Image.fromarray(a); self.mask = Image.fromarray(mk)

    def save(self, out, name):
        self.tex.save(f'{out}/{name}.png')
        a = np.array(self.tex)[..., 3]; m = np.array(self.mask)
        Image.fromarray(np.dstack([m, np.zeros_like(m), np.zeros_like(m), a]), 'RGBA').save(f'{out}/{name}m.png')


def shield_part(path, top, bottom, widen=1.35):
    """a tower shield sized to stand from `top` to `bottom` (canvas px), made wider than the painting"""
    wt, wm = part(path)
    ta = np.array(wt); solid = ndimage.binary_fill_holes(ta[..., 3] > 40)     # a shield is solid: no see-through face
    edge = ndimage.binary_dilation(solid, iterations=3) & ~solid                # and a solid outline, no soft gap
    ta[edge] = (14, 14, 18, 255); ta[..., 3] = np.where(solid | edge, 255, 0); wt = Image.fromarray(ta)
    a = np.array(wt)[..., 3] > 100; widths = a.sum(1); full = widths.max()
    start = int(np.argmax(widths > full * 0.6))            # drop the narrow mounting block on top
    wt, wm = wt.crop((0, start, wt.width, wt.height)), wm.crop((0, start, wm.width, wm.height))
    h = bottom - top; w = int(wt.width * h / wt.height * widen)
    wt = wt.resize((w, h), Image.LANCZOS); a = np.array(wt); a[..., 3] = np.where(a[..., 3] > 60, 255, 0)
    return Image.fromarray(a), wm.resize((w, h), Image.LANCZOS)


def bbox(im):
    a = np.array(im)[..., 3] > 100; ys, xs = np.nonzero(a)
    return xs.min(), ys.min(), xs.max(), ys.max()


def base_plate(src, side, P):
    """the suit's plain plate (no weapon hardware), if the assembly exported one: it sets the cuff and the back view"""
    f = f'{src}/south_plate{side}base.png'
    if not os.path.exists(f): return P
    B = Layer(); B.put_assembly(f, f'{src}/south_plate{side}base_m.png'); return B


def build(spec, out):
    os.makedirs(out, exist_ok=True)
    src = spec['assembly']                       # front-view layers exported by the assembly
    pieces = {}
    # ---------------- south: straight from the front-view assembly (keeps the nesting into the shoulders)
    for p, f in (('Body', 'body'), ('Helmet', 'helmet'), ('ArmL', f"armL_{spec['weapon_l']}"), ('ArmR', f"armR_{spec['weapon_r']}")):
        if f.endswith('_none'):
            # a bare arm (no weapon fitted): the plate and its cuff, with the same hole the chest nests into
            sd = f[3]; L = Layer(); L.put_assembly(f'{src}/south_plate{sd}full.png', f'{src}/south_plate{sd}full_m.png')
            a_ = Layer(); a_.put_assembly(f'{src}/south_arm{sd}_minigun.png', f'{src}/south_arm{sd}_minigun_m.png')
            b_ = Layer(); b_.put_assembly(f'{src}/south_arm{sd}full_minigun.png', f'{src}/south_arm{sd}full_minigun_m.png')
            hole = (np.array(b_.tex)[..., 3] > 100) & ~(np.array(a_.tex)[..., 3] > 100)
            t_ = np.array(L.tex); t_[hole, 3] = 0; m_ = np.array(L.mask); m_[hole] = 0
            L.tex = Image.fromarray(t_); L.mask = Image.fromarray(m_); pieces[(p, 'south')] = L; continue
        L = Layer(); L.put_assembly(f'{src}/south_{f}.png', f'{src}/south_{f}_m.png'); pieces[(p, 'south')] = L
    body_bb = bbox(pieces[('Body', 'south')].tex); helm_bb = bbox(pieces[('Helmet', 'south')].tex)
    armL_bb = bbox(pieces[('ArmL', 'south')].tex)
    body_h = body_bb[3] - body_bb[1]; helm_h = helm_bb[3] - helm_bb[1]; cx = (body_bb[0] + body_bb[2]) / 2
    plate_h = int(body_h * 0.62); plate_top = armL_bb[1]
    # legs (south) under the hips
    L = Layer(); L.put(legs_stub(spec['legs']['south']), cx, top=body_bb[3] - int(body_h * 0.12), w=int((body_bb[2] - body_bb[0]) * 0.72), behind=True)
    pieces[('Legs', 'south')] = L
    def moved(f, cx_to, top_to, k=1.0, flip=False):
        """a full front-view arm layer, scaled by k and moved so its centre x / top land on cx_to / top_to"""
        L = Layer(); L.put_assembly(f'{src}/south_{f}.png', f'{src}/south_{f}_m.png')
        x0, y0, x1, y1 = bbox(L.tex); box = (x0, y0, x1 + 1, y1 + 1)
        pm = (L.tex.crop(box), L.mask.crop(box)); N = Layer()
        N.put(pm, cx_to, top=top_to, h=int((y1 - y0) * k), flip=flip); return N
    armR_bb = bbox(pieces[('ArmR', 'south')].tex)
    bw = body_bb[2] - body_bb[0]
    _P = Layer(); _P.put_assembly(f'{src}/south_plateLfull.png', f'{src}/south_plateLfull_m.png'); plL_bb = bbox(_P.tex)
    # ---------------- east: one whole side painting cut into pieces (keeps the front view's bulk), if given
    if spec.get('full_east'):
        fe = spec['full_east']
        rgb = load(fe['image']); fg = cut_out(rgb)
        rgb = rgb.copy(); lum = rgb.mean(2); body = fg & (lum > 75)
        rgb[body] = np.clip(rgb[body] * (fe.get('match_lum', 140) / np.median(lum[body])), 0, 255)   # match the front's brightness
        ring = ndimage.binary_dilation(fg, iterations=2) & ~fg; rgb[ring] = 12; fg = fg | ring
        pm = plate_mask(rgb) * fg; n = rgb.shape[0]; sc = n / 1024
        ys, xs = np.nonzero(fg)
        # scale: painting height = the front view's assembled height (helmet top, lifted, to the feet)
        south = Image.new('RGBA', (C, C))
        for p in ('Legs', 'Body', 'ArmL', 'ArmR', 'Helmet'):
            south.alpha_composite(pieces[(p, 'south')].tex)          # pieces are still in shown position here
        sx0, sy0, sx1, sy1 = bbox(south)
        k = (sy1 - sy0) / (ys.max() - ys.min())
        def poly_mask(pts):
            m = Image.new('L', (n, n), 0); ImageDraw.Draw(m).polygon([(x * sc, y * sc) for x, y in pts], fill=255)
            return np.array(m) > 127
        def prep(path):
            r = load(path); f = cut_out(r); r = r.copy(); lm = r.mean(2); bd = f & (lm > 75)
            r[bd] = np.clip(r[bd] * (fe.get('match_lum', 140) / np.median(lm[bd])), 0, 255)
            rg = ndimage.binary_dilation(f, iterations=2) & ~f; r[rg] = 12; f = f | rg
            return r, f, plate_mask(r) * f
        srcs = {'full': (rgb, fg, pm)}
        if fe.get('body_image'): srcs['body'] = prep(fe['body_image'])
        bsrc = srcs.get('body', srcs['full'])
        arm_m = poly_mask(fe['pieces']['ArmL']) & fg
        masks = {'ArmL': ('full', arm_m)}
        for q in ('Helmet', 'Legs'): masks[q] = ('body' if 'body' in srcs else 'full', poly_mask(fe['pieces'][q]) & bsrc[1])
        rest = bsrc[1].copy()
        for q in ('Helmet', 'Legs'): rest &= ~masks[q][1]
        if 'body' not in srcs: rest &= ~arm_m
        masks['Body'] = ('body' if 'body' in srcs else 'full', rest)
        if fe.get('over_from'):
            # pack hardware on the near shoulder (e.g. a net launcher): what the pack repaint added over its base,
            # in the top part of the painting, drawn over the helmet instead of being cut away with it
            base = load(fe['over_from']); r_ = srcs['body'][0]
            add = (np.abs(r_.astype(float) - base.astype(float)).max(2) > 40) & srcs['body'][1]
            add[int(n * fe.get('over_rows', 0.36)):] = False
            add = ndimage.binary_opening(add, iterations=2)
            add = ndimage.binary_dilation(ndimage.binary_fill_holes(ndimage.binary_closing(add, iterations=6)), iterations=3) & srcs['body'][1]
            masks['Over'] = ('body', add); masks['Body'] = (masks['Body'][0], rest & ~add)
        for q, (which, m) in masks.items():
            L = Layer(); r_, f_, pm_ = srcs[which]
            t = Image.fromarray(np.dstack([np.where(m[..., None], r_, 0).astype(np.uint8), (m * 255).astype(np.uint8)]), 'RGBA')
            mk = Image.fromarray((np.where(m, pm_, 0) * 255).astype(np.uint8), 'L')
            t = t.resize((round(n * k), round(n * k)), Image.LANCZOS); mk = mk.resize(t.size, Image.LANCZOS)
            x = int(cx - (xs.min() + xs.max()) / 2 * k); y = int(sy0 - ys.min() * k + (HEAD if q == 'Helmet' else 0) - (HEAD if q == 'Helmet' else 0))
            L.tex.alpha_composite(t, (x, y)); L.mask.paste(mk, (x, y), t.split()[3])
            pieces[(q, 'east')] = L
        if spec['helmet'].get('east_override'):
            # this suit's own helmet in the side view, in the painted helmet's place and size
            H_ = pieces[('Helmet', 'east')]; hb_ = bbox(H_.tex); N_ = Layer()
            N_.put(part(spec['helmet']['east_override']), (hb_[0] + hb_[2]) / 2, bottom=hb_[3], h=hb_[3] - hb_[1])
            pieces[('Helmet', 'east')] = N_
        # the shoulder armour starts at the same height as in the front and back views
        A_ = pieces[('ArmL', 'east')]
        ab = bbox(A_.tex); wname = spec['weapon_l']
        ey = ab[1] + int((ab[3] - ab[1]) * 0.80)                   # the elbow, at the end of the ribbed hose
        if wname in spec.get('east_plates', {}):
            # this suit's own side-view plate painting (pauldron + elbow) replaces the painted heavy arm, same box
            A_ = Layer(); pieces[('ArmL', 'east')] = A_
            A_.put(part(spec['east_plates'][wname]), (ab[0] + ab[2]) / 2, top=ab[1], h=ab[3] - ab[1])
            ab = bbox(A_.tex); ey = ab[1] + int((ab[3] - ab[1]) * 0.80)
        elif spec.get('east_plate_from_front'):
            # this suit's own plate (light frame + weapon hardware) replaces the painted heavy one:
            # its outer face, i.e. the front-view plate, over a ribbed swivel; the weapon hangs at its cuff
            P_ = Layer(); P_.put_assembly(f'{src}/south_plateLfull.png', f'{src}/south_plateLfull_m.png')
            B_ = base_plate(src, 'L', P_); bx = bbox(B_.tex); px = bbox(P_.tex)
            k_ = (ab[3] - ab[1]) * 0.78 / (bx[3] - bx[1])
            box_ = (px[0], px[1], px[2] + 1, px[3] + 1)
            A_ = Layer(); pieces[('ArmL', 'east')] = A_
            pcx_ = (ab[0] + ab[2]) / 2 - ((bx[0] + bx[2]) / 2 - (px[0] + px[2]) / 2) * k_
            A_.put((P_.tex.crop(box_), P_.mask.crop(box_)), pcx_, top=ab[1] + int((px[1] - bx[1]) * k_), h=int((px[3] - px[1]) * k_))
            ey = ab[1] + int((bx[3] - bx[1]) * k_) - 6
            A_.joint(int((ab[0] + ab[2]) / 2), ey - 12)
            ab = (ab[0], ab[1], ab[2], ey)
        if wname == 'none':
            pass                                                     # bare arm: plate and elbow only
        elif wname in spec.get('shields', ()):
            feet = bbox(pieces[('Legs', 'south')].tex)[3]
            st0 = plL_bb[1] + 40                                     # same top as in the front and back views
            A_.put(shield_part(spec['weapons_east'][wname], st0, feet + 6, widen=1.6), ab[2] + 4, top=st0)
        else:
            wt, wm = part(spec['weapons_east'][wname]); wt, wm = wt.rotate(90, expand=True), wm.rotate(90, expand=True)
            ln = int(spec['weapon_h'][wname] * K * 1.05); h = max(1, round(wt.height * ln / wt.width))
            A_.put((wt, wm), ab[0] + (ab[2] - ab[0]) * 0.80 + ln / 2, top=ey - h // 2, w=ln)
        before = np.array(A_.tex)[..., 3] > 100
        A_.shift(plL_bb[1] - bbox(A_.tex)[1]); after = np.array(A_.tex)[..., 3] > 100
        if ('Over', 'east') in pieces:                           # over the helmet, under the near plate
            O_ = pieces.pop(('Over', 'east')); arm_a = np.array(A_.tex)[..., 3] > 100
            A_.mask = Image.fromarray(np.where(arm_a, np.array(A_.mask), np.array(O_.mask)).astype(np.uint8))
            A_.tex = Image.alpha_composite(O_.tex, A_.tex)
        # the far arm: drawn behind everything, a little higher; only what sticks out past the body shows
        F_ = Layer(); far = spec['weapon_r']; feet = bbox(pieces[('Legs', 'south')].tex)[3]
        if far == 'none':
            pass                                                     # a bare far arm is hidden behind the body
        elif far in spec.get('shields', ()):
            st0 = plL_bb[1] + 40
            F_.put(shield_part(spec['weapons_east'][far], st0, feet + 6, widen=1.6), ab[2] + 26, top=st0)
        else:
            wt, wm = part(spec['weapons_east'][far]); wt, wm = wt.rotate(90, expand=True), wm.rotate(90, expand=True)
            ln = int(spec['weapon_h'][far] * K * 0.98); h = max(1, round(wt.height * ln / wt.width))
            fa = np.array(F_.tex)
            F_.put((wt, wm), ab[0] + (ab[2] - ab[0]) * 0.95 + ln / 2, top=ey - 22 - h // 2, w=ln)
            t_ = np.array(F_.tex).astype(float); t_[..., :3] *= 0.82; F_.tex = Image.fromarray(t_.astype(np.uint8))   # far side, in shadow
        pieces[('ArmR', 'east')] = F_
    else:
        # ---------------- east (side view, the owner's pick over the three-quarter view): one near arm, gun aimed forward
        L = Layer(); L.put(part(spec['body']['east']), cx, bottom=body_bb[3], h=body_h); pieces[('Body', 'east')] = L
        eb = bbox(L.tex)
        L = Layer(); L.put(legs_stub(spec['legs']['east']), cx, top=eb[3] - int(body_h * 0.12), h=int(body_h * 0.42)); pieces[('Legs', 'east')] = L
        L = Layer(); L.put(part(spec['helmet']['east']), cx + 4, bottom=helm_bb[3] - int(helm_h * 0.06), h=int(helm_h * 0.92)); pieces[('Helmet', 'east')] = L
        L = moved('plateLfull', cx - int(bw * 0.16), plL_bb[1] + int((plL_bb[3] - plL_bb[1]) * 0.22), 0.80)
        pb = bbox(L.tex)
        wname = spec['weapon_l']
        wt, wm = part(spec['weapons_east'][wname]); wt, wm = wt.rotate(90, expand=True), wm.rotate(90, expand=True)
        ln = int(spec['weapon_h'][wname] * K); h = max(1, round(wt.height * ln / wt.width))
        elbow_y = pb[3] - 6
        L.put((wt, wm), (pb[0] + pb[2]) / 2 + ln * 0.42, top=elbow_y - h // 2, w=ln, behind=True)
        L.joint(int((pb[0] + pb[2]) / 2), elbow_y - 20)
        pieces[('ArmL', 'east')] = L; pieces[('ArmR', 'east')] = Layer()
    # ---------------- north (back view): the arms swap sides and are mirrored; shoulders cover the body
    side_top = bbox(pieces[('Body', 'east')].tex)[1]
    if spec.get('full_east', {}).get('body_ref'):
        # a pack repaint with pylons or a launcher sticking up: the body's top is the plain pack's top
        fe = spec['full_east']; rest_ref = cut_out(load(fe['body_ref']))
        for q in ('Helmet', 'Legs'): rest_ref &= ~poly_mask(fe['pieces'][q])
        side_top = int(sy0 - ys.min() * k + np.nonzero(rest_ref.any(1))[0].min() * k)
    nref = spec['body'].get('north_ref')
    L = Layer(); put_like(L, spec['body']['north'], nref, cx, side_top, body_bb[3] - side_top); pieces[('Body', 'north')] = L
    if spec['body'].get('cavity'):
        # the open back (climbing in), gullwing: the pack swings up on a hinge at its top edge. From behind we see its
        # outside upside down and foreshortened above the shoulders, over the open cavity - so every pack reuses its own
        # closed back art, and one cavity painting serves every suit.
        nb_ = bbox(L.tex); O = Layer()
        cb = O.put(part(spec['body']['cavity']), cx, bottom=nb_[3], w=nb_[2] - nb_[0])
        ref = nref or spec['body']['north']; base = spec['body'].get('pack_base', ref)
        rgb = load(spec['body']['north']); fg = cut_out(rgb); n_ = rgb.shape[0]; f_ = n_ / 1024
        x0_, x1_, yb_ = [int(v * f_) for v in spec['body'].get('pack_box', (300, 724, 830))]
        col = np.zeros_like(fg); col[:yb_, x0_:x1_] = True
        added = (np.abs(rgb.astype(float) - load(base).astype(float)).max(2) > 40) & fg   # what this pack adds (pylons, thrusters...)
        added = ndimage.binary_opening(added, iterations=2)
        pk = fg & (col | ndimage.binary_dilation(added, iterations=3))
        lab, nl = ndimage.label(pk); sz = ndimage.sum(pk, lab, range(1, nl + 1))
        pk = np.isin(lab, np.nonzero(np.array(sz) > 400)[0] + 1)
        pk = pk & (ndimage.gaussian_filter(pk.astype(float), 9 * f_) > 0.5)        # round off the cut corners
        ring = ndimage.binary_dilation(pk, iterations=2) & ~pk; r2 = rgb.copy(); r2[ring] = 12; pk = pk | ring
        ys_, xs_ = np.nonzero(pk); bx = (xs_.min(), ys_.min(), xs_.max() + 1, ys_.max() + 1)
        r2 = r2.astype(float) * 0.84; r2[~pk] = 0                                  # tilted away from the light
        t = Image.fromarray(np.dstack([r2.astype(np.uint8), (pk * 255).astype(np.uint8)]), 'RGBA').crop(bx)
        mk = Image.fromarray((plate_mask(rgb) * pk * 255).astype(np.uint8), 'L').crop(bx)
        t, mk = t.transpose(Image.FLIP_TOP_BOTTOM), mk.transpose(Image.FLIP_TOP_BOTTOM)  # swung up past level: bottom edge on top
        if spec['body'].get('lid_inside', True):
            # the lid swings up toward us, so we see its INSIDE: drawn on the pack's own outline - lilac rim, recessed
            # dark face, two harness straps with buckles and a waist strap (colours from the old swing door)
            outside = np.array(t).astype(float)
            colm = (pk & ndimage.binary_dilation(col & fg, iterations=2))[bx[1]:bx[3], bx[0]:bx[2]][::-1]
            colm = colm & (ndimage.gaussian_filter(colm.astype(float), 9 * f_) > 0.5)
            sil = colm; H_, W_ = sil.shape
            rim_w = max(6, int(min(H_, W_) * 0.07))
            face = ndimage.binary_erosion(sil, iterations=rim_w); lip = ndimage.binary_erosion(sil, iterations=3)
            img = np.zeros((H_, W_, 4), np.uint8)
            img[sil] = (14, 14, 18, 255); img[lip] = (165, 137, 160, 255)
            yy = np.arange(H_)[:, None] * np.ones((1, W_))
            shade = (0.85 + 0.25 * yy / H_)[..., None]                     # lit toward the hinge (bottom)
            img[face, :3] = np.clip(np.array([92, 74, 96]) * shade, 0, 255)[face]
            edge = face & ~ndimage.binary_erosion(face, iterations=3); img[edge, :3] = (14, 14, 18)
            inner = ndimage.binary_erosion(face, iterations=3); top_sh = inner & (yy < np.nonzero(inner.any(1))[0].min() + 10)
            img[top_sh, :3] = (66, 48, 69)                                   # the rim's shadow on the face
            im_ = Image.fromarray(img, 'RGBA'); d_ = ImageDraw.Draw(im_)
            fy, fx = np.nonzero(face); fx0, fx1, fy0, fy1 = fx.min(), fx.max(), fy.min(), fy.max(); fw, fh = fx1 - fx0, fy1 - fy0
            sw = max(6, int(fw * 0.13))
            for cxs in (fx0 + fw * 0.34, fx0 + fw * 0.66):              # shoulder straps
                d_.rounded_rectangle((cxs - sw / 2, fy0 + fh * 0.08, cxs + sw / 2, fy1 - fh * 0.08), radius=sw // 3,
                                     fill=(60, 52, 64, 255), outline=(14, 14, 18, 255), width=2)
                bky = fy0 + fh * 0.45; bkw = sw * 1.15
                d_.rectangle((cxs - bkw / 2, bky - bkw / 2, cxs + bkw / 2, bky + bkw / 2), fill=(150, 150, 160, 255), outline=(14, 14, 18, 255), width=2)
                d_.rectangle((cxs - bkw / 4, bky - bkw / 4, cxs + bkw / 4, bky + bkw / 4), fill=(60, 52, 64, 255))
            wy = fy0 + fh * 0.74                                             # waist strap
            d_.rounded_rectangle((fx0 + fw * 0.16, wy - sw * 0.4, fx1 - fw * 0.16, wy + sw * 0.4), radius=sw // 3,
                                 fill=(60, 52, 64, 255), outline=(14, 14, 18, 255), width=2)
            d_.rectangle((fx0 + fw / 2 - sw * 0.55, wy - sw * 0.55, fx0 + fw / 2 + sw * 0.55, wy + sw * 0.55), fill=(150, 150, 160, 255), outline=(14, 14, 18, 255), width=2)
            # hardware on the outside (thrusters, launcher, pylons) peeks past the lid's edges, in shadow
            outside[..., :3] *= 0.55; outside[sil, 3] = 0
            t = Image.fromarray(outside.astype(np.uint8), 'RGBA'); t.alpha_composite(im_)
            mk = Image.fromarray(np.where(lip & ~face, 255, 0).astype(np.uint8), 'L')   # the rim takes the paint
        rb = src_bbox(ref); kk = (body_bb[3] - side_top) / (rb[3] - rb[1])
        pw_, ph_ = (bx[2] - bx[0]) * kk, (bx[3] - bx[1]) * kk * spec['body'].get('gull_squash', 0.5)
        t, mk = t.resize((max(1, round(pw_)), max(1, round(ph_))), Image.LANCZOS), mk.resize((max(1, round(pw_)), max(1, round(ph_))), Image.LANCZOS)
        pcx = cx + ((bx[0] + bx[2]) - (rb[0] + rb[2])) / 2 * kk
        # hinge = the top edge of the opening: the pack's hinge edge tucks behind the collar, so it rises out of the suit
        hy = cb[1] + int((cb[3] - cb[1]) * spec['body'].get('hinge_at', 0.17))
        PK = Layer(); pb_ = PK.put((t, mk), pcx, bottom=hy, h=t.height)
        # two hinge knuckles where the pack meets the collar, either side of the head
        d = ImageDraw.Draw(PK.tex); dm = ImageDraw.Draw(PK.mask); kw, kh = 26, 30
        for hx in (pb_[0] + 22, pb_[2] - 22):
            box = (hx - kw / 2, hy - kh / 2, hx + kw / 2, hy + kh / 2)
            d.rounded_rectangle(box, radius=6, fill=(70, 70, 78, 255), outline=(14, 14, 18, 255), width=3)
            for yy in (box[1] + kh / 3, box[1] + 2 * kh / 3): d.line((box[0] + 3, yy, box[2] - 3, yy), fill=(30, 30, 36, 255), width=2)
            d.line((box[0] + 5, box[1] + 4, box[2] - 5, box[1] + 4), fill=(150, 150, 160, 255), width=2)
            dm.rectangle(box, fill=0)
        pieces[('Body', 'northopen')] = O; open_pack = PK          # joined at the end: behind the collar and the helmet
    nb = bbox(L.tex)
    L = Layer(); L.put(legs_stub(spec['legs']['north']), cx, top=nb[3] - int(body_h * 0.12), w=int(bw * 0.72)); pieces[('Legs', 'north')] = L
    eh = bbox(pieces[('Helmet', 'east')].tex)
    L = Layer(); hb = L.put(part(spec['helmet']['north']), cx, top=eh[1], h=int(helm_h * 0.86))   # same top as the side view
    # the back rim of the collar is nearer than the head from behind: a shaded armour band over the helmet's base
    pieces[('Helmet', 'north')] = L
    north_plates = {}
    for p, plate, full, wname in (('ArmL', 'plateLfull', 'armLfull', spec['weapon_l']), ('ArmR', 'plateRfull', 'armRfull', spec['weapon_r'])):
        P = Layer(); P.put_assembly(f'{src}/south_{plate}.png', f'{src}/south_{plate}_m.png')
        fw = 'minigun' if wname == 'none' else wname
        F = Layer(); F.put_assembly(f'{src}/south_{full}_{fw}.png', f'{src}/south_{full}_{fw}_m.png')
        pa = np.array(P.tex)[..., 3] > 100; fa = np.array(F.tex)[..., 3] > 100
        wy, wx = np.nonzero(fa & ~ndimage.binary_dilation(pa, iterations=3))
        mx = lambda x: C - x                                       # mirror across the canvas centre
        N = Layer(); fx = mx((wx.min() + wx.max()) / 2)
        P = base_plate(src, plate[5], P)                          # from behind: the plain plate
        x0, y0, x1, y1 = bbox(P.tex); box = (x0, y0, x1 + 1, y1 + 1)
        pw = x1 - x0
        # weapon rear view: same bottom as the front view's weapon, no wider than 70% of the plate
        if wname != 'none':
            wt, wm = part(spec['weapons_north'][wname]); wh = int(spec['weapon_h'][wname] * K)
            kk = min(wh / wt.height, pw * 0.70 / wt.width)
            N.put((wt, wm), fx, bottom=wy.max(), h=int(wt.height * kk), flip=True)
        # shoulder plate from behind: the front plate's exact outline (mirrored), filled with the plate's back face
        sil = P.tex.crop(box).transpose(Image.FLIP_LEFT_RIGHT); sa = np.array(sil)[..., 3] > 100
        # back of the plate = the front plate mirrored, its dark hook interior painted over as solid back armour
        pt = np.array(P.tex.crop(box)).astype(float); pmk = np.array(P.mask.crop(box))
        pa_ = pt[..., 3] > 100; lum = pt[..., :3].mean(2)
        inner = pa_ & ndimage.binary_erosion(pa_, iterations=6)
        dark = inner & (lum < 95)
        dark = ndimage.binary_closing(dark, iterations=3) & inner
        lit = pa_ & (lum > 110)
        col = np.median(pt[..., :3][lit], 0) if lit.any() else np.array([140, 140, 150.])
        ys_ = np.nonzero(dark)[0]
        if len(ys_):
            yy = np.arange(pt.shape[0])[:, None] * np.ones((1, pt.shape[1]))
            sh = 1.04 - 0.18 * np.clip((yy - ys_.min()) / max(1, ys_.max() - ys_.min()), 0, 1)
            for c in range(3): pt[..., c] = np.where(dark, col[c] * sh, pt[..., c])
            pmk = np.where(dark, 255, pmk)
            seam = dark & ~ndimage.binary_erosion(dark, iterations=2)       # a soft seam where the hook was
            pt[seam, :3] *= 0.75
        tb = Image.fromarray(pt.astype(np.uint8), 'RGBA').transpose(Image.FLIP_LEFT_RIGHT)
        mb = Image.fromarray(pmk.astype(np.uint8), 'L').transpose(Image.FLIP_LEFT_RIGHT)
        N.put((tb, mb), mx((x0 + x1) / 2), top=y0, h=y1 - y0)
        BP = Layer(); BP.put((tb, mb), mx((x0 + x1) / 2), top=y0, h=y1 - y0); north_plates[p] = BP
        pieces[(p, 'north')] = N
    if spec.get('backpack_peek'):
        bt, bm = part(spec['body']['north'])
        rb = src_bbox(nref or spec['body']['north']); vb = src_bbox(spec['body']['north'])
        cut = int((rb[1] - vb[1]) + (rb[3] - rb[1]) * 0.30)        # 30% of the backpack, plus what sticks up above it
        bt = bt.crop((0, 0, bt.width, cut)); bm = bm.crop((0, 0, bm.width, cut))
        a = np.array(bt).astype(float); a[..., :3] *= 0.72; bt = Image.fromarray(a.astype(np.uint8), 'RGBA')   # the far side: in shadow
        nbb = bbox(pieces[('Body', 'north')].tex)
        kp = (nbb[3] - nbb[1]) / (vb[3] - vb[1])                    # the back view's scale
        pieces[('Body', 'south')].put((bt, bm), cx, top=nbb[1], w=int(bt.width * kp * 0.55), behind=True)
    # ---------------- weapons aimed forward in the front/back views too (end-on art), where it exists
    fwd = spec.get('weapons_fwd', {}); front_over = set()
    for p_, plate, wname, side in (('ArmL', 'plateLfull', spec['weapon_l'], 'L'), ('ArmR', 'plateRfull', spec['weapon_r'], 'R')):
        if wname not in fwd: continue
        P = Layer(); P.put_assembly(f'{src}/south_{plate}.png', f'{src}/south_{plate}_m.png')
        cutL = Layer(); cutL.put_assembly(f'{src}/south_arm{side}_{wname}.png', f'{src}/south_arm{side}_{wname}_m.png')
        fullL = Layer(); fullL.put_assembly(f'{src}/south_arm{side}full_{wname}.png', f'{src}/south_arm{side}full_{wname}_m.png')
        hole = (np.array(fullL.tex)[..., 3] > 100) & ~(np.array(cutL.tex)[..., 3] > 100)   # where the chest nests in
        Pb = base_plate(src, side, P)                              # the cuff is on the plain plate, not its hoses
        x0, y0, x1, y1 = bbox(Pb.tex); pw = x1 - x0
        pa_ = np.array(Pb.tex)[..., 3] > 100; cuff_x = np.nonzero(pa_[y1 - 12:y1 + 1].any(0))[0]
        pcx = (cuff_x.min() + cuff_x.max()) / 2; cw = cuff_x.max() - cuff_x.min()
        for facing in ('south', 'north'):
            N = Layer()
            wcx = pcx if facing == 'south' else C - pcx
            if wname in spec.get('shields', ()):
                # a hand shield (VEF style): a big shield in front of the body facing south, behind it facing north
                feet = bbox(pieces[('Legs', 'south')].tex)[3]
                inward = (cx - pcx) * float(os.environ.get('SHIELD_INWARD', '0.55'))   # a pair of shields: less, so they don't overlap
                if facing == 'south':
                    pm2 = shield_part(spec['weapons_south'][wname], y0 + 40, feet + 6)
                    N.put(pm2, pcx + inward, top=y0 + 40)
                    front_over.add(p_)
                else:
                    # back of the same shield: the front shape mirrored, plain and in shadow, at the mirrored spot
                    bt_, bm_ = shield_part(spec['weapons_south'][wname], y0 + 40, feet + 6)
                    ba_ = np.array(bt_).astype(float); al = ba_[..., 3] > 100
                    inner = al & ndimage.binary_erosion(al, iterations=10)
                    col = np.median(ba_[..., :3][inner], 0) * 0.78
                    for c_ in range(3): ba_[..., c_] = np.where(inner, col[c_], ba_[..., c_])
                    rim = inner & ~ndimage.binary_erosion(inner, iterations=3); ba_[rim, :3] *= 0.6
                    N.put((Image.fromarray(ba_.astype(np.uint8)), bm_), C - (pcx + inward), top=y0 + 40, flip=True)
                    front_over.add(p_)
            elif facing == 'north' and spec.get('weapons_back'):
                wt, wm = part(spec['weapons_back'][wname])
                kk = min(int(spec['weapon_h'][wname] * K * 0.85) / wt.height, cw * 1.9 / wt.width)
                N.put((wt, wm), wcx, top=y1 - 10, h=int(wt.height * kk), flip=True, behind=True)
            else:
                wt, wm = part(fwd[wname][facing]); kk = cw * 1.6 / wt.width
                N.put((wt, wm), wcx, top=y1 - 6, h=int(wt.height * kk), behind=True)
            if facing == 'south':
                if wname in spec.get('shields', ()):
                    pt = np.array(P.tex); pt[hole, 3] = 0; pm_ = np.array(P.mask); pm_[hole] = 0
                    S_ = Layer(); S_.tex = Image.fromarray(pt); S_.mask = Image.fromarray(np.where(pt[..., 3] > 100, pm_, 0).astype(np.uint8))
                    # the arm draws above the head for the shield; its plate must stay under the helmet
                    helm_a = np.array(pieces[('Helmet', 'south')].tex)[..., 3] > 100
                    under = helm_a & ~(np.array(N.tex)[..., 3] > 100)
                    st_ = np.array(S_.tex); st_[under, 3] = 0; S_.tex = Image.fromarray(st_)
                    sm_ = np.array(S_.mask); sm_[under] = 0; S_.mask = Image.fromarray(sm_)
                    S_.tex.alpha_composite(N.tex)
                    over = np.array(N.tex)[..., 3] > 20                    # over the shield only the shield's own paint
                    S_.mask = Image.fromarray(np.where(over, np.array(N.mask), np.array(S_.mask)).astype(np.uint8))
                    pieces[(p_, 'south')] = S_; continue
                pt = np.array(P.tex); pt[hole, 3] = 0; pm_ = np.array(P.mask); pm_[hole] = 0
                N.tex.alpha_composite(Image.fromarray(pt)); N.mask = Image.fromarray(np.maximum(np.array(N.mask), np.where(pt[..., 3] > 100, pm_, 0)).astype(np.uint8))
                pieces[(p_, 'south')] = N
            else:
                BP = north_plates[p_]
                if wname in spec.get('shields', ()):
                    # the shield is behind the body from this side: only what sticks out past the body shows
                    body_a = np.array(pieces[('Body', 'north')].tex)[..., 3] > 100
                    legs_a = np.array(pieces[('Legs', 'north')].tex)[..., 3] > 100
                    na = np.array(N.tex); hide = body_a | legs_a; na[hide, 3] = 0
                    nm = np.array(N.mask); nm[hide] = 0; N.tex = Image.fromarray(na); N.mask = Image.fromarray(nm)
                N.tex.alpha_composite(BP.tex); N.mask = Image.fromarray(np.maximum(np.array(N.mask), np.array(BP.mask)).astype(np.uint8))
                pieces[(p_, 'north')] = N
    if spec['body'].get('north_over_from'):
        # pack hardware sticking up (the net launcher) would hide under the shoulder plate facing north: what the
        # back painting adds over its base, in the top rows, is copied onto the topmost arm layer
        B = Layer(); put_like(B, spec['body']['north_over_from'], nref, cx, side_top, body_bb[3] - side_top)
        bt_ = np.array(pieces[('Body', 'north')].tex).astype(float); bb_ = np.array(B.tex).astype(float)
        add = (np.abs(bt_[..., :3] - bb_[..., :3]).max(2) > 40) & (bt_[..., 3] > 100)
        add[int(nb[1] + (nb[3] - nb[1]) * 0.30):] = False
        add = ndimage.binary_opening(add, iterations=2)
        add = ndimage.binary_dilation(ndimage.binary_fill_holes(ndimage.binary_closing(add, iterations=6)), iterations=3) & (bt_[..., 3] > 100)
        top = ORDER['north'][-1]; T = pieces[(top, 'north')]
        ov = np.array(pieces[('Body', 'north')].tex); ov[~add] = 0
        om = np.array(pieces[('Body', 'north')].mask); om[~add] = 0
        T.tex.alpha_composite(Image.fromarray(ov))
        T.mask = Image.fromarray(np.where(add, om, np.array(T.mask)).astype(np.uint8))
    if ('Body', 'northopen') in pieces:
        # the raised pack is attached at the top of the opening: drawn over the collar (and the head behind it)
        O = pieces[('Body', 'northopen')]; J = Layer(); J.tex = O.tex.copy(); J.mask = O.mask.copy()
        pa = np.array(open_pack.tex)[..., 3] > 100
        J.tex.alpha_composite(open_pack.tex)
        J.mask = Image.fromarray(np.where(pa, np.array(open_pack.mask), np.array(O.mask)).astype(np.uint8)); pieces[('Body', 'northopen')] = J
    # ---------------- save: helmet stored HEAD px lower (the game lifts it to the head)
    for (p, f), L in pieces.items():
        if p == 'Helmet': L.shift(HEAD)
        L.save(out, f'{p}_{f}')
    open(f'{out}/above_head.txt', 'w').write('\n'.join(sorted(front_over)))
    preview(out, spec.get('colors', [(0.56, 0.58, 0.60), (0.58, 0.60, 0.42)]))


ORDER = {'south': ['Legs', 'Body', 'ArmL', 'ArmR', 'Helmet'], 'east': ['ArmR', 'Legs', 'Body', 'Helmet', 'ArmL'],
         'north': ['Legs', 'Helmet', 'Body', 'ArmL', 'ArmR']}


def stack(out, facing, color=None):
    c = Image.new('RGBA', (C, C))
    order = list(ORDER[facing])
    try: over = [l for l in open(f'{out}/above_head.txt').read().split() if l]
    except OSError: over = []
    if facing == 'south':                      # a shield arm draws above the head facing south
        for p in over: order.remove(p); order.append(p)
    for p in order:
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


def _bulwark_base(sp):
    """the Bulwark; sp = folder with the source paintings (scratchpad or Source/Art/nano/modular)"""
    ws = ['minigun', 'rockets', 'chainsaw', 'laser', 'flamer', 'hammer', 'autocannon', 'grenade', 'arc', 'towershield']
    return dict(
        assembly=f'{sp}/kit_src', weapon_l='minigun', weapon_r='rockets',
        body=dict(east=f'{sp}/views/chassis_east_caps.png', north=f'{sp}/views/chassis_north_tall.png'), backpack_peek=True,
        helmet=dict(east=f'{sp}/views/helmet_east.png', north=f'{sp}/views/helmet_north.png'),
        plate=dict(east=f'{sp}/views/plate_east.png', north=f'{sp}/views/plate_north.png', back=f'{sp}/views/plate_back.png'),
        legs=dict(south=f'{sp}/views/legs_south.png', east=f'{sp}/views/legs_east2.png', north=f'{sp}/views/legs_north.png'),
        weapons_south={w: f'{sp}/weap/{w}.png' for w in ws},
        weapons_east={w: f'{sp}/weap_east/{w}.png' for w in ws},
        weapons_north={w: f'{sp}/weap_north/{w}.png' for w in ws},
        shields=('towershield',),
        weapons_back={w: f'{sp}/weap_back2/{w}.png' for w in ws},
        weapons_fwd={w: dict(south=f'{sp}/weap_fwd/{w}_south.png', north=f'{sp}/weap_fwd/{w}_north.png') for w in ws},
        full_east=dict(image=f'{sp}/views/full_east.png', body_image=f'{sp}/views/full_east_noarm.png', pieces={            # outlines in the 1024 painting
            'Helmet': [(372, 175), (378, 95), (450, 55), (650, 55), (705, 120), (705, 372), (640, 388), (590, 372), (560, 330), (540, 188)],
            'ArmL': [(285, 330), (345, 185), (545, 182), (605, 318), (605, 470), (545, 505), (505, 640), (455, 640), (345, 605), (285, 480)],
            'Legs': [(370, 772), (660, 772), (660, 1000), (370, 1000)]}),
        weapon_h={w: 120 for w in ws})


def bulwark_spec(sp):
    s = _bulwark_base(sp)
    s['body'] = dict(s['body'], cavity=f'{sp}/views/chassis_north_cavity.png', pack_base=f'{sp}/views/chassis_north_tall.png')
    if os.environ.get('PACK') == 'shield':          # the optional shield-generator backpack (three cells, emitter pylons)
        s['body'] = dict(s['body'], north=f'{sp}/own/chassis_north_shield.png', north_ref=f'{sp}/views/chassis_north_tall.png')
        s['full_east'] = dict(s['full_east'], body_image=f'{sp}/own/full_east_noarm_shield.png', body_ref=f'{sp}/views/full_east_noarm.png')
    return s


def bughunter_spec(sp):
    """the Bughunter: a Bulwark variant - shares body side/back, legs, plates and weapons; own front chest and helmet"""
    s = bulwark_spec(sp)
    s['helmet'] = dict(east=s['helmet']['east'], east_override=f'{sp}/own/bh_helmet_east.png', north=f'{sp}/own/bh_helmet_north.png')
    s['weapon_l'], s['weapon_r'] = 'flamer', 'hammer'
    s['colors'] = [(0.66, 0.56, 0.40), (0.56, 0.58, 0.60)]
    # its own side-view chest (the rounded chevron chest, not the Bulwark's slab plates): repainted from the
    # Bulwark's side painting, so the frame still lines up; own/full_east_bh_base.png is it without the launcher
    if os.environ.get('JUMP', '1') == '1':          # the jump-pack backpack (three cells, thrusters) with the net launcher on top
        s['body'] = dict(s['body'], north=f'{sp}/own/chassis_north_jumpnet.png', north_ref=f'{sp}/views/chassis_north_tall.png',
                         north_over_from=f'{sp}/own/chassis_north_jump.png')
        s['full_east'] = dict(s['full_east'], body_image=f'{sp}/own/full_east_bh_jumpnet.png', over_from=f'{sp}/own/full_east_bh_base.png', body_ref=f'{sp}/views/full_east_noarm.png')
    else:                                            # the plain pack, with the net launcher (a chassis ability) on top
        s['body'] = dict(s['body'], north=f'{sp}/own/chassis_north_net.png', north_ref=f'{sp}/views/chassis_north_tall.png',
                         north_over_from=f'{sp}/views/chassis_north_tall.png')
        s['full_east'] = dict(s['full_east'], body_image=f'{sp}/own/full_east_bh_net.png', over_from=f'{sp}/own/full_east_bh_base.png', body_ref=f'{sp}/views/full_east_noarm.png')
    # its light plates in the side view (pauldron + elbow paintings), not the Bulwark's painted heavy arm
    s['east_plates'] = {'flamer': f'{sp}/own/plate_east_fuel.png', 'hammer': f'{sp}/own/plate_east_pneumatic.png',
                        'none': f'{sp}/own/plate_east_fuel.png'}   # the near arm is the left (fuel) one
    return s


def work_spec(sp, tool, chest_side, pack_key=None):
    """a work suit on the Bulwark's frame: own chest (front export in kit_src, side painting), helmet views and
    tool arm (own/<tool>_front|east|back|fwd_south|fwd_north), the generic light open-frame plates, and the
    plain tall pack or (PACK=<pack_key>) its own pack (own/chassis_north_pack, <chest_side>_pack)"""
    s = bulwark_spec(sp)
    s['helmet'] = dict(east=s['helmet']['east'], east_override=f'{sp}/own/helmet_east.png', north=f'{sp}/own/helmet_north.png')
    s['weapon_l'], s['weapon_r'] = tool, tool
    s['weapons_south'] = dict(s['weapons_south'], **{tool: f'{sp}/own/{tool}_front.png'})
    s['weapons_east'] = dict(s['weapons_east'], **{tool: f'{sp}/own/{tool}_east.png'})
    s['weapons_north'] = dict(s['weapons_north'], **{tool: f'{sp}/own/{tool}_back.png'})
    s['weapons_back'] = dict(s['weapons_back'], **{tool: f'{sp}/own/{tool}_back.png'})
    s['weapons_fwd'] = dict(s['weapons_fwd'], **{tool: dict(south=f'{sp}/own/{tool}_fwd_south.png', north=f'{sp}/own/{tool}_fwd_north.png')})
    s['weapon_h'] = dict(s['weapon_h'], **{tool: 120})
    # the generic plate in the side view, whatever the arm carries
    s['east_plates'] = {w: f'{sp}/own/plate_east_generic.png' for w in (tool, 'none')}
    s['full_east'] = dict(s['full_east'], body_image=f'{sp}/own/{chest_side}.png', body_ref=f'{sp}/views/full_east_noarm.png')
    if pack_key and os.environ.get('PACK') == pack_key:
        s['body'] = dict(s['body'], north=f'{sp}/own/chassis_north_pack.png', north_ref=f'{sp}/views/chassis_north_tall.png')
        s['full_east'] = dict(s['full_east'], body_image=f'{sp}/own/{chest_side}_pack.png')
    return s


def miner_spec(sp):
    """the Miner: drill arms; PACK=booster for the drill booster pack"""
    s = work_spec(sp, 'drill', 'full_east_miner', 'booster')
    s['colors'] = [(0.78, 0.62, 0.30), (0.56, 0.58, 0.60)]
    return s


def builder_spec(sp):
    """the Builder: combo construction drill + nail gun arms"""
    s = work_spec(sp, 'combo', 'full_east_builder')
    s['colors'] = [(0.86, 0.66, 0.22), (0.56, 0.58, 0.60)]
    return s


SPECS = {'bulwark': bulwark_spec, 'bughunter': bughunter_spec, 'miner': miner_spec, 'builder': builder_spec}

if __name__ == '__main__':
    sp, out = sys.argv[1], sys.argv[2]
    spec = SPECS[os.environ.get('SPEC', 'bulwark')](sp)
    if os.environ.get('ASSEMBLY'): spec['assembly'] = os.environ['ASSEMBLY']   # e.g. a kit_src exported for other arms
    for k in ('weapon_l', 'weapon_r'):
        if os.environ.get(k.upper()): spec[k] = os.environ[k.upper()]
    build(spec, out)
