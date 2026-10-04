"""Gentle pass: keep the soft washed-out fills and inner lines; only darken the outer silhouette."""
import sys; SP=sys.argv[1]
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
def soft(rgb, out_col=80, width=3, inner=0.0):
    a=rgb.astype(float); L=a.mean(2)
    fg=ndimage.binary_fill_holes(ndimage.binary_closing(L<244,iterations=3)); fg=ndimage.binary_opening(fg,iterations=2)
    lab,n=ndimage.label(fg); sizes=ndimage.sum(fg,lab,range(1,n+1)); fg=np.isin(lab,np.nonzero(sizes>800)[0]+1)
    out=a.copy()
    if inner>0:                                          # optional: nudge the existing grey lines a little darker
        loc=ndimage.uniform_filter(L,9); line=(L<loc-12)&fg
        out[line]=out[line]*(1-inner)
    edge=fg&~ndimage.binary_erosion(fg,iterations=width)   # the outer edge, drawn inside the silhouette
    out[edge]=out_col
    out[~fg]=255
    return np.clip(out,0,255).astype(np.uint8), fg
src=np.array(Image.open(SP+'/gemini/noncombat1.jpg').convert('RGB'))[40:480]
opts=[('as given',None),('A: outline grey-80, 3px',dict(out_col=80,width=3)),('B: outline grey-55, 4px',dict(out_col=55,width=4)),('C: B + inner lines 20% darker',dict(out_col=55,width=4,inner=0.2))]
floor=(92,84,70); W=src.shape[1]; H=src.shape[0]
sheet=Image.new('RGB',(W+260,len(opts)*(H//2+30)+10),floor); d=ImageDraw.Draw(sheet)
for i,(lab,kw) in enumerate(opts):
    if kw is None:
        a=src.astype(float); L=a.mean(2); fg=ndimage.binary_fill_holes(ndimage.binary_closing(L<244,iterations=3)); img=src
    else: img,fg=soft(src,**kw)
    rgba=Image.fromarray(np.dstack([img,(fg*255).astype(np.uint8)]),'RGBA')
    y=i*(H//2+30)+10; d.text((6,y),lab,fill=(255,255,255))
    half=rgba.resize((W//2,H//2),Image.LANCZOS); sheet.paste(half,(0,y+14),half)
    for k,x0 in enumerate((20,360,680)):                  # in-game size, on the ground colour
        t=rgba.crop((x0,0,x0+330,H)).resize((54,72),Image.LANCZOS); sheet.paste(t,(W//2+20+k*70,y+40),t)
    if kw: Image.fromarray(img).save(SP+f'/gemini/noncombat1_soft_{lab[0]}.png')
sheet=sheet.crop((0,0,W//2+240,sheet.height)); sheet.save(SP+'/noncombat_soft.png')
