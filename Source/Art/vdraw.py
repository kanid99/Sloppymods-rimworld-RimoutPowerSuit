"""Small 2D painting kit: shapes as masks, automatic bevel shading from a light direction, panel lines, glow, outlines."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage
N=1024
LIGHT=np.array([-0.55,-0.75]); LIGHT=LIGHT/np.linalg.norm(LIGHT)   # from top-left
INK=np.array([14,14,18.])
class Canvas:
    def __init__(s,n=N):
        s.n=n; s.rgb=np.ones((n,n,3))*255; s.a=np.zeros((n,n),bool); s.lines=np.zeros((n,n),bool)
    # ---- shape masks
    def poly(s,pts,mirror=False):
        m=Image.new('L',(s.n,s.n),0); d=ImageDraw.Draw(m); d.polygon([tuple(p) for p in pts],fill=255)
        if mirror: d.polygon([(s.n-1-x,y) for x,y in pts],fill=255)
        return np.array(m)>127
    def ell(s,box):
        m=Image.new('L',(s.n,s.n),0); ImageDraw.Draw(m).ellipse(box,fill=255); return np.array(m)>127
    def rrect(s,box,r):
        m=Image.new('L',(s.n,s.n),0); ImageDraw.Draw(m).rounded_rectangle(box,radius=r,fill=255); return np.array(m)>127
    # ---- painting
    def fill(s,mask,col,bevel=18,strength=0.55,grad=0.18,edge=4,spec=True):
        col=np.array(col,float)
        d=ndimage.distance_transform_edt(mask)
        h=np.clip(d/bevel,0,1); h=np.sin(h*np.pi/2)
        gy,gx=np.gradient(ndimage.gaussian_filter(h,2))
        lit=-(gx*LIGHT[0]+gy*LIGHT[1]); lit=lit/ (np.abs(lit).max()+1e-6)
        ys=np.linspace(0,1,s.n)[:,None]*np.ones((1,s.n))
        # vertical gradient across the shape's own extent
        yy,xx=np.nonzero(mask)
        if len(yy):
            t=np.clip((ys-yy.min()/s.n)/max(1e-3,(yy.max()-yy.min())/s.n),0,1)
        else: t=ys
        f=1+strength*lit+grad*(0.5-t)
        c=col[None,None,:]*f[...,None]
        if spec:
            hl=(lit>0.55)&(d<bevel*0.7)
            c[hl]=c[hl]*0.6+255*0.4
        c=np.clip(c,0,255)
        s.rgb[mask]=c[mask]
        # thin inner edge line
        ring=mask&~ndimage.binary_erosion(mask,iterations=edge)
        s.rgb[ring]=s.rgb[ring]*0.25+INK*0.75
        s.a|=mask
    def groove(s,mask,w=5):
        "a dark panel line along the mask's centre region (pass a thin mask)"
        s.rgb[mask]=s.rgb[mask]*0.25+INK*0.75
    def line(s,pts,w=8,col=INK):
        m=Image.new('L',(s.n,s.n),0); ImageDraw.Draw(m).line([tuple(p) for p in pts],fill=255,width=w,joint='curve')
        mk=np.array(m)>127; s.rgb[mk]=np.array(col,float)
    def glow(s,mask,col,radius=22,amount=0.9):
        g=ndimage.gaussian_filter(mask.astype(float),radius); g=g/g.max()*amount
        col=np.array(col,float); s.rgb=s.rgb*(1-g[...,None])+col*g[...,None]
    def bolt(s,cx,cy,r,col=(150,152,160)):
        s.fill(s.ell((cx-r,cy-r,cx+r,cy+r)),col,bevel=r*0.7,strength=0.8,edge=3)
    def outline(s,w=16):
        ring=ndimage.binary_dilation(s.a,iterations=w)&~s.a
        s.rgb[ring]=INK; s.a|=ring
    def save(s,path,size=None):
        im=Image.fromarray(s.rgb.astype(np.uint8))
        bg=Image.new('RGB',im.size,'white'); bg.paste(im,mask=Image.fromarray((s.a*255).astype(np.uint8)))
        bg.save(path)

def fill_cyl(c,mask,col,edge=4,hi=0.32):
    "vertical cylinder shading: light stripe at `hi` across the width, darker towards both edges"
    col=np.array(col,float); xs=np.nonzero(mask.any(0))[0]
    if not len(xs): return
    x0,x1=xs.min(),xs.max(); t=(np.arange(c.n)-x0)/max(1,x1-x0)
    f=0.62+0.55*np.exp(-((t-hi)/0.16)**2)+0.25*np.clip(1-np.abs(t-0.5)*2,0,1)
    f=np.clip(f,0,1.5)[None,:]*np.ones((c.n,1))
    cc=np.clip(col[None,None,:]*f[...,None],0,255)
    c.rgb[mask]=cc[mask]
    ring=mask&~ndimage.binary_erosion(mask,iterations=edge)
    c.rgb[ring]=c.rgb[ring]*0.25+INK*0.75
    c.a|=mask

# ---- VFE / vanilla style: flat tone + soft top-down gradient, thin dark inner line, no bevel/specular
FLAT_LINE=(40,40,44)
def fill_flat(c,mask,col,line=10,grad=0.14,line_col=FLAT_LINE):
    col=np.array(col,float); yy,xx=np.nonzero(mask)
    if not len(yy): return
    t=np.clip((np.arange(c.n)-yy.min())/max(1,yy.max()-yy.min()),0,1)[:,None]*np.ones((1,c.n))
    f=1+grad*(0.5-t)
    cc=np.clip(col[None,None,:]*f[...,None],0,255); c.rgb[mask]=cc[mask]
    if line:
        ring=mask&~ndimage.binary_erosion(mask,iterations=line); c.rgb[ring]=line_col
    c.a|=mask

# ---- VFE shading v2: soft form shading + cast shadows, still clean and light
SHADE=dict(form=0.34, light=0.22, shadow=0.32, shadow_off=(10,14), shadow_blur=8)
def fill_vfe(c,mask,col,line=10,form='round',line_col=FLAT_LINE,shadow=True,k=None):
    k=k or SHADE; col=np.array(col,float)
    yy,xx=np.nonzero(mask)
    if not len(yy): return
    # cast shadow of this piece onto what is already drawn underneath
    if shadow and c.a.any():
        dx,dy=k['shadow_off']; sh=np.zeros_like(mask); sh[dy:,dx:]=mask[:-dy,:-dx]
        sh=ndimage.gaussian_filter(sh.astype(float),k['shadow_blur'])*(c.a&~mask)
        c.rgb*=(1-k['shadow']*sh)[...,None]
    y0,y1,x0,x1=yy.min(),yy.max(),xx.min(),xx.max()
    Y,X=np.mgrid[0:c.n,0:c.n]
    u=(X-x0)/max(1,x1-x0); v=(Y-y0)/max(1,y1-y0)
    if form=='round':
        d=ndimage.distance_transform_edt(mask); dn=d/max(1,d.max())
        f=1-k['form']*(1-np.sqrt(np.clip(dn,0,1)))          # darker toward the rim, soft
    elif form=='cyl':
        f=1-k['form']*np.clip(np.abs(u-0.36)*1.8,0,1)**1.5   # light band left of centre
    else: f=np.ones_like(u,dtype=float)
    f=f+k['light']*(0.5-0.5*u-0.5*v)                          # light from the upper left
    cc=np.clip(col[None,None,:]*f[...,None],0,255); c.rgb[mask]=cc[mask]
    if line:
        ring=mask&~ndimage.binary_erosion(mask,iterations=line); c.rgb[ring]=line_col
    c.a|=mask

# ---- chamfer faces: a crisp edge band, lit toward the upper left, clearly darker where it faces away
def chamfer(c,mask,bevel,lit=1.10,side=0.60,mid=0.84,seam=3):
    if bevel<=0: return
    d=ndimage.distance_transform_edt(mask); band=mask&(d<bevel)
    gy,gx=np.gradient(ndimage.gaussian_filter(d,bevel*0.35))
    n=np.sqrt(gx*gx+gy*gy)+1e-6; dot=(0.6*gx+0.8*gy)/n        # outward normal . direction to the light
    f=np.where(dot>0.25,lit,np.where(dot<-0.15,side,mid))
    c.rgb[band]=np.clip(c.rgb[band]*f[band][:,None],0,255)
    inner=mask&(d>=bevel)&(d<bevel+seam); c.rgb[inner]=c.rgb[inner]*0.72   # soft seam between face and top
_fill_vfe_plain=fill_vfe
def fill_vfe(c,mask,col,line=10,form='round',line_col=FLAT_LINE,shadow=True,k=None,bevel=0):
    _fill_vfe_plain(c,mask,col,0,form,line_col,shadow,k)
    chamfer(c,mask,bevel)
    if line:
        ring=mask&~ndimage.binary_erosion(mask,iterations=line); c.rgb[ring]=line_col
