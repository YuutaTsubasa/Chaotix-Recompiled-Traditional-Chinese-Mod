import sys
from PIL import Image
for n in sys.argv[1:]:
    D='work/scenes/'+n+'/'
    ims=[Image.open(D+f+'.png').convert('RGB') for f in ['full','md','32x']]
    w,h=ims[0].size
    M=Image.new('RGB',(w*2*3,h*2))
    for k,i in enumerate(ims): M.paste(i.resize((w*2,h*2),Image.NEAREST),(k*w*2,0))
    M.save(D+'tri.png')
