"""The power-armour frame as SVG: the same drawing code as the PNGs (frame4/frame5), recorded by a stand-in
for PIL's ImageDraw that writes vector shapes instead of pixels. Pillow-matching details: polygon and
ellipse outlines sit inside the shape (a double-width stroke clipped to it).
    python3 frame_svg.py <out dir> [<vanilla Pawn/Humanlike dir> for the with-pilot previews]"""
import base64, io, math, sys
import frame4 as F
import frame5 as G
from frame4 import C, K, RAISE, OL, OLW, BONE, BONE_HI, BONE_SH, MET_DK, X, flat, _line, poly, bez

def col(c):
    if c is None:
        return 'none', 1
    r, g, b = c[:3]; a = c[3] / 255 if len(c) > 3 else 1
    return f'#{r:02x}{g:02x}{b:02x}', a

def num(v):
    return f'{v / K:.2f}'.rstrip('0').rstrip('.')

class SvgDraw:
    """records ImageDraw calls (coordinates in K-supersampled pixels) as SVG elements in canvas pixels"""
    def __init__(self, sink, ids):
        self.out, self.ids = sink, ids
    def _id(self):
        self.ids[0] += 1; return f'c{self.ids[0]}'
    def _paint(self, kind, fill):
        c, a = col(fill)
        return f'{kind}="{c}"' + (f' {kind}-opacity="{a:.3f}"' if a < 1 else '')
    def _shape(self, tag, geo, fill, outline, width):
        if fill is not None:
            self.out.append(f'<{tag} {geo} {self._paint("fill", fill)}/>')
        if outline is not None and width:
            cid = self._id()                                       # Pillow puts the outline inside the shape
            self.out.append(f'<clipPath id="{cid}"><{tag} {geo}/></clipPath>')
            self.out.append(f'<{tag} {geo} fill="none" {self._paint("stroke", outline)} stroke-width="{num(2 * width)}" '
                            f'stroke-linejoin="round" clip-path="url(#{cid})"/>')
    def polygon(self, xy, fill=None, outline=None, width=1):
        pts = ' '.join(f'{num(x)},{num(y)}' for x, y in xy)
        self._shape('polygon', f'points="{pts}"', fill, outline, width if outline is not None else 0)
    def line(self, xy, fill=None, width=1, joint=None):
        pts = ' '.join(f'{num(x)},{num(y)}' for x, y in xy)
        self.out.append(f'<polyline points="{pts}" fill="none" {self._paint("stroke", fill)} stroke-width="{num(width)}" '
                        f'stroke-linejoin="round"/>')
    def ellipse(self, box, fill=None, outline=None, width=1):
        x0, y0, x1, y1 = box
        geo = f'cx="{num((x0 + x1) / 2)}" cy="{num((y0 + y1) / 2)}" rx="{num((x1 - x0) / 2)}" ry="{num((y1 - y0) / 2)}"'
        self._shape('ellipse', geo, fill, outline, width if outline is not None else 0)
    def rounded_rectangle(self, box, radius=0, fill=None, outline=None, width=1):
        x0, y0, x1, y1 = box
        geo = f'x="{num(x0)}" y="{num(y0)}" width="{num(x1 - x0)}" height="{num(y1 - y0)}" rx="{num(radius)}"'
        self._shape('rect', geo, fill, outline, width if outline is not None else 0)
    def rectangle(self, box, fill=None, outline=None, width=1):
        self.rounded_rectangle(box, 0, fill, outline, width)
    def arc(self, box, start, end, fill=None, width=1):
        """Pillow's arc: clockwise from 3 o'clock, the stroke inside the box"""
        x0, y0, x1, y1 = box; w = width
        cx, cy, rx, ry = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2 - w / 2, (y1 - y0) / 2 - w / 2
        pts = [(cx + rx * math.cos(math.radians(a)), cy + ry * math.sin(math.radians(a)))
               for a in [start + (end - start) * i / 32 for i in range(33)]]
        self.line(pts, fill, w)
    def group(self, extra=''):
        sub = SvgDraw([], self.ids); sub._extra = extra; return sub
    def place(self, sub, attrs=''):
        self.out.append(f'<g {attrs}>' + ''.join(sub.out) + '</g>')

# ---- vector versions of the three raster tricks in frame5
def solid(d, polys, fill):
    """one solid, one outline: every piece stroked first (the outline that shows outside the union), then filled"""
    for p in polys:
        pts = ' '.join(f'{x:.2f},{y:.2f}' for x, y in p)
        d.out.append(f'<polygon points="{pts}" fill="{col(OL)[0]}" stroke="{col(OL)[0]}" stroke-width="{2 * OLW:.2f}" stroke-linejoin="round"/>')
    for p in polys:
        pts = ' '.join(f'{x:.2f},{y:.2f}' for x, y in p)
        d.out.append(f'<polygon points="{pts}" fill="{col(fill)[0]}"/>')

