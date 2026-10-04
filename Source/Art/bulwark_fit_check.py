import sys, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
SP=sys.argv[1]; G=SP+'/gameart/'; tags=sys.argv[2:]
def stubs(suit):
    W,H=suit.size
    src=np.array(Image.open(SP+'/views/legs_south.png').convert('RGB')).astype(int)
    fg=ndimage.binary_fill_holes(ndimage.binary_closing(src.min(2)<232,iterations=2)); ys,xs=np.nonzero(fg)
    legs=Image.fromarray(np.dstack([src,(fg*255)]).astype(np.uint8),'RGBA').crop((xs.min(),ys.min(),xs.max()+1,ys.max()+1))
    legs=legs.crop((0,int(legs.height*0.45),legs.width,legs.height))
    sa=np.array(suit); m=sa[...,3]>100; L=sa[...,:3][m].mean(1); ref=np.median(sa[...,:3][m][(L>90)&(L<160)],0)
    la=np.array(legs).astype(float); lm=la[...,3]>100; lref=np.median(la[...,:3][lm][(la[...,:3][lm].mean(1)>120)],0)
    la[...,:3]*=ref/lref; legs=Image.fromarray(la.clip(0,255).astype(np.uint8),'RGBA')
    sy,sx=np.nonzero(m); bot=sy.max(); hx=np.nonzero(m[bot-20:bot].any(0))[0]
    w=int((hx.max()-hx.min())*0.72); h=int(legs.height*w/legs.width*0.85)
    lg=legs.resize((w,h),Image.LANCZOS); c=Image.new('RGBA',(W,H+h+40)); cx=(hx.min()+hx.max())//2
    c.alpha_composite(lg,(cx-w//2,bot-int(h*0.25))); c.alpha_composite(suit); return c.crop(c.getbbox())
def L2(p): return Image.open(p).convert('RGBA').resize((256,256),Image.LANCZOS)
def tintc(im,col):
    a=np.array(im).astype(float); a[...,:3]*=np.array(col)/255; return Image.fromarray(a.clip(0,255).astype(np.uint8),'RGBA')
skin=(234,200,170)
pawn=Image.new('RGBA',(256,330)); pawn.alpha_composite(tintc(L2(G+'ex/Things/Pawn/Humanlike/Bodies/Naked_Male_south.png'),skin),(0,74)); pawn.alpha_composite(tintc(L2(G+'ex/Things/Pawn/Humanlike/Heads/Male/Male_Average_Normal_south.png'),skin),(0,16))
pawn=pawn.crop(pawn.getbbox()); pa=np.array(pawn); dark=(pa[...,:3].mean(2)<60)&(pa[...,3]>200); py,px=np.nonzero(dark[:int(pawn.height*0.45)])
mid=(px>pawn.width*0.3)&(px<pawn.width*0.7)&(py>pawn.height*0.08); pe=int(np.median(py[mid]))
K=1.45; GROUND=520; out=Image.new('RGB',(len(tags)*420,560),(92,84,70)); d=ImageDraw.Draw(out)
for i,t in enumerate(tags):
    c=stubs(Image.open(f'{SP}/suit_h{t}.png')); c.save(f'{SP}/suit_stubs_h{t}.png')
    a=np.array(c).astype(int); top=int(a.shape[0]*0.4); red=(a[:top,:,0]>150)&(a[:top,:,1]<80)&(a[:top,:,3]>200); ry,rx=np.nonzero(red); eye=int(np.median(ry))
    s=c.resize((int(c.width*K),int(c.height*K)),Image.LANCZOS); x=i*420+210-s.width//2; y=GROUND-s.height
    out.paste(s,(x,y),s); d.text((i*420+8,6),f'suit x1.45, helmet x{t}',fill=(255,255,255))
    g=np.array(pawn).copy(); g[...,3]=(g[...,3]*0.55).astype(np.uint8); g=Image.fromarray(g)
    out.paste(g,(i*420+210-g.width//2,y+int(eye*K)-pe),g)
    sm=s.resize((int(s.width*72/s.height*1.0),72),Image.LANCZOS); out.paste(sm,(i*420+330,40),sm)
out.save(SP+'/helmet_fit.png')
