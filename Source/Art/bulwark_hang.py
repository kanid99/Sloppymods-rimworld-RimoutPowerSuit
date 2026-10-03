import sys
SP=sys.argv[1]
exec(open(SP+'/bulwark_chest.py').read().split("HF=helm")[0])
def place(path,cx,top,h,side):
    rgb=load(path); fig=cut_out(rgb)
    ys,xs=np.nonzero(fig); y0,y1,x0,x1=ys.min(),ys.max()+1,xs.min(),xs.max()+1
    scale=h/(y1-y0)
    ring=ndimage.binary_dilation(fig,iterations=max(1,round(OUTER/scale)))&~fig
    rgb[ring]=8; fig=fig|ring
    mask=plate_mask(rgb)*fig; rgb[~fig]=0
    c=lambda a:a[y0:y1,x0:x1]; w,hh=round((x1-x0)*scale),round((y1-y0)*scale)
    body=Image.fromarray(np.dstack([c(rgb).astype(np.uint8),c((fig*255).astype(np.uint8))]),'RGBA').resize((w,hh),Image.LANCZOS)
    m=Image.fromarray(c((mask*255).astype(np.uint8)),'L').resize((w,hh),Image.LANCZOS)
    left=int(cx-w/2); tex=Image.new('RGBA',(WC,S)); tex.paste(body,(left,top),body)
    red=Image.new('L',(WC,S),0); red.paste(m,(left,top)); z=Image.new('L',(WC,S),0)
    pair=(tex,Image.merge('RGBA',(red,z,z,tex.split()[3])))
    if side=='right': pair=tuple(i.transpose(Image.FLIP_LEFT_RIGHT) for i in pair)
    return pair
import os
_p=place(SP+'/arms/arm_bulwark.png',WC//2,58,110,'left')[0]
_w=int(np.count_nonzero((np.array(_p.split()[3])>0).any(0))); print('plate w',_w)
PW_CX=pad+int(os.environ.get('PR','62'))-_w/2
# the Bulwark shoulder plate as it sits now: right edge at the shoulder joint, top 58, height 110
plate=lambda side: clip_behind(place(SP+'/arms/arm_bulwark.png',PW_CX,58,110,side),ringw)
pb=np.array(plate('left')[0].split()[3])>0; xs=np.nonzero(pb.any(0))[0]; PCX=(xs.min()+xs.max())/2
import os; OUT=int(os.environ.get('OUT','8'))
H={'minigun':118,'rockets':104,'chainsaw':124,'laser':118,'flamer':112,'hammer':112}
def arm(name,side):
    w=clip_behind(place(f'{SP}/weap/{name}.png',PCX-OUT,58+int(os.environ.get('TOP','80')),H[name],side),ringw)
    return [w,plate(side)]
ch=chas(SP+'/mod4/chassis_bulwark_plated2.png'); cb=np.nonzero((np.array(ch[0].split()[3])>0).any(0))[0]; print('chassis x',cb.min(),cb.max(),'plate cx',PCX); HL=helm(SP+'/mod2/helmet_bulwark_lamps2.png')
loadouts=[('minigun / rockets','minigun','rockets'),('laser / chainsaw','laser','chainsaw'),('flamer / minigun','flamer','minigun'),('hammer / rockets','hammer','rockets'),('laser / laser','laser','laser'),('chainsaw / flamer','chainsaw','flamer')]
img=Image.new('RGBA',(3*345,2*330),floor); d=ImageDraw.Draw(img)
for i,(lab,a,b) in enumerate(loadouts):
    out=Image.new('RGBA',(WC,S))
    for t,m in [ch,*arm(a,'left'),*arm(b,'right'),HL]: out.alpha_composite(tint(t,m,COL['bulwark']))
    x,y=(i%3)*345,(i//3)*330
    d.text((x+6,y+4),lab,fill=(255,255,255,255))
    img.alpha_composite(out,(x+8,y+20)); img.alpha_composite(out.resize((82,64),Image.LANCZOS),(x+130,y+262))
img.save(SP+'/bulwark_hang.png')
