from PIL import ImageDraw
import os
import sys
SP=sys.argv[1]
exec(open(SP+'/bulwark_chest.py').read().split("HF=helm")[0])
def place(path,cx,top,h,side,ref=None):
    rgb=load(path); fig=cut_out(rgb)
    ys,xs=np.nonzero(fig); y0,y1,x0,x1=ys.min(),ys.max()+1,xs.min(),xs.max()+1
    scale=h/(y1-y0)
    if ref is not None:   # a repaint of a reference piece: keep the reference's scale and anchor, extras hang outside it
        f=rgb.shape[0]/ref[4]; ry0,ry1,rx0,rx1=[round(v*f) for v in ref[:4]]; scale=h/(ry1-ry0)
        cx=cx+(x0+x1-rx0-rx1)/2*scale; top=top+round((y0-ry0)*scale*float(os.environ.get('PSQ','1')))
    sq=float(os.environ.get('PSQ','1')) if ref is not None else 1.0   # squash a plate shorter, same width
    ring=ndimage.binary_dilation(fig,iterations=max(1,round(OUTER/scale)))&~fig
    rgb[ring]=8; fig=fig|ring
    mask=plate_mask(rgb)*fig; rgb[~fig]=0
    c=lambda a:a[y0:y1,x0:x1]; w,hh=round((x1-x0)*scale),round((y1-y0)*scale*sq)
    body=Image.fromarray(np.dstack([c(rgb).astype(np.uint8),c((fig*255).astype(np.uint8))]),'RGBA').resize((w,hh),Image.LANCZOS)
    m=Image.fromarray(c((mask*255).astype(np.uint8)),'L').resize((w,hh),Image.LANCZOS)
    left=int(cx-w/2); tex=Image.new('RGBA',(WC,S)); tex.paste(body,(left,top),body)
    red=Image.new('L',(WC,S),0); red.paste(m,(left,top)); z=Image.new('L',(WC,S),0)
    pair=(tex,Image.merge('RGBA',(red,z,z,tex.split()[3])))
    if side=='right': pair=tuple(i.transpose(Image.FLIP_LEFT_RIGHT) for i in pair)
    return pair
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
# PLATE_BASE: the suit's own plain plate (default the Bulwark's); PLATES: per-weapon repaints of it,
# e.g. PLATES=hammer:arm_pneumatic_lc,flamer:arm_fuel_lc - placed at the base's scale and anchor
BASE=os.environ.get('PLATE_BASE','arm_bulwark')
_rf=cut_out(load(f'{SP}/arms/{BASE}.png')); _ry,_rx=np.nonzero(_rf); REF=(_ry.min(),_ry.max()+1,_rx.min(),_rx.max()+1,_rf.shape[0])
PLATES=dict(kv.split(':') for kv in os.environ.get('PLATES','').split(',') if kv)
PH=int(os.environ.get('PH','110'))
def plate(side,wn=None):
    f=PLATES.get(wn,BASE)
    if f=='arm_bulwark': return _outlined(place(SP+'/arms/arm_bulwark.png',PW_CX,int(os.environ.get('PT','58')),110,side))
    return _outlined(place(f'{SP}/arms/{f}.png',PW_CX,int(os.environ.get('PT','58')),PH,side,ref=REF),round_r=3)
pb=np.array(plate('left')[0].split()[3])>0; xs=np.nonzero(pb.any(0))[0]; PCX=(xs.min()+xs.max())/2
import os; OUT=int(os.environ.get('OUT','8'))
H={w:120 for w in ('minigun','rockets','chainsaw','laser','flamer','hammer','autocannon','grenade','arc','towershield','drill','combo')}   # one length: both arms end at the same height
def arm(name,side):
    w=clip_behind(place(f'{SP}/weap/{name}.png',PCX-OUT,58+int(os.environ.get('TOP','80')),H[name],side),ringw)
    return [w,plate(side,name),joint(side)]
