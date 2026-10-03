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

BRASS=(214,168,70); STEEL=(128,130,140); DK=(70,72,82); BLK=(26,26,32)
def half_ell(c,box,lower=True):
    m=c.ell(box); cy=(box[1]+box[3])//2
    yy=np.arange(c.n)[:,None]
    return m&((yy>=cy) if lower else (yy<cy))

# ---- autocannon (after the vanilla turret / warcasket heavy guns): compact receiver, long barrel, brake, U-belt
from vdraw import fill_cyl
b=Board()
b.put(MOUNT((300,240)),X,30)
def ac(c):
    # ammo box low on the outer side + U-shaped brass belt looping up into the receiver
    c.fill(c.rrect((X+190,560,X+460,860),28),(96,100,92),bevel=26)            # olive ammo can
    c.fill(c.rrect((X+220,590,X+430,640),12),(70,74,68),bevel=8)
    for k in range(9):
        ang=np.pi*(k/8)                                                       # U loop from the can to the receiver
        bx=X+280-150*np.cos(ang)*0.9; by=860+150*np.sin(ang)-40
        c.fill(c.rrect((bx-40,by-26,bx+40,by+26),12),BRASS,bevel=12)
    # receiver
    c.fill(c.rrect((X-230,240,X+230,620),34),STEEL,bevel=34)
    c.fill(c.rrect((X-230,330,X+230,380),10),DK,bevel=8)                      # top-cover seam
    c.fill(c.rrect((X-260,420,X-180,600),18),DK,bevel=12)                     # side plate
    c.fill(c.rrect((X+180,420,X+260,600),18),DK,bevel=12)
    for bx in (X-150,X+150): c.bolt(bx,290,18)
    # long barrel with a recoil sleeve and reinforcing rings
    fill_cyl(c,c.rrect((X-120,600,X+120,820),20),STEEL)                       # recoil sleeve
    fill_cyl(c,c.rrect((X-80,800,X+80,1720),14),STEEL)                        # barrel
    for yy in (860,1180):
        fill_cyl(c,c.rrect((X-110,yy,X+110,yy+60),14),DK)
    # muzzle brake: stepped block with side baffles, dark bore at the tip
    fill_cyl(c,c.rrect((X-150,1680,X+150,1900),26),STEEL)
    for yy in (1715,1790):
        for x0,x1 in ((X-215,X-140),(X+140,X+215)): c.fill(c.rrect((x0,yy,x1,yy+50),12),DK,bevel=10)
    c.fill(c.ell((X-95,1850,X+95,1950)),(26,26,32),bevel=10,spec=False)
b.vd(ac); b.save(W('autocannon'))

# ---- grenade launcher: drum magazine on the side showing six rounds, fat tube, sight
b=Board()
y=b.put(MOUNT((340,260)),X,40)
y=b.put(P('minigun',(830,250,1240,720),(560,620)),X,y-30)
yt=y
y=b.put(P('flamer',(860,480,1190,1560),(470,880)),X,y-40)
def gl(c):
    cx,cy,r=X+330,yt+120,250
    c.fill(c.ell((cx-r,cy-r,cx+r,cy+r)),STEEL,bevel=36)
    c.fill(c.ell((cx-r+50,cy-r+50,cx+r-50,cy+r-50)),DK,bevel=14,spec=False)
    for k in range(6):
        ang=k*np.pi/3; gx,gy=cx+120*np.cos(ang),cy+120*np.sin(ang)
        c.fill(c.ell((gx-52,gy-52,gx+52,gy+52)),BRASS,bevel=20)
        c.fill(c.ell((gx-24,gy-24,gx+24,gy+24)),(240,120,40),bevel=10)
    c.fill(c.ell((cx-44,cy-44,cx+44,cy+44)),STEEL,bevel=16)
    c.fill(c.ell((X-250,y-120,X+250,y+120)),STEEL,bevel=32)          # mouth
    c.fill(c.ell((X-165,y-70,X+165,y+76)),BLK,bevel=10,spec=False)
    c.fill(c.rrect((X-260,yt+420,X+260,yt+500),24),DK,bevel=16)       # barrel band
b.vd(gl); b.save(W('grenade'))

# ---- arc projector: coils wrap the body (back half behind, front half in front)
b=Board()
COP=(186,110,62); COPD=(108,60,32)
CY=(1000,1190,1380)
def back(c):
    for yy in CY: c.fill(half_ell(c,(X-280,yy-30,X+280,yy+190),False),COPD,bevel=24,strength=0.4)
b.vd(back)
b.put(P('laser',(700,90,1500,1740)),X+100,40)
def front(c):
    for yy in CY:
        ring=half_ell(c,(X-280,yy-30,X+280,yy+190),True)&~c.ell((X-200,yy+10,X+200,yy+110))
        c.fill(ring,COP,bevel=26,strength=0.75)
    c.fill(c.rrect((X-180,1660,X+180,1760),26),STEEL,bevel=22)
    for sx in (-1,1):
        c.fill(c.poly([(X+sx*90,1740),(X+sx*190,1740),(X+sx*170,1960),(X+sx*110,1960)]),STEEL,bevel=22)
        c.bolt(X+sx*130,1700,20)
    sp=c.poly([(X,1760),(X-70,1860),(X+10,1870),(X-50,2010),(X+90,1840),(X+24,1832),(X+64,1760)])
    c.glow(sp,(120,230,255),40,0.55); c.fill(sp,(150,240,255),bevel=10,strength=0.3)
b.vd(front); b.save(W('arc'))

# ---- tower shield: drawn big, bevelled rim, ridge, bolts cut from the chest plate
b=Board()
b.put(MOUNT((340,280)),X,30)
chest=Image.open(CH).convert('RGB')
def shield(c):
    outer=[(X-380,260),(X+380,260),(X+400,1150),(X,1960),(X-400,1150)]
    inner=[(X-300,330),(X+300,330),(X+318,1120),(X,1820),(X-318,1120)]
    c.fill(c.poly(outer),(150,152,160),bevel=60,strength=0.7)        # thick bevelled rim
    c.fill(c.poly(inner),(118,120,130),bevel=40,strength=0.55)       # inset face
    c.fill(c.poly([(X-34,340),(X+34,340),(X+40,1700),(X,1800),(X-40,1700)]),(150,152,160),bevel=26,strength=0.8)  # ridge
    c.fill(c.rrect((X-250,520,X+250,600),30),BLK,bevel=10,spec=False)  # vision slit
    c.fill(c.rrect((X-262,600,X+262,640),16),(150,152,160),bevel=10)   # slit lip
b.vd(shield)
def bolts(c):
    for bx,by in [(X-322,320),(X+322,320),(X-338,1120),(X+338,1120),(X-170,1540),(X+170,1540)]: c.bolt(bx,by,34,(158,160,168))
b.vd(bolts)
b.save(W('towershield'))
