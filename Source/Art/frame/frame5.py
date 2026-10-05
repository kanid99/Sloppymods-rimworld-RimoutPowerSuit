"""Frame v5 climb-in: the back hatch as a solid shell (rotated in 3D about its hinge, drawn with a slight
top-down tilt so its depth shows), a fixed collar ring with the neck hole in the frame itself, and the
pilot climbing up into the frame in every view.

    python3 frame5.py <out dir> <vanilla Pawn/Humanlike dir>
"""
import math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import frame4 as F
from frame4 import (bez, aux_tank, arm, pauldron, C, K, W, RAISE, OL, OLW, BONE, BONE_HI, BONE_SH, MET, MET_HI, MET_DK, RUST, RUST_HI, YEL,
                    X, mirror, plate, poly, flat, seam, rivet, tube, wheel, _line, layer, ease, pawn_parts)

HINGE = 92             # the hatch's hinge line, along the top of its humps (as in the side view)
DEPTH = 30             # the hatch shell's depth, as in the side view
TILT = 0.25            # how much depth shows as screen height (a slight top-down view)
# the hatch outline at rest, seen from behind: humps rising beside the head (as in the side view), a notch for the neck
HATCH = mirror([(160, 104), (172, 103), (182, 98), (192, 91), (206, 92), (214, 102), (218, 124), (216, 160), (206, 186), (188, 200), (160, 202)])

def P(x, y, w, th, cam):
    """a point of the hatch (outline coords x, y; w = depth, 0 = outer face, -DEPTH = lining) swung up by th,
    projected for the north view (cam=+1, looking at the back) or the south view (cam=-1, mirrored)"""
    v = y - HINGE
    Y = HINGE + v * math.cos(th) - w * math.sin(th)
    Z = v * math.sin(th) + w * math.cos(th)
    return (x, Y + TILT * Z) if cam > 0 else (320 - x, Y - TILT * Z)

def area(p):
    return sum(p[i - 1][0] * p[i][1] - p[i][0] * p[i - 1][1] for i in range(len(p))) / 2

REST_SIGN = math.copysign(1, area([P(x, y, 0, 0, 1) for x, y in HATCH]))

LEATHER, LEATHER_DK = (104, 80, 64, 255), (78, 58, 46, 255)

def scaled(pts, sx, sy, cy=150):
    return [(160 + (x - 160) * sx, cy + (y - cy) * sy) for x, y in pts]

def solid(d, polys, fill):
    """fill the union of polygons as one solid with a single outline round it"""
    img = d._image
    m = Image.new('L', img.size); md = ImageDraw.Draw(m)
    for p in polys:
        md.polygon([(x * K, y * K) for x, y in p], fill=255)
    edge = m.filter(ImageFilter.MaxFilter(2 * int(OLW * K) + 1))
    img.alpha_composite(Image.composite(Image.new('RGBA', img.size, OL), Image.new('RGBA', img.size), edge))
    img.alpha_composite(Image.composite(Image.new('RGBA', img.size, fill), Image.new('RGBA', img.size), m))

def hatch(d, th, cam):
    """the hatch as one solid shell: its outline round the whole piece (face, walls, top), then whichever
    face is towards us - the armoured outside, or the padded lining inside a lip"""
    f = lambda pts, w=0: [P(x, y, w, th, cam) for x, y in pts]
    outer, inner = f(HATCH), f(HATCH, -DEPTH)
    walls = [[outer[i - 1], outer[i], inner[i], inner[i - 1]] for i in range(len(HATCH))]
    solid(d, [outer, inner] + walls, BONE_SH)
    if math.copysign(1, area(outer)) == REST_SIGN:                    # the outside: armour shell
        flat(d, outer, BONE)
        flat(d, f([(186, 94), (204, 95), (212, 104), (196, 101)]), BONE_HI)
        flat(d, f([(206, 182), (214, 160), (216, 164), (208, 186)]), BONE_SH)
        _line(d, outer + outer[:1], 1.6, OL)                          # the face's edge: a seam, not a second outline
        for y in (150, 176):
            seam(d, f([(108, y), (212, y)]))
        for x, y in ((122, 128), (198, 128), (124, 186), (196, 186)):
            rivet(d, *f([(x, y)])[0])
        tube(d, f([(138, 120), (138, 132), (182, 132), (182, 120)]), 4, MET_DK, MET)
        (cx, cy), = f([(160, 140)]); wheel(d, cx, cy, 9 * max(0.35, abs(math.cos(th))))
        tube(d, f([(146, 190), (174, 190)]), 4, MET_DK, MET)
    else:                                                            # the inside: a lip round quilted padding
        flat(d, inner, BONE_SH)
        _line(d, inner + inner[:1], 1.6, OL)
        pad = f(scaled(HATCH, 0.84, 0.86), -DEPTH)
        poly(d, pad, LEATHER)
        q = Image.new('RGBA', d._image.size); qd = ImageDraw.Draw(q)    # quilting, clipped to the padding
        for k in range(-4, 5):
            x0 = 160 + k * 16
            _line(qd, f([(x0 - 16, 100), (x0 + 16, 196)], -DEPTH), 1.4, LEATHER_DK)
            _line(qd, f([(x0 + 16, 100), (x0 - 16, 196)], -DEPTH), 1.4, LEATHER_DK)
        m = Image.new('L', q.size); ImageDraw.Draw(m).polygon([(x * K, y * K) for x, y in pad], fill=255)
        q.putalpha(Image.fromarray((np.array(q)[..., 3].astype(float) * np.array(m) / 255).astype('uint8')))
        d._image.alpha_composite(q)
        _line(d, pad + pad[:1], 2.2, OL)

