import sys,os
from PIL import Image, ImageDraw
# stack.py out maxw sheets... : wrap each sheet at maxw, stack with labels
out=sys.argv[1]; maxw=int(sys.argv[2]); parts=[]
for f in sys.argv[3:]:
    i=Image.open(f).convert('RGB'); n=(i.width+maxw-1)//maxw
    M=Image.new('RGB',(maxw,n*i.height+12),(0,0,0)); ImageDraw.Draw(M).text((2,0),os.path.basename(f),fill=(255,255,0))
    for k in range(n): M.paste(i.crop((k*maxw,0,min(i.width,(k+1)*maxw),i.height)),(0,12+k*i.height))
    parts.append(M)
T=Image.new('RGB',(maxw,sum(p.height for p in parts)),(0,0,0)); y=0
for p in parts: T.paste(p,(0,y)); y+=p.height
T.save(out)
