"""Builds inventory/inventory.json and inventory/sheets/*.png from the dumps in work/.

The dumps are made with chaotix_headless (see inventory/README.md, "How this was made").
Run from the repository root with a Python that has Pillow and numpy.
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, 'tools')
from frames import parse

OUT = 'inventory'
SHEETS = os.path.join(OUT, 'sheets')
os.makedirs(SHEETS, exist_ok=True)
SCALE = 3
W = 'work/'

# ---- 32X sprite items -------------------------------------------------------
# (id, scenes, bank, frame, en, sheet dir with a good palette, style, drawing notes)
X = [
 # title screen, bank 55
 ('title_logo_left', ['title'], 0x55, 0x0a, 'CHAOTIX (left half) / FEATURING KNUCKLES THE ECHIDNA. / WELCOME TO THE NEXT LEVEL / IN 32X WORLD / [PUSH START box]', 'title/sheets',
  'logo in purple/gold 3D letters; tagline 3 lines of ~6 px dark-olive letters on the gold bar; boxed PUSH START in blue',
  'the logo, tagline and the PUSH START box are one picture split in two halves (0a left, 0b right, 146x112 each); words cross the split, so both halves must be redrawn together'),
 ('title_logo_right', ['title'], 0x55, 0x0b, 'CHAOTIX (right half) + TM / tagline right half / [PUSH START box]', 'title/sheets', 'see title_logo_left', 'right half of the logo picture'),
 ('title_push_start', ['title'], 0x55, 0x09, 'PUSH START', 'title/sheets', 'white/pink 8 px letters with magenta shading', 'whole phrase, one sprite (the flashing text in the logo box)'),
 ('title_copyright', ['title'], 0x55, 0x0d, '©SEGA ENTERPRISES,LTD.1995', 'title/sheets', 'white 8 px letters, black outline', 'whole line, one sprite; legal line, probably kept as is'),
 # HUD, bank 13
 ('hud_points', ['level', 'results'], 0x13, 0x00, 'POINTS', 'tc/sheets', 'yellow, dark-red shadow, 14 px', 'whole word'),
 ('hud_rings', ['level', 'bonus', 'special', 'results'], 0x13, 0x01, 'RINGS', 'tc/sheets', 'yellow, 14 px', 'whole word; 0x02 is the red flashing copy'),
 ('hud_rings_red', ['level'], 0x13, 0x02, 'RINGS (red)', 'tc/sheets', 'red flashing variant (no rings)', 'whole word'),
 ('hud_time', ['level', 'results'], 0x13, 0x03, 'TIME', 'tc/sheets', 'yellow, 14 px', 'whole word; 0x04 red copy'),
 ('hud_time_red', ['level'], 0x13, 0x04, 'TIME (red)', 'tc/sheets', 'red flashing variant', 'whole word'),
 ('hud_pause', ['level (paused)'], 0x13, 0x05, 'PAUSE', 'tc/sheets', 'yellow, 14 px', 'whole word; followed by "!" (frame 0x06) as a separate sprite'),
 ('hud_exclaim', ['level (paused)'], 0x13, 0x06, '!', 'tc/sheets', 'yellow', 'punctuation sprite after PAUSE (could be blanked)'),
 ('hud_limits', ['special'], 0x13, 0x07, 'LIMITS', 'tc/sheets', 'yellow, 14 px', 'whole word; 0x08 red copy'),
 ('hud_limits_red', ['special'], 0x13, 0x08, 'LIMITS (red)', 'tc/sheets', 'red variant', 'whole word'),
 ('hud_attack', ['not seen (special/2P?)'], 0x13, 0x09, 'ATTACK', 'tc/sheets', 'yellow, 14 px', 'whole word; 0x0a red copy'),
 ('hud_attack_red', ['not seen'], 0x13, 0x0a, 'ATTACK (red)', 'tc/sheets', 'red variant', 'whole word'),
 ('hud_hurry', ['not seen'], 0x13, 0x0b, 'HURRY', 'tc/sheets', 'yellow, 14 px', 'whole word'),
 ('hud_up', ['not seen'], 0x13, 0x0c, 'UP', 'tc/sheets', 'yellow, 14 px', 'whole word'),
 ('hud_score', ['level', 'bonus', 'results'], 0x13, 0x25, 'SCORE', 'tc/sheets', 'yellow, dark-red shadow, 14 px', 'whole word'),
 ('hud_hold', ['level'], 0x13, 0x26, 'HOLD!', 'tc/sheets', 'black letters in a white speech bubble', 'whole picture'),
 ('hud_score_red', ['not seen'], 0x13, 0x3a, 'SCORE (red)', 'tc/sheets', 'red variant', 'whole word'),
 ('hud_level', ['not seen'], 0x13, 0x3d, 'LEVEL', 'tc/sheets', 'yellow, 14 px', 'whole word'),
 ('hud_demo', ['attract demo'], 0x13, 0x40, '-DEMO-', 'tc/sheets', 'yellow on black bar', 'whole word'),
 # title card, bank 40
 ('card_level', ['title card'], 0x40, 0x07, 'L E V E L', 'tc/sheets', 'white spaced letters on black, ~7 px, at the bottom of a 68x54 black box', 'whole word'),
 ('card_botanic_base', ['title card'], 0x40, 0x08, 'NEWTROGIC HIGH ZONE / BOTANIC BASE / CHAOTIX', 'tc/sheets',
  'zone name ~24 px tall, green (palette per zone) with dark shading; two ~7 px white lines above and below', 'whole picture 200x52 per zone (name + both small lines)'),
 ('card_marina_madness', ['title card'], 0x40, 0x09, 'NEWTROGIC HIGH ZONE / MARINA MADNESS / CHAOTIX', 'tc/sheets', 'as card_botanic_base', 'whole picture'),
 ('card_amazing_arena', ['title card'], 0x40, 0x0a, 'NEWTROGIC HIGH ZONE / AMAZING ARENA / CHAOTIX', 'tc/sheets', 'as card_botanic_base', 'whole picture'),
 ('card_techno_tower', ['title card'], 0x40, 0x0b, 'NEWTROGIC HIGH ZONE / TECHNO TOWER / CHAOTIX', 'tc/sheets', 'as card_botanic_base', 'whole picture'),
 ('card_speed_slider', ['title card'], 0x40, 0x0c, 'NEWTROGIC HIGH ZONE / SPEED SLIDER / CHAOTIX', 'tc/sheets', 'as card_botanic_base', 'whole picture'),
 ('card_isolated_island', ['title card (intro, training)'], 0x40, 0x10, 'NEWTROGIC HIGH ZONE / ISOLATED ISLAND / CHAOTIX', 'tc/sheets', 'as card_botanic_base', 'whole picture'),
 ('card_cast_list', ['title card'], 0x40, 0x0d, 'ESPIO!! KNUCKLES!! MIGHTY!! CHARMY BEE!! VECTOR!! HEAVY!! BOMB!!', 'tc/sheets',
  '7 lines of tiny (~6 px) yellow letters on a yellow/black panel; decorative', 'whole picture'),
 ('card_barcode', ['title card'], 0x40, 0x0f, '023420019023 (barcode digits)', 'tc/sheets', 'black digits over a barcode', 'decoration; no translation needed'),
]

RES = [
  ('you', 0x00, 'YOU'), ('got', 0x01, 'GOT'), ('through', 0x02, 'THROUGH'), ('time', 0x03, 'TIME'), ('ring', 0x04, 'RING'),
  ('secret', 0x05, 'SECRET'), ('bonus', 0x06, 'BONUS'), ('total', 0x07, 'TOTAL'), ('score', 0x08, 'SCORE'), ('up', 0x09, 'UP!'),
  ('player', 0x0a, 'PLAYER'), ('miss', 0x0b, 'MISS'), ('botanic_base', 0x0c, 'BOTANIC BASE'), ('speed_slider', 0x0d, 'SPEED SLIDER'),
  ('amazing_arena', 0x0e, 'AMAZING ARENA'), ('techno_tower', 0x0f, 'TECHNO TOWER'), ('marina_madness', 0x10, 'MARINA MADNESS'),
  ('lv1', 0x11, 'Lv1'), ('lv2', 0x12, 'Lv2'), ('lv3', 0x13, 'Lv3'), ('lv4', 0x14, 'Lv4'), ('lv5', 0x15, 'Lv5'),
  ('start', 0x16, 'START'), ('the', 0x17, 'THE'), ('clock', 0x18, 'CLOCK!'), ('to_y', 0x19, 'TO'), ('next_y', 0x1a, 'NEXT'),
  ('level_y', 0x1b, 'LEVEL!'), ('go', 0x1c, 'GO'), ('for', 0x1d, 'FOR'), ('goal', 0x1e, 'GOAL!'), ('get', 0x1f, 'GET'),
  ('enemies', 0x20, 'ENEMIES!'), ('score_y', 0x21, 'SCORE'), ('points', 0x22, 'POINTS'), ('finish', 0x23, 'FINISH'),
  ('its', 0x24, "IT'S"), ('a', 0x25, 'A'), ('new', 0x26, 'NEW'), ('record', 0x27, 'RECORD!'),
  ('to_w', 0x28, 'TO'), ('next_w', 0x29, 'NEXT'), ('level_w', 0x2a, 'LEVEL!'), ('rings', 0x2e, 'RINGS')]
for k, f, en in RES:
    yellow = 0x16 <= f <= 0x27 and f != 0x23
    big = f in (0x0c, 0x0d, 0x0e, 0x0f, 0x10)
    seen = f <= 0x07 or f in (0x0c, 0x11)
    X.append(('res_' + k, ['results (seen)' if seen else 'results / level messages (not seen on screen)'], 0x4a, f, en, 'scenes/results3/sheets',
              ('yellow with dark shading' if yellow else 'white/grey with dark shading') + (', 23 px tall' if big else ', 14-15 px tall'),
              'one word per sprite; phrases (YOU GOT THROUGH, TIME BONUS, IT\'S A NEW RECORD!, START THE CLOCK!, ...) are built by the game from several word sprites at fixed positions'))

X += [
 ('goal_clear', ['level end (goal sign)'], 0x23, 0x06, 'CLEAR', 'scenes/results3/sheets', 'rainbow 3D letters on the goal signboard', 'whole picture; the sign spins (0x05 / 0x07 are its edge and back)'),
 ('aa_no_clear', ['Amazing Arena'], 0x3d, 0x03, '·NO CLEAR·', 'z2/sheets', 'yellow letters with red outline on a dark plate, ~20 px', 'whole picture'),
 ('aa_challenge_again', ['Amazing Arena'], 0x29, 0x23, '◀CHALLENGE AGAIN!!▶', 'z2/sheets', 'yellow 8 px letters with dark outline, arrows at both ends', 'whole phrase, one sprite (128x10)'),
 ('obj_lock_on', ['Techno Tower (target object)'], 0x2d, 0x02, 'LOCK ON', 'tt1/sheets', 'tiny yellow letters (2 lines, ~5 px) above a target reticle', 'whole picture 20x28'),
 ('bonus_500pts', ['bonus stage'], 0x26, 0x01, '500 PTS.', 'z9/sheets', 'white/yellow on orange block', 'whole block picture'),
 ('bonus_exit_1', ['bonus stage'], 0x26, 0x1a, 'EXIT', 'z9/sheets', 'orange letters on a round red button', 'whole picture; three colour variants 1a-1c'),
 ('bonus_exit_2', ['bonus stage'], 0x26, 0x1b, 'EXIT', 'z9/sheets', 'yellow letters on a green button', 'whole picture'),
 ('bonus_exit_3', ['bonus stage'], 0x26, 0x1c, 'EXIT', 'z9/sheets', 'white letters on a green button', 'whole picture'),
 ('bonus_up', ['bonus stage'], 0x26, 0x20, 'UP', 'z9/sheets', 'white letters on a blue/orange button', 'whole picture'),
 ('bonus_down', ['bonus stage'], 0x26, 0x21, 'DOWN', 'z9/sheets', 'white letters on a blue/orange button', 'whole picture'),
]
for k, f, en in [('time', 0x00, 'TIME'), ('course', 0x01, 'COURSE'), ('out', 0x02, 'OUT'), ('got_pts', 0x03, 'GOT .... pts!'),
                 ('bad', 0x04, 'BAD!'), ('too', 0x05, 'TOO'), ('coooool', 0x06, 'COOOOL'), ('next', 0x07, 'NEXT'), ('excl', 0x08, '!'),
                 ('to_go', 0x09, 'TO  GO'), ('spheres', 0x0a, 'SPHERES'), ('blue', 0x0b, 'BLUE'), ('get', 0x0c, 'GET')]:
    X.append(('sp_' + k, ['special stage'], 0x4d, f, en, 'z10/sheets', 'white with grey shading, 15 px (drawn scaled up in the tube)',
              'one word per sprite; "GET nn BLUE SPHERES TO GO" etc. are built from word sprites and drawn scaled; numbers come from bank 13'))
X += [
 ('lobby_exit_sign', ['World Entrance (lobby)'], 0x59, 0x00, 'EXIT', 'lobby2/sheets', 'big pale letters with dark outline on a yellow arrow sign', 'whole picture (56x48)'),
 ('lobby_play_sign', ['World Entrance (lobby)'], 0x59, 0x01, 'PLAY', 'lobby2/sheets', 'as lobby_exit_sign', 'whole picture (56x50)'),
 ('lobby_catcher', ['World Entrance (Combi Catcher)'], 0x58, 0x00, 'COMBI / CATCHER (alternating)', None, 'sign on top of the Combi Catcher machine; ~8 px letters',
  'one picture with the machine (60x82). The two words are drawn over each other in different palette indices (COMBI in 0x6C/0x6D, CATCHER in 0x6E) and palette cycling shows one at a time; a replacement must keep that scheme (two words in two index sets in the same 46x8 area). Crop is from the dump (the sheet was exported while the colour was faded out)'),
 ('lobby_attraction_info', ['World Entrance (attraction board)'], 0x5e, 0x00, 'NEWTROGIC HIGH ZONE / ATTRACTION INFORMATION', 'lobby2/sheets',
  'blue/white top line, orange bottom two lines on a panel', 'whole picture 92x46'),
 ('lobby_clear', ['World Entrance (attraction board)'], 0x5e, 0x01, 'CLEAR', 'lobby2/sheets', 'tiny grey letters, 7 px', 'whole word'),
 ('lobby_level', ['World Entrance (attraction board)'], 0x5e, 0x02, 'LEVEL', 'lobby2/sheets', 'tiny grey letters, 5 px', 'whole word; digits 1-5 are 5e_03..07'),
 ('debug_test', ['debug (low priority)'], 0x24, 0x1a, 'Test', 'tt1/sheets', 'yellow hand-drawn letters', 'debug graphic'),
 ('debug_skull', ['debug (low priority)'], 0x24, 0x19, 'skull with small text', 'tt1/sheets', 'yellow tiny text under a skull', 'debug graphic'),
]


def ink_bbox(img_idx):
    a = np.asarray(img_idx)
    ys, xs = np.nonzero(a)
    if len(xs) == 0:
        return None
    return [int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)]


def tp(im):
    """Index 0 (transparent) shown as dark grey, for review."""
    a = np.asarray(im)
    r = np.asarray(im.convert('RGB')).copy()
    r[a == 0] = (48, 48, 56)
    return Image.fromarray(r)


entries = []
crops = {}
for iid, scenes, bank, frame, en, sd, style, how in X:
    if sd is None:
        src = W + 'lobby2/dump/32x_%02x_%02x.png' % (bank, frame)
        im = Image.open(src)
        box = [im.width, im.height]
        work = src
    else:
        fr = parse(W + sd + '/32x_%02x.txt' % bank)
        x, y, w, h = fr[frame]
        sheet = Image.open(W + sd + '/32x_%02x.png' % bank)
        im = sheet.crop((x, y, x + w, y + h))
        box = [w, h]
        work = W + sd + '/32x_%02x.png' % bank
    c = tp(im).resize((im.width * SCALE, im.height * SCALE), Image.NEAREST)
    crops[iid] = c
    fn = 'sheets/32x_%02x_%02x.png' % (bank, frame)
    c.save(os.path.join(OUT, fn))
    entries.append(dict(id=iid, scene=scenes, kind='32x', bank='%02x' % bank, frame='%02x' % frame,
                        replace_with='32x_%02x_%02x.png (or the cell in sheet 32x_%02x.png)' % (bank, frame, bank),
                        en=en, size_px=box, ink_px=ink_bbox(im), style=style, drawing=how, letter_font=False,
                        work_file=work, review_crop=fn))

# ---- Mega Drive tile items ----------------------------------------------------
md = json.load(open(W + 'md_items.json'))
font16 = json.load(open(W + 'font8x16.json'))
f16 = set(h for v in font16.values() for h in v)
font8 = json.load(open(W + 'font8x8.json'))
for it in md:
    sc = it['scene']
    iid = it['id']
    x0, y0, x1, y1 = it['box']
    shot = Image.open(W + 'scenes/%s/md.png' % sc).convert('RGB')
    c = shot.crop((x0, y0, x1, y1))
    c = c.resize((c.width * SCALE, c.height * SCALE), Image.NEAREST)
    crops[iid] = c
    fn = 'sheets/md_%s.png' % iid
    c.save(os.path.join(OUT, fn))
    tiles = it['tiles']
    hs = []
    for t in tiles:
        if t['hash'] not in hs:
            hs.append(t['hash'])
    if sc in ('menu', 'options'):
        style = '8x8 tile letter font, white (selected) / grey (others), 7 px glyphs'
        kind_font = 'font8x8'
    elif iid in ('tr_zone_name', 'psel_player_select', 'psel_char_name'):
        style = '8x16 game font (MENU_ART.md): yellow capitals shaded brown, black drop shadow, 15 px'
        kind_font = 'font8x16'
    elif sc == 'soundtest':
        style = 'yellow 16 px tile letters with white digits (FM/PSG/PWM labels and the SOUND TEST bar)'
        kind_font = 'letters'
    elif iid in ('ps_1p_small', 'ps_cpu'):
        style = 'small 8 px tile letters between arrows (1P yellow, CPU pink)'
        kind_font = None
    elif iid in ('ps_1p_big', 'ps_2p_big'):
        style = '16 px tile lettering, yellow/white'
        kind_font = None
    elif iid in ('dl_new', 'dl_no_save'):
        style = '16-24 px tile lettering (NEW green, NO pink + SAVE yellow), black shadow'
        kind_font = None
    else:
        style = 'banner lettering: big yellow letters (brown = inactive) with dark shading and black shadow, 3-4 tiles tall'
        kind_font = None
    if tiles:
        bx = [min(t['x'] for t in tiles), min(t['y'] for t in tiles), max(t['x'] for t in tiles) + 8, max(t['y'] for t in tiles) + 8]
    else:
        bx = [x0, y0, x1, y1]
    how = {
        'font8x8': 'REUSABLE LETTER FONT: each letter is one 8x8 tile, shared by every string on the title menu and OPTIONS; strings come from a table (ROM 0x6C0E for OPTIONS, letters stored as ASCII - 0x20); cannot be translated word by word with tile replacement',
        'font8x16': 'REUSABLE LETTER FONT: the 8x16 game font (sprites, 2 tiles per glyph, ROM 0x2C4B20), written by code from ASCII strings (character names at ROM 0x3267A..); cannot be translated word by word',
        'letters': 'tile letters reused between the labels (F, M, P, S, G and digits); debug-style screen, low priority',
        None: 'word drawn as a block of tiles on a plane; the tiles of identical letter runs are shared between banners (PLAY in PLAY / PLAYER SELECT, DATA in DATA LOAD / DATA n, ELE in DELETE / SELECT); see README',
    }[kind_font]
    e = dict(id=iid, scene=[sc], kind='md', en=it['en'], tile_hashes=hs, tile_count=len(tiles),
             screen_box=bx, size_px=[bx[2] - bx[0], bx[3] - bx[1]], style=style, drawing=how,
             letter_font=kind_font in ('font8x8', 'font8x16', 'letters'),
             work_file=W + 'scenes/%s/ (full.png, md.png = Mega Drive layer only, dump/ = md_<hash>.png tiles)' % sc,
             review_crop=fn,
             hash_note='hashes found by matching the dumped tiles against the Mega Drive layer screenshot; a box can include a few background tiles')
    if kind_font == 'font8x16':
        e['tiles_in_8x16_font'] = sum(1 for h in hs if h in f16)
    entries.append(e)

json.dump(dict(game="Knuckles' Chaotix (32X) as run by Knuckles' Chaotix Recompiled",
               count=len(entries),
               fonts=dict(
                   game_font_8x16=dict(source='Nemesis at ROM 0x2C4B20, 94 tiles, palette ROM 0x03E8CA line 0; glyph -> [top tile hash, bottom tile hash]',
                                       glyphs=font16),
                   menu_font_8x8=dict(source='title menu and OPTIONS screen, read from the screen; glyph -> tile hash (letters seen only)',
                                      glyphs=font8)),
               entries=entries),
          open(os.path.join(OUT, 'inventory.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)


# ---- contact sheets per group ------------------------------------------------
def contact(name, ids, maxw=1400):
    items = [(i, crops[i]) for i in ids]
    x = y = 0
    rowh = 0
    pos = []
    for i, c in items:
        w = max(c.width, len(i) * 6 + 4)
        if x + w > maxw and x:
            x = 0
            y += rowh + 16
            rowh = 0
        pos.append((x, y))
        x += w + 8
        rowh = max(rowh, c.height)
    M = Image.new('RGB', (maxw, y + rowh + 16), (20, 20, 24))
    d = ImageDraw.Draw(M)
    for (i, c), (x, y) in zip(items, pos):
        d.text((x, y), i, fill=(255, 255, 0))
        M.paste(c, (x, y + 14))
    M.save(os.path.join(SHEETS, 'contact_%s.png' % name))


ids = [e['id'] for e in entries]
contact('title_hud_card', [i for i in ids if i.startswith(('title_', 'hud_', 'card_'))])
contact('results', [i for i in ids if i.startswith(('res_', 'goal_'))])
contact('stages_lobby', [i for i in ids if i.startswith(('aa_', 'obj_', 'bonus_', 'sp_', 'lobby_', 'debug_'))])
contact('md_menus', [e['id'] for e in entries if e['kind'] == 'md'], 1800)
print(len(entries), 'entries;', sum(1 for e in entries if e['kind'] == '32x'), '32x,', sum(1 for e in entries if e['kind'] == 'md'), 'md')
