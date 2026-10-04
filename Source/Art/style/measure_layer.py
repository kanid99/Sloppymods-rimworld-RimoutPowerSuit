import sys; import numpy as np; from PIL import Image
from scipy import ndimage
def measure(p):
    im=np.array(Image.open(p).convert('RGBA')).astype(float); A=im[...,3]>128; L=im[...,:3].mean(2)
    ys,xs=np.nonzero(A); out=[]
    for y in range(0,256,3):
        r=np.nonzero(A[y])[0]
        if len(r)<20: continue
        for x0,st in ((r.min(),1),(r.max(),-1)):
            k=0;x=x0
            while 0<=x<256 and A[y,x] and L[y,x]<60: k+=1;x+=st
            if k: out.append(k)
    inner=A&(ndimage.distance_transform_edt(A)>6)
    return dict(box=(int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())),w=round((xs.max()-xs.min()+1)/256,2),h=round((ys.max()-ys.min()+1)/256,2),
                outline=float(np.median(out)) if out else 0,median_tone=int(np.median(L[inner])),sat=int((im[...,:3].max(2)-im[...,:3].min(2))[A].max()))
if __name__=='__main__':
    for p in sys.argv[1:]: print(p.split('/')[-1],measure(p))
