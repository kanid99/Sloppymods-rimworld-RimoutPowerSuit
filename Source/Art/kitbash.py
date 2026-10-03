"""Kitbash: cut pieces out of generated art and assemble new parts; vdraw fills the gaps."""
import sys; sys.path.insert(0,sys.argv[1]); SP=sys.argv[1]
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
import vdraw
INK=(14,14,18)
def plate(path,seed,grow=14,size=None):
    "one outlined plate: the light region around seed bounded by the black outline, plus that outline"
    im=Image.open(path).convert('RGB'); a=np.array(im).astype(int)
    light=a.min(2)>70
    lab,_=ndimage.label(light); m=lab==lab[seed[1],seed[0]]
    m=ndimage.binary_closing(m,iterations=6)
    m=ndimage.binary_fill_holes(m)
    m=ndimage.binary_dilation(m,iterations=grow)&(a.min(2)<232)|m
    ys,xs=np.nonzero(m); bb=(xs.min(),ys.min(),xs.max()+1,ys.max()+1)
    rgba=Image.fromarray(np.dstack([a.astype(np.uint8),(m*255).astype(np.uint8)]),'RGBA').crop(bb)
    if size: rgba=rgba.resize(size,Image.LANCZOS)
    return rgba
def piece(path,box,size=None,flip=False):
    im=Image.open(path).convert('RGB').crop(box)
    a=np.array(im).astype(int); fg=(a.min(2)<232)
    holes=ndimage.binary_fill_holes(fg)&~fg
    lab_h,nh=ndimage.label(holes)
    for i in range(1,nh+1):                      # fill only holes that are not white background
        h=lab_h==i
        if a[h].min(1).mean()<200: fg|=h
    fg=ndimage.binary_opening(fg,iterations=2)
    lab,n=ndimage.label(fg)
    if n>1:
        sizes=ndimage.sum(fg,lab,range(1,n+1)); keep=[i+1 for i,s in enumerate(sizes) if s>0.02*fg.sum()]
        fg=np.isin(lab,keep)
    rgba=Image.fromarray(np.dstack([a.astype(np.uint8),(fg*255).astype(np.uint8)]),'RGBA')
    if size: rgba=rgba.resize(size,Image.LANCZOS)
    if flip: rgba=rgba.transpose(Image.FLIP_LEFT_RIGHT)
    return rgba
class Board:
    def __init__(s,n=2048): s.im=Image.new('RGBA',(n,n),(0,0,0,0)); s.n=n
    def put(s,p,cx,top): s.im.alpha_composite(p,(int(cx-p.width/2),int(top))); return top+p.height
    def vd(s,fn):
        "draw with vdraw on a transparent layer of the same size"
        c=vdraw.Canvas(s.n); fn(c)
        lay=np.dstack([c.rgb.astype(np.uint8),(c.a*255).astype(np.uint8)])
        s.im.alpha_composite(Image.fromarray(lay,'RGBA'))
    def save(s,path,outline=22):
        a=np.array(s.im); m=a[...,3]>128
        ring=ndimage.binary_dilation(m,iterations=outline)&~m
        a[ring]=(*INK,255)
        # clean the edges of straight cuts: a thin dark line where the alpha is soft
        rgb=Image.new('RGB',s.im.size,'white'); rgb.paste(Image.fromarray(a,'RGBA'),mask=Image.fromarray(a,'RGBA').split()[3])
        bb=Image.fromarray((m|ring).astype(np.uint8)*255).getbbox()
        rgb=rgb.crop(bb); n=max(rgb.size)+80
        sq=Image.new('RGB',(n,n),'white'); sq.paste(rgb,((n-rgb.width)//2,(n-rgb.height)//2)); sq.save(path)
W=lambda n:f'{SP}/weap/{n}.png'
CH=f'{SP}/mod4/chassis_bulwark_plated2.png'
X=1024
P=lambda n,box,size=None: piece(W(n),box,size)
MOUNT=lambda size=(300,250): P('hammer',(840,90,1210,400),size)

# ---- autocannon
b=Board()
b.put(P('rockets',(700,240,1340,1520),(270,560)),X+250,340)                # side ammo box
y=b.put(P('minigun',(830,100,1240,720)),X,60)                               # mount + receiver
y=b.put(P('hammer',(900,440,1100,1310),(250,860)),X,y-30)                   # single fat barrel
clamp=P('minigun',(830,1040,1240,1210),(400,170))
b.put(clamp,X,y-330); b.put(clamp,X,y-150)                                  # muzzle brake
b.save(W('autocannon'))

# ---- grenade launcher
b=Board()
y=b.put(MOUNT(),X,40)
y=b.put(P('minigun',(830,250,1240,720),(600,700)),X,y-30)                   # revolver drum
y=b.put(P('flamer',(860,480,1190,1560),(440,900)),X,y-40)                   # tube
def mouth(c):
    c.fill(c.ell((X-230,y-110,X+230,y+110)),(104,106,116),bevel=28)
    c.fill(c.ell((X-150,y-62,X+150,y+70)),(26,26,32),bevel=10,spec=False)
b.vd(mouth); b.save(W('grenade'))

# ---- arc projector
b=Board()
y=b.put(P('laser',(700,90,1500,1740)),X+int(__import__('os').environ.get('LX','100')),40)
def coils(c):
    for yy in (1000,1190,1380):
        c.fill(c.ell((X-260,yy,X+260,yy+130)),(198,112,56),bevel=30,strength=0.7)
        c.fill(c.ell((X-160,yy+32,X+160,yy+98)),(110,58,28),bevel=10,spec=False)
    c.fill(c.rrect((X-170,1660,X+170,1750),24),(124,126,134),bevel=18)
    for sx in (-1,1): c.fill(c.rrect((X+sx*120-50,1720,X+sx*120+50,1940),20),(124,126,134),bevel=18)
    sp=c.poly([(X,1740),(X-60,1840),(X+10,1850),(X-40,1980),(X+80,1820),(X+20,1815),(X+60,1740)])
    c.fill(sp,(110,235,255),bevel=10,strength=0.3); c.glow(sp,(140,240,255),30,0.6)
    for sx in (-1,1): c.bolt(X+sx*120,1700,18)
b.vd(coils); b.save(W('arc'))

# ---- tower shield: the chest's bolted slab plate, stretched tall
b=Board()
b.put(MOUNT(),X,40)
slab=plate(CH,(640,1000)).resize((520,1500),Image.LANCZOS)
g=np.array(slab).astype(float); lum=g[...,:3].mean(2,keepdims=True)
g[...,:3]=lum*np.array([0.96,0.98,1.04])                      # grey steel
half=Image.fromarray(g.clip(0,255).astype(np.uint8),'RGBA').crop((0,240,300,1500))
sym=Image.new('RGBA',(600,1260)); sym.paste(half,(0,0)); sym.paste(half.transpose(Image.FLIP_LEFT_RIGHT),(300,0))
b.put(sym,X,250)
def slit(c): c.fill(c.rrect((X-200,420,X+200,480),20),(26,26,32),bevel=8,spec=False)
b.vd(slit); b.save(W('towershield'))