def hinges(d):
    """the hinge barrels, fixed on the frame along the top of the opening"""
    for s in (-1, 1):
        hx, hy = 160 + s * 34, HINGE - 2
        d.rounded_rectangle(((hx - 8 - OLW) * K, (hy - 4 - OLW) * K, (hx + 8 + OLW) * K, (hy + 4 + OLW) * K), radius=4 * K, fill=OL)
        d.rounded_rectangle(((hx - 8) * K, (hy - 4) * K, (hx + 8) * K, (hy + 4) * K), radius=3 * K, fill=MET)
        d.rectangle(((hx - 6) * K, (hy - 3) * K, (hx + 6) * K, (hy - 1.5) * K), fill=MET_HI)

# the frame's opening: a rim the same shape as the hatch, and the cavity inside it
RIM = scaled(HATCH, 1.05, 1.04)
CAVITY = scaled(HATCH, 0.86, 0.9)

def north_far(d):
    F.north_far(d)
    poly(d, scaled(HATCH, 0.95, 0.97), MET_DK)                        # the torso's inside
    for y in (140, 172):
        tube(d, [(124, y), (196, y)], 5, MET, MET_HI)                 # its frame struts

def north_near(d):
    """the rim round the opening (the hatch closes onto it), the collar, lumbar plate and tank, arms"""
    rim = Image.new('RGBA', d._image.size); rd = ImageDraw.Draw(rim)
    solid(rd, [RIM], BONE)
    flat(rd, scaled([(186, 94), (204, 95), (212, 104), (196, 101)], 1.05, 1.04), BONE_HI)
    rd.polygon([(x * K, y * K) for x, y in CAVITY], fill=(0, 0, 0, 0))   # the opening
    _line(rd, CAVITY + CAVITY[:1], 2.4, OL)
    d._image.alpha_composite(rim)
    collar_back(d)
    tube(d, bez((110, 222), (130, 234), (190, 234), (210, 222)), 12)
    plate(d, [(128, 196), (192, 196), (196, 222), (124, 222)], hi=[(131, 199), (189, 199), (190, 202), (130, 202)])
    aux_tank(d, 132, 188, 209, 15)
    for s in (-1, 1):
        plate(d, X([(194, 214), (216, 216), (220, 236), (200, 240)], s))
        arm(d, s, back=True); pauldron(d, s, back=True)

# the frame's own collar: the neck hole the head comes up through
def collar_back(d):
    d.ellipse((128 * K, 100 * K, 192 * K, 124 * K), fill=OL)
    d.ellipse((130 * K, 102 * K, 190 * K, 122 * K), fill=BONE)
    d.ellipse((134 * K, 106 * K, 186 * K, 120 * K), fill=MET_DK)

def collar_front(d):
    d.arc((128 * K, 100 * K, 192 * K, 124 * K), 0, 180, fill=OL, width=int(10 * K))
    d.arc((130 * K, 102 * K, 190 * K, 122 * K), 0, 180, fill=BONE, width=int(5 * K))


SOUTH_INSIDE = mirror([(160, 104), (190, 106), (206, 120), (208, 180), (196, 230), (176, 272), (160, 274)])

def south_back(d):
    poly(d, SOUTH_INSIDE, MET_DK)                                     # the inside of the suit
    F.south(d, 'back')

def masked(im, below):
    """the pilot hidden below a screen row (inside the suit: only what rises out of the collar shows)"""
    a = np.array(im); a[below:, :, 3] = 0; return Image.fromarray(a)

