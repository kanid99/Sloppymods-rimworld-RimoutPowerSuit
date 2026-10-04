import sys; SP=sys.argv[1]
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
src=np.array(Image.open(SP+'/gemini/noncombat_noattach.jpg').convert('RGB')).astype(float)
def cut(box,thr=46,outline=5,keep_largest=True,exclude=None):
    x0,y0,x1,y1=box; a=src[y0:y1,x0:x1].copy(); L=a.mean(2)
    fg=ndimage.binary_fill_holes(ndimage.binary_closing(L>thr,iterations=3))
    if exclude is not None:
        Y,Xg=np.mgrid[y0:y1,x0:x1]; fg&=~exclude(Xg,Y)
    lab,n=ndimage.label(fg); sz=ndimage.sum(fg,lab,range(1,n+1))
    fg=lab==(np.argmax(sz)+1) if keep_largest else np.isin(lab,np.nonzero(sz>200)[0]+1)
    ring=ndimage.binary_dilation(fg,iterations=outline)&~fg; a[ring]=14; m=fg|ring
    a[~m]=0
    im=Image.fromarray(np.dstack([a.astype(np.uint8),(m*255).astype(np.uint8)]),'RGBA'); return im.crop(im.getbbox())
parts={'miner':cut((20,60,345,430)),'engineer':cut((355,60,675,430)),'hazard':cut((685,60,1005,430)),
       'drill':cut((70,540,200,895),exclude=lambda X,Y:(X>196)),'hammer':cut((140,600,320,935),exclude=lambda X,Y:(X<200)&(Y<888)|(X<168)&(Y<900)),'claw':cut((735,540,915,835))}
for k,v in parts.items(): v.save(f'{SP}/gemini/nc_{k}.png')
floor=(92,84,70,255)
sheet=Image.new('RGBA',(1500,820),floor); d=ImageDraw.Draw(sheet)
x=10
for k in ('miner','engineer','hazard'):
    im=parts[k]; d.text((x,4),k,fill=(255,255,255,255)); sheet.alpha_composite(im,(x,24)); x+=im.width+20
x=10
for k in ('drill','hammer','claw'):
    im=parts[k].copy(); im.thumbnail((200,300)); d.text((x,420),k,fill=(255,255,255,255)); sheet.alpha_composite(im,(x,440)); x+=im.width+30
# miner kit: body + drill and pick-hammer hanging below the forearms (scaled to the body)
body=parts['miner']; B=Image.new('RGBA',(body.width+160,body.height+180)); ox=80
B.alpha_composite(body,(ox,0))
dr=parts['drill'].copy(); dr=dr.resize((int(dr.width*0.55),int(dr.height*0.55)),Image.LANCZOS)
hm=parts['hammer'].copy(); hm=hm.resize((int(hm.width*0.55),int(hm.height*0.55)),Image.LANCZOS)
a=np.array(body)[...,3]>60; ys,xs=np.nonzero(a)
B.alpha_composite(dr,(ox+18,int(ys.max()*0.62)))
B.alpha_composite(hm,(ox+body.width-hm.width+10,int(ys.max()*0.66)))
B=B.crop(B.getbbox()); B.save(SP+'/gemini/nc_miner_kit.png')
d.text((760,420),'miner kit (body + drill + pick-hammer)',fill=(255,255,255,255))
mk=B.copy(); mk.thumbnail((360,380)); sheet.alpha_composite(mk,(760,440))
sm=mk.resize((int(mk.width*72/mk.height),72),Image.LANCZOS); sheet.alpha_composite(sm,(1160,740))
sheet.save(SP+'/nc_parts.png')
