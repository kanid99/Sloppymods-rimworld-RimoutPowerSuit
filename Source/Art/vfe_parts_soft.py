"""Flat VFE-style chassis and shoulder plate for the Bulwark (Plated 2 design)."""
import sys; sys.path.insert(0,sys.argv[1]); SP=sys.argv[1]
from vdraw import *
import vdraw as _vd; _vd.use_soft_preset(); from vdraw import FLAT_LINE
W1=(238,238,240); W2=(206,206,210); W3=(164,164,170); DKF=(72,72,78)
def rgba(c,path): Image.fromarray(np.dstack([c.rgb.astype(np.uint8),(c.a*255).astype(np.uint8)]),'RGBA').save(path)
C=512; Ln=8
M=lambda pts:[(x,y) for x,y in pts]+[(2*C-x,y) for x,y in reversed(pts)]
c=Canvas(1024)
fill_vfe(c,c.poly(M([(C,760),(C-300,770),(C-330,900),(C-200,940),(C,946)])),W3,Ln,bevel=22)              # hips
fill_vfe(c,c.poly(M([(C,230),(C-290,250),(C-335,420),(C-300,640),(C-215,780),(C,800)])),W2,Ln,bevel=24)  # torso under the plates
for sx in (-1,1):
    x=C+sx*335; fill_vfe(c,c.ell((x-82,220,x+82,384)),W2,Ln); fill_vfe(c,c.ell((x-44,258,x+44,346)),W3,Ln)   # shoulder joints
fill_vfe(c,c.rrect((C-205,610,C+205,770),40),W2,Ln,bevel=18)                                              # abdomen
fill_vfe(c,c.rrect((C-190,662,C+190,690),10),W3,0)                                               # one suggested seam
for sx in (-1,1):                                                                                  # the two slab plates
    P=[(C+sx*40,290),(C+sx*285,305),(C+sx*318,450),(C+sx*258,600),(C+sx*44,570)]
    fill_vfe(c,c.poly(P),W1,Ln,bevel=22)
    for bx,by in ((C+sx*250,350),(C+sx*230,540)): fill_vfe(c,c.ell((bx-16,by-16,bx+16,by+16)),W3,0)   # suggested bolts
fill_vfe(c,c.poly([(C-44,262),(C+44,262),(C+34,620),(C,668),(C-34,620)]),W2,Ln,bevel=14)                  # centre ridge
fill_vfe(c,c.ell((C-182,140,C+182,268)),W3,Ln); fill_vfe(c,c.ell((C-136,166,C+136,244)),(52,52,58),0)   # collar ring
c.outline(18); rgba(c,SP+'/mod2/chassis_bulwark_soft.png')
# arm shield: a shorter, rounded-top shield on each arm, with a rim and a boss
p=Canvas(1024)
shield=p.poly([(200,230),(300,130),(512,96),(724,130),(824,230),(824,560),(700,740),(512,812),(324,740),(200,560)])
fill_vfe(p,shield,W1,Ln*2,bevel=46)
inner=p.poly([(300,270),(370,200),(512,176),(654,200),(724,270),(724,540),(630,676),(512,724),(394,676),(300,540)])
fill_vfe(p,inner,W2,Ln,bevel=30,shadow=False)
fill_vfe(p,p.ell((440,360,584,504)),W1,Ln,bevel=20)        # boss
p.outline(40); rgba(p,SP+'/mod2/plate_bulwark_soft.png')
