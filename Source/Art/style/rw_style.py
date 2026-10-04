"""Minimal renderer for the VFE warcasket look: flat greyscale planes, one vertical gradient,
a black stroke around every plate (overlaps make the inner lines). Draws at 4x, outputs 256."""
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
K=4; N=256*K
class Layer:
    def __init__(s): s.v=np.zeros((N,N)); s.a=np.zeros((N,N),bool)
    def _mask(s,draw):
        m=Image.new('L',(N,N),0); draw(ImageDraw.Draw(m)); return np.array(m)>127
    def poly(s,pts): return s._mask(lambda d:d.polygon([(x*K,y*K) for x,y in pts],fill=255))
    def ell(s,x0,y0,x1,y1): return s._mask(lambda d:d.ellipse((x0*K,y0*K,x1*K,y1*K),fill=255))
    def rrect(s,x0,y0,x1,y1,r): return s._mask(lambda d:d.rounded_rectangle((x0*K,y0*K,x1*K,y1*K),radius=r*K,fill=255))
    def plate(s,m,tone,bottom=None,stroke=4,mirror=False):
        ms=[m,m[:,::-1]] if mirror else [m]
        for mm in ms:
            if stroke:
                st=ndimage.binary_dilation(mm,iterations=int(stroke*K))
                s.v[st]=12; s.a|=st
            if bottom is None: s.v[mm]=tone
            else:
                ys=np.nonzero(mm.any(1))[0]; t=np.clip((np.arange(N)-ys.min())/max(1,ys.max()-ys.min()),0,1)
                g=(tone+(bottom-tone)*t)[:,None]*np.ones((1,N)); s.v[mm]=g[mm]
            s.a|=mm
    def mark(s,m,tone=85,mirror=False):
        "a small dark mark (vent, slot) with a thin outline"
        s.plate(m,tone,stroke=2,mirror=mirror)
    def image(s):
        v=np.clip(s.v,0,255).astype(np.uint8)
        im=Image.fromarray(np.dstack([v,v,v,(s.a*255).astype(np.uint8)]),'RGBA')
        return im.resize((256,256),Image.LANCZOS)
