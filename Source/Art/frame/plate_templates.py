"""Plate templates over the frame: for each facing, the frame (shut, pilot in) faded, with the zone each
fitted part covers marked. Template_<facing>.png is 320x320 on the suit canvas, to draw plates over;
PLATE_TEMPLATES.png is the labelled overview.
    python3 plate_templates.py <out dir> <vanilla Pawn/Humanlike dir>"""
import math, os, sys
from PIL import Image, ImageDraw, ImageFont
import frame5 as G
from frame4 import C, RAISE, X

out, art = sys.argv[1], sys.argv[2]
kit = f'{out}/frame_kit'
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 11)
big = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
COL = {'Helmet': (220, 60, 60), 'Chest plate': (60, 140, 220), 'Pack (on the hatch)': (150, 80, 200),
       'Pack (behind)': (150, 80, 200), 'Arm': (40, 170, 90), 'Leg': (230, 150, 30)}
HEAD = [(160 + 34 * math.cos(a / 16 * math.pi), 82 + 30 * math.sin(a / 16 * math.pi)) for a in range(32)]
ZONES = {
    'south': [('Pack (behind)', [(124, 84), (196, 84), (204, 104), (116, 104)]),
              ('Helmet', HEAD),
              ('Chest plate', [(116, 106), (204, 106), (222, 124), (222, 182), (196, 196), (124, 196), (98, 182), (98, 124)]),
              ('Arm', [(204, 100), (264, 100), (268, 140), (266, 242), (226, 242), (222, 150)]),
              ('Arm', X([(204, 100), (264, 100), (268, 140), (266, 242), (226, 242), (222, 150)], -1)),
              ('Leg', [(170, 224), (216, 224), (214, 298), (176, 298)]),
              ('Leg', X([(170, 224), (216, 224), (214, 298), (176, 298)], -1))],
    'east': [('Pack (on the hatch)', [(72, 92), (138, 92), (142, 208), (84, 212), (70, 160)]),
             ('Helmet', [(x + 4, y) for x, y in HEAD]),
             ('Chest plate', [(142, 104), (196, 112), (212, 144), (206, 178), (186, 196), (142, 196)]),
             ('Arm', [(134, 102), (190, 104), (194, 140), (204, 222), (196, 262), (166, 262), (154, 150)]),
             ('Leg', [(140, 226), (186, 228), (186, 300), (138, 300)])],
    'north': [('Helmet', HEAD),
              ('Pack (on the hatch)', [(114, 96), (206, 96), (212, 120), (206, 190), (186, 204), (134, 204), (114, 190), (108, 120)]),
              ('Arm', [(204, 100), (264, 100), (268, 140), (266, 242), (226, 242), (222, 150)]),
              ('Arm', X([(204, 100), (264, 100), (268, 140), (266, 242), (226, 242), (222, 150)], -1)),
              ('Leg', [(170, 224), (216, 224), (214, 298), (176, 298)]),
              ('Leg', X([(170, 224), (216, 224), (214, 298), (176, 298)], -1))],
}
Z = 2
sheet = Image.new('RGB', (3 * C * Z + 40, C * Z + 150), (250, 248, 244)); sd = ImageDraw.Draw(sheet)
for i, (f, zones) in enumerate(ZONES.items()):
    fr = G.compose(art, f, 0, ('in', 0, -RAISE), C, 0)
    a = fr.split()[3].point(lambda v: v * 0.45)
    faded = fr.copy(); faded.putalpha(a)
    t = Image.new('RGBA', (C, C), (255, 255, 255, 255)); t.alpha_composite(faded)
    ov = Image.new('RGBA', (C, C)); od = ImageDraw.Draw(ov)
    for name, pts in zones:
        c = COL[name]
        od.polygon(pts, fill=c + (46,), outline=c + (255,), width=2)
    t.alpha_composite(ov)
    t.save(f'{kit}/Template_{f}.png')
    big_t = t.resize((C * Z, C * Z), Image.LANCZOS); bd = ImageDraw.Draw(big_t)
    for name, pts in zones:
        cx = sum(x for x, _ in pts) / len(pts) * Z; cy = sum(y for _, y in pts) / len(pts) * Z
        w = bd.textlength(name, font=font)
        bd.rectangle((cx - w / 2 - 3, cy - 8, cx + w / 2 + 3, cy + 8), fill=(255, 255, 255, 230))
        bd.text((cx - w / 2, cy - 7), name, fill=COL[name] + (255,), font=font)
    sheet.paste(big_t.convert('RGB'), (20 + i * C * Z, 40))
    sd.text((20 + i * C * Z, 12), f, fill=(20, 20, 20), font=big)
sd.text((20, C * Z + 52), 'Plates are drawn to the frame (option A). Arms and legs: one zone per side, left and right drawn separately.\n'
        'The pack rides on the back hatch: drawn flat on the shut hatch, then fitted to each hatch stage (it swings up with it).\n'
        'Helmet: optional; when fitted it covers the pilot\'s head (shown here at the raised pilot height).\n'
        'Chest plate: the front of the torso (south/east). From the north the hatch and pack cover the back.', fill=(20, 20, 20), font=font)
sheet.save(f'{kit}/PLATE_TEMPLATES.png')
print('ok')
