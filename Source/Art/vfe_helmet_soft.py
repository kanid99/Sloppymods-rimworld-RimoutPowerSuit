import sys; sys.path.insert(0,sys.argv[1]); SP=sys.argv[1]
from vdraw import *
import vdraw as _vd; _vd.use_soft_preset(); from vdraw import FLAT_LINE
c=Canvas(1024); C=512; Ln=16
W1=(236,236,238); W2=(204,204,208); W3=(160,160,166); DKF=(70,70,76); BLKF=(30,30,34)
M=lambda pts:[(x,y) for x,y in pts]+[(2*C-x,y) for x,y in reversed(pts)]
for sx in (-1,1):                                   # lamps on the crown
    x=C+sx*140
    fill_vfe(c,c.ell((x-76,120,x+76,272)),W3,Ln)
    fill_vfe(c,c.ell((x-50,146,x+50,246)),(255,176,60),Ln//2)
fill_vfe(c,c.poly(M([(C,215),(C-190,222),(C-280,320),(C-292,560),(C-250,745),(C-165,850)])),W1,Ln,bevel=40)   # shell
fill_vfe(c,c.poly(M([(C,372),(C-100,352),(C-250,368),(C-262,446),(C-60,452),(C,492)])),W2,Ln,bevel=22)      # brow
for sx in (-1,1):
    fill_vfe(c,c.poly([(C+sx*52,480),(C+sx*238,446),(C+sx*228,526),(C+sx*72,580)]),BLKF,0)          # eye socket
    fill_vfe(c,c.poly([(C+sx*84,500),(C+sx*210,474),(C+sx*204,512),(C+sx*96,546)]),(214,52,40),0)  # eye
fill_vfe(c,c.poly(M([(C,620),(C-112,630),(C-128,790),(C-86,884),(C,900)])),W2,Ln,bevel=24)                    # breather
for y in (700,770): fill_vfe(c,c.rrect((C-70,y,C+70,y+34),12),DKF,0)
for sx in (-1,1): fill_vfe(c,c.ell((C+sx*186-52,700,C+sx*186+52,804)),W3,Ln)                          # filters
c.outline(40)
c.save(SP+'/mod2/helmet_bulwark_soft.png')
Image.fromarray(np.dstack([c.rgb.astype(np.uint8),(c.a*255).astype(np.uint8)]),'RGBA').save(SP+'/mod2/helmet_bulwark_soft_rgba.png')
