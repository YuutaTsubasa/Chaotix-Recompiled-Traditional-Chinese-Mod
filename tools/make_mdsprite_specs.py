"""One-off: write text/mdsprite/*.json (phase 4, Mega Drive sprite text).

    python tools/make_mdsprite_specs.py

The banners, PLAY STYLE's CPU and the SAVEMODE box take their sprite lines
from the game's sprite dumps in work/p4 (tools/cap_sprites.sh); the text in
the 8x16 game font (zone names, character names, PLAYER / COMBI SELECT,
SOUND TEST) is put together from the font's tile hashes
(inventory/inventory.json): one 1x2 sprite per character, 8 px apart, a
space leaving 8 px, which is how the game writes it (checked against the
dumps for every string that was reached, see `check` below).
Overwrites the specs; run it only to start again.

Captures (tools/cap_sprites.sh NAME LASTFRAME SHOTS ARGS), base presses
T = --press 1800:start:6 --press 1900:down:4 --press 1960:start:6 (TRAINING),
D = --press 1800:start:6 --press 1950:start:6 (DATA LOAD),
O = --press 1800:start:6 --press 1900:down:4 --press 1930:down:4 --press 1980:start:6 --press 2050:down:4 --press 2200:start:6 (SOUND TEST):
  dl     2600 2000,2100,2200,2300,2499  D
  b      3000 2300,...,2999  D --press 2150:down:6 --press 2250:start:6       (SAVEMODE)
  tr     2600 2050,...,2599  T --press 2250:right:6 --press 2350:down:6       (TRAINING, EXIT chosen)
  ps     3000 2300,...,2999  T --press 2250:start:6                           (PLAY STYLE)
  ps2    2800 2340,...,2799  (ps) --press 2350:right:6 --press 2450:right:6 --press 2550:down:6 --press 2650:left:6
  psel   3000 2400,...,2999  (ps) --press 2350:start:6 --press 2550:right:6 ... (PLAYER SELECT)
  psel2  3200 2600,...,3199  (ps) --press 2350:start:6 --press 2550:start:6 --press 2800:down:6 (COMBI SELECT)
  st_all 4200 2300,2430,...  O then --press F:right:4 every 40 frames from 2400 (every title)
  really 2700 2300,...,2699  D --sram work/p4/t2.srm --press 2150:down:6 --press 2250:right:6 --press 2350:start:6 --press 2500:down:6
  dlt2   2500 2100,...,2499  D --sram work/p4/t2.srm --press 2150:down:6 --press 2250:down:6 --press 2350:down:6
(t2.srm: tools/make_sram.py, a save whose slots have cleared every zone.)
BOMB and HEAVY (hidden characters) and the zones other than ISOLATED ISLAND
(TRAINING lists only the zones a save has reached; a poked save did not
change that) were not seen: their patterns follow the font rule above.
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_sprites as B  # noqa: E402
import mdspr  # noqa: E402
import sprlib as L  # noqa: E402

OUT = os.path.join(L.ROOT, "text", "mdsprite")
P4 = os.path.join(L.ROOT, "work", "p4")
INV = json.load(open(os.path.join(L.ROOT, "inventory", "inventory.json"), encoding="utf8"))
GLYPH = INV["fonts"]["game_font_8x16"]["glyphs"]
CHAR = {"'": "rsquo", "=": "rsquo"}

# palette lines as dumped (tile PNGs), for the previews only
LINE0 = [[0, 0, 0], [255, 255, 255], [219, 146, 219], [109, 36, 109], [73, 0, 73], [0, 0, 0], [0, 0, 219], [36, 73, 255],
         [73, 146, 255], [182, 255, 255], [255, 219, 0], [182, 73, 0], [73, 0, 0], [0, 73, 0], [0, 146, 0], [0, 255, 0]]
LINE3 = LINE0[:13] + [[0, 0, 0]] * 3


def dump(name, n):
    return mdspr.Dump(os.path.join(P4, name, "dump", "Text", "sprites_%06d.txt" % n))


def group(name, n, gid):
    d = dump(name, n)
    g = d.groups[gid]
    return dict(source="work/p4/%s/dump/Text/sprites_%06d.txt group %d (screen %d,%d, palette line %d)"
                % (name, n, gid, g["x"], g["y"], g["pal"]),
                sprites=[mdspr.sprite_line(s) for s in g["sprites"]])


def font_sprites(text):
    out, x = [], 0
    for c in text:
        if c != " ":
            top, bot = GLYPH[CHAR.get(c, c)]
            out.append("sprite %d 0 1x2 %s %s" % (x, top, bot))
        x += 8
    return out


def font_text(text, where):
    return dict(source="8x16 game font tiles (inventory.json), %r, %s" % (text, where), sprites=font_sprites(text))


def check(text, name, n, y):
    """The font pattern of `text` is there in the dump, on line y (the
    dump's groups split at gaps wider than 8 px, so all of the line's
    sprites are searched)."""
    d = dump(name, n)
    have = set()
    for g in d.groups.values():
        if g["y"] == y:
            have |= {(s["dx"] + g["x"], " ".join(s["tiles"])) for s in g["sprites"] if s["w"] == 1 and s["h"] == 2}
    want = [(int(w.split()[1]), " ".join(w.split()[4:])) for w in font_sprites(text)]
    for x, t in have:
        if t == want[0][1] and all((x + dx, tt) in have for dx, tt in want):
            return
    raise SystemExit("font pattern %r not found in %s/%d" % (text, name, n))


NOTO = "NotoSansTC-Black.ttf"


def banner_big(zh, **kw):
    # the top banners: letters 22 px with a 2 px black drop shadow
    return dict(align="center", layers=[dict(font=NOTO, size=22, thresh=140, gap=1, zh=zh, style="banner", align="center", y=0)],
                preview_palette=LINE0, **kw)


def banner_small(zh, **kw):
    # the bottom banners (PLAY, DELETE, EXIT, PLAYER SELECT): 16 px letters
    return dict(align="center", layers=[dict(font=NOTO, size=17, thresh=140, gap=1, zh=zh, style="banner", align="center", y=0)],
                preview_palette=LINE0, **kw)


def font16(zh, align="center", region=None, pal=LINE0, **kw):
    # text the game writes in its 8x16 font: 15 px glyphs and a 1 px drop
    # shadow in the font's own entries (10 yellow, 5 black)
    # 15 px of ink + the shadow = the 16 px line; a few glyphs (the dot of
    # 音, 午's top) need a higher threshold for that
    lay = dict(font=NOTO, size=16, thresh=140, gap=1, zh=zh, style="font16", align=align, y=0)
    while B.text_mask(lay).shape[0] > 15:
        lay["thresh"] += 10
    if region:
        lay["region"] = region
    return dict(align="left", layers=[lay], preview_palette=pal, **kw)


S = {}
# --- banners ---------------------------------------------------------------
S["banner_data_load"] = dict(en="DATA LOAD (banner)", zh="讀取存檔", screen="DATA LOAD", **group("dl", 2023, 1), **banner_big("讀取存檔"))
S["banner_play"] = dict(en="PLAY (banner)", zh="開始", screen="DATA LOAD, TRAINING", **group("dl", 2023, 10), **banner_small("開始"))
S["banner_delete"] = dict(en="DELETE (banner)", zh="刪除", screen="DATA LOAD", **group("dl", 2023, 11), **banner_small("刪除"))
S["banner_training"] = dict(en="TRAINING (banner)", zh="練習模式", screen="TRAINING", **group("tr", 2043, 1), **banner_big("練習模式"))
S["banner_exit"] = dict(en="EXIT (menu) banner", zh="離開", screen="TRAINING", **group("tr", 2043, 14), **banner_small("離開"))
S["banner_play_style"] = dict(en="PLAY STYLE (banner)", zh="遊玩方式", screen="PLAY STYLE", **group("ps", 2300, 1), **banner_big("遊玩方式"))
S["banner_player_select"] = dict(en="PLAYER SELECT (banner)", zh="選擇角色", screen="PLAY STYLE", **group("ps", 2300, 14), **banner_small("選擇角色"))

# The top banners slide in and out sideways; Knuckles' Chaotix Recompiled
# 0.7.1 matches a group that is partly off the screen (the sprites left out
# of the list are taken as there), so the whole banner's pattern covers the
# slide and no patterns for parts of a banner are needed.
for key in ("banner_data_load", "banner_training", "banner_play_style"):
    S[key]["layers"][0]["region"] = [0, 128]

# --- PLAY STYLE: the partner's CPU selector, arrows included -----------------
ARROW_L = ["...#", "..##", ".###", "####", ".###", "..##", "...#"]
ARROW_R = [r[::-1] for r in ARROW_L]
# 電腦 needs the whole 16 px line (at the English letters' 7 px it is a blot)
S["ps_cpu"] = dict(en="CPU (PLAY STYLE partner)", zh="電腦", screen="PLAY STYLE", **group("ps", 2300, 10), align="left",
                   preview_palette=LINE0, size=[50, 16], offset=[0, -2],
                   layers=[dict(art=ARROW_L, style="small_pink", x=1, y=4),
                           dict(font=NOTO, size=16, thresh=140, gap=1, zh="電腦", style="small_pink", align="center", region=[6, 43], y=0),
                           dict(art=ARROW_R, style="small_pink", x=44, y=4)])

# --- SAVEMODE box (two sprite groups: the top with SAVEMODE and AUTO, the
# bottom with MANUAL); the box is drawn here too, since the image replaces
# the sprites, panel included: rects in box coordinates, 80x48 + shadow
BOX_RECTS = [[0, 0, 80, 48, 8], [0, 0, 80, 4, 1], [0, 4, 76, 5, 9], [76, 4, 80, 5, 8], [0, 5, 4, 42, 9],
             [76, 5, 80, 43, 7], [0, 42, 4, 43, 8], [0, 43, 80, 44, 7], [0, 44, 80, 48, 6], [4, 44, 5, 48, 7], [75, 44, 76, 48, 7],
             [72, 0, 73, 4, 9], [74, 0, 75, 4, 9], [75, 1, 77, 4, 9], [77, 2, 78, 4, 9], [78, 2, 79, 4, 8]]
BOX_HOLES = [(0, 0), (1, 0), (2, 0), (3, 0), (0, 1), (1, 1), (0, 2), (0, 3), (76, 0), (77, 0), (78, 0), (79, 0), (78, 1), (79, 1),
             (79, 2), (79, 3), (0, 44), (0, 45), (1, 46), (0, 46), (0, 47), (1, 47), (2, 47), (3, 47), (76, 47), (77, 47),
             (78, 47), (79, 47), (79, 46), (78, 46), (79, 45), (79, 44)]
BOX_CHECKER = [[80, 8, 88, 56, 5, 0], [8, 48, 80, 56, 5, 0]]


def box_part(y0, y1):
    """The box's rects, checker and corner pixels between lines y0 and y1, moved up by y0."""
    clip = lambda r: [r[0], max(r[1], y0) - y0, r[2], min(r[3], y1) - y0] + r[4:]
    rects = [clip(r) for r in BOX_RECTS if r[1] < y1 and r[3] > y0]
    chk = [clip(r) for r in BOX_CHECKER if r[1] < y1 and r[3] > y0]
    for c in chk:  # keep the dither's phase
        if (y0 % 2):
            c[5] ^= 1
    px = [[x, y - y0, 0] for x, y in BOX_HOLES if y0 <= y < y1]
    return dict(rects=rects, checker=chk, pixels=px)


