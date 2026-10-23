import sys,os,re
from PIL import Image, ImageDraw
def parse(txt):
    hx=hy=0; fr={}
    for l in open(txt):
        p=l.split()
        if not p: continue
        if p[0]=='hotspot': hx,hy=int(p[1]),int(p[2])
        if p[0]=='frame' and len(p)>=11 and p[6] not in('empty','same'):
            f=int(p[1],16); X,Y,W,H,x0,x1,y0,y1=map(int,p[2:10]); fr[f]=(X+hx+x0,Y+hy+y0,x1-x0,y1-y0+1)
    return fr
def crop(sheetdir,bank,frame,scale=3):
    fr=parse(os.path.join(sheetdir,'32x_%02x.txt'%bank))
    x,y,w,h=fr[frame]
    im=Image.open(os.path.join(sheetdir,'32x_%02x.png'%bank))
    c=im.crop((x,y,x+w,y+h)).convert('RGBA')
    # make index 0 transparent -> show on dark grey
    idx=im.crop((x,y,x+w,y+h)); px=idx.load(); a=c.load()
    for j in range(h):
        for i in range(w):
            if px[i,j]==0: a[i,j]=(48,48,56,255)
    return c.resize((w*scale,h*scale),Image.NEAREST),(w,h)
if __name__=='__main__':
    sd,bank,out=sys.argv[1],int(sys.argv[2],16),sys.argv[3]
    fr=parse(os.path.join(sd,'32x_%02x.txt'%bank))
    items=[(f,)+crop(sd,bank,f,2) for f in sorted(fr)]
    maxw=1500; x=y=0; rowh=0; pos=[]
    for f,c,_ in items:
        if x+c.width>maxw and x: x=0;y+=rowh+14;rowh=0
        pos.append((x,y)); x+=max(c.width,40)+6; rowh=max(rowh,c.height)
    M=Image.new('RGB',(maxw,y+rowh+14),(0,0,0)); d=ImageDraw.Draw(M)
    for (f,c,s),(x,y) in zip(items,pos):
        d.text((x,y),'%02x %dx%d'%(f,s[0],s[1]),fill=(255,255,0)); M.paste(c,(x,y+12))
    M.save(out)
