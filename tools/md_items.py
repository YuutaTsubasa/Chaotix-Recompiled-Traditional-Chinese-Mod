import json,os,glob,sys
import numpy as np
from PIL import Image
from numpy.lib.stride_tricks import sliding_window_view as swv
ITEMS=[
 ('menu','menu_scenario_quest','SCENARIO QUEST',(94,118,210,132)),
 ('menu','menu_training','TRAINING',(116,134,186,148)),
 ('menu','menu_options','OPTIONS',(124,150,186,164)),
 ('options','opt_control_configuration','CONTROL CONFIGURATION',(28,37,204,51)),
 ('options','opt_1p_type','1P   TYPE 1',(54,53,137,67)),
 ('options','opt_2p_type','2P   TYPE 1',(181,53,265,67)),
 ('options','opt_a_call','A:CALL (x2)',(68,69,250,83)),
 ('options','opt_b_hold','B:HOLD (x2)',(68,85,250,99)),
 ('options','opt_c_jump','C:JUMP (x2)',(68,101,250,115)),
 ('options','opt_sound_test','SOUND TEST',(29,125,112,139)),
 ('options','opt_color_test','COLOR TEST',(29,149,112,163)),
 ('options','opt_exit','EXIT',(29,173,66,187)),
 ('dataload','dl_data_load','DATA LOAD',(174,6,306,42)),
 ('dataload','dl_no_save','NO SAVE',(126,60,194,84)),
 ('dataload','dl_new','NEW',(134,116,186,142)),
 ('dataload','dl_play','PLAY',(28,176,84,208)),
 ('dataload','dl_delete','DELETE',(92,176,164,208)),
 ('dataload','dl_data_n','DATA 1',(170,174,246,200)),
 ('training','tr_training','TRAINING',(176,6,300,38)),
 ('training','tr_zone_name','ISOLATED ISLAND',(94,100,218,124)),
 ('training','tr_play','PLAY',(36,178,90,206)),
 ('training','tr_exit','EXIT',(100,178,148,206)),
 ('playstyle','ps_play_style','PLAY STYLE',(20,6,154,38)),
 ('playstyle','ps_1p_big','1P',(148,62,174,82)),
 ('playstyle','ps_1p_small','1P (selector)',(94,132,140,148)),
 ('playstyle','ps_cpu','CPU',(182,132,226,148)),
 ('playstyle','ps_2p_big','2P',(100,172,126,194)),
 ('playstyle','ps_player_select_banner','PLAYER SELECT',(156,176,290,208)),
 ('playersel','psel_player_select','PLAYER SELECT',(100,12,218,34)),
 ('playersel','psel_char_name','KNUCKLES THE ECHIDNA',(78,106,242,126)),
 ('dataload2','dl_data_n_header','DATA 1 (slot header, yellow)',(124,64,198,88)),
 ('soundtest','st_channel_labels','FM1-FM6 PSG1-PSG3 PWM',(18,12,58,180)),
 ('soundtest','st_sound_test','--- SOUND TEST ---',(34,192,206,212)),
]
def load_tiles(dd):
    T=[]
    for f in sorted(glob.glob(os.path.join(dd,'md_*.png'))):
        im=Image.open(f); idx=np.asarray(im).astype(np.int32)
        if (idx>0).sum()<6 or len(set(idx.flatten().tolist()))<2: continue
        T.append((os.path.basename(f)[3:19],idx))
    return T
def match(T,S,box):
    x0,y0,x1,y1=box; R=S[y0:y1,x0:x1]; Wn=swv(R,(8,8)); hits=[]
    for h,idx in T:
        for fl,i2 in enumerate([idx,idx[:,::-1],idx[::-1],idx[::-1,::-1]]):
            m2=i2>0; eq=np.ones(Wn.shape[:2],bool); reps=[]
            for v in np.unique(i2[m2]):
                ys,xs=np.nonzero(i2==v); rep=Wn[:,:,ys[0],xs[0]]; reps.append(rep)
                for a,b in zip(ys[1:],xs[1:]): eq&=Wn[:,:,a,b]==rep
                if not eq.any(): break
            if not eq.any(): continue
            for a in range(len(reps)):
                for b in range(a+1,len(reps)): eq&=reps[a]!=reps[b]
            ty,tx=np.nonzero(~m2)
            for a,b in zip(ty,tx):
                for r in reps: eq&=Wn[:,:,a,b]!=r
            for yy,xx in zip(*np.nonzero(eq)): hits.append((int(m2.sum()),int(xx+x0),int(yy+y0),h,fl))
    hits.sort(key=lambda t:-t[0]); occ=np.zeros(S.shape,bool); sel=[]
    for n,x,y,h,fl in hits:
        if occ[y:y+8,x:x+8].sum()>8: continue
        occ[y:y+8,x:x+8]=True; sel.append(dict(x=x,y=y,hash=h,flip=fl,opaque=n))
    sel.sort(key=lambda t:(t['y']//4,t['x']))
    return sel
cache={}; out=[]
for scene,iid,en,box in ITEMS:
    D='work/scenes/%s/'%scene
    if scene not in cache:
        S=np.asarray(Image.open(D+'md.png').convert('RGB')).astype(np.int32)
        cache[scene]=(load_tiles(D+'dump'),S[:,:,0]*65536+S[:,:,1]*256+S[:,:,2])
    T,S=cache[scene]; sel=match(T,S,box)
    out.append(dict(scene=scene,id=iid,en=en,box=box,tiles=sel))
    print(iid,len(sel),len(set(t['hash'] for t in sel)),file=sys.stderr)
json.dump(out,open('work/md_items.json','w'),indent=0)
