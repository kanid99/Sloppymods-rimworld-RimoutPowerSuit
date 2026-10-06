"""Renderer v2 for armour: parts built from facets, each lit by its own normal (light from the upper left, toward
the viewer), with flat / cylinder / dome gradients, specular glints, edge highlights on lit edges, faint seams
between facets, a soft cast shadow and one light silhouette outline per part, and grime toward the bottom.
Tones: 'light' (takes the suit tint), 'dark' (undersuit; carbon weave), 'metal' (bare steel)."""
import math

OLC = '#1c1a19'
L3 = (-0.42, -0.62, 0.66)
_n = math.sqrt(sum(v * v for v in L3)); L3 = tuple(v / _n for v in L3)
L2 = (-0.56, -0.83)
TONES = {'light': ((64, 66, 74), (172, 174, 181), (242, 243, 246)),
         'dark': ((18, 18, 22), (58, 60, 66), (128, 131, 140)),
         'metal': ((40, 42, 48), (120, 124, 132), (214, 218, 226))}

def P(p):
    return ' '.join(f'{x:.2f},{y:.2f}' for x, y in p)

def col(I, tone):
    d, m, l = TONES[tone]; I = max(0.0, min(1.0, I))
    a, b, t = (d, m, I / 0.55) if I < 0.55 else (m, l, (I - 0.55) / 0.45)
    return '#%02x%02x%02x' % tuple(int(a[k] + (b[k] - a[k]) * t) for k in range(3))

def norm(n):
    s = math.sqrt(sum(v * v for v in n)) or 1
    return tuple(v / s for v in n)

def lit(n):
    n = norm(n)
    return 0.22 + 0.78 * max(0.0, sum(n[k] * L3[k] for k in range(3)))

def orient(p):
    return sum(p[i - 1][0] * p[i][1] - p[i][0] * p[i - 1][1] for i in range(len(p)))

def mirror(p, s):
    return [(160 + s * (x - 160), y) for x, y in p]

def mn(n, s):
    return (n[0] * s, n[1], n[2])

