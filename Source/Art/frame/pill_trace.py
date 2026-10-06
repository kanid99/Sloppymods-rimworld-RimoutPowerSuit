"""Owner's pill-body sheet (east/south/north) traced by part, reduced to RimWorld tintable grey, and fitted to our
frame canvas (320 = 2.717 tiles): helmet top at the raised pilot's head (y 52), base at the frame's feet (y 318).
    python3 pill_trace.py <out dir> <sheet image>"""
import colorsys, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage
from scipy.cluster.vq import kmeans2
import vtracer

out, SRC = sys.argv[1], sys.argv[2]
UP = 3
sheet = Image.open(SRC).convert('RGB')
BG = np.array(sheet.getpixel((5, 5)), float)
TOP, BOT = 52, 318

VIEWS = {
    'south': ((348, 64, 674, 562), [
        ('pauldron_left', [(348, 175), (448, 175), (448, 305), (348, 305)]),
        ('pauldron_right', [(574, 175), (674, 175), (674, 305), (574, 305)]),
        ('helmet', [(415, 64), (607, 64), (607, 240), (415, 240)]),
        ('body', [(348, 64), (674, 64), (674, 562), (348, 562)])]),
    'north': ((694, 64, 1008, 562), [
        ('pauldron_left', [(694, 178), (790, 178), (790, 300), (694, 300)]),
        ('pauldron_right', [(912, 178), (1008, 178), (1008, 300), (912, 300)]),
        ('helmet', [(750, 64), (950, 64), (950, 168), (750, 168)]),
        ('body', [(694, 64), (1008, 64), (1008, 562), (694, 562)])]),
    'east': ((14, 64, 312, 562), [
        ('pack', [(14, 120), (100, 120), (100, 410), (14, 410)]),
        ('shoulder', [(96, 188), (240, 188), (240, 335), (96, 335)]),
        ('helmet', [(90, 64), (312, 64), (312, 245), (240, 245), (240, 188), (90, 188)]),
        ('body', [(14, 64), (312, 64), (312, 562), (14, 562)])]),
}
DRAW_ORDER = {'south': ['body', 'pauldron_left', 'pauldron_right', 'helmet'],
              'north': ['body', 'helmet', 'pauldron_left', 'pauldron_right'],
              'east': ['pack', 'body', 'helmet', 'shoulder']}

def reduce(rgb, alpha, k=7):
    px = np.array(rgb).reshape(-1, 3).astype(float); on = alpha.reshape(-1) > 0
    cent, lab = kmeans2(px[on], k, minit='++', seed=3)
    out = []
    for c in cent:
        r, g, b = c / 255; h, s, v = colorsys.rgb_to_hsv(r, g, b); lum = 0.3 * r + 0.59 * g + 0.11 * b
        if v > 0.82 and s < 0.15:                 # the white star decal: keep
            out.append(c)
        elif lum < 0.12:                          # outline: soft dark grey-brown
            out.append(np.array([44, 40, 40.0]))
        else:                                     # plates, rust, wear: neutral grey for the tint
            g_ = min(235, 30 + lum * 255 * 1.35); out.append(np.array([g_, g_, g_ + 3]))
    q = np.zeros_like(px); q[on] = np.array(out)[lab]
    return np.dstack([q.reshape(alpha.shape + (3,)).astype(np.uint8), alpha])

for view, ((x0, y0, x1, y1), parts) in VIEWS.items():
    im = sheet.crop((x0, y0, x1, y1)); w, h = im.size
    im = im.resize((w * UP, h * UP), Image.LANCZOS)
    a = np.array(im).astype(float)
    near = np.sqrt(((a - BG) ** 2).sum(-1)) < 28
    lab, _ = ndimage.label(near)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    alpha = (~ndimage.binary_opening(np.isin(lab, list(edge)), iterations=2)).astype(np.uint8) * 255
    rgb = Image.fromarray(np.array(im)).filter(ImageFilter.MedianFilter(5))
    taken = np.zeros(alpha.shape, bool); groups = {}
    for name, poly in parts:
        m = Image.new('L', im.size); ImageDraw.Draw(m).polygon([((x - x0) * UP, (y - y0) * UP) for x, y in poly], fill=255)
        mine = (np.array(m) > 0) & ~taken & (alpha > 0); taken |= mine
        rgba = reduce(rgb, (mine * 255).astype(np.uint8))
        p = f'pill_parts/{view}_{name}.png'; Image.fromarray(rgba, 'RGBA').save(p)
        vtracer.convert_image_to_svg_py(p, p[:-4] + '.svg', colormode='color', hierarchical='stacked', mode='spline',
                                        filter_speckle=12, color_precision=8, layer_difference=6, corner_threshold=60,
                                        length_threshold=4.0, splice_threshold=45, path_precision=1)
        body = open(p[:-4] + '.svg').read(); groups[name] = body[body.index('<path'):body.rindex('</svg>')]
    s = (BOT - TOP) / (h * UP); tx = 160 - w * UP * s / 2
    inner = ''.join(f'<g id="{n}">{groups[n]}</g>' for n in DRAW_ORDER[view])
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 320" width="320" height="320"><title>Pill-body suit ({view})</title>'
           f'<g transform="translate({tx:.2f} {TOP}) scale({s:.5f})">{inner}</g></svg>')
    open(f'{out}/svg/pill_suit_{view}.svg', 'w').write(svg)
    print(view, len(svg) // 1024, 'KB')
