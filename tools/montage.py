import sys,glob,os
from PIL import Image, ImageDraw
# usage: montage.py out.png scale cols files...
out=sys.argv[1]; sc=float(sys.argv[2]); cols=int(sys.argv[3]); fs=sys.argv[4:]
ims=[Image.open(f).convert('RGB') for f in fs]
w=max(i.width for i in ims); h=max(i.height for i in ims)
w2,h2=int(w*sc),int(h*sc)
rows=(len(ims)+cols-1)//cols
M=Image.new('RGB',(cols*w2,rows*(h2+12)),(40,40,40))
d=ImageDraw.Draw(M)
for k,(f,i) in enumerate(zip(fs,ims)):
    x=(k%cols)*w2; y=(k//cols)*(h2+12)
    M.paste(i.resize((int(i.width*sc),int(i.height*sc)),Image.NEAREST),(x,y+12))
    d.text((x+2,y),os.path.basename(f),fill=(255,255,0))
M.save(out)
