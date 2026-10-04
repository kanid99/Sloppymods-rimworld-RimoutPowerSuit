"""Original weapon arms drawn in our style, designed after vanilla RimWorld weapons (shape reference only)."""
import sys; sys.path.insert(0,sys.argv[1]); SP=sys.argv[1]
import numpy as np
from PIL import Image
from scipy import ndimage
import vdraw
from vdraw import fill_cyl, fill_flat
import vdraw as _v
def _flat_fill(self,mask,col,**k): fill_flat(self,mask,col,24)
_v.Canvas.fill=_flat_fill
fill_cyl=lambda c,m,col,**k: fill_flat(c,m,col,24)
_v.Canvas.glow=lambda self,*a,**k: None
N=2048; X=1024
STEEL=(150,152,160); DK=(86,88,96); BLK=(26,26,32); OLIVE=(104,116,82); PALE=(214,206,150)
BRASS=(214,168,70); TAN=(176,150,118); ORANGE=(226,120,40); CYAN=(110,230,255); RED=(196,52,40)
def ell(c,cx,cy,rx,ry): return c.ell((cx-rx,cy-ry,cx+rx,cy+ry))
def save(c,name,outline=60):
    c.outline(outline)
    m=c.a; ys,xs=np.nonzero(m); bb=(xs.min(),ys.min(),xs.max()+1,ys.max()+1)
    im=Image.fromarray(c.rgb.astype(np.uint8)); mk=Image.fromarray((m*255).astype(np.uint8))
    bg=Image.new('RGB',im.size,'white'); bg.paste(im,mask=mk); bg=bg.crop(bb)
    n=max(bg.size)+80; sq=Image.new('RGB',(n,n),'white'); sq.paste(bg,((n-bg.width)//2,(n-bg.height)//2)); sq.save(f'{SP}/weap/{name}_vfe.png')
def mount(c): c.fill(c.rrect((X-120,40,X+120,210),26),DK,bevel=20)

def autocannon():
    c=vdraw.Canvas(N); mount(c)
    for sx in (-1,1):                                            # twin ammo drums
        x0,x1=sorted((X+sx*235,X+sx*410))
        fill_cyl(c,c.rrect((x0,250,x1,760),40),OLIVE)
        for y in (330,620): fill_cyl(c,c.rrect((x0,y,x1,y+50),10),PALE)
        c.fill(c.rrect((min(X+sx*200,X+sx*250),420,max(X+sx*200,X+sx*250),520),12),DK,bevel=10)
    c.fill(c.poly([(X-235,190),(X+235,190),(X+190,600),(X-190,600)]),STEEL,bevel=34)   # wedge receiver
    c.fill(c.rrect((X-100,280,X+100,350),18),DK,bevel=10)
    fill_cyl(c,c.rrect((X-100,580,X+100,1700),24),STEEL)       # perforated jacket
    for y in range(720,1600,190): c.fill(ell(c,X,y,58,66),BLK,bevel=8,spec=False)
    fill_cyl(c,c.rrect((X-58,1690,X+58,1880),12),DK)
    fill_cyl(c,c.rrect((X-92,1840,X+92,1930),18),STEEL); c.fill(ell(c,X,1930,52,24),BLK,bevel=4,spec=False)
    save(c,'v_autocannon')

def minigun():
    c=vdraw.Canvas(N); mount(c)
    for k in range(6):                                          # belt from the ammo box into the receiver
        ang=np.pi*k/5; bx=X+260-80*np.cos(ang); by=600+120*np.sin(ang)
        c.fill(c.rrect((bx-34,by-22,bx+34,by+22),10),BRASS,bevel=10)
    c.fill(c.rrect((X+210,260,X+430,620),26),(198,160,52),bevel=26)          # yellow ammo box
    for y in (330,420,510): c.fill(c.rrect((X+235,y,X+405,y+28),8),(150,116,36),bevel=6)
    c.fill(c.rrect((X-210,180,X+220,620),36),STEEL,bevel=34)                 # receiver
    c.fill(c.rrect((X-150,260,X-60,560),16),DK,bevel=10)
    for bx in (X-96,X+96,X): fill_cyl(c,c.rrect((bx-42,600,bx+42,1800),16),STEEL if bx==X else (112,114,124))
    for y in (860,1380): fill_cyl(c,c.rrect((X-170,y,X+170,y+70),20),DK)
    fill_cyl(c,c.rrect((X-170,1760,X+170,1840),20),DK)
    for bx in (X-96,X,X+96): c.fill(ell(c,bx,1840,30,16),BLK,bevel=4,spec=False)
    save(c,'v_minigun')

def rockets():
    c=vdraw.Canvas(N); mount(c)
    c.fill(c.rrect((X-300,190,X+300,1060),50),STEEL,bevel=40)               # ribbed housing
    for x in range(X-230,X+260,92): c.fill(c.rrect((x-18,250,x+18,1000),14),DK,bevel=8)
    for sx in (-1,1): c.fill(c.poly([(X+sx*300,380),(X+sx*400,470),(X+sx*400,920),(X+sx*300,1000)]),DK,bevel=18)  # fins
    c.fill(c.rrect((X-250,1000,X+250,1120),30),DK,bevel=18)                 # launch ring
    c.fill(c.poly([(X-150,1080),(X+150,1080),(X+150,1260),(X+90,1400),(X,1460),(X-90,1400),(X-150,1260)]),RED,bevel=40,strength=0.7)  # warhead
    c.fill(c.rrect((X-150,1110,X+150,1160),10),(150,40,30),bevel=6)
    save(c,'v_rockets')

def laser():
    c=vdraw.Canvas(N); mount(c)
    c.fill(c.poly([(X-190,190),(X+190,190),(X+230,520),(X+120,1500),(X,1640),(X-120,1500),(X-230,520)]),TAN,bevel=36)
    for sx in (-1,1):
        c.fill(c.poly([(X+sx*200,560),(X+sx*360,700),(X+sx*360,820),(X+sx*170,900)]),(150,124,94),bevel=22)
        c.fill(c.poly([(X+sx*160,1000),(X+sx*290,1120),(X+sx*290,1220),(X+sx*130,1280)]),(150,124,94),bevel=22)
    core=c.rrect((X-34,300,X+34,1560),30); c.fill(core,(70,90,110),bevel=10,spec=False)
    c.glow(core,CYAN,26,0.55); c.fill(c.rrect((X-14,320,X+14,1540),12),(200,250,255),bevel=6,strength=0.2)
    tip=ell(c,X,1640,60,60); c.glow(tip,CYAN,40,0.7); c.fill(ell(c,X,1640,40,40),(210,252,255),bevel=10,strength=0.2)
    save(c,'v_laser')

def flamer():
    c=vdraw.Canvas(N); mount(c)
    fill_cyl(c,c.rrect((X+210,240,X+420,900),70),ORANGE)                    # fuel tank
    for y in (330,800): fill_cyl(c,c.rrect((X+210,y,X+420,y+40),10),(150,70,20))
    c.line([(X+300,900),(X+300,1000),(X+120,1060)],46,DK); c.line([(X+300,900),(X+300,1000),(X+120,1060)],30,(90,92,100))
    c.fill(c.rrect((X-190,180,X+190,640),34),STEEL,bevel=32)
    fill_cyl(c,c.rrect((X-80,620,X+80,1500),20),STEEL)
    for y in (760,1060): fill_cyl(c,c.rrect((X-110,y,X+110,y+50),14),DK)
    c.fill(c.poly([(X-80,1480),(X+80,1480),(X+170,1680),(X-170,1680)]),DK,bevel=24)   # flared nozzle
    fl=c.poly([(X-90,1690),(X+90,1690),(X+40,1800),(X,1880),(X-40,1800)]); c.glow(fl,(255,160,40),30,0.6); c.fill(fl,(255,170,50),bevel=14,strength=0.3)
    save(c,'v_flamer')

def hammer():
    c=vdraw.Canvas(N); mount(c)
    fill_cyl(c,c.rrect((X-62,200,X+62,1360),20),DK)                         # haft
    for y in (420,520): fill_cyl(c,c.rrect((X-82,y,X+82,y+50),12),STEEL)
    c.fill(c.rrect((X-300,1320,X+300,1780),110),STEEL,bevel=50)             # rounded head
    c.fill(c.rrect((X-220,1380,X+220,1720),80),(116,118,128),bevel=30)
    for cx,cy in ((X-140,1550),(X+140,1550),(X,1550)):
        e=ell(c,cx,cy,44,44); c.glow(e,CYAN,22,0.5); c.fill(e,(170,240,255),bevel=12,strength=0.3)
    for sx in (-1,1): c.fill(c.rrect((X+sx*300-(40 if sx>0 else 0),1440,X+sx*300+(0 if sx>0 else 40),1660),18),DK,bevel=12)
    save(c,'v_hammer')

for f in (autocannon,minigun,rockets,laser,flamer,hammer): f()
