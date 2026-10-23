"""One-off: write text/mdtext/*.json from the text dumps in work/p3
(tools/cap_text.sh): the pattern rows, a preview palette and the drawing.

    cd work/p3 && python ../../tools/make_mdtext_specs.py

Overwrites the specs; run it only to start again from the dumps.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import mdgrid
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'text', 'mdtext')
def tok_rect(dump, pl, cx, cy, w, h, shot):
    d = mdgrid.Dump(dump)
    return dict(source='work/p3/%s plane %s cells %d,%d %dx%d' % (dump, pl, cx, cy, w, h),
                plane=pl, rows=[' '.join(r) for r in d.rect(pl, cx, cy, w, h)],
                preview_palette=d.sample_palette(shot, pl, cx, cy, w, h))
def run_tokens(dump, run_id, a, b, shot):
    d = mdgrid.Dump(dump)
    r = [x for x in d.runs if x['id'] == run_id][0]
    return tok_rect(dump, r['plane'], r['cx'] + a, r['cy'], b - a, 1, shot)
BLANK = '171bb79dc8e18503'  # the blank tile (the space in SCENARIO QUEST)
def menu16(zh, align, width=None, thresh=140, **tok):
    # Title menu and OPTIONS: every line of text has a blank tile row under it
    # (the lines are 16 px apart), so the pattern takes that row too and the
    # Chinese is drawn 16 px high (Noto Sans TC Black, no anti-aliasing): the
    # font's index 4 and a 1 px shadow in index 8, which is black in palette
    # line 0 (the chosen title entry, the OPTIONS controls) and dark blue in
    # line 1 (the other entries), as the original text's colour changes.
    # 15 px of text + the shadow = 16 (音's dot needs thresh 160 for that).
    n = len(tok['rows'][0].split())
    tok['rows'] = tok['rows'] + [' '.join([BLANK] * n)]
    pal = tok['preview_palette']
    pal[8] = [0, 0, 0] if pal[4] == [255, 255, 255] else [0, 0, 73]
    out = dict(align=align, **tok, layers=[dict(font='NotoSansTC-Black.ttf', size=16, thresh=thresh, gap=1, zh=zh,
                                                style='menu16', align=align, y=0)])
    if width:
        out['size'] = [width, 16]
    return out
S = {}
M, MS = 'tr/dump/Text/text_001790.txt', 'tr/frame_01950.png'
S['title_scenario_quest'] = dict(en='SCENARIO QUEST', zh='劇情模式', screen='title menu', **menu16('劇情模式', 'center', **run_tokens(M, 1, 0, 14, MS)))
S['title_training'] = dict(en='TRAINING (title menu)', zh='練習模式', screen='title menu', **menu16('練習模式', 'center', **run_tokens(M, 2, 0, 8, MS)))
S['title_options'] = dict(en='OPTIONS', zh='設定', screen='title menu', **menu16('設定', 'center', **run_tokens(M, 3, 0, 7, MS)))
O, OS = 'opt/dump/Text/text_001968.txt', 'opt/frame_02100.png'
O2, OS2 = 'opt2/dump/Text/text_002138.txt', 'opt2/frame_02190.png'
S['opt_control_configuration'] = dict(en='CONTROL CONFIGURATION', zh='按鍵設定', screen='OPTIONS', **menu16('按鍵設定', 'left', **run_tokens(O, 1, 0, 21, OS)))
S['opt_type'] = dict(en='TYPE (controls): 1P/2P TYPE n', zh='類型', screen='OPTIONS', **menu16('類型', 'center', **run_tokens(O, 3, 0, 4, OS)))
S['opt_call'] = dict(en='CALL (controls): A:CALL', zh='呼叫', screen='OPTIONS', **menu16('呼叫', 'left', **run_tokens(O, 6, 2, 6, OS)))
S['opt_hold'] = dict(en='HOLD (controls): B:HOLD', zh='抓住', screen='OPTIONS', **menu16('抓住', 'left', **run_tokens(O, 8, 2, 6, OS)))
S['opt_jump'] = dict(en='JUMP (controls): C:JUMP', zh='跳躍', screen='OPTIONS', **menu16('跳躍', 'left', **run_tokens(O, 11, 2, 6, OS)))
S['opt_hold_jump'] = dict(en='HOLD&JUMP (controls, TYPE 3)', zh='抓住&跳躍', screen='OPTIONS', **menu16('抓住&跳躍', 'left', width=80, **run_tokens(O2, 8, 2, 11, OS2)))
S['opt_sound_test'] = dict(en='SOUND TEST', zh='音效測試', screen='OPTIONS', **menu16('音效測試', 'left', thresh=160, **run_tokens(O, 12, 0, 10, OS)))
S['opt_color_test'] = dict(en='COLOR TEST', zh='色彩測試', screen='OPTIONS', **menu16('色彩測試', 'left', **run_tokens(O, 13, 0, 10, OS)))
S['opt_exit'] = dict(en='EXIT (menu)', zh='離開', screen='OPTIONS', **menu16('離開', 'left', **run_tokens(O, 14, 0, 4, OS)))
D, DS = 'dl/dump/Text/text_002049.txt', 'dl/frame_02499.png'
NOTO = 'NotoSansTC-Black.ttf'
CAST = dict(idx=5, dx=2, dy=7, y0=16, grow=1)
S['dl_no_save'] = dict(en='NO SAVE', zh='不存檔', screen='DATA LOAD (slot header)', align='center', **tok_rect(D, 'A', 10, 0, 9, 3, DS),
    layers=[dict(font=NOTO, size=14, thresh=140, gap=1, zh='不', style='slot_pink', x=10, y=0, cast=CAST),
            dict(font=NOTO, size=14, thresh=140, gap=1, zh='存檔', style='slot_yellow', x=27, y=0, cast=CAST)])
S['dl_new'] = dict(en='NEW (save slot)', zh='新遊戲', screen='DATA LOAD (slot)', align='center', **tok_rect(D, 'A', 11, 7, 7, 3, DS),
    layers=[dict(font=NOTO, size=16, thresh=140, gap=1, zh='新遊戲', style='slot_green', align='center', region=[0, 53], y=0,
                 cast=dict(idx=5, dx=3, dy=6, y0=17, grow=1))])
D1, DS1 = 'dl2/dump/Text/text_002154.txt', 'dl2/frame_02300.png'
D2, DS2 = 'slots/dump/Text/text_002254.txt', 'slots/frame_02340.png'
for n, (dd, ss, cy) in {1: (D1, DS1, 14), 2: (D2, DS2, 28), 3: (D2, DS2, 42)}.items():
    S['dl_data%d' % n] = dict(en='DATA n (save slot): DATA %d' % n, zh='存檔 %d' % n, screen='DATA LOAD (slot header)', align='center',
        **tok_rect(dd, 'A', 10, cy, 9, 3, ss),
        layers=[dict(font=NOTO, size=14, thresh=140, gap=1, zh='存檔', style='slot_yellow', x=10, y=0, cast=CAST),
                dict(font=NOTO, size=14, thresh=140, gap=1, zh=str(n), style='slot_white', x=48, y=0, cast=CAST)])
# phase 4: the slots' CLEAR marks (a slot with a cleared zone, seen with a
# poked save, work/p4/dlt2 = tools/cap_sprites.sh dlt2 ... --sram): four are
# plane text, the fifth is a sprite (text/mdsprite/dl_clear5.json)
C, CS = '../p4/dlt2/dump/Text/text_002154.txt', '../p4/dlt2/frame_02200.png'
S['dl_clear'] = dict(en='CLEAR (save slot, cleared zone)', zh='過關', screen='DATA LOAD (used slot)', align='center',
    **tok_rect(C, 'A', 2, 21, 5, 3, CS),
    layers=[dict(font=NOTO, size=16, thresh=140, gap=1, zh='過關', style='slot_yellow', align='center', region=[0, 38], y=1)])
S['dl_clear']['source'] = 'work/p4/dlt2/dump/Text/text_002154.txt plane A cells 2,21 5x3'
for k, v in S.items():
    json.dump(v, open(os.path.join(OUT, k + '.json'), 'w', encoding='utf8', newline='\n'), ensure_ascii=False, indent=1)
print(len(S))
