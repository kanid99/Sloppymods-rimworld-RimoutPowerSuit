# hand-drawn (code) weapon arms in the suit's cartoon style: flat fills, a light band, a dark band, thick outline
import sys
from PIL import Image, ImageDraw
SP=sys.argv[1]; K=2   # supersample
OL=9*K; INK=(14,14,16)
GREY=(112,114,122); DARK=(70,72,80); COPPER=(196,112,58); CYAN=(80,230,255)
def sh(c,f): return tuple(max(0,min(255,int(v*f))) for v in c)
def new(w=300,h=820): im=Image.new('RGB',(w*K,h*K),'white'); return im,ImageDraw.Draw(im)
def S(*v): return [x*K for x in v]
def box(d,x0,y0,x1,y1,c=GREY,r=14,shade=True):
    d.rounded_rectangle(S(x0,y0,x1,y1),radius=r*K,fill=INK)
    i=OL
    d.rounded_rectangle([x0*K+i,y0*K+i,x1*K-i,y1*K-i],radius=max(1,r*K-i),fill=c)
    if shade:
        w=x1-x0
        d.rectangle([x0*K+i+int(w*0.12*K),y0*K+i+4*K,x0*K+i+int(w*0.26*K),y1*K-i-4*K],fill=sh(c,1.28))
        d.rectangle([x1*K-i-int(w*0.2*K),y0*K+i,x1*K-i,y1*K-i],fill=sh(c,0.72))
def ell(d,x0,y0,x1,y1,c=GREY):
    d.ellipse(S(x0,y0,x1,y1),fill=INK); d.ellipse([x0*K+OL,y0*K+OL,x1*K-OL,y1*K-OL],fill=c)
def line(d,x0,y0,x1,y1,w=6,c=INK): d.line(S(x0,y0,x1,y1),fill=c,width=w*K)
def bolt(d,x,y,r=11): ell(d,x-r,y-r,x+r,y+r,sh(GREY,1.15))
def mount(d,cx=150): box(d,cx-62,10,cx+62,92,DARK,12)
WIDEN={'towershield':1.9,'arc':1.5}
def save(im,name):
    im=im.resize((int(im.width//K*WIDEN.get(name,1.6)),im.height//K),Image.LANCZOS); n=max(im.size)+40
    sq=Image.new('RGB',(n,n),'white'); sq.paste(im,((n-im.width)//2,(n-im.height)//2)); sq.save(f'{SP}/weap/{name}.png')

# autocannon: receiver, side ammo box, one fat barrel, slotted muzzle brake
im,d=new(); mount(d)
box(d,150+60,150,150+128,330,sh(GREY,0.9),10)          # ammo box on the side
line(d,150+70,240,150+118,240,5)
box(d,70,70,230,360,GREY,22)                             # receiver
line(d,90,200,210,200,6); bolt(d,100,110); bolt(d,200,110)
box(d,112,350,188,650,GREY,10)                           # barrel
box(d,92,640,208,780,DARK,16)                            # muzzle brake
for y in (670,705,740): box(d,104,y,196,y+18,INK,6,False)
save(im,'autocannon')

# grenade launcher: fluted revolver drum, wide short tube, dark round mouth
im,d=new(); mount(d)
box(d,58,80,242,330,GREY,40)                             # drum
for x in (100,150,200): line(d,x,110,x,300,8)
box(d,88,320,212,700,GREY,18)                            # tube
box(d,78,430,222,470,DARK,8)                             # band
ell(d,82,660,218,770,DARK); ell(d,108,684,192,748,INK)  # mouth
save(im,'grenade')

# arc projector: core rod, three copper coils, forked emitter, blue spark
im,d=new(); mount(d)
box(d,118,80,182,640,DARK,10)                            # core
for y in (170,300,430): ell(d,74,y,226,y+76,COPPER); ell(d,108,y+20,192,y+56,sh(COPPER,0.6)); box(d,118,y+30,182,y+60,DARK,4,False)
box(d,90,600,210,660,GREY,12)                            # emitter yoke
box(d,86,650,128,760,GREY,10); box(d,172,650,214,760,GREY,10)   # prongs
pts=[(150,662),(118,722),(146,728),(126,800),(184,716),(156,710),(176,662)]
d.polygon([(x*K,y*K) for x,y in pts],fill=CYAN,outline=INK,width=4*K)
save(im,'arc')

# tower shield: tapered slab with a centre ridge, vision slit, bolts
im,d=new(260,860)
box(d,82,10,178,92,DARK,12)
pts=[(20,70),(240,70),(240,690),(130,840),(20,690)]
d.polygon([(x*K,y*K) for x,y in pts],fill=INK)
inn=[(36,86),(224,86),(224,682),(130,814),(36,682)]
d.polygon([(x*K,y*K) for x,y in inn],fill=GREY)
d.polygon([(x*K,y*K) for x,y in [(36,86),(70,86),(70,700),(36,682)]],fill=sh(GREY,1.25))
d.polygon([(x*K,y*K) for x,y in [(130,86),(224,86),(224,682),(130,814)]],fill=sh(GREY,0.8))
line(d,130,86,130,814,6)
box(d,56,200,204,226,INK,8,False)
for x in (56,204): bolt(d,x,120,13); bolt(d,x,640,13)
save(im,'towershield')
