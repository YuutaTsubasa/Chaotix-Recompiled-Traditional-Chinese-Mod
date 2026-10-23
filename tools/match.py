# match.py DUMPDIR SHOT.png x0 y0 x1 y1 [--grid]  -> MD tiles found in region
import sys,os,glob,json
import numpy as np
from PIL import Image
dd,shot=sys.argv[1],sys.argv[2]; x0,y0,x1,y1=map(int,sys.argv[3:7])
S=np.asarray(Image.open(shot).convert('RGB')).astype(np.int32)
S=S[:,:,0]*65536+S[:,:,1]*256+S[:,:,2]
R=S[y0:y1,x0:x1]
from numpy.lib.stride_tricks import sliding_window_view as swv
Wn=swv(R,(8,8))  # (h-7,w-7,8,8)
cache=os.path.join(dd,'_tiles.npz')
tiles=[]
for f in sorted(glob.glob(os.path.join(dd,'md_*.png'))):
    im=Image.open(f); idx=np.asarray(im).astype(np.int32); pal=im.getpalette()
    if (idx>0).sum()<6: continue
    rgb=np.array([pal[3*i]*65536+pal[3*i+1]*256+pal[3*i+2] for i in range(16)])
    col=idx; m=idx>0
    if len(set(idx.flatten().tolist()))<2: continue
    tiles.append((os.path.basename(f)[3:19],col,m))
hits=[]
for h,col,m in tiles:
    for fl,(c2,m2) in enumerate([(col,m),(col[:,::-1],m[:,::-1]),(col[::-1],m[::-1]),(col[::-1,::-1],m[::-1,::-1])]):
        idx2=c2  # here c2 holds indices
        eq=np.ones(Wn.shape[:2],bool); reps=[]
        for v in np.unique(idx2[m2]):
            ys,xs=np.nonzero((idx2==v)&m2); ry,rx=ys[0],xs[0]
            rep=Wn[:,:,ry,rx]; reps.append(rep)
            for yy_,xx_ in zip(ys[1:],xs[1:]): eq&=Wn[:,:,yy_,xx_]==rep
        for a in range(len(reps)):
            for b in range(a+1,len(reps)): eq&=reps[a]!=reps[b]
        ty,tx=np.nonzero(~m2)
        for yy_,xx_ in zip(ty,tx):
            for r in reps: eq&=Wn[:,:,yy_,xx_]!=r
        for yy,xx in zip(*np.nonzero(eq)):
            hits.append(dict(x=int(xx+x0),y=int(yy+y0),hash=h,flip=fl,n=int(m2.sum())))
# keep best (most opaque px) per position, dedupe
best={}
for t in hits:
    k=(t['x'],t['y'])
    if k not in best or t['n']>best[k]['n']: best[k]=t
out=sorted(best.values(),key=lambda t:(t['y'],t['x']))
print(json.dumps(out))
