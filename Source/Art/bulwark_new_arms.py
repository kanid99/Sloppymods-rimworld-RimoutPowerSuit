import sys,os
SP=sys.argv[1]
exec(open(SP+'/bulwark_hang2.py').read().split("loadouts=[")[0])
OUTX={'towershield':6}
_arm=arm
def arm(name,side):
    w=clip_behind(place(f'{SP}/weap/{name}.png',PCX-OUT-OUTX.get(name,0),58+int(os.environ.get('TOP','80')),H[name],side),ringw)
    return [w,plate(side)]
H.update({'autocannon':120,'grenade':104,'arc':134,'towershield':136})
loadouts=[('autocannon / grenade','autocannon','grenade'),('arc / minigun','arc','minigun'),('tower shield / autocannon','towershield','autocannon'),('grenade / chainsaw','grenade','chainsaw'),('tower shield / hammer','towershield','hammer'),('arc / arc','arc','arc')]
img=Image.new('RGBA',(3*345,2*330),floor); d=ImageDraw.Draw(img)
for i,(lab,a,b) in enumerate(loadouts):
    out=Image.new('RGBA',(WC,S))
    for t,m in [ch,*arm(a,'left'),*arm(b,'right'),HL]: out.alpha_composite(tint(t,m,COL['bulwark']))
    x,y=(i%3)*345,(i//3)*330
    d.text((x+6,y+4),lab,fill=(255,255,255,255))
    img.alpha_composite(out,(x+8,y+20)); img.alpha_composite(out.resize((82,64),Image.LANCZOS),(x+130,y+262))
img.save(SP+'/bulwark_new_arms.png')
