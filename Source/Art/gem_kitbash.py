import sys,os
SP=sys.argv[1]; sys.argv=[sys.argv[0],SP]
exec(open(SP+'/vfe_build.py').read().split("if __name__")[0])
src=Image.open(SP+'/gemini/bulwark_try1.jpg').convert('RGB'); a=np.array(src).astype(int)
fg=ndimage.binary_fill_holes(ndimage.binary_closing(a.min(2)<225,iterations=2))
lab,n=ndimage.label(fg); sizes=ndimage.sum(fg,lab,range(1,n+1)); fg=lab==(np.argmax(sizes)+1)
# keep the body: chest, abdomen, hips and shoulder joints; drop the helmet top, the shoulder discs and the guns
keep=np.zeros_like(fg); keep[300:,262:762]=True
body=fg&keep
# a fresh outline along the cuts
edge=body&~ndimage.binary_erosion(body,iterations=6)
rgb=a.copy(); rgb[edge&~ndimage.binary_erosion(fg,iterations=6)]=rgb[edge&~ndimage.binary_erosion(fg,iterations=6)]
cut=edge&ndimage.binary_erosion(fg,iterations=6); rgb[cut]=20
im=Image.fromarray(np.dstack([rgb.astype(np.uint8),(body*255).astype(np.uint8)]),'RGBA'); im=im.crop(im.getbbox())
# fit to our chassis box
o=np.array(CHF)[...,3]>60; ys,xs=np.nonzero(o); H_=ys.max()-ys.min()
im=im.resize((int(im.width*H_*1.08/im.height),int(H_*1.08)),Image.LANCZOS)
GB=Image.new('RGBA',(WC,HT)); GB.alpha_composite(im,(int((xs.min()+xs.max())/2-im.width/2),int(ys.min()+4)))
def suit_gem(a_,b_,top=136):
    c=Image.new('RGBA',(WC,HT)); c.alpha_composite(GB)
    for name,side in ((a_,'left'),(b_,'right')):
        w=wpn(name+'_vfe',WH[name],side); cx=PCX-OUT if side=='left' else WC-(PCX-OUT)
        c.alpha_composite(w,(int(cx-w.width/2),top))
    c.alpha_composite(PLF); c.alpha_composite(HV); return c
WH.update({'gem_rockets':104,'gem_claw':140,'gem_cannon':150})
loadouts=[('minigun / gem rocket pod','v_minigun','gem_rockets'),('gem cannon / gem rocket pod','gem_cannon','gem_rockets'),('gem claw / flamer','gem_claw','v_flamer'),('autocannon / hammer','v_autocannon','v_hammer')]
T=360; cols=[(1,1,1),(0.62,0.66,0.72)]
sheet=Image.new('RGBA',(len(loadouts)*T,2*(T-30)+30),floor); d=ImageDraw.Draw(sheet)
for i,(lab_,a_,b_) in enumerate(loadouts):
    im_=suit_gem(a_,b_); d.text((i*T+6,4),lab_,fill=(255,255,255,255))
    for j,c in enumerate(cols):
        p=tint_light(im_,c); p=p.crop(p.getbbox()); p.thumbnail((T-90,T-50),Image.LANCZOS)
        y=22+j*(T-30); sheet.alpha_composite(p,(i*T+6,y))
        sm=p.resize((max(1,int(p.width*64/p.height)),64),Image.LANCZOS); sheet.alpha_composite(sm,(i*T+T-sm.width-8,y+T-110))
sheet.save(SP+'/gem_kitbash.png')
