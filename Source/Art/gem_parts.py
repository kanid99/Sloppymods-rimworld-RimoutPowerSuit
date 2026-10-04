import sys; SP=sys.argv[1]
import numpy as np
from PIL import Image
from scipy import ndimage
src=np.array(Image.open(SP+'/gemini/variations1.jpg').convert('RGB')).astype(int)
def part(box,name,seed=None):
    x0,y0,x1,y1=box; a=src[y0:y1,x0:x1]
    fg=ndimage.binary_fill_holes(ndimage.binary_closing(a.min(2)<228,iterations=2))
    lab,n=ndimage.label(fg); sizes=ndimage.sum(fg,lab,range(1,n+1)); fg=lab==(np.argmax(sizes)+1)
    rgb=a.copy(); rgb[~fg]=255
    im=Image.fromarray(rgb.astype(np.uint8)); im=im.crop(Image.fromarray((fg*255).astype(np.uint8)).getbbox())
    n=max(im.size)+30; sq=Image.new('RGB',(n,n),'white'); sq.paste(im,((n-im.width)//2,(n-im.height)//2))
    sq=sq.resize((n*4,n*4),Image.LANCZOS); sq.save(f'{SP}/weap/{name}_vfe.png')
part((920,258,1016,410),'gem_rockets')
part((6,250,114,458),'gem_claw')
part((686,248,770,448),'gem_cannon')