def north_near(d):
    """the rim round the opening as a ring with a real hole (even-odd), then the rest as in frame5"""
    rim = d.group()
    solid(rim, [G.RIM], BONE)
    flat(rim, G.scaled([(186, 94), (204, 95), (212, 104), (196, 101)], 1.05, 1.04), BONE_HI)
    _line(rim, G.CAVITY + G.CAVITY[:1], 2.4, OL)
    cid = d._id()
    ring = 'M' + ' L'.join(f'{x - 40:.2f},{y - 40:.2f}' for x, y in [(0, 0), (C + 80, 0), (C + 80, C + 80), (0, C + 80)]) + ' Z ' + \
           'M' + ' L'.join(f'{x:.2f},{y:.2f}' for x, y in G.CAVITY) + ' Z'
    d.out.append(f'<clipPath id="{cid}"><path d="{ring}" clip-rule="evenodd"/></clipPath>')
    d.place(rim, f'clip-path="url(#{cid})"')                              # everything but the opening
    _line(d, G.CAVITY + G.CAVITY[:1], 2.4, OL)
    G.collar_back(d)
    F.tube(d, bez((110, 222), (130, 234), (190, 234), (210, 222)), 12)
    F.plate(d, [(128, 196), (192, 196), (196, 222), (124, 222)], hi=[(131, 199), (189, 199), (190, 202), (130, 202)])
    F.aux_tank(d, 132, 188, 209, 15)
    for s in (-1, 1):
        F.plate(d, X([(194, 214), (216, 216), (220, 236), (200, 240)], s))
        F.arm(d, s, back=True); F.pauldron(d, s, back=True)

def hatch(d, th, cam):
    """frame5.hatch with the quilting clipped by an SVG clip path"""
    P = G.P
    f = lambda pts, w=0: [P(x, y, w, th, cam) for x, y in pts]
    outer = f(G.HATCH)
    if math.copysign(1, G.area(outer)) == G.REST_SIGN:
        return G._hatch_raster(d, th, cam)                             # outside face: no raster tricks beyond solid()
    inner = f(G.HATCH, -G.DEPTH)
    walls = [[outer[i - 1], outer[i], inner[i], inner[i - 1]] for i in range(len(G.HATCH))]
    solid(d, [outer, inner] + walls, BONE_SH)
    flat(d, inner, BONE_SH); _line(d, inner + inner[:1], 1.6, OL)
    pad = f(G.scaled(G.HATCH, 0.84, 0.86), -G.DEPTH)
    poly(d, pad, G.LEATHER)
    q = d.group()
    for k in range(-4, 5):
        x0 = 160 + k * 16
        _line(q, f([(x0 - 16, 100), (x0 + 16, 196)], -G.DEPTH), 1.4, G.LEATHER_DK)
        _line(q, f([(x0 + 16, 100), (x0 - 16, 196)], -G.DEPTH), 1.4, G.LEATHER_DK)
    cid = d._id()
    d.out.append(f'<clipPath id="{cid}"><polygon points="' + ' '.join(f'{x:.2f},{y:.2f}' for x, y in pad) + '"/></clipPath>')
    d.place(q, f'clip-path="url(#{cid})"')
    _line(d, pad + pad[:1], 2.2, OL)

G._hatch_raster = G.hatch
G.solid = solid                       # frame5.hatch's outside face calls solid(): use the vector one
G.hatch = hatch
G.north_near = north_near
F.layer  # (unused here: SVG views are composed directly below)

def png_b64(im):
    b = io.BytesIO(); im.save(b, 'PNG'); return base64.b64encode(b.getvalue()).decode()

def view(facing, th=0.0, pilot=None, art=None):
    """one facing as a list of SVG elements, drawn in the same order as frame5.compose"""
    ids = [0]; d = SvgDraw([], ids)
    body = head = None
    if pilot and art:
        body, head = F.pawn_parts(art, facing)
    py = -RAISE
    def img(im, clip_below=None):
        if im is None:
            return
        attrs = ''
        if clip_below is not None:
            cid = d._id(); d.out.append(f'<clipPath id="{cid}"><rect x="0" y="-400" width="{C}" height="{clip_below + 400}"/></clipPath>')
            attrs = f' clip-path="url(#{cid})"'
        d.out.append(f'<g{attrs}><image x="0" y="{py}" width="{C}" height="{C}" href="data:image/png;base64,{png_b64(im)}"/></g>')
    if facing == 'north':
        G.north_far(d); img(body); north_near(d); img(head); G.collar_front(d)
        if th < 0.05 * math.pi:
            G.hatch(d, th, 1); G.hinges(d)
        else:
            G.hinges(d); G.hatch(d, th, 1)
    elif facing == 'south':
        G.hatch(d, th, -1); G.south_back(d); img(body, 112); img(head, 112); F.south(d, 'front')
    else:
        F.east(d, 'back'); img(body); img(head); F.east_hood(d, th); F.east(d, 'front')
    return d.out

VIEWS = [('south', 'south', 0.0), ('east', 'east', 0.0), ('north_shut', 'north', 0.0),
         ('north_open', 'north', 0.75 * math.pi), ('east_open', 'east', 0.75 * math.pi)]

def svg_doc(body, w, h, bg=None):
    b = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w * 2}" height="{h * 2}">'
            f'<title>Power armour frame</title>{b}{body}</svg>')

if __name__ == '__main__':
    out = sys.argv[1]; art = sys.argv[2] if len(sys.argv) > 2 else None
    import os; os.makedirs(f'{out}/svg', exist_ok=True)
    parts = []
    for i, (name, f, th) in enumerate(VIEWS):
        els = view(f, th)
        open(f'{out}/svg/frame_{name}.svg', 'w').write(svg_doc(''.join(els), C, C))
        # unique clip ids per view inside the combined sheet
        body = ''.join(els).replace('id="c', f'id="v{i}c').replace('#c', f'#v{i}c')
        parts.append(f'<g transform="translate({i * C},0)"><clipPath id="v{i}box"><rect width="{C}" height="{C}"/></clipPath>'
                     f'<g clip-path="url(#v{i}box)">{body}</g></g>')
        if art:
            open(f'{out}/svg/frame_{name}_pilot.svg', 'w').write(svg_doc(''.join(view(f, th, True, art)), C, C, '#605c62'))
    open(f'{out}/svg/frame_all_views.svg', 'w').write(svg_doc(''.join(parts), C * len(VIEWS), C, '#605c62'))
    print('ok')