def compose(art, facing, th, pilot, h, top, left=0):
    img = Image.new('RGBA', (C + left, h))
    def put(im, dx=0, dy=0):
        img.alpha_composite(im, (left + dx, top + dy))
    L = lambda fn: layer(fn, h - top)
    st, px, py = pilot if pilot else (None, 0, 0)
    body, head = pawn_parts(art, facing) if pilot else (None, None)
    if facing == 'north':
        put(L(north_far))
        if st == 'in': put(body, 0, py)
        put(L(north_near))
        if st == 'in': put(head, 0, py)
        put(L(collar_front))
        if st == 'mid': put(body, 0, py); put(head, 0, py)
        if th < 0.05 * math.pi:                                       # shut: the hinge barrels sit on top
            put(L(lambda d: (hatch(d, th, 1), hinges(d))))
        else:                                                         # swinging: the hatch hides them
            put(L(lambda d: (hinges(d), hatch(d, th, 1))))
        if st == 'out': put(body, 0, py); put(head, 0, py)
    elif facing == 'south':
        hl = L(lambda d: hatch(d, th, -1))
        if st == 'out':                                               # behind the frame, passing under the raised hatch
            put(body, 0, py); put(head, 0, py)
        put(hl); put(L(south_back))
        if st == 'in':                                                # inside: only what rises out of the collar shows
            cut = 112 - py
            put(masked(body, cut), 0, py); put(masked(head, cut), 0, py)
        put(L(lambda d: F.south(d, 'front')))
    else:
        put(L(lambda d: F.east(d, 'back')))
        if st: put(body, px, py); put(head, px, py)
        put(L(lambda d: F.east_hood(d, th)))                          # the hatch always over the pilot
        put(L(lambda d: F.east(d, 'front')))
    return img

def path(facing, phase, t):
    lift = -12 * math.sin(t * math.pi)
    if phase == 'in':
        return ('in', 0, -RAISE)
    if facing == 'north':
        if phase == 'walk':
            return ('out', 0, round(110 + (40 - 110) * t))
        dy = round(40 + (-RAISE - 40) * t + lift); return ('mid' if dy > -13 else 'in', 0, dy)
    if facing == 'south':
        if phase == 'walk':
            return ('out', 0, round(-150 + (44 + 150) * t))
        return ('in', 0, round(44 + (-RAISE - 44) * t + lift))
    if phase == 'walk':
        return ('out', round(-150 + 80 * t), 16)
    return ('in', round(-70 * (1 - t)), round(16 + (-RAISE - 16) * t + lift))

def animate_north(out, art):
    HO = 0.75 * math.pi
    seq = [(0, None, 0)] * 8 + [(ease(i / 19) * HO, None, 0) for i in range(20)] + [(HO, 'walk', i / 25) for i in range(26)] \
        + [(HO, 'climb', ease(i / 15)) for i in range(16)] + [((1 - ease(i / 21)) * HO, 'in', 1) for i in range(22)] + [(0, 'in', 1)] * 14
    TOP, H = 100, C + 200
    frames = []
    for th, phase, t in seq:
        f = Image.new('RGBA', (C, H), (96, 92, 98, 255))
        f.alpha_composite(compose(art, 'north', th, path('north', phase, t) if phase else None, H, TOP))
        frames.append(f.convert('RGB').resize((C * 2, H * 2), Image.LANCZOS))
    frames[0].save(f'{out}/frame5c_north_climb_in.gif', save_all=True, append_images=frames[1:], duration=70, loop=0)
    return frames

def animate(out, art):
    HO = 0.75 * math.pi
    seq = []
    for i in range(8): seq.append((0, None, 0))
    for i in range(20): seq.append((ease(i / 19) * HO, None, 0))
    for i in range(26): seq.append((HO, 'walk', i / 25))
    for i in range(16): seq.append((HO, 'climb', ease(i / 15)))
    for i in range(22): seq.append(((1 - ease(i / 21)) * HO, 'in', 1))
    for i in range(14): seq.append((0, 'in', 1))
    TOP, H, LEFT = 100, C + 200, 160
    frames = []
    for th, phase, t in seq:
        row = Image.new('RGBA', (3 * C + LEFT, H), (96, 92, 98, 255))
        x = 0
        for f in ('south', 'east', 'north'):
            lft = LEFT if f == 'east' else 0
            row.alpha_composite(compose(art, f, th, path(f, phase, t) if phase else None, H, TOP, lft), (x, 0))
            x += C + lft
        frames.append(row.convert('RGB'))
    frames[0].save(f'{out}/frame5b_climb_in.gif', save_all=True, append_images=frames[1:], duration=70, loop=0)
    return frames

if __name__ == '__main__':
    fr = animate(sys.argv[1], sys.argv[2])
    keys = [10, 20, 34, 46, 54, 58, 62, 66, 72, 80, len(fr) - 1]
    sh = Image.new('RGB', (fr[0].width, 300 * len(keys)))
    for j, k in enumerate(keys):
        sh.paste(fr[k].crop((0, 100, fr[0].width, 400)), (0, j * 300))
    sh.save(f'{sys.argv[1]}/frame5b_keys.png')
