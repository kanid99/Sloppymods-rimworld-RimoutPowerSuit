import sys; sys.path.insert(0,'.')
SP=sys.argv[1]
src=open(SP+'/build_arms_flat4.py').read().split('floor=(92,84,70,255)')[0].replace("SP=sys.argv[1]","SP=sys.argv[1]; sys.argv=[sys.argv[0],SP,'92']")
exec(src)
from PIL import ImageDraw
floor=(92,84,70,255)
def armpair(name,ix,top,h):
    return (clip_behind(arm_layer(f'{SP}/arms/arm_{name}.png',ix,top,h,'left'),ring_final),
            clip_behind(arm_layer(f'{SP}/arms/arm_{name}.png',ix,top,h,'right'),ring_final))
FL=armpair('flamer',102,70,150); HM=armpair('hammer',100,64,156)
builds=[('Bughunter: flamer + hammer',[C['bughunter'],FL[0],HM[1],H['bughunter']],COL['bughunter']),
        ('Bughunter: two hammers',[C['bughunter'],HM[0],HM[1],H['bughunter']],COL['bughunter']),
        ('Bughunter: two flamers',[C['bughunter'],FL[0],FL[1],H['bughunter']],COL['bughunter']),
        ('Bulwark chassis: flamer + hammer',[C['bulwark'],FL[0],HM[1],H['bulwark']],COL['bulwark'])]
img=Image.new('RGBA',(4*250,330),floor); d=ImageDraw.Draw(img)
for i,(lab,layers,col) in enumerate(builds):
    s=stack(layers,col); d.text((i*250+6,4),lab,fill=(255,255,255,255))
    img.alpha_composite(s.resize((240,240),Image.LANCZOS),(i*250+5,20))
    img.alpha_composite(s.resize((64,64),Image.LANCZOS),(i*250+90,262))
img.save(SP+'/bughunter_weapons.png')