class Doc:
    def __init__(self, prefix):
        self.p, self.k, self.defs, self.out = prefix, 0, [], []
        self.blur = self.id(); self.defs.append(f'<filter id="{self.blur}" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="2.4"/></filter>')
        self.glow = self.id(); self.defs.append(f'<filter id="{self.glow}" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="1.5"/></filter>')
        self.soft = self.id(); self.defs.append(f'<filter id="{self.soft}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="1.1"/></filter>')
        self.carbon = self.id()
        self.defs.append(f'<pattern id="{self.carbon}" width="3" height="3" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
                         f'<rect width="1.5" height="3" fill="#ffffff" fill-opacity="0.06"/><rect x="1.5" width="1.5" height="1.5" fill="#000" fill-opacity="0.18"/></pattern>')
    def id(self):
        self.k += 1; return f'{self.p}{self.k}'
    def add(self, s):
        self.out.append(s)
    def svg(self):
        return f'<defs>{"".join(self.defs)}</defs>' + ''.join(self.out)

    def grad(self, I, kind, tone, angle=0):
        gid = self.id()
        if kind == 'dome':
            self.defs.append(f'<radialGradient id="{gid}" cx="0.38" cy="0.3" r="0.85">'
                             f'<stop offset="0" stop-color="{col(I + 0.2, tone)}"/><stop offset="0.55" stop-color="{col(I, tone)}"/>'
                             f'<stop offset="1" stop-color="{col(I - 0.3, tone)}"/></radialGradient>')
            return gid
        if kind == 'flat':
            stops = [(0, I + 0.07), (1, I - 0.09)]; x2, y2 = 1, 1
        else:
            # a cylinder: dark sides, a bright band a third across, the turn away, reflected light at the far edge
            stops = [(0, I - 0.44), (0.16, I + 0.02), (0.3, I + 0.26), (0.42, I + 0.06), (0.72, I - 0.16), (0.9, I - 0.3), (1, I - 0.22)]
            x2, y2 = (1, 0) if kind == 'cyl_h' else (0, 1)
        tr = f' gradientTransform="rotate({angle} 0.5 0.5)"' if angle else ''
        self.defs.append(f'<linearGradient id="{gid}" x1="0" y1="0" x2="{x2}" y2="{y2}"{tr}>' +
                         ''.join(f'<stop offset="{o}" stop-color="{col(v, tone)}"/>' for o, v in stops) + '</linearGradient>')
        return gid

    def part(self, facets, shadow=True, grime=True, outline=True, glints=True):
        """facets: [(pts, normal, kind, tone)] drawn as one solid part"""
        polys = [f[0] for f in facets]
        if shadow:
            self.add(''.join(f'<polygon points="{P([(x + 2.4, y + 3.2) for x, y in p])}" fill="#000" fill-opacity="0.42" filter="url(#{self.blur})"/>' for p in polys))
        if outline:
            self.add(''.join(f'<polygon points="{P(p)}" fill="{OLC}" stroke="{OLC}" stroke-width="3.2" stroke-linejoin="round"/>' for p in polys))
        for pts, n, kind, tone in facets:
            I = lit(n)
            self.add(f'<polygon points="{P(pts)}" fill="url(#{self.grad(I, kind, tone)})"/>')
            if tone == 'dark':
                self.add(f'<polygon points="{P(pts)}" fill="url(#{self.carbon})"/>')
        for pts, n, kind, tone in facets:                       # faint seams, then light on the lit edges
            self.add(f'<polygon points="{P(pts)}" fill="none" stroke="{OLC}" stroke-width="0.55" stroke-opacity="0.32" stroke-linejoin="round"/>')
            cyl = kind.startswith('cyl')
            s = 1 if orient(pts) > 0 else -1
            for i in range(len(pts) if not cyl else 0):
                a, b = pts[i - 1], pts[i]
                dx, dy = b[0] - a[0], b[1] - a[1]; Ln = math.hypot(dx, dy) or 1
                nx, ny = -dy / Ln * s, dx / Ln * s
                t = nx * L2[0] + ny * L2[1]
                if t > 0.35 and Ln > 3:
                    ix, iy = -nx * 0.7, -ny * 0.7
                    op = 0.35 + 0.45 * (t - 0.35) / 0.65
                    self.add(f'<line x1="{a[0] + ix:.2f}" y1="{a[1] + iy:.2f}" x2="{b[0] + ix:.2f}" y2="{b[1] + iy:.2f}" stroke="#ffffff" stroke-width="0.8" stroke-opacity="{op:.2f}" stroke-linecap="round"/>')
            if cyl:                                              # a soft specular streak along the cylinder
                xs = [x for x, _ in pts]; ys = [y for _, y in pts]
                w = max(xs) - min(xs); h = max(ys) - min(ys)
                sop = 0.5 if tone != 'dark' else 0.22
                cid = self.id()
                self.defs.append(f'<clipPath id="{cid}"><polygon points="{P(pts)}"/></clipPath>')
                if kind == 'cyl_h':
                    x = min(xs) + w * 0.3
                    self.add(f'<g clip-path="url(#{cid})"><line x1="{x:.1f}" y1="{min(ys) - 2}" x2="{x:.1f}" y2="{max(ys) + 2}" stroke="#fff" stroke-width="{max(1.2, w * 0.07):.1f}" stroke-opacity="{sop}" filter="url(#{self.soft})"/></g>')
                else:
                    y = min(ys) + h * 0.3
                    self.add(f'<g clip-path="url(#{cid})"><line x1="{min(xs) - 2}" y1="{y:.1f}" x2="{max(xs) + 2}" y2="{y:.1f}" stroke="#fff" stroke-width="{max(1.2, h * 0.07):.1f}" stroke-opacity="{sop}" filter="url(#{self.soft})"/></g>')
            if glints and not cyl and tone != 'dark' and lit(n) > 0.82:
                xs = [x for x, _ in pts]; ys = [y for _, y in pts]
                cx, cy = min(xs) + (max(xs) - min(xs)) * 0.32, min(ys) + (max(ys) - min(ys)) * 0.28
                rx, ry = (max(xs) - min(xs)) * 0.2, (max(ys) - min(ys)) * 0.1
                cid = self.id()
                self.defs.append(f'<clipPath id="{cid}"><polygon points="{P(pts)}"/></clipPath>')
                self.add(f'<g clip-path="url(#{cid})"><ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{max(ry, 1.2):.1f}" fill="#fff" fill-opacity="0.38" filter="url(#{self.soft})"/></g>')
        if grime:
            ys = [y for p in polys for _, y in p]; y0, y1 = min(ys), max(ys)
            gid, cid = self.id(), self.id()
            self.defs.append(f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="0" y1="{y0}" x2="0" y2="{y1}">'
                             f'<stop offset="0.55" stop-color="#3a3026" stop-opacity="0"/><stop offset="1" stop-color="#3a3026" stop-opacity="0.22"/></linearGradient>')
            self.defs.append(f'<clipPath id="{cid}">' + ''.join(f'<polygon points="{P(p)}"/>' for p in polys) + '</clipPath>')
            self.add(f'<rect x="0" y="{y0}" width="320" height="{y1 - y0}" fill="url(#{gid})" clip-path="url(#{cid})"/>')

    # ---------------------------------------------------------------- details
    def groove(self, pts, w=0.9):
        self.add(f'<polyline points="{P(pts)}" fill="none" stroke="{OLC}" stroke-width="{w}" stroke-opacity="0.55" stroke-linecap="round" stroke-linejoin="round"/>'
                 f'<polyline points="{P([(x + 0.5, y + 0.9) for x, y in pts])}" fill="none" stroke="#ffffff" stroke-width="0.7" stroke-opacity="0.5" stroke-linecap="round" stroke-linejoin="round"/>')
    def recess(self, pts, tone='light'):
        """a sunken panel: darker inside, shadow along its top-left, light on its bottom-right lip"""
        self.add(f'<polygon points="{P(pts)}" fill="{col(0.4 if tone == "light" else 0.15, tone)}"/>')
        cid = self.id()
        self.defs.append(f'<clipPath id="{cid}"><polygon points="{P(pts)}"/></clipPath>')
        self.add(f'<g clip-path="url(#{cid})"><polygon points="{P([(x - 1.6, y - 1.6) for x, y in pts])}" fill="none" stroke="#000" stroke-width="2.6" stroke-opacity="0.45" filter="url(#{self.soft})"/></g>')
        self.add(f'<polygon points="{P(pts)}" fill="none" stroke="{OLC}" stroke-width="0.7" stroke-opacity="0.6"/>')
    def vent(self, x0, y0, x1, y1, n):
        self.recess([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], 'dark')
        for k in range(n):
            y = y0 + (y1 - y0) * (k + 0.5) / n
            self.add(f'<line x1="{x0 + 1}" y1="{y - 0.6:.2f}" x2="{x1 - 1}" y2="{y - 0.6:.2f}" stroke="#8a8c94" stroke-width="0.9"/>'
                     f'<line x1="{x0 + 1}" y1="{y + 0.4:.2f}" x2="{x1 - 1}" y2="{y + 0.4:.2f}" stroke="#0e0e10" stroke-width="0.7"/>')
    def bolt(self, x, y, r=1.3):
        self.add(f'<circle cx="{x}" cy="{y}" r="{r + 0.55}" fill="{OLC}" fill-opacity="0.8"/><circle cx="{x}" cy="{y}" r="{r}" fill="#8f9098"/>'
                 f'<circle cx="{x - r * 0.3}" cy="{y - r * 0.3}" r="{r * 0.5}" fill="#f4f4f6"/>')
    def light(self, x, y, w, h, c, core):
        r = min(w, h) / 2
        self.add(f'<rect x="{x - 0.6}" y="{y - 0.6}" width="{w + 1.2}" height="{h + 1.2}" rx="{r + 0.6}" fill="{OLC}"/>'
                 f'<rect x="{x - 1.5}" y="{y - 1.5}" width="{w + 3}" height="{h + 3}" rx="{r + 1.5}" fill="{c}" fill-opacity="0.55" filter="url(#{self.glow})"/>'
                 f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{c}"/><rect x="{x + 0.7}" y="{y + 0.5}" width="{w * 0.5}" height="{h * 0.4}" rx="{r * 0.4}" fill="{core}"/>')
    def tube(self, pts, w, c='#4a4b52', hi='#9a9ca6'):
        self.add(f'<polyline points="{P(pts)}" fill="none" stroke="{OLC}" stroke-width="{w + 1.4}" stroke-linecap="round" stroke-linejoin="round"/>'
                 f'<polyline points="{P(pts)}" fill="none" stroke="{c}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>'
                 f'<polyline points="{P([(x - w * 0.22, y - w * 0.22) for x, y in pts])}" fill="none" stroke="{hi}" stroke-width="{max(0.6, w * 0.28)}" stroke-linecap="round" stroke-opacity="0.85"/>')
    def piston(self, a, b, w=3.6):
        m = (a[0] + (b[0] - a[0]) * 0.55, a[1] + (b[1] - a[1]) * 0.55)
        self.tube([a, b], w * 0.62, '#b9bbc3', '#f2f2f6')
        self.tube([a, m], w, '#55575e', '#a8aab2')
    def stencil(self, x, y, t, size=3.4, anchor='middle', op=0.6):
        self.add(f'<text x="{x}" y="{y}" font-family="DejaVu Sans Mono, monospace" font-weight="bold" font-size="{size}" fill="#2e2c30" fill-opacity="{op}" text-anchor="{anchor}">{t}</text>')
    def hazard(self, pts, step=4.2):
        xs = [x for x, _ in pts]; ys = [y for _, y in pts]; h = max(ys) - min(ys)
        cid = self.id()
        self.defs.append(f'<clipPath id="{cid}"><polygon points="{P(pts)}"/></clipPath>')
        s = f'<g clip-path="url(#{cid})"><rect x="{min(xs)}" y="{min(ys)}" width="{max(xs) - min(xs)}" height="{h}" fill="#dcaa3a"/>'
        x = min(xs) - h
        while x < max(xs) + h:
            s += f'<polygon points="{P([(x, max(ys)), (x + step / 2, max(ys)), (x + step / 2 + h, min(ys)), (x + h, min(ys))])}" fill="#262220"/>'
            x += step
        self.add(s + '</g>')
