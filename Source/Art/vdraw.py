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
