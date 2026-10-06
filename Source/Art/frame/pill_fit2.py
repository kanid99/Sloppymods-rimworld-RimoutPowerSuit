"""Pill-body sheets (east/south/north per suit) broken into pieces and fitted to our frame canvas, any number of
suits. Part cuts are given relative to each view's box (taken from the first sheet), colour rules per suit.
    python3 pill_fit2.py <out dir>"""
import colorsys, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage
from scipy.cluster.vq import kmeans2
import vtracer

out = sys.argv[1]
UP = 3
U = '/root/.claude/uploads/5d357003-b193-5b47-8842-37bd7505c103/'
# part cuts relative to the view box (x, y in 0..1), from the first sheet
def rel(box, poly):
    x0, y0, x1, y1 = box
    return [((x - x0) / (x1 - x0), (y - y0) / (y1 - y0)) for x, y in poly]
B0 = {'south': (348, 64, 674, 562), 'north': (694, 64, 1008, 562), 'east': (14, 64, 312, 562)}
CUTS = {
    'south': [('pauldron_left', rel(B0['south'], [(348, 175), (448, 175), (448, 305), (348, 305)])),
              ('pauldron_right', rel(B0['south'], [(574, 175), (674, 175), (674, 305), (574, 305)])),
              ('helmet', rel(B0['south'], [(415, 64), (607, 64), (607, 240), (415, 240)])),
              ('groin', rel(B0['south'], [(476, 440), (548, 440), (548, 530), (476, 530)])),
              ('belt', rel(B0['south'], [(348, 408), (674, 408), (674, 462), (348, 462)])),
              ('chest', rel(B0['south'], [(398, 228), (626, 228), (626, 410), (398, 410)]))],
    'north': [('pauldron_left', rel(B0['north'], [(694, 178), (790, 178), (790, 300), (694, 300)])),
              ('pauldron_right', rel(B0['north'], [(912, 178), (1008, 178), (1008, 300), (912, 300)])),
              ('helmet', rel(B0['north'], [(750, 64), (950, 64), (950, 168), (750, 168)])),
              ('groin', rel(B0['north'], [(792, 432), (910, 432), (910, 528), (792, 528)])),
              ('belt', rel(B0['north'], [(694, 405), (1008, 405), (1008, 460), (694, 460)])),
              ('chest', rel(B0['north'], [(744, 160), (958, 160), (958, 407), (744, 407)]))],
    'east': [('pack', rel(B0['east'], [(14, 120), (100, 120), (100, 410), (14, 410)])),
             ('shoulder', rel(B0['east'], [(96, 188), (240, 188), (240, 335), (96, 335)])),
             ('helmet', rel(B0['east'], [(90, 64), (312, 64), (312, 245), (240, 245), (240, 188), (90, 188)])),
             ('belt', rel(B0['east'], [(14, 405), (312, 405), (312, 468), (14, 468)])),
             ('chest', rel(B0['east'], [(96, 186), (312, 186), (312, 407), (96, 407)]))],
}
PLACE = {
    'south': {'helmet': (160, 46, None, 78), 'chest': (160, 100, None, 130), 'pauldron_left': (80, None, 126, 64),
              'pauldron_right': (240, None, 126, 64), 'belt': (160, 200, None, 128), 'groin': (160, 214, None, 34)},
    'north': {'helmet': (160, 48, None, 80), 'chest': (160, 98, None, 130), 'pauldron_left': (78, None, 128, 62),
              'pauldron_right': (242, None, 128, 62), 'belt': (160, 200, None, 128), 'groin': (160, 212, None, 46)},
    'east': {'pack': (112, 92, None, 34), 'helmet': (166, 46, None, 84), 'chest': (158, 100, None, 92),
             'shoulder': (160, None, 142, 58), 'belt': (160, 200, None, 92)},
}
ORDER = {'south': ['belt', 'groin', 'chest', 'pauldron_left', 'pauldron_right', 'helmet'],
         'north': ['belt', 'groin', 'chest', 'helmet', 'pauldron_left', 'pauldron_right'],
         'east': ['pack', 'belt', 'chest', 'helmet', 'shoulder']}

