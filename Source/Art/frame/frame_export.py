"""Frame v5 deliverables:
  1. frame_sheet_v5.png - the still views (south, east, north shut, north open), with and without the pawn
  2. frame_kit/ - the frame as game-ready layers (320x320, drawSize 2.717, pawn position at the centre),
     the hatch at 6 swing stages per facing, a guide sheet and a README with the draw order
  3. fit_<Suit>.png - the current suit art laid over the frame, per facing
    python3 frame_export.py <out dir> <vanilla Pawn/Humanlike dir> <mod root>"""
import math, os, sys
from PIL import Image, ImageDraw, ImageFont
import frame4 as F
import frame5 as G
from frame4 import C, RAISE

out, art, mod = sys.argv[1], sys.argv[2], sys.argv[3]
L = lambda fn: G.layer(fn, C)
BG = (96, 92, 98, 255)
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 13)
OPEN = 0.75 * math.pi
STAGES = [OPEN * i / 5 for i in range(6)]          # stage 0 = shut ... stage 5 = fully open

def on_bg(im, bg=BG):
    b = Image.new('RGBA', im.size, bg); b.alpha_composite(im); return b

# ------------------------------------------------------------------ 1. still sheet
def still(facing, opened, pilot):
    th = OPEN if opened else 0
    p = ('in', 0, -RAISE) if pilot else None
    return G.compose(art, facing, th, p, C, 0)

cols = [('south', 'south', False), ('east', 'east', False), ('north (shut)', 'north', False), ('north (open)', 'north', True), ('east (open)', 'east', True)]
Z = 2
sh = Image.new('RGB', (170 + len(cols) * C * Z, 46 + 2 * C * Z), (236, 230, 220)); sd = ImageDraw.Draw(sh)
for i, (lab, f, o) in enumerate(cols):
    sd.text((170 + i * C * Z + 16, 12), lab, fill=(20, 20, 20), font=font)
