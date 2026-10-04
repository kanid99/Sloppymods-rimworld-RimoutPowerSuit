"""Put the VFE punch back into washed-out art: dark inner lines, heavy black silhouette, stronger tones."""
import sys; SP=sys.argv[1]
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
def restyle(rgb, outer=7):
    a=rgb.astype(float); L=a.mean(2)
    fg=ndimage.binary_fill_holes(ndimage.binary_closing(L<244,iterations=3))
    fg=ndimage.binary_opening(fg,iterations=2)
    lab,n=ndimage.label(fg); sizes=ndimage.sum(fg,lab,range(1,n+1)); fg=np.isin(lab,np.nonzero(sizes>800)[0]+1)
    # line work: pixels clearly darker than their neighbourhood
    loc=ndimage.uniform_filter(L,9); line=(L<loc-14)&(L<200)&fg
    out=a.copy()
    # stronger tones: stretch the fill values (light stays light, mid greys become real side faces)
    lo,hi=np.percentile(L[fg&~line],[3,97]); t=np.clip((L-lo)/max(1,hi-lo),0,1)
    tone=60+(245-60)*t**1.25
    out[fg]=(a[fg]/np.maximum(L[fg],1)[:,None])*tone[fg][:,None]
    out[line]=np.minimum(out[line],0)+38
    ring=ndimage.binary_dilation(fg,iterations=outer)&~fg
    edge=fg&~ndimage.binary_erosion(fg,iterations=2)
    out[ring|edge]=14; out[~(fg|ring)]=255
    return np.clip(out,0,255).astype(np.uint8)
src=np.array(Image.open(SP+'/gemini/noncombat1.jpg').convert('RGB'))
top=src[40:480]
fixed=restyle(top)
before=Image.fromarray(top); after=Image.fromarray(fixed)
W,H=before.size; sheet=Image.new('RGB',(W,H*2+60),(92,84,70)); d=ImageDraw.Draw(sheet)
sheet.paste(before,(0,20)); sheet.paste(after,(0,H+50)); d.text((6,4),'Gemini as given',fill=(255,255,255)); d.text((6,H+34),'restyled: dark lines, heavy outline, stronger tones',fill=(255,255,255))
# game-size thumbnails of each suit
for i,x0 in enumerate((20,360,680)):
    for j,img in enumerate((before,after)):
        t=img.crop((x0,0,x0+330,H)).resize((60,80),Image.LANCZOS); sheet.paste(t,(W-200+j*70,40+i*90 if False else 20+j*(H+30)+i*0))
after.save(SP+'/gemini/noncombat1_restyled.png'); sheet.save(SP+'/noncombat_restyle.png')
