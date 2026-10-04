import glob,os,sys
import numpy as np
from PIL import Image
from scipy import ndimage
V=sys.argv[1]+'/vfep/Textures/Things/Pawn/Warcasketlike/'
rows=[]
for d in sorted(glob.glob(V+'Warcasket*')):
    n=os.path.basename(d)
    for part in ('','Shoulders','Helmet'):
        p=f'{d}/{n}{part}_south.png'
        if not os.path.exists(p): continue
        im=np.array(Image.open(p).convert('RGBA')).astype(float); H,W=im.shape[:2]
        A=im[...,3]>128; L=im[...,:3].mean(2)
        if A.sum()<50: continue
        ys,xs=np.nonzero(A)
        # outline: dark pixels touching transparency, width = distance into the shape until L>80
        dist=ndimage.distance_transform_edt(A)
        edge_dark=A&(L<60)
        ow=np.percentile(dist[edge_dark&(dist<20)],95) if edge_dark.any() else 0
        inner=A&(dist>ow+2)
        Li=L[inner]
        dark_lines=inner&(L<70)
        rows.append(dict(name=n.replace('Warcasket','') or 'Base',part=part or 'Body',size=f'{W}x{H}',
            fillW=round((xs.max()-xs.min()+1)/W,2),fillH=round((ys.max()-ys.min()+1)/H,2),
            outline=round(ow,1),p10=int(np.percentile(Li,10)),p50=int(np.percentile(Li,50)),p90=int(np.percentile(Li,90)),
            linefrac=round(dark_lines.sum()/inner.sum(),3),
            tones=len(np.unique((Li//24).astype(int)))))
import json
for r in rows: print(json.dumps(r))