for j, (lab, pw) in enumerate((('frame', False), ('frame + pawn', True))):
    sd.text((10, 46 + j * C * Z + C * Z // 2), lab, fill=(20, 20, 20), font=font)
    for i, (_, f, o) in enumerate(cols):
        sh.paste(on_bg(still(f, o, pw)).resize((C * Z, C * Z), Image.LANCZOS).convert('RGB'), (170 + i * C * Z, 46 + j * C * Z))
sh.save(f'{out}/frame_sheet_v5.png')

# ------------------------------------------------------------------ 2. layered kit
kit = f'{out}/frame_kit'
os.makedirs(kit, exist_ok=True)
layers = {
    'south': [('Frame_back', G.south_back), ('Frame_front', lambda d: F.south(d, 'front'))],
    'east': [('Frame_back', lambda d: F.east(d, 'back')), ('Frame_front', lambda d: F.east(d, 'front'))],
    'north': [('Frame_back', G.north_far), ('Frame_front', G.north_near), ('Collar_front', G.collar_front), ('Hinges', G.hinges)],
}
hatch = {'south': lambda th: (lambda d: G.hatch(d, th, -1)),
         'east': lambda th: (lambda d: F.east_hood(d, th)),
         'north': lambda th: (lambda d: G.hatch(d, th, 1))}
made = {}
for f, ls in layers.items():
    made[f] = []
    for name, fn in ls:
        im = L(fn); im.save(f'{kit}/{name}_{f}.png'); made[f].append((name, im))
    for i, th in enumerate(STAGES):
        im = L(hatch[f](th)); im.save(f'{kit}/Hatch_{f}_stage{i}.png'); made[f].append((f'Hatch stage {i}', im))
    body, head = F.pawn_parts(art, f)
    ref = Image.new('RGBA', (C, C)); ref.alpha_composite(body, (0, -RAISE)); ref.alpha_composite(head, (0, -RAISE))
    ref.save(f'{kit}/Pilot_reference_{f}.png')

# guide sheet: every layer on a checker, with the pawn position, head, collar and feet lines and the tile grid
TILE = C / 2.717
def guides(im, label):
    g = Image.new('RGBA', (C, C), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    for yy in range(0, C, 16):
        for xx in range(0, C, 16):
            gd.rectangle((xx, yy, xx + 15, yy + 15), fill=(214, 210, 204, 255) if (xx + yy) // 16 % 2 else (232, 228, 222, 255))
    g.alpha_composite(im); gd = ImageDraw.Draw(g)
    for k in range(-2, 3):                                            # tile grid round the pawn position
        v = 160 + k * TILE
        gd.line((v, 0, v, C), fill=(120, 160, 220, 120)); gd.line((0, v, C, v), fill=(120, 160, 220, 120))
    for y, col in ((58, (40, 160, 60, 255)), (108, (200, 120, 0, 255)), (318, (200, 40, 40, 255))):
        gd.line((0, y, C, y), fill=col)
    gd.line((150, 160, 170, 160), fill=(255, 0, 0, 255)); gd.line((160, 150, 160, 170), fill=(255, 0, 0, 255))
    gd.text((4, 302), label, fill=(20, 20, 20), font=small)
    return g
rows = list(made.items())
wmax = max(len(v) for _, v in rows)
gs = Image.new('RGB', (wmax * (C + 8) + 8, len(rows) * (C + 30) + 40), (250, 248, 244)); gsd = ImageDraw.Draw(gs)
gsd.text((8, 8), 'green: head top (pilot raised)   orange: chin / collar   red: feet   red cross: pawn position   blue: tile grid (1 tile = 117.8 px)', fill=(20, 20, 20), font=small)
for j, (f, ims) in enumerate(rows):
    gsd.text((8, 30 + j * (C + 30)), f, fill=(20, 20, 20), font=font)
    for i, (name, im) in enumerate(ims):
        gs.paste(guides(im, name).convert('RGB'), (8 + i * (C + 8), 52 + j * (C + 30)))
gs.save(f'{kit}/GUIDE.png')
open(f'{kit}/README.txt', 'w').write('''POWER ARMOUR FRAME - layer kit (concept art, not yet in the mod)

Every file is 320 x 320 px on the suit's canvas: drawSize (2.717, 2.717), the pawn's position at the
centre (160,160), the same as the suit textures in Textures/Things/Pawn/PowerSuit/. West = east mirrored.
Redraw any layer in place (same size, same position) and it drops straight in.

Draw order, back to front (the pilot's body and head are the game's own pawn, drawn 26 px higher than
normal so the head clears the collar - see Pilot_reference_*.png):

SOUTH   Hatch_south_stageN  ->  Frame_back_south  ->  pilot  ->  Frame_front_south
        (while the pilot walks up behind the frame, they go first, under the raised hatch; once inside only
         what rises above y = 112 shows, so the head comes up through the collar)
EAST    Frame_back_east  ->  pilot  ->  Hatch_east_stageN  ->  Frame_front_east
NORTH   Frame_back_north  ->  pilot body  ->  Frame_front_north  ->  pilot head  ->  Collar_front_north
        ->  Hinges_north (only while shut; once the hatch moves they go under it)  ->  Hatch_north_stageN
        (while the pilot walks up from behind, they are drawn last, over everything)

Hatch stages: 0 = shut, 5 = fully open (135 degrees), evenly spaced. In game the climb-in plays
open 0->5, pilot steps in, close 5->0.
GUIDE.png shows every layer with the pawn position, head, collar and feet lines and the tile grid.
''')

# ------------------------------------------------------------------ 3. fit check against the current suits
ORDER = {'south': ['Legs', 'Body', 'ArmL', 'ArmR', 'Helmet'], 'east': ['ArmR', 'Legs', 'Body', 'Helmet', 'ArmL'],
         'north': ['Legs', 'Helmet', 'Body', 'ArmL', 'ArmR']}
def suit_image(suit, f):
    im = Image.new('RGBA', (C, C))
    for p in ORDER[f]:
        path = f'{mod}/Textures/Things/Pawn/PowerSuit/{suit}/{p}_{f}.png'
        if os.path.exists(path):
            im.alpha_composite(Image.open(path).convert('RGBA').resize((C, C)))
    return im
def outline(im, col):
    import numpy as np
    from PIL import ImageFilter
    a = im.split()[3].point(lambda v: 255 if v > 60 else 0)
    e = Image.fromarray((np.array(a.filter(ImageFilter.MaxFilter(3))).astype(int) - np.array(a)).clip(0, 255).astype('uint8'))
    o = Image.new('RGBA', im.size, col); o.putalpha(e); return o
for suit in ('Bulwark', 'Bughunter', 'Miner', 'Builder'):
    Z = 2
    fs = Image.new('RGB', (150 + 3 * C * Z, 46 + 3 * C * Z), (236, 230, 220)); fd = ImageDraw.Draw(fs)
    for i, lab in enumerate(('frame (shut)', f'{suit} (current art)', 'suit outline (red) over frame')):
        fd.text((150 + i * C * Z + 16, 12), lab, fill=(20, 20, 20), font=font)
    for j, f in enumerate(('south', 'east', 'north')):
        fd.text((10, 46 + j * C * Z + C * Z // 2), f, fill=(20, 20, 20), font=font)
        fr = G.compose(art, f, 0, None, C, 0); su = suit_image(suit, f)
        ov = on_bg(fr); ov.alpha_composite(outline(su, (255, 40, 40, 255)))
        for i, im in enumerate((on_bg(fr), on_bg(su), ov)):
            fs.paste(im.resize((C * Z, C * Z), Image.LANCZOS).convert('RGB'), (150 + i * C * Z, 46 + j * C * Z))
    fs.save(f'{out}/fit_{suit}.png')
print('done')