def keep_classic(h, s, v):   return v > 0.82 and s < 0.15                       # the white star
def keep_mining(h, s, v):    return v > 0.86 and s < 0.5                        # headlamps
def keep_future(h, s, v):    return s > 0.45 and v > 0.45                       # red visor, orange/cyan lights
SUITS = {
    'classic': (U + '5bfa7880-image.jpg', B0, keep_classic),
    'mining': (U + '7d027756-image.jpg', {'east': (12, 52, 250, 430), 'south': (290, 55, 540, 425), 'north': (565, 55, 815, 430)}, keep_mining),
    'future': (U + '7d027756-image.jpg', {'east': (15, 565, 255, 945), 'south': (290, 570, 545, 945), 'north': (565, 565, 815, 950)}, keep_future),
}

def reduce(rgb, alpha, keep, k=8):
    px = np.array(rgb).reshape(-1, 3).astype(float); on = alpha.reshape(-1) > 0
    cent, lab = kmeans2(px[on], k, minit='++', seed=3)
    res = []
    for c in cent:
        r, g, b = c / 255; h, s, v = colorsys.rgb_to_hsv(r, g, b); lum = 0.3 * r + 0.59 * g + 0.11 * b
        if keep(h, s, v): res.append(c)
        elif lum < 0.12: res.append(np.array([44, 40, 40.0]))
        else:
            g_ = min(235, 30 + lum * 255 * 1.35); res.append(np.array([g_, g_, g_ + 3]))
    q = np.zeros_like(px); q[on] = np.array(res)[lab]
    return np.dstack([q.reshape(alpha.shape + (3,)).astype(np.uint8), alpha])

for suit, (src, boxes, keep) in SUITS.items():
    sheet = Image.open(src).convert('RGB'); BG = np.array(sheet.getpixel((5, 5)), float)
    for view, (x0, y0, x1, y1) in boxes.items():
        im = sheet.crop((x0, y0, x1, y1)); w, h = im.size
        im = im.resize((w * UP, h * UP), Image.LANCZOS); a = np.array(im).astype(float)
        near = np.sqrt(((a - BG) ** 2).sum(-1)) < 28
        lab, _ = ndimage.label(near)
        edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
        alpha = (~ndimage.binary_opening(np.isin(lab, list(edge)), iterations=2)).astype(np.uint8) * 255
        rgb = Image.fromarray(np.array(im)).filter(ImageFilter.MedianFilter(5))
        taken = np.zeros(alpha.shape, bool); groups = {}; bx = {}
        for name, poly in CUTS[view]:
            m = Image.new('L', im.size); ImageDraw.Draw(m).polygon([(px_ * w * UP, py_ * h * UP) for px_, py_ in poly], fill=255)
            mine = (np.array(m) > 0) & ~taken & (alpha > 0); taken |= mine
            if not mine.any(): continue
            ys_, xs_ = np.nonzero(mine); bx[name] = (xs_.min(), ys_.min(), xs_.max(), ys_.max())
            p = f'pill_parts/{suit}_{view}_{name}.png'
            Image.fromarray(reduce(rgb, (mine * 255).astype(np.uint8), keep), 'RGBA').save(p)
            vtracer.convert_image_to_svg_py(p, p[:-4] + '.svg', colormode='color', hierarchical='stacked', mode='spline',
                                            filter_speckle=12, color_precision=8, layer_difference=6, corner_threshold=60,
                                            length_threshold=4.0, splice_threshold=45, path_precision=1)
            body = open(p[:-4] + '.svg').read(); groups[name] = body[body.index('<path'):body.rindex('</svg>')]
        inner = ''
        for n in ORDER[view]:
            if n not in bx: continue
            bx0, by0, bx1, by1 = bx[n]; cx, top, cy, wd = PLACE[view][n]
            sc = wd / (bx1 - bx0); hh = (by1 - by0) * sc
            ty = top if top is not None else cy - hh / 2
            inner += f'<g id="{n}" transform="translate({cx - wd / 2:.2f} {ty:.2f}) scale({sc:.5f}) translate({-bx0} {-by0})">{groups[n]}</g>'
        open(f'{out}/svg/pill_pieces_{suit}_{view}.svg', 'w').write(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 320" width="320" height="320"><title>{suit} pieces on the frame ({view})</title>{inner}</svg>')
        print(suit, view)
