import sys,os
from PIL import Image, ImageDraw
# gal.py out.png scale maxw files...: gallery packing with labels
out=sys.argv[1]; sc=int(sys.argv[2]); maxw=int(sys.argv[3]); fs=sys.argv[4:]
items=[]
for f in fs:
    i=Image.open(f).convert('RGBA')
    i=i.resize((i.width*sc,i.height*sc),Image.NEAREST)
    items.append((os.path.basename(f).replace('.png',''),i))
x=y=0; rowh=0; pos=[]
for n,i in items:
    w=max(i.width,len(n)*6+4)
    if x+w>maxw and x>0: x=0; y+=rowh+14; rowh=0
    pos.append((x,y)); x+=w+6; rowh=max(rowh,i.height)
H=y+rowh+14
M=Image.new('RGBA',(maxw,H),(60,60,70,255)); d=ImageDraw.Draw(M)
for (n,i),(x,y) in zip(items,pos):
    d.text((x,y),n,fill=(255,255,0,255)); M.alpha_composite(i,(x,y+12))
M.convert('RGB').save(out)
