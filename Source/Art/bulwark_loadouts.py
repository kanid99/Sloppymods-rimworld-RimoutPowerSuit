import sys; sys.path.insert(0,'.')
SP=sys.argv[1]
src=open(SP+'/build_arms_flat4.py').read().split('floor=(92,84,70,255)')[0].replace("SP=sys.argv[1]","SP=sys.argv[1]; sys.argv=[sys.argv[0],SP,'92']")
exec(src)
from PIL import ImageDraw
floor=(92,84,70,255)
WC=328; pad=(WC-S)//2
ringw=np.zeros((S,WC),bool); ringw[:,pad:pad+S]=ring_final
def warm(name,side,h=196):
    # the plate sits where the Bulwark plate sat: inner edge near x=98+pad, top at 58
    p=arm_layer(f'{SP}/arms2/arm_{name}.png',98+pad+18,58,h,'left')   # built on the wide canvas
    return p
def arm_wide(name,side,h=196):
    rgbpair=arm_layer_wide(f'{SP}/arms2/arm_{name}.png',side,h)
    return clip_behind(rgbpair,ringw)
def arm_layer_wide(path,side,h):
    import numpy as np
    from PIL import Image
    rgb=load(path); fig=cut_out(rgb)
    ys,xs=np.nonzero(fig); y0,y1,x0,x1=ys.min(),ys.max()+1,xs.min(),xs.max()+1
    scale=h/(y1-y0)
    ring=ndimage.binary_dilation(fig,iterations=max(1,round(OUTER/scale)))&~fig
    rgb[ring]=8; fig=fig|ring
    mask=plate_mask(rgb)*fig; rgb[~fig]=0
    crop=lambda a:a[y0:y1,x0:x1]
    w,hh=round((x1-x0)*scale),round((y1-y0)*scale)
    body=Image.fromarray(np.dstack([crop(rgb).astype(np.uint8),crop((fig*255).astype(np.uint8))]),'RGBA').resize((w,hh),Image.LANCZOS)
    m=Image.fromarray(crop((mask*255).astype(np.uint8)),'L').resize((w,hh),Image.LANCZOS)
    left=int(pad+104-w)   # inner (right) edge of the left piece at the shoulder joint
    tex=Image.new('RGBA',(WC,S)); tex.paste(body,(left,58),body)
    red=Image.new('L',(WC,S),0); red.paste(m,(left,58)); z=Image.new('L',(WC,S),0)
    pair=(tex,Image.merge('RGBA',(red,z,z,tex.split()[3])))
    if side=='right': pair=tuple(i.transpose(Image.FLIP_LEFT_RIGHT) for i in pair)
    return pair
CHW=widen(C['bulwark'],WC)
def helm(path): return widen(rescale(helmet_layer(path,127,CANON_BOTTOM+DROP,HW),GS),WC)
HB=helm(SP+'/mod2/helmet_bulwark.png')
loadouts=[('minigun / rockets','minigun','rockets'),('laser / chainsaw','laser','chainsaw'),('flamer / minigun','flamer','minigun'),('hammer / rockets','hammer','rockets'),('laser / laser','laser','laser'),('chainsaw / flamer','chainsaw','flamer')]
img=Image.new('RGBA',(3*345,2*330),floor); d=ImageDraw.Draw(img)
for i,(lab,a,b) in enumerate(loadouts):
    out=Image.new('RGBA',(WC,S))
    for t,m in [CHW,arm_wide(a,'left'),arm_wide(b,'right'),HB]: out.alpha_composite(tint(t,m,COL['bulwark']))
    x,y=(i%3)*345,(i//3)*330
    d.text((x+6,y+4),lab,fill=(255,255,255,255))
    img.alpha_composite(out,(x+8,y+20))
    img.alpha_composite(out.resize((82,64),Image.LANCZOS),(x+130,y+262))
img.save(SP+'/bulwark_loadouts.png')
# helmet options on the suit
img=Image.new('RGBA',(3*345,300),floor); d=ImageDraw.Draw(img)
for i,(lab,p) in enumerate([('current helmet',SP+'/mod2/helmet_bulwark.png'),('new face 1',SP+'/mod2/helmet_bulwark_face1.png'),('new face 2',SP+'/mod2/helmet_bulwark_face2.png')]):
    out=Image.new('RGBA',(WC,S))
    for t,m in [CHW,arm_wide('minigun','left'),arm_wide('rockets','right'),helm(p)]: out.alpha_composite(tint(t,m,COL['bulwark']))
    d.text((i*345+6,4),lab,fill=(255,255,255,255))
    img.alpha_composite(out,(i*345+8,20))
    img.alpha_composite(out.resize((82,64),Image.LANCZOS),(i*345+130,232) )
img.save(SP+'/bulwark_helmets.png')
