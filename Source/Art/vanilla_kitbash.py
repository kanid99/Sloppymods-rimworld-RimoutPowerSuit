import sys; SP=sys.argv[1]
import numpy as np
from PIL import Image
from scipy import ndimage
K=8
def big(path):
    im=Image.open(path).convert('RGBA'); bb=im.getbbox(); im=im.crop(bb)
    # premultiplied upscale so transparent edges don't go dark/halo
    a=np.array(im).astype(float); al=a[...,3:]/255
    pm=Image.fromarray(np.dstack([(a[...,:3]*al).astype(np.uint8),a[...,3].astype(np.uint8)]),'RGBA')
    up=np.array(pm.resize((im.width*K,im.height*K),Image.LANCZOS)).astype(float)
    al=np.clip(up[...,3:]/255,1e-3,1); rgb=np.clip(up[...,:3]/al,0,255)
    A=(ndimage.gaussian_filter(up[...,3],K*0.3)>127)*255
    return Image.fromarray(np.dstack([rgb,A]).astype(np.uint8),'RGBA'),bb
def sq(im,name):
    n=max(im.size)+120; s=Image.new('RGB',(n,n),'white'); s.paste(im,((n-im.width)//2,(n-im.height)//2),im); s.save(f'{SP}/weap/{name}.png')
full,_=big(SP+'/gameart/ac_full.png'); full=full.rotate(-90,expand=True); sq(full,'ac_vanilla')
# one-drum kitbash: barrel + body from the full image, one drum moved to the outer side
body,bb=big(SP+'/gameart/ac_main_Body.png'); barrel,bb2=big(SP+'/gameart/ac_barrel.png'); feed,bb3=big(SP+'/gameart/ac_ammo_feed.png'); border,bb4=big(SP+'/gameart/ac_gun_border.png')
# rebuild in original 192 coords x K, then rotate
W=192*K; canvas=Image.new('RGBA',(W,W))
def at(im,b,dx=0,dy=0): canvas.alpha_composite(im,(b[0]*K+dx,b[1]*K+dy))
fh=feed.height//2
drum=feed.crop((0,0,feed.width,int(feed.height*0.38)))           # top drum only
at(border,bb4); at(barrel,bb2); at(body,bb)
canvas.alpha_composite(drum,(bb3[0]*K+4*K, bb[1]*K-int(drum.height*0.45)))
one=canvas.crop(canvas.getbbox()).rotate(-90,expand=True); sq(one,'ac_vanilla_onedrum')
