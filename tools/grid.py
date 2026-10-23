import sys
from PIL import Image, ImageDraw
# grid.py in out : 3x scale with grid lines every 8px (labels every 16)
i=Image.open(sys.argv[1]).convert('RGB'); s=3
M=i.resize((i.width*s,i.height*s),Image.NEAREST); d=ImageDraw.Draw(M)
for x in range(0,i.width,8): d.line([(x*s,0),(x*s,M.height)],fill=(80,80,80) if x%32 else (200,0,0))
for y in range(0,i.height,8): d.line([(0,y*s),(M.width,y*s)],fill=(80,80,80) if y%32 else (200,0,0))
for x in range(0,i.width,32): d.text((x*s+2,2),str(x),fill=(255,255,0))
for y in range(0,i.height,32): d.text((2,y*s+2),str(y),fill=(255,255,0))
M.save(sys.argv[2])
