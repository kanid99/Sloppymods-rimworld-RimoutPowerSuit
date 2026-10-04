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
S.plate(S.ell(46,84,82,118),246,212,stroke=3,mirror=True)                         # shield boss
# ---------------- HELMET
H=Layer()
H.plate(H.poly(sym([(128,66),(98,68),(76,84),(68,120),(72,160),(88,186),(110,196),(128,199)])),255,222,stroke=7)  # shell
H.plate(H.poly([(71,112),(86,110),(93,168),(89,184),(75,160)]),200,stroke=3,mirror=True)                   # cheek planes
H.plate(H.poly(sym([(128,164),(108,166),(104,188),(128,197)])),200,184,stroke=2)                            # simple chin plate, clear of the eyes
H.mark(H.rrect(118,176,138,181,2))                                                                         # one slot
H.plate(H.poly(sym([(128,104),(100,97),(77,104),(80,123),(104,123),(128,129)])),252,226,stroke=3)         # heavy brow
H.plate(H.poly([(84,124),(125,133),(124,151),(87,145)]),212,stroke=0,mirror=True)                          # bevel rim around the socket
H.plate(H.poly([(88,128),(121,137),(120,147),(91,141)]),68,stroke=1.5,mirror=True)                         # eye recess (thin line)
H.plate(H.poly([(92,137),(120,143),(120,147),(91,141)]),128,stroke=0,mirror=True)                          # lit inner bottom wall = depth
H.plate(H.ell(84,62,108,86),214,stroke=3,mirror=True)                                                      # crown lamp housings, on the shell
H.plate(H.ell(89,66,103,80),252,stroke=2,mirror=True)                                                      # lamp lenses
body,sh,hm=B.image(),S.image(),H.image()
for n,im in (('body',body),('shoulders',sh),('helmet',hm)): im.save(f'{SP}/bw2/Bulwark_{n}_south.png')
