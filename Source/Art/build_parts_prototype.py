import sys, pickle; sys.path.insert(0,'.')
from parts_lib import *
from PIL import ImageDraw
SP=sys.argv[1]
HW,DROP,GS=104,14,0.8
CANON_CY,CANON_BOTTOM=64.0,106.0
T=base_transform('nano/south.png')
V=['medic','builder','miner','bulwark','bughunter','harvester']
COL={'medic':(0.93,0.93,0.91),'builder':(0.95,0.76,0.28),'miner':(0.72,0.54,0.38),'bulwark':(0.56,0.58,0.60),'bughunter':(0.66,0.56,0.40),'harvester':(0.56,0.68,0.42)}
C={};H={}
for k in V:
    src = f'{SP}/mod5/chassis_harvester.png' if k == 'harvester' else f'{SP}/mod4/chassis_{k}.png'
    lay=layer(src,T); c=collar(lay[0])
    lay=shift(lay,0,CANON_CY-c[1])
    C[k]=rescale(lay if k == 'harvester' else flatten_collar(lay),GS)
    H[k]=rescale(helmet_layer(f'{SP}/mod2/helmet_{k}.png',127,CANON_BOTTOM+DROP,HW*{'harvester':1.25,'miner':1.1}.get(k,1)),GS)
# arm placement: (inner edge x on the left side, top y, height) in final canvas pixels
AX=float(sys.argv[2]) if len(sys.argv)>2 else 70
ARMS={'standard':(AX,96,66,False),'medic':(AX,98,62,False),'builder':(AX,86,74,False),'miner':(AX+2,94,70,False),
      'bulwark':(98,58,176,False),'bughunter':(AX+4,70,104,False)}
A={}
for a,(ix,top,h,fv) in ARMS.items():
    A[a]={'left':arm_layer(f'{SP}/arms/arm_{a}.png',ix,top,h,'left',fv),'right':arm_layer(f'{SP}/arms/arm_{a}.png',ix,top,h,'right',fv)}
def suit(ch,he,al,ar,col):
    return stack([C[ch],A[al]['left'],A[ar]['right'],H[he]],col)   # pauldrons over the shoulder joints, under the helmet
floor=(92,84,70,255)
# sheet: each variant with matching arms
match={'medic':'medic','builder':'builder','miner':'miner','bulwark':'bulwark','bughunter':'bughunter','harvester':'standard'}
out=Image.new('RGBA',(6*230,2*250+20),floor); d=ImageDraw.Draw(out)
for i,k in enumerate(V):
    d.text((i*230+6,4),k.title()+' + '+match[k]+' arms',fill=(255,255,255,255))
    out.alpha_composite(suit(k,k,match[k],match[k],COL[k]).resize((220,220),Image.LANCZOS),(i*230+5,20))
mixes=[('bulwark','bughunter','bulwark','bughunter','bulwark'),('miner','builder','miner','builder','miner'),('medic','medic','standard','medic','medic'),
       ('builder','miner','builder','standard','builder'),('bughunter','bulwark','bughunter','bughunter','bughunter'),('harvester','harvester','medic','miner','harvester')]
for i,(ch,he,al,ar,c) in enumerate(mixes):
    d.text((i*230+6,254),f'{ch} chassis, {he} helmet,\n{al}/{ar} arms',fill=(255,255,255,255))
    out.alpha_composite(suit(ch,he,al,ar,COL[c]).resize((220,220),Image.LANCZOS),(i*230+5,280))
out.save(SP+'/arms_suits_flat4.png')
# helmetless chassis with arms, to show the flat collar
row=Image.new('RGBA',(6*230,250),floor); d=ImageDraw.Draw(row)
for i,k in enumerate(V):
    d.text((i*230+6,4),k.title()+' (no helmet)',fill=(255,255,255,255))
    row.alpha_composite(stack([C[k],A[match[k]]['left'],A[match[k]]['right']],COL[k]).resize((220,220),Image.LANCZOS),(i*230+5,20))
row.save(SP+'/chassis_flat4.png')
