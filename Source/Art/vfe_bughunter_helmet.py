"""Bughunter helmet: twin-filter gas mask, four eye lenses, two crown lamps. Soft VFE style."""
import sys; sys.path.insert(0,sys.argv[1]); SP=sys.argv[1]
from vdraw import *
import vdraw as _vd; _vd.use_soft_preset()
from vdraw import FLAT_LINE
c=Canvas(1024); C=512; Ln=12
W1=(240,240,242); W2=(212,212,216); W3=(176,176,182); DK=(86,86,94); GL=(58,60,66)
M=lambda pts:[(x,y) for x,y in pts]+[(2*C-x,y) for x,y in reversed(pts)]
def mirror(fn):
    for sx in (-1,1): fn(sx)
# crown lamps (behind the shell)
def lamp(sx):
    x=C+sx*128
    fill_vfe(c,c.rrect((x-36,150,x+36,240),14),W3,Ln,bevel=10)
    fill_vfe(c,c.ell((x-70,96,x+70,232)),W2,Ln,bevel=18)
    fill_vfe(c,c.ell((x-48,118,x+48,210)),(255,184,70),Ln//2,shadow=False)
    c.line([(x-24,140),(x-6,130)],10,(255,246,224))
mirror(lamp)
def egg(cx,top,bottom,wtop,wbot,n=90):
    pts=[]
    for i in range(n):
        t=2*np.pi*i/n; y=np.cos(t); x=np.sin(t)
        yy=(top+bottom)/2-y*(bottom-top)/2
        w=wtop if y>0 else wbot+(wtop-wbot)*(1+y)**1.6
        pts.append((cx+x*w,yy))
    return pts
shell=c.poly(egg(C,170,840,300,150))
fill_vfe(c,shell,W1,Ln,bevel=44)
# cheek plates sweeping down to the jaw
mirror(lambda sx: fill_vfe(c,c.poly([(C+sx*292,430),(C+sx*296,540),(C+sx*262,660),(C+sx*186,770),(C+sx*150,700),(C+sx*214,560),(C+sx*230,470)]),W2,Ln,bevel=22))
# brow ridge with the two small upper lenses
fill_vfe(c,c.poly(M([(C,300),(C-90,292),(C-176,318),(C-186,368),(C-80,374),(C,392)])),W2,Ln,bevel=18)
def small_eye(sx):
    x=C+sx*84; fill_vfe(c,c.ell((x-38,306,x+38,374)),W3,Ln//2,shadow=False)
    fill_vfe(c,c.ell((x-26,316,x+26,364)),GL,0,shadow=False); c.line([(x-12,328),(x-2,324)],8,(230,232,236))
mirror(small_eye)
# big teardrop lenses, slanting up and out like an insect's
def big_eye(sx):
    p=[(C+sx*36,500),(C+sx*70,446),(C+sx*150,418),(C+sx*244,410),(C+sx*258,446),(C+sx*214,512),(C+sx*120,560),(C+sx*56,556)]
    fill_vfe(c,c.poly(p),DK,Ln,shadow=False)
    q=[(C+sx*58,502),(C+sx*86,462),(C+sx*156,438),(C+sx*230,430),(C+sx*238,452),(C+sx*202,500),(C+sx*118,538),(C+sx*72,536)]
    fill_vfe(c,c.poly(q),GL,0,shadow=False)
    c.line([(C+sx*110,462),(C+sx*180,446)],11,(226,228,232))
mirror(big_eye)
# narrow mask snout with a hexagonal port
fill_vfe(c,c.poly(M([(C,566),(C-86,580),(C-122,664),(C-104,766),(C-50,820),(C,828)])),W2,Ln,bevel=26)
fill_vfe(c,c.poly(M([(C,640),(C-58,652),(C-74,706),(C-54,764),(C,776)])),DK,Ln,shadow=False)
fill_vfe(c,c.poly(M([(C,664),(C-36,672),(C-46,706),(C-34,744),(C,750)])),GL,0,shadow=False)
# filter canisters hanging low and angled out
def filt(sx):
    cx,cy=C+sx*196,748
    fill_vfe(c,c.ell((cx-92,cy-76,cx+92,cy+76)),W3,Ln,bevel=24)
    fill_vfe(c,c.ell((cx-68,cy-54,cx+68,cy+54)),W2,Ln,bevel=14,shadow=False)
    fill_vfe(c,c.ell((cx-40,cy-32,cx+40,cy+32)),DK,Ln//2,shadow=False)
    fill_vfe(c,c.ell((cx-22,cy-18,cx+22,cy+18)),GL,0,shadow=False)
mirror(filt)
c.outline(40)
Image.fromarray(np.dstack([c.rgb.astype(np.uint8),(c.a*255).astype(np.uint8)]),'RGBA').save(SP+'/mod2/helmet_bughunter_soft_rgba.png')
c.save(SP+'/mod2/helmet_bughunter_soft.png')