S["savemode_top"] = dict(en="SAVEMODE, AUTO (save mode): save slot box, top", zh="存檔方式 / 自動", screen="DATA LOAD (NEW slot chosen)",
                         **group("b", 2257, 4), align="left", preview_palette=LINE0, **box_part(0, 32),
                         layers=[dict(font=NOTO, size=14, thresh=140, gap=1, zh="存檔方式", style="box_title", align="center", region=[4, 76], y=6),
                                 dict(font="fusion8", zh="自動", gap=1, style="box_pink", x=24, y=22)])
S["savemode_bottom"] = dict(en="MANUAL (save mode): save slot box, bottom", zh="手動", screen="DATA LOAD (NEW slot chosen)",
                            **group("b", 2257, 8), align="left", preview_palette=LINE0, **box_part(32, 56),
                            layers=[dict(font="fusion8", zh="手動", gap=1, style="box_green", x=24, y=0)])

# the DELETE confirmation (DELETE on a used slot): the same box
S["really_top"] = dict(en="REALLY? (delete confirmation), NO (delete confirmation): box, top", zh="確定嗎？ / 否", screen="DATA LOAD (DELETE chosen)",
                       **group("really", 2357, 4), align="left", preview_palette=LINE0, **box_part(0, 32),
                       layers=[dict(font=NOTO, size=14, thresh=140, gap=1, zh="確定嗎？", style="box_title", align="center", region=[4, 76], y=6),
                               dict(font="fusion8", zh="否", gap=1, style="box_pink", x=24, y=22)])