import cv2
def joint(side,w=22,h=18):
    "a ribbed square swivel between the shoulder plate and the weapon"
    pa=np.array(plate('left')[0].split()[3])>100; ys,xs=np.nonzero(pa)
    cx=PCX-OUT; top=ys.max()-4
    if side=='right': cx=WC-cx
    K=4; img=Image.new('RGBA',(WC*K,S*K)); d=ImageDraw.Draw(img)
    x0,y0,x1,y1=(cx-w/2)*K,top*K,(cx+w/2)*K,(top+h)*K
    d.rounded_rectangle((x0-1.5*K,y0-1.5*K,x1+1.5*K,y1+1.5*K),radius=3*K,fill=(14,14,18,255))
    for i in range(int(y1-y0)):                       # vertical shading: lit top, darker bottom
        v=int(150-50*i/(y1-y0)); d.line((x0,y0+i,x1,y0+i),fill=(v,v+2,v+8,255))
    for k in (1,2,3):                                  # three horizontal ribs
        yy=y0+(y1-y0)*k/4; d.line((x0,yy,x1,yy),fill=(30,30,36,255),width=int(1.4*K))
    d.line((x0+2*K,y0+1.5*K,x1-2*K,y0+1.5*K),fill=(190,192,200,255),width=int(K))   # top highlight
    img=img.resize((WC,S),Image.LANCZOS); return img,Image.new('RGBA',(WC,S))
def chest_front(wl=None,wr=None):
    """the chest armour shows through every part of each shoulder plate that is not its lit front:
    the hook and the front block (with their own outline) stay in front, the rest of the plate is cut away"""
    ct,cm=ch; ca=np.array(ct.split()[3])>100
    T=np.array(ct); Mk=np.array(cm); band=np.zeros((S,WC),bool)
    for side in ('left','right'):
        pt=np.array(plate(side)[0]).astype(float); pa=pt[...,3]>100; L=pt[...,:3].mean(2)
        light=pa&(L>=int(os.environ.get('LIGHT','118')))
        light=ndimage.binary_opening(light,iterations=1)
        lab,n=ndimage.label(light); sz=ndimage.sum(light,lab,range(1,n+1))
        light=np.isin(lab,np.nonzero(np.array(sz)>40)[0]+1)
        front=ndimage.binary_dilation(ndimage.binary_fill_holes(light),iterations=2)   # lit faces + their outline
        cut=pa&~front
        wn=wl if side=='left' else wr
        if PLATES.get(wn):    # weapon hardware on a repainted plate always stays in front of the chest
            pv=np.array(plate(side,wn)[0]).astype(float); va=pv[...,3]>100
            hw=(va&~pa)|(va&pa&(np.abs(pv[...,:3]-pt[...,:3]).max(2)>30))
            cut&=~ndimage.binary_dilation(hw,iterations=2)
        band|=cut
    band&=ca
    if os.environ.get('NEST','1')=='0': band[:]=False   # a light plate sits fully in front of the chest
    out_t=np.zeros((S,WC,4),np.uint8); out_m=np.zeros((S,WC,4),np.uint8)
    out_t[band]=T[band]; out_m[band]=Mk[band]
    return Image.fromarray(out_t,'RGBA'),Image.fromarray(out_m,'RGBA')
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
ch=chas(SP+'/mod4/'+os.environ.get('CHAS','chassis_bulwark_plated2.png')); cb=np.nonzero((np.array(ch[0].split()[3])>0).any(0))[0]; print('chassis x',cb.min(),cb.max(),'plate cx',PCX); HL=helm(SP+'/mod2/'+os.environ.get('HELM','helmet_bulwark_fwd2.png'))
def _hbox(pair):
    a=np.array(pair[0].split()[3])>100; ys,xs=np.nonzero(a); return xs.min(),ys.min(),xs.max(),ys.max()
