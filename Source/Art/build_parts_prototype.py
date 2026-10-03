import sys; sys.path.insert(0,'.')
from parts_lib import *
from PIL import ImageDraw
SP=sys.argv[1]; HW=float(sys.argv[2]); DROP=float(sys.argv[3]); GS=float(sys.argv[4])
CANON_CY, CANON_BOTTOM = 66.0, 106.0
T=base_transform('nano/south.png')
names=[('medic','Medic',(0.93,0.93,0.91),'medic_chassis'),('builder','Builder',(0.95,0.76,0.28),'builder_chassis'),
       ('miner_drill','Miner',(0.72,0.54,0.38),'miner_drill_chassis'),('bulwark','Bulwark',(0.56,0.58,0.60),'bulwark_chassis2'),
       ('bughunter','Bughunter',(0.78,0.68,0.50),'bughunter_chassis2'),('harvester','Harvester',(0.56,0.68,0.42),'harvester_chassis')]
C={}; H={}
for k,_,_,f in names:
    lay=layer(f'{SP}/mod/{f}.png',T); c=collar(lay[0])
    C[k]=shift(lay,0,CANON_CY-c[1])
    HWk={'harvester':HW*1.3,'miner_drill':HW*1.08,'medic':HW*0.98}.get(k,HW)
    H[k]=helmet_layer(f'{SP}/mod/{k}_helmetfinal.png',127,CANON_BOTTOM+DROP,HWk)
    C[k]=rescale(C[k],GS); H[k]=rescale(H[k],GS)
floor=(92,84,70,255)
out=Image.new('RGBA',(6*230,3*240+20),floor); d=ImageDraw.Draw(out)
for i,(k,lab,col,_) in enumerate(names):
    x=i*230; d.text((x+6,4),lab,fill=(255,255,255,255))
    out.alpha_composite(stack([C[k]],col).resize((220,220),Image.LANCZOS),(x+5,20))
    out.alpha_composite(stack([H[k]],col).resize((220,220),Image.LANCZOS),(x+5,260))
    out.alpha_composite(stack([C[k],H[k]],col).resize((220,220),Image.LANCZOS),(x+5,500))
out.save(SP+'/mod_parts2.png')
cell=120; g=Image.new('RGBA',(cell*7,cell*7),floor); d=ImageDraw.Draw(g)
for j,(ck,cl,_,_) in enumerate(names): d.text((cell*(j+1)+6,cell-14),cl,fill=(255,255,255,255))
for i,(hk,hl,_,_) in enumerate(names):
    d.text((4,cell*(i+1)+50),hl+'\nhelmet',fill=(255,255,255,255))
    for j,(ck,_,col,_) in enumerate(names):
        g.alpha_composite(stack([C[ck],H[hk]],col).resize((cell,cell),Image.LANCZOS),(cell*(j+1),cell*(i+1)))
g.save(SP+'/mod_grid2.png')
import pickle; pickle.dump({'C':{k:[im.tobytes() for im in v] for k,v in C.items()}},open(SP+'/parts.pkl','wb'))
