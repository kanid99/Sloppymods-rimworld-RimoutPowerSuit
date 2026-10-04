"""Re-render art in the VFE/vanilla RimWorld style: light flat tones, clean thin inner lines,
heavy black silhouette outline, small detail dropped. Works at 4x, returns at 1x."""
import numpy as np, cv2
from PIL import Image
from scipy import ndimage
def vfe_style(im, levels=(70,150,205,238), shares=(0.05,0.17,0.33), outer=5, inner=2, min_detail=110, smooth=12, K=4, accents=True):
    im=im.convert('RGBA'); W,H=im.size
    a=np.array(im.resize((W*K,H*K),Image.LANCZOS)); al=a[...,3]>110
    rgb=np.ascontiguousarray(a[...,:3])
    sm=cv2.pyrMeanShiftFiltering(rgb,sp=smooth*K//2,sr=34); sm=cv2.pyrMeanShiftFiltering(sm,sp=smooth*K//2,sr=34)               # flatten texture, keep shapes
    hsv=cv2.cvtColor(sm,cv2.COLOR_RGB2HSV); L=hsv[...,2].astype(float); S=hsv[...,1].astype(float)
    acc=(S>70)&(L>70)&al; acc=ndimage.binary_opening(acc,iterations=K) if accents else np.zeros_like(al)
    # quantise brightness into a few flat tones (the darkest band becomes recess, not line)
    vals=L[al&~acc]; c=np.cumsum(shares)
    cuts=[np.percentile(vals,100*x) for x in c]          # darkest 5% = recess, next 17% = shadow, next 33% = mid, rest = light
    q=np.digitize(L,cuts)
    # drop small detail: a region smaller than min_detail (at 1x) takes its neighbours' tone
    for _ in range(2):
        out=q.copy()
        for t in range(4):
            lab,n=ndimage.label((q==t)&al)
            if n==0: continue
            sizes=ndimage.sum(np.ones_like(q),lab,range(1,n+1))
            small=np.isin(lab,np.nonzero(sizes<min_detail*K*K)[0]+1)
            if small.any():
                md=cv2.medianBlur(q.astype(np.uint8),2*(4*K)+1)
                out[small]=md[small]
        q=out
    tone=np.array(levels,float)[q]
    # a soft top-down gradient like VFE's plates
    yy=np.linspace(1.06,0.94,H*K)[:,None]; tone=tone*yy
    res=np.dstack([tone,tone,tone])
    if accents: res[acc]=sm[acc]*1.0
    # inner lines on tone boundaries
    qa=np.where(al,q+1,0).astype(np.uint8)
    edge=cv2.morphologyEx(qa,cv2.MORPH_GRADIENT,np.ones((3,3),np.uint8))>0
    edge=cv2.dilate(edge.astype(np.uint8),np.ones((inner*K//2+1,inner*K//2+1),np.uint8))>0
    res[edge&al]=res[edge&al]*0.0+48
    # heavy black silhouette
    ring=cv2.dilate(al.astype(np.uint8),cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*outer*K+1,2*outer*K+1)))>0
    border=ring&~al
    edge_out=al&~cv2.erode(al.astype(np.uint8),np.ones((3,3),np.uint8)).astype(bool)
    res[border|edge_out]=14
    A=(ring*255).astype(np.uint8)
    out=Image.fromarray(np.dstack([np.clip(res,0,255).astype(np.uint8),A]),'RGBA')
    return out.resize((W,H),Image.LANCZOS)
def tint_light(im,col):
    "how the game paints a grey texture: multiply the non-accent greys by the colour"
    a=np.array(im).astype(float); rgb=a[...,:3]; sat=rgb.max(2)-rgb.min(2); m=(sat<25)&(a[...,3]>0)
    rgb[m]=rgb[m]*np.array(col)[None,:]; a[...,:3]=rgb; return Image.fromarray(np.clip(a,0,255).astype(np.uint8),'RGBA')
