import sys; sys.path.insert(0,sys.argv[1]); SP=sys.argv[1]
from vdraw import *
c=Canvas(); C=512
G=(150,152,160); D=(96,98,108); DD=(44,46,54)
M=lambda pts:[(x,y) for x,y in pts]+[(2*C-x,y) for x,y in reversed(pts)]
# shell: wide, faceted, flat-topped
shell=c.poly(M([(C,220),(C-190,228),(C-275,320),(C-290,560),(C-250,740),(C-170,840)]))
c.fill(shell,G,bevel=28)
for sx in (-1,1):   # cheek facets
    c.fill(c.poly([(C+sx*272,330),(C+sx*290,560),(C+sx*250,740),(C+sx*205,720),(C+sx*228,540),(C+sx*222,350)]),(124,126,136),bevel=14)
c.fill(c.poly(M([(C,232),(C-150,240),(C-195,320),(C-40,338)])),(162,164,172),bevel=16)   # crown plate
c.fill(c.poly([(C-24,236),(C+24,236),(C+28,420),(C,450),(C-28,420)]),(170,172,180),bevel=12,strength=0.7)  # ridge
brow=c.poly(M([(C,372),(C-90,352),(C-240,365),(C-258,440),(C-200,452),(C-60,448),(C,488)]))
c.fill(brow,(156,158,166),bevel=22,strength=0.75)
for sx in (-1,1):   # deep sockets, strongly slanted eyes (low at the centre)
    sock=c.poly([(C+sx*48,480),(C+sx*232,446),(C+sx*226,520),(C+sx*68,575)])
    c.fill(sock,DD,bevel=10,strength=0.3,spec=False)
    eye=c.poly([(C+sx*76,494),(C+sx*212,465),(C+sx*204,508),(C+sx*88,552)])
    c.fill(eye,(180,28,28),bevel=14,strength=0.6); c.glow(eye,(255,70,50),10,0.45)
    c.line([(C+sx*110,500),(C+sx*180,482)],5,(255,200,190))
for sx in (-1,1):   # jaw plates
    c.fill(c.poly([(C+sx*44,600),(C+sx*222,560),(C+sx*210,720),(C+sx*140,808),(C+sx*70,806)]),(140,142,150),bevel=18)
snout=c.poly(M([(C,612),(C-108,624),(C-124,780),(C-84,880),(C,896)]))
c.fill(snout,(118,120,130),bevel=26,strength=0.8)
c.fill(c.poly(M([(C,640),(C-80,648),(C-90,700),(C,700)])),(140,142,150),bevel=12)    # snout top plate
for y in (718,756,794,832):
    c.fill(c.rrect((C-70,y,C+70,y+22),9),DD,bevel=5,strength=0.2,spec=False)
for sx in (-1,1):
    x=C+sx*178
    c.fill(c.ell((x-56,700,x+56,812)),D,bevel=16)
    c.fill(c.ell((x-34,722,x+34,790)),DD,bevel=8,spec=False)
    for k in (-14,0,14): c.line([(x+k,730),(x+k,782)],5,(100,102,112))
for x,y in [(C-226,395),(C+226,395),(C-245,640),(C+245,640)]: c.bolt(x,y,14)
# lamps bolted ON TOP of the crown (drawn after the shell so they sit in front)
for sx in (-1,1):
    x=C+sx*138
    c.fill(c.rrect((x-30,232,x+30,290),10),D,bevel=10)                    # bracket
    c.fill(c.ell((x-70,120,x+70,262)),D,bevel=16)                         # housing
    c.fill(c.ell((x-56,134,x+56,248)),DD,bevel=8,spec=False)
    lens=c.ell((x-44,146,x+44,236)); c.fill(lens,(255,165,30),bevel=18,strength=0.55)
    c.glow(lens,(255,210,110),12,0.45)
    c.line([(x-22,166),(x-4,158)],7,(255,245,220))
c.outline(16)
c.save(SP+'/mod2/helmet_bulwark_drawn.png')
