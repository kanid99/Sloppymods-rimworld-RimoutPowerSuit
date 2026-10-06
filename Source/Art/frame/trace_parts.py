"""Trace the owner's target image to SVG part by part (each part its own group), so pieces stay editable."""
import re, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
import vtracer

SRC = '/root/.claude/uploads/5d357003-b193-5b47-8842-37bd7505c103/07c06321-image.jpg'
UP = 3
im = Image.open(SRC).convert('RGB').crop((20, 200, 455, 905))
W0, H0 = im.size
bgc = np.array(im.getpixel((5, 5)), float)
im = im.resize((W0 * UP, H0 * UP), Image.LANCZOS)
a = np.array(im).astype(float)
near = np.sqrt(((a - bgc) ** 2).sum(-1)) < 30
lab, _ = ndimage.label(near)
edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
bgmask = np.isin(lab, list(edge))
bgmask = ndimage.binary_opening(bgmask, iterations=2)
alpha = (~bgmask).astype(np.uint8) * 255

M = lambda p: [(435 - x, y) for x, y in p]
PARTS = [('helmet', [(135, 10), (285, 10), (296, 100), (286, 172), (138, 172), (126, 100)]),
         ('exhaust', [(296, 8), (352, 8), (352, 112), (296, 112)]),
         ('pauldron_left', [(4, 90), (140, 80), (152, 172), (132, 218), (104, 238), (4, 234)]),
         ('pauldron_right', M([(4, 90), (140, 80), (152, 172), (132, 218), (104, 238), (4, 234)])),
         ('arm_left', [(4, 214), (132, 214), (138, 285), (128, 474), (4, 474)]),
         ('arm_right', M([(4, 214), (132, 214), (138, 285), (128, 474), (4, 474)])),
         ('torso', [(92, 150), (343, 150), (348, 332), (266, 336), (252, 402), (184, 402), (169, 336), (88, 332)]),
         ('leg_left', [(70, 300), (218, 300), (218, 705), (70, 705)]),
         ('leg_right', [(218, 300), (366, 300), (366, 705), (218, 705)])]
taken = np.zeros(alpha.shape, bool)
groups = []
for name, poly in PARTS:
    m = Image.new('L', (W0 * UP, H0 * UP)); ImageDraw.Draw(m).polygon([(x * UP, y * UP) for x, y in poly], fill=255)
    mine = (np.array(m) > 0) & ~taken & (alpha > 0)
    taken |= mine
    rgba = np.dstack([np.array(im), (mine * 255).astype(np.uint8)])
    p = f'target_parts/{name}.png'; Image.fromarray(rgba, 'RGBA').save(p)
    vtracer.convert_image_to_svg_py(p, f'target_parts/{name}.svg', colormode='color', hierarchical='stacked', mode='spline',
                                    filter_speckle=8, color_precision=6, layer_difference=14, corner_threshold=60,
                                    length_threshold=4.0, splice_threshold=45, path_precision=1)
    body = open(f'target_parts/{name}.svg').read()
    body = body[body.index('<path'):body.rindex('</svg>')]
    groups.append((name, body))
rest = (alpha > 0) & ~taken
print('unassigned px:', int(rest.sum()))
order = ['exhaust', 'leg_left', 'leg_right', 'torso', 'arm_left', 'arm_right', 'pauldron_left', 'pauldron_right', 'helmet']
gd = dict(groups)
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W0 * UP} {H0 * UP}" width="{W0}" height="{H0}"><title>Target suit (traced by part)</title>'
       + ''.join(f'<g id="{n}">{gd[n]}</g>' for n in order) + '</svg>')
open(f'{sys.argv[1]}/svg/target_traced_parts.svg', 'w').write(svg)
print(len(svg) // 1024, 'KB', svg.count('<path'), 'paths')