S["really_bottom"] = dict(en="YES (delete confirmation): box, bottom", zh="是", screen="DATA LOAD (DELETE chosen)",
                          **group("really", 2357, 8), align="left", preview_palette=LINE0, **box_part(32, 56),
                          layers=[dict(font="fusion8", zh="是", gap=1, style="box_green", x=24, y=0)])
# the fifth CLEAR mark of a used slot is a sprite (the other four are plane
# text, text/mdtext/dl_clear.json): drawn the same
S["dl_clear5"] = dict(en="CLEAR (save slot, fifth zone)", zh="過關", screen="DATA LOAD (used slot)", **group("really", 2357, 9),
                      align="left", preview_palette=LINE0,
                      layers=[dict(font=NOTO, size=16, thresh=140, gap=1, zh="過關", style="slot_yellow", align="center", region=[0, 38], y=1)])

# --- game font text ----------------------------------------------------------
ZONES = [("ISOLATED ISLAND", "孤立之島"), ("BOTANIC BASE", "植物基地"), ("SPEED SLIDER", "極速滑道"), ("AMAZING ARENA", "驚奇競技場"),
         ("TECHNO TOWER", "科技之塔"), ("MARINA MADNESS", "瘋狂海港"), ("WORLD ENTRANCE", "世界入口")]
