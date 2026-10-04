import sys; sys.path.insert(0,sys.argv[1]); SP=sys.argv[1]
from rw_style import *
def sym(left):            # left half points (x<128) -> full symmetric outline
    return left+[(256-x,y) for x,y in reversed(left)]
# ---------------- BODY: a rounded cuirass (breastplate, belly plates, belt, hanging hip plates)
B=Layer()
cut=lambda m,y: m&(np.arange(N)[:,None]<y*K)
cuir=cut(B.ell(34,18,222,250),214)
B.plate(cuir,236,206)                                                          # cuirass (sides show as the flanks)
B.plate(cuir&~B.ell(50,18,206,250),204,stroke=0)                               # rounded flank side faces
B.plate(B.rrect(76,16,180,92,30),245,225)                                      # collar rim
B.plate(B.ell(84,30,172,96),82,stroke=4)                                       # neck opening (under the helmet)
B.plate(cut(B.ell(36,26,220,204),184),255,230)                                 # breastplate, full chest width, curved lower edge
B.plate(B.poly([(118,60),(138,60),(136,168),(128,178),(120,168)]),222,stroke=3)  # breastplate keel
B.plate(B.rrect(56,180,200,198,10),230,214)                                    # belly plate 1
B.plate(B.rrect(66,196,190,212,9),220,204)                                     # belly plate 2
B.plate(B.poly([(40,212),(94,216),(98,250),(58,246),(38,228)]),212,184,mirror=True)   # hip plates (tassets)
B.plate(B.rrect(56,206,200,220,6),172)                                         # belt
B.plate(B.poly([(100,220),(156,220),(150,254),(106,254)]),240,210)             # centre hip plate
B.mark(B.rrect(120,209,136,217,2),110)                                         # belt buckle
# ---------------- SHOULDERS: one stylised pauldron per side, no arm plates below
S=Layer()
SX,SY=0.76,-12                     # pauldron placement: narrower toward the helmet, raised
_poly,_ell=S.poly,S.ell
TILT=np.radians(19); PX,PY=96,110        # tilt: outer edge rises, pivoting near the inner corner
def _tf(x,y):
    x,y=x-PX,y-PY; x,y=x*np.cos(TILT)-y*np.sin(TILT),x*np.sin(TILT)+y*np.cos(TILT); x,y=x+PX,y+PY
    return 2+(x-2)*SX, y+SY
S.poly=lambda pts:_poly([_tf(x,y) for x,y in pts])
S.ell=lambda x0,y0,x1,y1:(lambda c0,c1:_ell(c0[0]-(x1-x0)*SX/2,c0[1]-(y1-y0)/2,c0[0]+(x1-x0)*SX/2,c0[1]+(y1-y0)/2))(_tf((x0+x1)/2,(y0+y1)/2),None)
def arc(cx,cy,rx,ry,a0,a1,n=40):
    return [(cx+rx*np.cos(t),cy+ry*np.sin(t)) for t in np.linspace(np.radians(a0),np.radians(a1),n)]
shell=arc(60,112,56,62,180,330)+[(108,98),(104,122),(66,138),(26,146),(6,132)]   # domed top, flared angled lower edge
S.plate(S.poly(shell),255,220,mirror=True)
S.plate(S.poly(arc(60,112,56,62,180,262)+[(56,58),(46,66),(26,82),(14,104),(10,124)]),206,stroke=0,mirror=True)  # outer side face
rim=S.poly(arc(60,112,56,62,196,320)+list(reversed(arc(60,120,46,54,196,320))))
S.plate(rim,240,226,stroke=3,mirror=True)                                         # raised rim along the top
S.plate(S.poly([(10,132),(26,146),(66,138),(104,122),(104,130),(66,148),(24,156),(8,142)]),188,stroke=3,mirror=True)  # lip under the flare
S.plate(S.ell(30,62,78,96),255,stroke=0,mirror=True)                              # lit cap of the dome
S.plate(S.ell(52,86,84,118),246,212,stroke=3,mirror=True)                         # shield boss
for bx,by in ((24,112),(92,100)): S.plate(S.ell(bx-5,by-5,bx+5,by+5),236,stroke=1.5,mirror=True)   # bolt bumps
# ---------------- HELMET: domed, deep angled eyes under a heavy brow, faceplate ridge, protruding jaw
H=Layer()
def bez(p0,p1,p2,n=24):
    return [((1-t)**2*p0[0]+2*(1-t)*t*p1[0]+t*t*p2[0],(1-t)**2*p0[1]+2*(1-t)*t*p1[1]+t*t*p2[1]) for t in np.linspace(0,1,n)]
def bump(x,y,r=4.5): H.plate(H.ell(x-r,y-r,x+r,y+r),236,stroke=1.5)
# ear cylinders behind the shell
H.plate(H.rrect(63,120,80,160,7),198,176,stroke=4,mirror=True)
dome=bez((72,150),(64,66),(128,62))+bez((128,62),(192,66),(184,150))+bez((184,150),(176,196),(128,202))+bez((128,202),(80,196),(72,150))
H.plate(H.poly(dome),255,214,stroke=7)                                                                    # domed shell
H.plate(H.poly(bez((74,120),(70,170),(100,196))+[(104,184),(86,150),(86,118)]),206,stroke=0,mirror=True)  # shaded cheek side
face=bez((88,112),(128,98),(168,112))+[(166,150)]+bez((166,150),(160,192),(128,196))+bez((128,196),(96,192),(90,150))
H.plate(H.poly(face),246,222,stroke=3)                                                                    # faceplate
H.plate(H.poly([(122,104),(134,104),(134,186),(128,192),(122,186)]),224,stroke=2)                          # centre ridge
# heavy brow, one arch, overhanging the eyes
# deep-set eye lenses angled down toward the centre (recess rules: thin line, lit lower wall, bevel rim)
H.plate(H.poly([(82,124),(121,134),(122,158),(86,152)]),212,stroke=0,mirror=True)
H.plate(H.poly([(86,127),(118,137),(119,154),(90,149)]),62,stroke=1.5,mirror=True)
H.plate(H.poly([(90,144),(119,149),(119,154),(90,149)]),132,stroke=0,mirror=True)
brow=bez((78,118),(128,90),(178,118))+bez((178,128),(128,106),(78,128))
H.plate(H.poly(brow),252,226,stroke=3)
# protruding jaw: a rounded block standing out from the faceplate, one slot
H.plate(H.rrect(106,160,150,198,12),214,184,stroke=3)
H.plate(H.rrect(110,163,146,172,4),236,stroke=0)                                                          # lit top face of the jaw
H.mark(H.rrect(118,180,138,185,2))
# lamp windows set into the crown
def lamp(sx):
    q=lambda pts:[(128+sx*x,y) for x,y in pts]
    H.plate(H.poly(q([(14,74),(42,72),(46,92),(16,96)])),214,stroke=0)
    H.plate(H.poly(q([(18,77),(39,75),(42,89),(19,92)])),104,stroke=1.5)
    H.plate(H.poly(q([(20,79),(38,77),(40,86),(21,88)])),246,stroke=0)
for sx in (-1,1): lamp(sx)
for sx in (-1,1): bump(128+sx*52,174)                                                   # a few bolt bumps
body,sh,hm=B.image(),S.image(),H.image()
for n,im in (('body',body),('shoulders',sh),('helmet',hm)): im.save(f'{SP}/bw2/Bulwark_{n}_south.png')
