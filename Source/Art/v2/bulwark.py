import sys; sys.path.insert(0,sys.argv[1]); SP=sys.argv[1]
from rw_style import *
def sym(left):            # left half points (x<128) -> full symmetric outline
    return left+[(256-x,y) for x,y in reversed(left)]
# ---------------- BODY
B=Layer()
B.plate(B.rrect(40,26,216,212,36),226,196)                                    # torso block
B.plate(B.rrect(78,18,178,70,24),245,225)                                     # collar rim
B.plate(B.ell(102,28,154,52),82,stroke=4)                                      # neck opening
B.plate(B.poly([(42,186),(94,192),(100,248),(54,242),(38,212)]),205,178,mirror=True)   # side hip plates
B.plate(B.poly([(90,196),(166,196),(158,252),(98,252)]),242,208)              # centre hip plate
B.plate(B.rrect(66,158,190,202,10),192,176)                                   # abdomen
for y in (170,184): B.mark(B.rrect(80,y,104,y+5,2),mirror=True)               # two vent slots each side
B.plate(B.poly([(46,62),(122,72),(122,154),(72,166),(42,128)]),255,226,mirror=True)   # chest slabs
B.plate(B.poly([(72,166),(122,154),(122,164),(76,176)]),204,mirror=True)      # slab under-bevel
B.plate(B.poly([(118,66),(138,66),(135,170),(128,180),(121,170)]),212)        # centre ridge
# ---------------- SHOULDERS
S=Layer()
cut=lambda m,y: m&(np.arange(N)[:,None]<y*K)
S.plate(S.poly([(10,118),(78,112),(84,166),(18,172)]),168,150,mirror=True)                       # under-plate
pd=cut(S.ell(5,46,113,160),146)
S.plate(pd,255,222,mirror=True)                                                                 # rounded pauldron
S.plate(pd&~S.ell(15,52,121,166),204,stroke=0,mirror=True)                                       # outer rounded side face
S.plate(cut(S.ell(32,62,94,132),132),246,216,stroke=3,mirror=True)                              # raised shield boss
S.plate(S.poly([(12,140),(100,140),(100,150),(80,158),(16,156)]),190,stroke=3,mirror=True)         # lower rim band
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
