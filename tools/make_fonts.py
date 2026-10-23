import json
from collections import defaultdict
from PIL import Image
from rom import ROM
from nemesis import nemesis

d = {i['id']: i for i in json.load(open('md_items.json'))}
txt = {'menu_scenario_quest': 'SCENARIOQUEST', 'menu_training': 'TRAINING', 'menu_options': 'OPTIONS',
       'opt_control_configuration': 'CONTROLCONFIGURATION', 'opt_sound_test': 'SOUNDTEST',
       'opt_color_test': 'COLORTEST', 'opt_exit': 'EXIT'}
from collections import Counter
m = defaultdict(Counter)
for k, s in txt.items():
    ts = sorted(d[k]['tiles'], key=lambda t: t['x'])
    if len(ts) == len(s):
        for c, t in zip(s, ts):
            m[c][t['hash']] += 1
font = {c: v.most_common(1)[0][0] for c, v in sorted(m.items())}
json.dump(font, open('font8x8.json', 'w'), indent=0)
print('8x8 letters:', ''.join(font))

# 8x16 font picture, 4x, for review
t = nemesis(ROM, 0x2C4B20)
pal = []
for i in range(16):
    w = (ROM[0x03E8CA + 2 * i] << 8) | ROM[0x03E8CB + 2 * i]
    pal.append((((w >> 1) & 7) * 36, ((w >> 5) & 7) * 36, ((w >> 9) & 7) * 36))
n = len(t) // 64
img = Image.new('RGB', (n * 8, 16), (48, 48, 56))
for g in range(n):
    for half in range(2):
        tile = t[(2 * g + half) * 32:(2 * g + half + 1) * 32]
        for y in range(8):
            for x in range(8):
                b = tile[y * 4 + x // 2]
                v = (b >> 4) if x % 2 == 0 else (b & 15)
                if v:
                    img.putpixel((g * 8 + x, half * 8 + y), pal[v])
img.resize((img.width * 3, img.height * 3), Image.NEAREST).save('../inventory/sheets/font_8x16_game_font.png')
