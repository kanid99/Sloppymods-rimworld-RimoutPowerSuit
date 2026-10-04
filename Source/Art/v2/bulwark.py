import sys; sys.path.insert(0,sys.argv[1]); SP=sys.argv[1]
from rw_style import *
def sym(left):            # left half points (x<128) -> full symmetric outline
    return left+[(256-x,y) for x,y in reversed(left)]
# ---------------- BODY
B=Layer()
B.plate(B.rrect(40,26,216,212,36),226,196)                                    # torso block
B.plate(B.rrect(72,18,184,92,30),245,225)                                     # collar rim
B.plate(B.ell(84,30,172,96),82,stroke=4)                                      # neck opening
B.plate(B.poly([(42,186),(94,192),(100,248),(54,242),(38,212)]),205,178,mirror=True)   # side hip plates
B.plate(B.poly([(90,196),(166,196),(158,252),(98,252)]),242,208)              # centre hip plate
B.plate(B.rrect(62,150,194,204,12),236,206)                                   # lower chest plate, the part seen below the helmet
for y in (168,182): B.mark(B.rrect(76,y,100,y+5,2),mirror=True)               # two vent slots each side
B.plate(B.poly([(46,62),(122,72),(122,150),(78,156),(42,128)]),255,226,mirror=True)   # chest slabs
B.plate(B.poly([(118,66),(138,66),(136,150),(128,158),(120,150)]),212)        # centre ridge (ends under the helmet)
# ---------------- SHOULDERS: one stylised pauldron per side, no arm plates below
S=Layer()
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
H.plate(H.poly(sym([(128,148),(106,150),(94,170),(104,192),(128,197)])),186,170,stroke=3)                 # breather jaw (mid grey)
for y in (162,174): H.mark(H.rrect(117,y,139,y+5,2))                                                        # breather slots
H.plate(H.poly(sym([(128,104),(100,97),(77,104),(80,123),(104,123),(128,129)])),252,226,stroke=3)         # heavy brow
H.plate(H.poly([(88,128),(121,137),(120,147),(91,141)]),80,stroke=3,mirror=True)                           # slanted eye slits
H.plate(H.ell(84,62,108,86),214,stroke=3,mirror=True)                                                      # crown lamp housings, on the shell
H.plate(H.ell(89,66,103,80),252,stroke=2,mirror=True)                                                      # lamp lenses
body,sh,hm=B.image(),S.image(),H.image()
for n,im in (('body',body),('shoulders',sh),('helmet',hm)): im.save(f'{SP}/bw2/Bulwark_{n}_south.png')