check("ISOLATED ISLAND", "tr", 2043, y=104)
for en, zh in ZONES:
    S["zone_" + en.lower().replace(" ", "_")] = dict(en=en + " (TRAINING zone list)", zh=zh, screen="TRAINING",
                                                     **font_text(en, "TRAINING's zone panel"), **font16(zh, align="left", region=[2, 200]))
NAMES = [("KNUCKLES THE ECHIDNA", "納克魯斯"), ("MIGHTY THE ARMADILLO", "麥堤"), ("ESPIO THE CHAMELEON", "艾斯皮歐"),
         ("CHARMY BEE", "查米"), ("VECTOR THE CROCODILE", "貝庫特"), ("BOMB THE MECHANIC", "炸彈"), ("HEAVY THE MECHANIC", "海威")]
check("KNUCKLES THE ECHIDNA", "psel", 2408, y=108)
check("MIGHTY THE ARMADILLO", "psel2", 2539, y=108)
check("ESPIO THE CHAMELEON", "psel2", 2788, y=108)
for en, zh in NAMES:
    S["name_" + en.split()[0].lower()] = dict(en=en + " (character select)", zh=zh, screen="PLAYER SELECT, COMBI SELECT",
                                              **font_text(en, "centred on the screen"), **font16(zh, region=None))
    S["name_" + en.split()[0].lower()]["align"] = "center"
