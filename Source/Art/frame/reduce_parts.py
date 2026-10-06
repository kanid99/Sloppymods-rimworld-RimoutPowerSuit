"""RimWorld reduction of the traced target: per part, smooth out grime, quantise to a few flat tones, turn the
olive/rust plate colours into neutral grey of the same lightness (so the suit tint applies), keep accents
(hazard yellow, gauge, visor, dark joints), soften the black outline to a dark grey-brown, trace with coarser speckle."""
import colorsys, sys
import numpy as np
from PIL import Image, ImageFilter
from scipy.cluster.vq import kmeans2
import vtracer

order = ['exhaust', 'leg_left', 'leg_right', 'torso', 'arm_left', 'arm_right', 'pauldron_left', 'pauldron_right', 'helmet']
K = {'helmet': 10, 'torso': 12}
groups = {}
np.random.seed(3)
for name in order:
    im = Image.open(f'target_parts/{name}.png').convert('RGBA')
    a = np.array(im); alpha = a[..., 3]
    rgb = Image.fromarray(a[..., :3]).filter(ImageFilter.MedianFilter(7))
    px = np.array(rgb).reshape(-1, 3).astype(float); on = alpha.reshape(-1) > 0
    cent, lab = kmeans2(px[on], K.get(name, 8), minit='++', seed=3)
    out = []
    for c in cent:
        r, g, b = c / 255; h, s, v = colorsys.rgb_to_hsv(r, g, b)
        lum = 0.3 * r + 0.59 * g + 0.11 * b
        if s > 0.5 and v > 0.55 and 0.08 < h < 0.17:          # hazard yellow / gauge: keep
            out.append(c)
        elif lum < 0.14:                                      # outline: soften to dark grey-brown
            out.append(np.array([52, 46, 44.0]))
        elif lum < 0.24:                                      # dark joints / undersuit: neutral dark
            g_ = lum * 255; out.append(np.array([g_, g_, g_ + 4]))
        elif v > 0.72 and s < 0.3 and name == 'torso':        # the cream star decal: keep, untinted
            out.append(c)
        else:                                                 # plates (olive, rust, wear): neutral grey for the tint, contrast kept
            g_ = min(232, 40 + lum * 255 * 1.2); out.append(np.array([g_, g_, g_ + 3]))
    q = np.zeros_like(px); q[on] = np.array(out)[lab]
    qa = np.dstack([q.reshape(a.shape[:2] + (3,)).astype(np.uint8), alpha])
    Image.fromarray(qa, 'RGBA').save(f'target_parts/{name}_rw.png')
    vtracer.convert_image_to_svg_py(f'target_parts/{name}_rw.png', f'target_parts/{name}_rw.svg', colormode='color',
                                    hierarchical='stacked', mode='spline', filter_speckle=14, color_precision=8,
                                    layer_difference=6, corner_threshold=60, length_threshold=4.0, splice_threshold=45, path_precision=1)
    body = open(f'target_parts/{name}_rw.svg').read()
    groups[name] = body[body.index('<path'):body.rindex('</svg>')]
W0, H0 = 435, 705
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W0 * 3} {H0 * 3}" width="{W0}" height="{H0}"><title>Target suit, RimWorld reduction</title>'
       + ''.join(f'<g id="{n}">{groups[n]}</g>' for n in order) + '</svg>')
open(f'{sys.argv[1]}/svg/target_rimworld.svg', 'w').write(svg)
print(len(svg) // 1024, 'KB', svg.count('<path'), 'paths')
