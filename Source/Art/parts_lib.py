import numpy as np
from PIL import Image
from scipy import ndimage
from process_nano import cut_out, plate_mask, tint, S, FIG_H, BOTTOM, MAX_W, OUTER
SRC=1024
def load(path):
    return np.array(Image.open(path).convert('RGB').resize((SRC,SRC),Image.LANCZOS)).astype(np.float32)
def base_transform(base_path):
    rgb=load(base_path); fig=cut_out(rgb)
    ys,xs=np.nonzero(fig); y0,y1,x0,x1=ys.min(),ys.max()+1,xs.min(),xs.max()+1
    scale=min(FIG_H/(y1-y0),MAX_W/(x1-x0))
    w=round((x1-x0)*scale); h=round((y1-y0)*scale)
    return dict(scale=scale,x0=x0,y0=y0,left=(S-w)//2,top=BOTTOM-h)
def layer(path,T):
    """A part on the shared 256px canvas: same transform for every part, so parts stack."""
    rgb=load(path); fig=cut_out(rgb)
    ring=ndimage.binary_dilation(fig,iterations=max(1,round(OUTER/T['scale'])))&~fig
    rgb[ring]=8; fig=fig|ring
    mask=plate_mask(rgb)*fig
    rgb[~fig]=0
    full=int(round(SRC*T['scale']))
    body=Image.fromarray(np.dstack([rgb.astype(np.uint8),(fig*255).astype(np.uint8)]),'RGBA').resize((full,full),Image.LANCZOS)
    m=Image.fromarray((mask*255).astype(np.uint8),'L').resize((full,full),Image.LANCZOS)
    ox=int(round(T['left']-T['x0']*T['scale'])); oy=int(round(T['top']-T['y0']*T['scale']))
    tex=Image.new('RGBA',(S,S)); tex.paste(body,(ox,oy),body)
    red=Image.new('L',(S,S),0); red.paste(m,(ox,oy))
    z=Image.new('L',(S,S),0)
    return tex, Image.merge('RGBA',(red,z,z,tex.split()[3]))
def stack(layers,color):
    out=Image.new('RGBA',(S,S))
    for t,m in layers: out.alpha_composite(tint(t,m,color))
    return out

def collar(tex):
    """The collar opening of a chassis layer: the biggest dark region in the upper middle.
    Returns (cx, cy, w, h, bottom) in canvas pixels."""
    a = np.array(tex).astype(np.float32)
    dark = (a[..., 3] > 200) & (a[..., :3].mean(2) < 60)
    dark[int(S * 0.62):, :] = False
    dark[:, :int(S * 0.25)] = False
    dark[:, int(S * 0.75):] = False
    lab, n = ndimage.label(ndimage.binary_opening(dark, iterations=2))
    if n == 0:
        return None
    sizes = ndimage.sum(dark, lab, range(1, n + 1))
    ys, xs = np.nonzero(lab == (1 + int(np.argmax(sizes))))
    return ((xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2, xs.max() - xs.min(), ys.max() - ys.min(), ys.max())

def shift(layer_pair, dx, dy):
    out = []
    for img in layer_pair:
        c = Image.new(img.mode, img.size)
        c.paste(img, (int(round(dx)), int(round(dy))))
        out.append(c)
    return tuple(out)

def helmet_layer(path, anchor_cx, anchor_bottom, width):
    """A standalone helmet painting scaled to `width` and seated so its bottom sits at the
    collar anchor."""
    rgb = load(path); fig = cut_out(rgb)
    ys, xs = np.nonzero(fig); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    scale = width / (x1 - x0)
    ring = ndimage.binary_dilation(fig, iterations=max(1, round(OUTER / scale))) & ~fig
    rgb[ring] = 8; fig = fig | ring
    mask = plate_mask(rgb) * fig
    rgb[~fig] = 0
    crop = lambda arr: arr[y0:y1, x0:x1]
    w, h = round((x1 - x0) * scale), round((y1 - y0) * scale)
    body = Image.fromarray(np.dstack([crop(rgb).astype(np.uint8), crop((fig * 255).astype(np.uint8))]), 'RGBA').resize((w, h), Image.LANCZOS)
    m = Image.fromarray(crop((mask * 255).astype(np.uint8)), 'L').resize((w, h), Image.LANCZOS)
    left, top = int(round(anchor_cx - w / 2)), int(round(anchor_bottom - h))
    tex = Image.new('RGBA', (S, S)); tex.paste(body, (left, top), body)
    red = Image.new('L', (S, S), 0); red.paste(m, (left, top))
    z = Image.new('L', (S, S), 0)
    return tex, Image.merge('RGBA', (red, z, z, tex.split()[3]))

def rescale(layer_pair, s, cx=S / 2, by=BOTTOM):
    """Scale a layer about the bottom centre of the figure, keeping the canvas size."""
    out = []
    for img in layer_pair:
        w = int(round(S * s))
        small = img.resize((w, w), Image.LANCZOS)
        c = Image.new(img.mode, img.size)
        c.paste(small, (int(round(cx - cx * s)), int(round(by - by * s))))
        out.append(c)
    return tuple(out)
