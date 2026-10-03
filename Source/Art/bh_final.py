import sys; sys.path.insert(0,'.')
SP=sys.argv[1]
src=open(SP+'/build_arms_flat4.py').read().split('floor=(92,84,70,255)')[0].replace("SP=sys.argv[1]","SP=sys.argv[1]; sys.argv=[sys.argv[0],SP,'92']")
exec(src)
from PIL import ImageDraw
floor=(92,84,70,255)
WC=320; pad=(WC-S)//2
ringw=np.zeros((S,WC),bool); ringw[:,pad:pad+S]=ring_final
def wide_clip(pair): return clip_behind(pair, ringw)
def chassis_of(path):
    lay=layer(path,T); c=collar(lay[0]); return rescale(flatten_collar(shift(lay,0,CANON_CY-c[1])),GS)
def helmet_of(path):
    return rescale(helmet_layer(path,127,CANON_BOTTOM+DROP,HW),GS)
FL=wide_clip(widen(clip_behind(arm_layer(f'{SP}/arms/arm_flamer.png',102,70,150,'left'),ring_final),WC))
# hammer: pivot in the shoulder plate (upper right of the left-side drawing), placed where the
# unswung plate sat; mirrored onto the right shoulder
def hammer(angle,height):
    # the plate's inner-top area, in the wide canvas, for the LEFT side
    piv=(pad+92, 84)
    return wide_clip(swung_arm_layer(f'{SP}/arms/arm_hammer.png',piv,(0.72,0.14),height,angle,'right',WC))
CH={'notches':chassis_of(SP+'/mod4/chassis_bughunter_v1.png'),'chevron':chassis_of(SP+'/mod4/chassis_bughunter_v2.png')}
HE={'lamps on top':helmet_of(SP+'/mod2/helmet_bughunter_lamps1.png'),'lamps in brow':helmet_of(SP+'/mod2/helmet_bughunter_lamps2.png')}
builds=[]
for hk in HE:
    for ck in CH:
        builds.append((f'helmet: {hk}\nchassis: {ck}',[widen(CH[ck],WC),FL,hammer(24,176),widen(HE[hk],WC)]))
img=Image.new('RGBA',(4*330,380),floor); d=ImageDraw.Draw(img)
for i,(lab,layers) in enumerate(builds):
    s=stack(layers,COL['bughunter']) if False else None
    out=Image.new('RGBA',(WC,S))
    for t,m in layers: out.alpha_composite(tint(t,m,COL['bughunter']))
    d.text((i*330+6,4),lab,fill=(255,255,255,255))
    img.alpha_composite(out.resize((int(WC*0.95),int(S*0.95)),Image.LANCZOS),(i*330+5,34))
    img.alpha_composite(out.resize((80,64),Image.LANCZOS),(i*330+120,300))
img.save(SP+'/bh_final.png')
