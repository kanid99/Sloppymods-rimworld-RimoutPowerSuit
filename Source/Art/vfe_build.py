import sys,os
SP=sys.argv[1]; sys.path.insert(0,SP)
exec(open(SP+'/vfep_cmp.py').read().split("ours_im=suit")[0])
from vfe_style import vfe_style, tint_light
def lay(pair):
    c=Image.new('RGBA',(WC,HT)); c.alpha_composite(pair[0]); return c
CHF=vfe_style(lay(ch),outer=4,min_detail=220)
PL=Image.new('RGBA',(WC,HT)); PL.alpha_composite(plate('left')[0]); PL.alpha_composite(plate('right')[0]); PLF=vfe_style(PL,outer=4)
def fit_helmet():
    old=np.array(HL[0])[...,3]>60; ys,xs=np.nonzero(old)
    w=xs.max()-xs.min(); bottom=ys.max(); cx=(xs.min()+xs.max())/2
    hv=Image.open(SP+'/mod2/helmet_bulwark_vfe_rgba.png'); hv=hv.crop(hv.getbbox())
    hv=hv.resize((int(w*1.04),int(hv.height*w*1.04/hv.width)),Image.LANCZOS)
    c=Image.new('RGBA',(WC,HT)); c.alpha_composite(hv,(int(cx-hv.width/2),int(bottom-hv.height+4))); return c
HV=fit_helmet()
def fit_to(old_rgba,path,flip=False):
    o=np.array(old_rgba)[...,3]>60; ys,xs=np.nonzero(o); x0,x1,y0,y1=xs.min(),xs.max(),ys.min(),ys.max()
    im=Image.open(path); im=im.crop(im.getbbox())
    if flip: im=im.transpose(Image.FLIP_LEFT_RIGHT)
    im=im.resize((x1-x0+1,y1-y0+1),Image.LANCZOS)
    c=Image.new('RGBA',(WC,HT)); c.alpha_composite(im,(int(x0),int(y0))); return c
CHF=fit_to(lay(ch),SP+'/mod2/chassis_bulwark_vfe.png')
def plate_vfe(side,w=86):
    o=np.array(plate('left')[0])[...,3]>60; ys,xs=np.nonzero(o)
    im=Image.open(SP+'/mod2/plate_bulwark_vfe.png'); im=im.crop(im.getbbox()); im=im.resize((w,int(im.height*w/im.width)),Image.LANCZOS)
    c=Image.new('RGBA',(WC,HT)); c.alpha_composite(im,(int(xs.max()+16-w),int(ys.min()-4)))
    return c if side=='left' else c.transpose(Image.FLIP_LEFT_RIGHT)
PLF=Image.new('RGBA',(WC,HT)); PLF.alpha_composite(plate_vfe('left')); PLF.alpha_composite(plate_vfe('right'))
def suit_vfe(a,b,top=136):
    c=Image.new('RGBA',(WC,HT)); c.alpha_composite(CHF)
    for name,side in ((a,'left'),(b,'right')):
        w=wpn(name+'_vfe',WH[name],side); cx=PCX-OUT if side=='left' else WC-(PCX-OUT)
        c.alpha_composite(w,(int(cx-w.width/2),top))
    c.alpha_composite(PLF); hv=Image.new('RGBA',(WC,HT)); hv.alpha_composite(HV); c.alpha_composite(hv)
    return c
if __name__=='__main__':
    loadouts=[('minigun / rockets','v_minigun','v_rockets'),('autocannon / hammer','v_autocannon','v_hammer'),('laser / flamer','v_laser','v_flamer')]
    T=330; STEELC=(0.62,0.66,0.72)
    row=[('VFE: Siegebreaker',warcasket('Siegebreaker')),('VFE: Marine',warcasket('Marine'))]+[(lab,suit_vfe(a,b)) for lab,a,b in loadouts]
    sheet=Image.new('RGBA',(len(row)*T,3*T+20),floor); d=ImageDraw.Draw(sheet)
    for i,(lab,im) in enumerate(row):
        big=im.crop(im.getbbox()); big.thumbnail((T-20,T-30),Image.LANCZOS)
        d.text((i*T+6,4),lab,fill=(255,255,255,255)); sheet.alpha_composite(big,(i*T+10,22))
        if i>=2:
            p=tint_light(im,STEELC); pb=p.crop(p.getbbox()); pb.thumbnail((T-20,T-30),Image.LANCZOS); sheet.alpha_composite(pb,(i*T+10,T+10))
            o=tint_light(im,(0.62,0.68,0.48)); ob_=o.crop(o.getbbox()); 
        sm=big.resize((max(1,int(big.width*64/big.height)),64),Image.LANCZOS); sheet.alpha_composite(sm,(i*T+T-sm.width-10,T-50))
        bb=im.getbbox(); cx=(bb[0]+bb[2])//2; cy=bb[1]+int((bb[3]-bb[1])*0.35)
        sheet.alpha_composite(im.crop((cx-60,cy-60,cx+60,cy+60)).resize((T-20,T-20),Image.NEAREST),(i*T+10,2*T+10))
    sheet.save(SP+'/vfe_build.png')
