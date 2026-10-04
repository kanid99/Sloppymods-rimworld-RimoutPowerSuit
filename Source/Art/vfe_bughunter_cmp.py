import sys,os
SP=sys.argv[1]; sys.argv=[sys.argv[0],SP]
src=open(SP+'/vfe_build_soft.py').read().split("def target_suit")[0]
exec(src)
def place_helmet(path):
    old=np.array(HL[0])[...,3]>60; ys,xs=np.nonzero(old)
    w=xs.max()-xs.min(); bottom=ys.max(); cx=(xs.min()+xs.max())/2
    hv=Image.open(path); hv=hv.crop(hv.getbbox()); hv=hv.resize((int(w*1.04),int(hv.height*w*1.04/hv.width)),Image.LANCZOS)
    c=Image.new('RGBA',(WC,HT)); c.alpha_composite(hv,(int(cx-hv.width/2),int(bottom-hv.height+4))); return c
HB=place_helmet(SP+'/mod2/helmet_bughunter_soft_rgba.png')
def suit_bh(a,b,top=136):
    c=Image.new('RGBA',(WC,HT)); c.alpha_composite(CHF)
    for name,side in ((a,'left'),(b,'right')):
        w=wpn(name+'_soft',WH[name],side); cx=PCX-OUT if side=='left' else WC-(PCX-OUT)
        c.alpha_composite(w,(int(cx-w.width/2),top))
    c.alpha_composite(PLF); c.alpha_composite(HB); return c
gem=Image.open(SP+'/gemini/sheet_bughunter_helmet.png')
mine=Image.open(SP+'/mod2/helmet_bughunter_soft_rgba.png'); mine=mine.crop(mine.getbbox())
s1=suit_bh('v_flamer','v_hammer'); s2=tint_light(s1,(0.70,0.62,0.46))
T=330; row=[('Gemini idea',gem),('our redraw',mine),('on the suit (flamer / hammer)',s1),('painted desert tan',s2)]
sheet=Image.new('RGBA',(len(row)*T,T+20),floor); d=ImageDraw.Draw(sheet)
for i,(lab,im) in enumerate(row):
    b=im.crop(im.getbbox()); b.thumbnail((T-20,T-40),Image.LANCZOS)
    d.text((i*T+6,4),lab,fill=(255,255,255,255)); sheet.alpha_composite(b,(i*T+10,22))
    if i>=2:
        sm=b.resize((max(1,int(b.width*64/b.height)),64),Image.LANCZOS); sheet.alpha_composite(sm,(i*T+T-sm.width-8,T-56))
sheet.save(SP+'/bh_helmet_cmp.png')
