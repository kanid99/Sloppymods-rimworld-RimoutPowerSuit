from PIL import ImageDraw
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
def _outlined(pair,w=1,round_r=10):
    tex,m=pair; a=np.array(tex.split()[3])>100
    # round off the straight-cut corners, then put the outline all the way round
    a=ndimage.binary_closing(a,structure=np.ones((3,3)),iterations=1)
    sm=ndimage.gaussian_filter(a.astype(float),round_r/3)>0.5; a=a&sm
    ring=ndimage.binary_dilation(a,iterations=w)&~a
    t=np.array(tex).copy(); t[...,3]=np.where(a,255,0); t[ring]=(14,14,18,255)
    mm=np.array(m).copy(); mm[...,3]=np.where(a|ring,255,0); mm[ring,0]=0
    return Image.fromarray(t,'RGBA'),Image.fromarray(mm,'RGBA')
plate=lambda side: _outlined(place(SP+'/arms/arm_bulwark.png',PW_CX,int(os.environ.get('PT','58')),110,side))
pb=np.array(plate('left')[0].split()[3])>0; xs=np.nonzero(pb.any(0))[0]; PCX=(xs.min()+xs.max())/2
import os; OUT=int(os.environ.get('OUT','8'))
H={'minigun':118,'rockets':104,'chainsaw':124,'laser':118,'flamer':112,'hammer':112}
def arm(name,side):
    w=clip_behind(place(f'{SP}/weap/{name}.png',PCX-OUT,58+int(os.environ.get('TOP','80')),H[name],side),ringw)
    return [w,plate(side),joint(side)]
import cv2
def joint(side,r=10):
    "a ball elbow between the shoulder plate and the weapon"
    pa=np.array(plate('left')[0].split()[3])>100; ys,xs=np.nonzero(pa)
    cx=PCX-OUT; cy=ys.max()+2
    if side=='right': cx=WC-cx
    K=4; n=WC*K; img=Image.new('RGBA',(WC*K,S*K)); d=ImageDraw.Draw(img)
    d.ellipse(((cx-r-1.5)*K,(cy-r-1.5)*K,(cx+r+1.5)*K,(cy+r+1.5)*K),fill=(14,14,18,255))
    for i in range(r*K,0,-1):                       # radial shading, light from the upper left
        t=i/(r*K); v=int(140-62*t)
        d.ellipse(((cx-r*0.18*(1-t))*K-i,(cy-r*0.22*(1-t))*K-i,(cx-r*0.18*(1-t))*K+i,(cy-r*0.22*(1-t))*K+i),fill=(v,v+2,v+8,255))
    img=img.resize((WC,S),Image.LANCZOS); z=Image.new('RGBA',(WC,S))
    return img,z
def soften(pair,keep=4,depth=0.72,erode=0):
    "remove inner black lines: fill them from the surrounding paint, leave a soft crease"
    tex,m=pair; t=np.array(tex).copy(); A=t[...,3]>100; L=t[...,:3].mean(2)
    d=ndimage.distance_transform_edt(A)
    dark=(L<70)&(d>keep); thick=ndimage.binary_opening(dark,iterations=2)
    line=dark&~ndimage.binary_dilation(thick,iterations=1)
    rgb=np.ascontiguousarray(t[...,:3]); filled=cv2.inpaint(rgb,(line*255).astype(np.uint8),5,cv2.INPAINT_TELEA)
    crease=ndimage.gaussian_filter(line.astype(float),1.2)
    out=filled.astype(float)*(1-(1-depth)*np.clip(crease*1.6,0,1))[...,None]
    t[...,:3]=np.clip(out,0,255).astype(np.uint8)
    if erode: A2=ndimage.binary_erosion(A,iterations=erode); t[...,3]=np.where(A2,t[...,3],0)
    mm=np.array(m).copy(); mm[...,3]=t[...,3]
    if line.any():                                   # paint the filled lines like their neighbours
        r=mm[...,0].astype(float); rf=cv2.inpaint(np.ascontiguousarray(mm[...,0]),(line*255).astype(np.uint8),5,cv2.INPAINT_TELEA); mm[...,0]=np.where(line,rf,r)
    return Image.fromarray(t,'RGBA'),Image.fromarray(mm,'RGBA')
ch=chas(SP+'/mod4/chassis_bulwark_plated2.png'); cb=np.nonzero((np.array(ch[0].split()[3])>0).any(0))[0]; print('chassis x',cb.min(),cb.max(),'plate cx',PCX); HL=helm(SP+'/mod2/helmet_bulwark_lamps2.png')
if os.environ.get('SOFT'): ch=soften(ch); HL=soften(HL,keep=4)
loadouts=[('minigun / rockets','minigun','rockets'),('laser / chainsaw','laser','chainsaw'),('flamer / minigun','flamer','minigun'),('hammer / rockets','hammer','rockets'),('laser / laser','laser','laser'),('chainsaw / flamer','chainsaw','flamer')]
img=Image.new('RGBA',(3*345,2*330),floor); d=ImageDraw.Draw(img)
for i,(lab,a,b) in enumerate(loadouts):
    out=Image.new('RGBA',(WC,S))
    for t,m in [ch,*arm(a,'left'),*arm(b,'right'),HL]: out.alpha_composite(tint(t,m,COL['bulwark']))
    x,y=(i%3)*345,(i//3)*330
    d.text((x+6,y+4),lab,fill=(255,255,255,255))
    img.alpha_composite(out,(x+8,y+20)); img.alpha_composite(out.resize((82,64),Image.LANCZOS),(x+130,y+262))
img.save(SP+'/bulwark_hang.png')