def match_height(pair,ref):
    "temple lamps make the helmet wider, so the width fit shrinks it: rescale to the reference helmet's height"
    x0,y0,x1,y1=_hbox(pair); r0,s0,r1,s1=_hbox(ref); k=(s1-s0)/(y1-y0)
    cx,by=(x0+x1)/2,y1; out=[]
    for im in pair:
        big=im.resize((int(im.width*k),int(im.height*k)),Image.LANCZOS); c=Image.new('RGBA',im.size)
        c.alpha_composite(big,(int(cx-cx*k),int(s1-by*k))) if True else None; out.append(c)
    return tuple(out)
def scale_layer(pair,k):
    "scale a layer about its bottom centre (the collar it sits in stays put)"
    x0,y0,x1,y1=_hbox(pair); cx,by=(x0+x1)/2,y1; out=[]
    for im in pair:
        big=im.resize((int(im.width*k),int(im.height*k)),Image.LANCZOS); c=Image.new('RGBA',im.size)
        c.alpha_composite(big,(int(cx-cx*k),int(by-by*k))); out.append(c)
    return tuple(out)
HL=scale_layer(HL,float(os.environ.get('HSCALE','1.3')))
if os.environ.get('FULLHEAD'): HL=match_height(HL,helm(SP+'/mod2/helmet_bulwark_fwd1.png'))
if os.environ.get('SOFT'): ch=soften(ch); HL=soften(HL,keep=4)
loadouts=[(os.environ['WL']+' / '+os.environ['WR'],os.environ['WL'],os.environ['WR'])] if os.environ.get('WL') else [('minigun / rockets','minigun','rockets'),('laser / chainsaw','laser','chainsaw'),('flamer / minigun','flamer','minigun'),('hammer / rockets','hammer','rockets'),('laser / laser','laser','laser'),('chainsaw / flamer','chainsaw','flamer')]
img=Image.new('RGBA',(3*345,2*330),floor); d=ImageDraw.Draw(img)
for i,(lab,a,b) in enumerate(loadouts):
    out=Image.new('RGBA',(WC,S))
    for t,m in [ch,*arm(a,'left'),*arm(b,'right'),chest_front(a,b),HL]: out.alpha_composite(tint(t,m,COL['bulwark']))
    out.save(f'{SP}/suit_{i}.png')
    if os.environ.get('EXPORT') and i==0:
        import pickle
        band=np.array(chest_front(os.environ.get('WL'),os.environ.get('WR'))[0].split()[3])>0
        def merge(parts,cut=None):
            t=Image.new('RGBA',(WC,S)); m=Image.new('RGBA',(WC,S))
            for tt,mm in parts: t.alpha_composite(tt); m.alpha_composite(mm)
            if cut is not None:
                ta=np.array(t); ma=np.array(m); ta[cut,3]=0; ma[cut,3]=0; t=Image.fromarray(ta); m=Image.fromarray(ma)
            return t,m
        KS=os.environ.get('KITSRC',SP+'/kit_src'); os.makedirs(KS,exist_ok=True)
        WEAPONS=[w for w in ('minigun','rockets','chainsaw','laser','flamer','hammer','autocannon','grenade','arc','towershield','drill','combo') if w in H]
        layers=[('body',ch),('helmet',HL),('plateLfull',merge(arm(os.environ.get('WL','minigun'),'left')[1:])),('plateRfull',merge(arm(os.environ.get('WR','minigun'),'right')[1:]))]
        layers+=[('plateLbase',plate('left')),('plateRbase',plate('right'))]
        for wn in WEAPONS: layers+= [(f'armL_{wn}',merge(arm(wn,'left'),band)),(f'armR_{wn}',merge(arm(wn,'right'),band)),(f'armLfull_{wn}',merge(arm(wn,'left'))),(f'armRfull_{wn}',merge(arm(wn,'right')))]
        for name,pair in layers:
            pair[0].save(f'{KS}/south_{name}.png'); pair[1].save(f'{KS}/south_{name}_m.png')
    x,y=(i%3)*345,(i//3)*330
    d.text((x+6,y+4),lab,fill=(255,255,255,255))
    img.alpha_composite(out,(x+8,y+20)); img.alpha_composite(out.resize((82,64),Image.LANCZOS),(x+130,y+262))
img.save(SP+'/bulwark_hang.png')