check("PLAYER  SELECT", "psel", 2408, y=16)
S["head_player_select"] = dict(en="PLAYER SELECT (header)", zh="選擇角色", screen="PLAYER SELECT",
                               **font_text("PLAYER  SELECT", "header"), **font16("選擇角色"))
S["head_player_select"]["align"] = "center"
check("COMBI SELECT", "psel2", 2539, y=16)
S["head_combi_select"] = dict(en="COMBI SELECT (header)", zh="選擇搭檔", screen="COMBI SELECT",
                              **font_text("COMBI SELECT", "header"), **font16("選擇搭檔"))
S["head_combi_select"]["align"] = "center"

# SOUND TEST: the header and S.E. (ROM 0x22734C, all at x 36). The song
# titles stay in English (user decision 2026-10-23): no patterns for them;
# the list is kept to find the S.E. capture and to check the font rule.
TITLES = ['DOOR INTO SUMMER', 'ELECTORIA', 'SPEED OF SOUND', 'SEASCAPE', 'MIDNIGHT GREENHOUSE', 'NEW MOON',
          'LABYRINTH', 'TRIAL AND ERROR', "WALKIN'", 'HYPER-HYPER', 'EVENING STAR', 'MOONRISE', 'OVERTURE',
          'THIS HORIZON', 'TAKE OFF', 'COMBINATION', 'TAKE A NAP', 'SURGING POWER', 'MECHANICAL DANCE', 'TUBE PANIC',
          'CRYSTAL NIGHTMARE', "CHILD'S SONG", 'SODA POP', 'PENDULUM', 'SILVER SCREEN', 'TACHY TOUCH',
          'CHAOTIC WORLD', 'SURPRISE!', 'NICE MEETING YOU', 'HAVE A HAPPY DAY', 'REACH THE GOAL', 'HIGH FIVE',
          'DECISION', 'FROM PARTY TO PARTY', 'HAVE SOME FUN', 'ORIENTAL LEGEND', 'STEEL HEART', 'TRIBUTE',
          'DESTRUCTIVE POWER', 'JUST ANOTHER DAY', 'DECISION 2ND']
shots = sorted(int(os.path.basename(f)[8:14]) for f in glob.glob(os.path.join(P4, "st_all", "dump", "Text", "sprites_*.txt")))
check("--- SOUND  TEST ---", "st_all", shots[0], y=192)
for en, n in zip(TITLES, shots[1:]):
    check(en, "st_all", n, y=192)
check("S.E.", "st_all", shots[len(TITLES) + 1], y=192)
S["st_header"] = dict(en="--- SOUND TEST --- (SOUND TEST title bar)", zh="音效測試", screen="SOUND TEST",
                      **font_text("--- SOUND  TEST ---", "title bar"), **font16("音效測試", pal=LINE3))
S["st_header"]["align"] = "center"
# S.E. nn (the sound effects): only S.E., the number stays
S["st_se"] = dict(en="S.E. (sound effect nn)", zh="音效", screen="SOUND TEST", **font_text("S.E.", "title bar"),
                  **font16("音效", align="left", region=[0, 40], pal=LINE3))
S["st_se"]["layers"][0]["size"] = 15

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for old in glob.glob(os.path.join(OUT, "[a-z0-9]*.json")):
        os.remove(old)
    for k, v in S.items():
        with open(os.path.join(OUT, k + ".json"), "w", encoding="utf8", newline="\n") as f:
            json.dump(v, f, ensure_ascii=False, indent=1)
    print(len(S))
