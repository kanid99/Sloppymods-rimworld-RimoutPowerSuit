import sys
SP=sys.argv[1]
exec(open(SP+'/bulwark_loadouts.py').read().split("loadouts=[")[0])
def chas(src):
    lay=layer(src,T); c=collar(lay[0]); lay=shift(lay,0,CANON_CY-c[1])
    return widen(rescale(flatten_collar(lay),GS),WC)
HF=helm(SP+'/mod2/helmet_bulwark_face1.png')
opts=[('current chest',SP+'/mod4/chassis_bulwark.png'),('plated 1',SP+'/mod4/chassis_bulwark_plated1.png'),('plated 2',SP+'/mod4/chassis_bulwark_plated2.png')]
img=Image.new('RGBA',(3*345,2*300),floor); d=ImageDraw.Draw(img)
for i,(lab,p) in enumerate(opts):
    ch=chas(p)
    for row,parts in enumerate([[ch],[ch,arm_wide('minigun','left'),arm_wide('rockets','right'),HF]]):
        out=Image.new('RGBA',(WC,S))
        for t,m in parts: out.alpha_composite(tint(t,m,COL['bulwark']))
        x,y=i*345,row*300
        d.text((x+6,y+4),lab,fill=(255,255,255,255))
        img.alpha_composite(out,(x+8,y+20)); img.alpha_composite(out.resize((82,64),Image.LANCZOS),(x+130,y+232))
img.save(SP+'/bulwark_chest.png')
