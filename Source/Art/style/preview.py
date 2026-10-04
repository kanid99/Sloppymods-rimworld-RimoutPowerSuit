import sys; SP=sys.argv[1]
import numpy as np
from PIL import Image, ImageDraw
V=SP+'/vfep/Textures/Things/Pawn/Warcasketlike/'
HEAD_UP=58   # RimWorld draws the helmet at the head position: 0.34 of the 1.5 mesh above the body
def stack(paths):
    c=Image.new('RGBA',(256,256+HEAD_UP))
    for i,p in enumerate(paths): c.alpha_composite(Image.open(p).convert('RGBA'),(0,HEAD_UP-(HEAD_UP if i==2 else 0)))
    return c
def vfe(n): return stack([f'{V}Warcasket{n}/Warcasket{n}{p}_south.png' for p in ('','Shoulders','Helmet')])
ours=stack([f'{SP}/bw2/Bulwark_{p}_south.png' for p in ('body','shoulders','helmet')])
def tint(im,c):
    a=np.array(im).astype(float); a[...,:3]*=np.array(c)/255; return Image.fromarray(a.astype(np.uint8),'RGBA')
floor=(92,84,70,255)
row=[('VFE Brute',vfe('Brute')),('VFE Cataphract',vfe('Cataphract')),('our Bulwark',ours),('ours, steel',tint(ours,(150,160,175))),('ours, olive',tint(ours,(150,165,110)))]
sheet=Image.new('RGBA',(len(row)*270,440),floor); d=ImageDraw.Draw(sheet)
for i,(lab,im) in enumerate(row):
    d.text((i*270+6,4),lab,fill=(255,255,255,255)); sheet.alpha_composite(im,(i*270+7,20))
    sheet.alpha_composite(im.resize((64,int(64*im.height/256)),Image.LANCZOS),(i*270+100,350))
sheet.save(SP+'/bw2_preview.png')
lay=Image.new('RGBA',(3*270,290),floor); d=ImageDraw.Draw(lay)
for i,p in enumerate(('body','shoulders','helmet')):
    d.text((i*270+6,4),p,fill=(255,255,255,255)); lay.alpha_composite(Image.open(f'{SP}/bw2/Bulwark_{p}_south.png'),(i*270+7,22))
lay.save(SP+'/bw2_layers.png')
