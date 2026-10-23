def nemesis(d,pos):
    h=(d[pos]<<8)|d[pos+1]; xor=h&0x8000; tiles=h&0x7fff; p=pos+2; codes={}; nyb=0
    b=d[p];p+=1
    while b!=0xFF:
        if b&0x80: nyb=b&15; b=d[p];p+=1
        cnt=((b>>4)&7)+1; ln=b&15; code=d[p];p+=1; codes[(ln,code)]=(nyb,cnt); b=d[p];p+=1
    bit=p*8; out=bytearray(tiles*32); st={'done':0,'row':0,'prev':0}; total=tiles*64
    def rb():
        nonlocal bit
        v=(d[bit>>3]>>(7-(bit&7)))&1; bit+=1; return v
    def put(v,c):
        for _ in range(c):
            if st['done']>=total: return
            st['row']=((st['row']<<4)|v)&0xffffffff
            if st['done']&7==7:
                r=st['row']
                if xor: r^=st['prev']
                st['prev']=r; a=(st['done']//8)*4; out[a:a+4]=r.to_bytes(4,'big'); st['row']=0
            st['done']+=1
    while st['done']<total:
        code=0;ln=0
        while True:
            code=(code<<1)|rb(); ln+=1
            if ln==6 and code==0x3f:
                c=0;v=0
                for _ in range(3): c=(c<<1)|rb()
                for _ in range(4): v=(v<<1)|rb()
                put(v,c+1); break
            if (ln,code) in codes: put(*codes[(ln,code)]); break
            if ln>8: raise Exception('bad code')
    return bytes(out)
def fnv(p):
    h=1469598103934665603
    for b in p: h=((h^b)*1099511628211)&0xffffffffffffffff
    return '%016x'%h
