"""Write text/sprites/*.json (the per-sprite specs) and _styles.json.

The specs are the data build_sprites.py draws from; this script is how they
were authored, so a change of layout or style is made here and re-run (or in
the JSON directly, for a one-off). Every Chinese string here must use the
glossary's terms (text/glossary.json); tools/check_text.py verifies that.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "text", "sprites")

TTF_BIG = "GlowSansTC-Condensed-Heavy.otf"     # OFL 1.1, Glow Sans TC (welai)
TTF_BLOCK = "NotoSansTC-Black.ttf"              # OFL 1.1, Noto Sans TC

S3 = [[1, 0], [0, 1], [1, 1]]
# 14-15 px words: Fusion Pixel at 2x was tried first, but dense characters
# (關, 戰, 體, 錄) were illegible as 2x of an 8 px design; Noto Sans TC Black
# rendered 1-bit at 15 px keeps them readable with the game's 2 px strokes.
WORD = {"font": "NotoSansTC-Black.ttf", "size": 15, "thresh": 140, "gap": 1}  # the game's drop shadow: right, below, corner

STYLES = {
    # HUD (bank 13): white top, yellow, orange, dark orange; black shadow
    "hud_yellow": {"fill": {"bands": [[0, 0x05], [2, 0x0a], [8, 0x0b], [11, 0x0c]]},
                   "shadow": {"idx": 0x01, "offsets": S3}},
    "hud_red": {"fill": {"bands": [[0, 0x0d], [1, 0x10], [12, 0x0f], [13, 0x0e]]},
                "shadow": {"idx": 0x01, "offsets": S3}},
    "hud_bubble": {"fill": 0x01},
    # results (bank 4a): white words, black shadow; yellow messages, grey shadow
    "res_white": {"fill": {"bands": [[0, 0x05], [12, 0x04]]},
                  "shadow": {"idx": 0x01, "offsets": S3}},
    "res_yellow": {"fill": {"bands": [[0, 0x0a], [11, 0x0b], [13, 0x0c]]},
                   "shadow": {"idx": 0x14, "offsets": S3}},
    "res_zone": {"fill": 0x05, "edge": {"br": 0x04}, "outline": {"idx": 0x02, "mode": "8"}},
    # special stage (bank 4d): white, black shadow
    "sp_white": {"fill": {"bands": [[0, 0x05], [12, 0x04]]},
                 "shadow": {"idx": 0x01, "offsets": S3}},
    # title card (bank 40)
    "card_small": {"fill": 0x4b},
    "card_zone": {"fill": 0x52, "edge": {"tl": 0x51, "br": 0x54}, "outline": {"idx": 0x56, "mode": "8"}},
    "card_cast": {"fill": 0x4a},
    # title (bank 55): tagline colours per column (colmap), PUSH START
    "title_tag": {"fill": 0x7f},
    "title_blue": {"fill": 0x29, "shadow": {"idx": 0x56, "offsets": [[-1, 0], [-1, 1], [0, 1]]}},
    "title_push": {"fill": 0x1e, "shadow": {"idx": 0x1a, "offsets": [[1, 0], [0, 1], [1, 1]]}},
    # goal sign (bank 23)
    "goal_yellow": {"fill": {"bands": [[0, 0x0a], [12, 0x0b], [16, 0x0c]]}, "edge": {"tl": 0x05},
                    "outline": {"idx": 0x0f, "mode": "8"}},
    "goal_blue": {"fill": 0x06, "edge": {"tl": 0x05, "br": 0x08}, "outline": {"idx": 0x09, "mode": "8"}},
    # Amazing Arena (3d, 29), Techno Tower (2d)
    "aa_noclear": {"fill": {"bands": [[0, 0x05], [3, 0x0a], [12, 0x0b], [17, 0x0c]]},
                   "outline": {"idx": 0x0d, "mode": "8"}},
    "aa_again": {"fill": 0x7e, "outline": {"idx": 0x60, "mode": "8"}},
    "tt_lock": {"fill": 0x4c, "shadow": {"idx": 0x42, "offsets": S3}},
    # bonus stage blocks (26)
    "bonus_pts": {"fill": 0x05},
    "bonus_exit1": {"fill": 0x0c, "outline": {"idx": 0x01, "mode": "8"}},
    "bonus_exit2": {"fill": 0x0a, "outline": {"idx": 0x02, "mode": "8"}},
    "bonus_exit3": {"fill": 0x05, "outline": {"idx": 0x03, "mode": "8"}},
    "bonus_up": {"fill": {"bands": [[0, 0x09], [2, 0x08], [3, 0x07], [4, 0x06], [7, 0x07], [8, 0x08], [9, 0x09]]},
                 "outline": {"idx": 0x01, "mode": "8"}},
    "bonus_down": {"fill": {"bands": [[0, 0x0d], [2, 0x0c], [3, 0x0b], [4, 0x0a], [7, 0x0b], [8, 0x0c], [9, 0x0d]]},
                   "outline": {"idx": 0x01, "mode": "8"}},
    # lobby (58, 59, 5e)
    "lobby_sign": {"fill": 0x42, "edge": {"tl": 0x43}, "shadow": {"idx": 0x3d, "offsets": [[1, 0], [1, 1]]},
                   "outline": {"idx": 0x3c, "mode": "8"}},
    "lobby_banner": {"fill": 0x09},
    "lobby_info": {"fill": {"bands": [[0, 0x05], [3, 0x0a], [8, 0x0b], [11, 0x0c]]}, "outline": {"idx": 0x0e, "mode": "8"}},
    "lobby_grey": {"fill": 0x04},
}


def hud(word, zh, style="hud_yellow", w=None, extra=None):
    d = {"en": word, "zh": zh, "layers": [dict(WORD, zh=zh, style=style, y=0, align="center")]}
    if extra:
        d.update(extra)
    return d


def res(word, zh, style="res_white", align="left", region=None, x=None, y=0):
    L = dict(WORD, zh=zh, style=style, y=y, align=align)
    if region:
        L["region"] = region
    if x is not None:
        L["x"] = x
    return {"en": word, "zh": zh, "layers": [L]}


def blank(word, note):
    return {"en": word, "zh": "", "blank": True, "why": note}


def keep(word, why):
    return {"en": word, "keep": True, "why": why}


SPECS = {}

# ---------------------------------------------------------------- HUD 13
SPECS.update({
    "13_00": hud("POINTS", "得分"),
    "13_01": hud("RINGS", "戒指"),
    "13_02": hud("RINGS (red)", "戒指", "hud_red"),
    "13_03": hud("TIME", "時間"),
    "13_04": hud("TIME (red)", "時間", "hud_red"),
    "13_05": hud("PAUSE", "暫停"),
    "13_06": keep("!", "punctuation after PAUSE; kept"),
    "13_07": hud("LIMITS", "關口"),
    "13_08": hud("LIMITS (red)", "關口", "hud_red"),
    "13_09": hud("ATTACK", "挑戰"),
    "13_0a": hud("ATTACK (red)", "挑戰", "hud_red"),
    "13_0b": hud("HURRY", "快點"),
    "13_0c": hud("UP", "！"),
    "13_25": hud("SCORE", "分數"),
    "13_3a": hud("SCORE (red)", "分數", "hud_red"),
    "13_3d": hud("LEVEL", "關卡"),
    "13_26": {"en": "HOLD! (speech bubble)", "zh": "抓住！", "canvas": "orig",
              "erase": [[2, 5, 33, 11]], "erase_idx": 0x05,
              "layers": [{"zh": "抓住！", "font": "fusion8", "scale": 1, "gap": 1, "style": "hud_bubble",
                          "y": 4, "align": "center", "region": [2, 33]}]},
    "13_40": {"en": "-DEMO-", "zh": "示範", "canvas": "orig", "erase": [[12, 0, 52, 13]],
              "layers": [dict(WORD, **{"zh": "示範", "style": "hud_yellow",
                          "y": 0, "align": "center", "region": [12, 52]})]},
})

# ---------------------------------------------------------------- title card 40
CARD = {"08": ("BOTANIC BASE", "植物基地"), "09": ("MARINA MADNESS", "瘋狂海港"),
        "0a": ("AMAZING ARENA", "驚奇競技場"), "0b": ("TECHNO TOWER", "科技之塔"),
        "0c": ("SPEED SLIDER", "極速滑道"), "10": ("ISOLATED ISLAND", "孤立之島")}
for ff, (en, zh) in CARD.items():
    SPECS["40_" + ff] = {
        "en": "NEWTROGIC HIGH ZONE / %s / CHAOTIX" % en, "zh": "紐托吉克高地／%s／卡歐提斯" % zh,
        "canvas": "orig", "erase": [[0, 1, 199, 51]],
        "layers": [
            {"zh": "紐托吉克高地", "font": "fusion8", "scale": 1, "gap": 1, "style": "card_small", "y": 4, "align": "center"},
            {"zh": zh, "font": TTF_BIG, "size": 24, "thresh": 120, "gap": 3, "style": "card_zone",
             "valign": [13, 39], "align": "center"},
            {"zh": "卡歐提斯", "font": "fusion8", "scale": 1, "gap": 1, "style": "card_small", "y": 41, "align": "center"},
        ]}
SPECS["40_07"] = {"en": "L E V E L", "zh": "關 卡", "canvas": "orig", "erase": [[1, 44, 67, 52]],
                  "layers": [{"zh": "關卡", "font": "fusion8", "scale": 1, "gap": 12, "style": "card_small",
                              "y": 45, "align": "center"}]}
SPECS["40_0f"] = keep("barcode digits", "barcode: decoration, not text to translate")
CAST = ["艾斯皮歐！！", "納克魯斯！！", "麥堤！！", "查米！！", "貝庫特！！", "海威！！", "炸彈！！"]


def cast_list():
    # 7 lines of 7 px glyphs, 7 px apart (the English lines' pitch), black on
    # the panel, with the panel's stubs redrawn to each line's width
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import sprlib
    layers, rects = [], []
    for i, z in enumerate(CAST):
        w = sprlib.fusion_text(z, gap=0).shape[1]
        y = 3 + 7 * i
        x = 8 + (56 - w) // 2
        layers.append({"zh": z, "font": "fusion8", "scale": 1, "gap": 0, "style": "card_cast", "y": y, "x": x})
        if x - 2 > 8:
            rects.append([8, y + 3, x - 2, y + 5, 0x4a])
        if x + w + 2 < 64:
            rects.append([x + w + 2, y + 3, 64, y + 5, 0x4a])
    return {"en": "ESPIO!! KNUCKLES!! MIGHTY!! CHARMY BEE!! VECTOR!! HEAVY!! BOMB!!",
            "zh": "／".join(CAST), "canvas": "orig", "erase": [[8, 2, 64, 54]], "rects": rects, "layers": layers}


# Tried (cast_list above): 7 lines of 7 px Chinese 7 px apart touch each
# other and could not be read in the game, so the cast list stays English.
SPECS["40_0d"] = keep("ESPIO!! KNUCKLES!! MIGHTY!! CHARMY BEE!! VECTOR!! HEAVY!! BOMB!!",
                      "too small: 7 lines in a 56 px panel; Chinese 7 px lines touch and are illegible")

# ---------------------------------------------------------------- results 4a
# Positions in the results screen (--sprites-log): YOU 96, GOT 128, THROUGH 160
# (y 56); TIME 72 / RING 73 / SECRET 56 then BONUS at 104; TOTAL 88.
SPECS.update({
    "4a_00": res("YOU (GOT THROUGH)", "順利過關", x=29),
    "4a_01": blank("GOT", "drawn by 4a_00 (順利過關)"),
    "4a_02": blank("THROUGH", "drawn by 4a_00 (順利過關)"),
    "4a_03": res("TIME (BONUS)", "時間", align="right", region=[0, 30]),
    "4a_04": res("RING (BONUS)", "戒指", align="right", region=[0, 29]),
    "4a_05": res("SECRET (BONUS)", "隱藏", align="right", region=[0, 46]),
    "4a_06": res("BONUS", "獎勵", x=0),
    "4a_07": res("TOTAL", "合計", align="right", region=[0, 38]),
    "4a_08": res("SCORE (UP!)", "分數", x=0),
    "4a_09": res("UP!", "提升！", x=0),
    "4a_0a": res("PLAYER (MISS)", "玩家", align="right", region=[0, 46]),
    "4a_0b": res("MISS", "失誤", x=0),
    "4a_11": keep("Lv1", "kept: Lv + digit (as the brief allows)"),
    "4a_12": keep("Lv2", "kept"), "4a_13": keep("Lv3", "kept"),
    "4a_14": keep("Lv4", "kept"), "4a_15": keep("Lv5", "kept"),
    # yellow messages: whole phrase in the first word, centred over the
    # English phrase (word widths + 8 px spaces), other words blank
    "4a_16": res("START (THE CLOCK!)", "開始計時！", style="res_yellow", align="center", region=[0, 128]),
    "4a_17": blank("THE", "drawn by 4a_16"), "4a_18": blank("CLOCK!", "drawn by 4a_16"),
    "4a_19": res("TO (NEXT LEVEL!) yellow", "前往下一關！", style="res_yellow", align="center", region=[0, 116]),
    "4a_1a": blank("NEXT", "drawn by 4a_19"), "4a_1b": blank("LEVEL!", "drawn by 4a_19"),
    "4a_1c": res("GO (FOR GOAL!)", "衝向終點！", style="res_yellow", align="center", region=[0, 96]),
    "4a_1d": blank("FOR", "drawn by 4a_1c"), "4a_1e": blank("GOAL!", "drawn by 4a_1c"),
    "4a_1f": res("GET (ENEMIES!)", "打倒", style="res_yellow", x=0),
    "4a_20": res("ENEMIES!", "敵人！", style="res_yellow", x=0),
    "4a_21": res("SCORE (POINTS) yellow", "賺取", style="res_yellow", align="right", region=[0, 38]),
    "4a_22": res("POINTS", "分數", style="res_yellow", x=0),
    "4a_23": res("FINISH", "完成！", align="center"),
    "4a_24": res("IT'S (A NEW RECORD!)", "新紀錄！", style="res_yellow", align="center", region=[0, 147]),
    "4a_25": blank("A", "drawn by 4a_24"), "4a_26": blank("NEW", "drawn by 4a_24"),
    "4a_27": blank("RECORD!", "drawn by 4a_24"),
    "4a_28": res("TO (NEXT LEVEL!) white", "前往下一關！", align="center", region=[0, 116]),
    "4a_29": blank("NEXT", "drawn by 4a_28"), "4a_2a": blank("LEVEL!", "drawn by 4a_28"),
    "4a_2e": res("RINGS", "戒指", align="center"),
})
ZONES = {"0c": ("BOTANIC BASE", "植物基地"), "0d": ("SPEED SLIDER", "極速滑道"),
         "0e": ("AMAZING ARENA", "驚奇競技場"), "0f": ("TECHNO TOWER", "科技之塔"),
         "10": ("MARINA MADNESS", "瘋狂海港")}
ZW = {"0c": 116, "0d": 118, "0e": 150, "0f": 138, "10": 154}
for ff, (en, zh) in ZONES.items():
    SPECS["4a_" + ff] = {"en": en, "zh": zh, "layers": [
        {"zh": zh, "font": TTF_BIG, "size": 22, "thresh": 120, "gap": 3, "style": "res_zone",
         "valign": [0, 23], "align": "right", "region": [0, ZW[ff] - 3]}]}

# ---------------------------------------------------------------- special stage 4d
SPECS.update({
    "4d_00": res("TIME (OUT)", "時間到！", style="sp_white", align="left", x=1),
    "4d_01": res("COURSE (OUT)", "衝出跑道！", style="sp_white", x=1),
    "4d_02": blank("OUT", "drawn by 4d_00 / 4d_01"),
    "4d_04": res("BAD!", "可惜了！", style="sp_white", x=1),
    # TOO and BAD! are 8 px apart in TOO BAD!: 太 is moved right to meet 可惜了！
    "4d_05": res("TOO (BAD!)", "太", style="sp_white", align="right", region=[0, 31]),
    "4d_06": res("COOOOL", "太酷了", style="sp_white", align="center"),
    "4d_07": res("NEXT", "下一關", style="sp_white", align="center"),
    "4d_08": keep("!", "punctuation; kept"),
    "4d_09": res("TO  GO", "待收集", style="sp_white", align="center"),
    "4d_0a": blank("SPHERES", "drawn by 4d_0b (顆藍色球體)"),
    "4d_0b": res("BLUE (SPHERES)", "顆藍色球體", style="sp_white", x=1),
    "4d_0c": res("GET", "收集", style="sp_white", align="center"),
    "4d_03": {"en": "GOT .... pts!", "zh": "得到 .... 分！", "canvas": "orig",
              "erase": [[0, 0, 26, 20], [80, 0, 110, 20]],
              "layers": [
                  dict(WORD, zh="得到", style="sp_white", y=0, x=1),
                  dict(WORD, zh="分！", style="sp_white", y=5, x=82)]},
})

# ---------------------------------------------------------------- title 55
TAG = [56, 55, 236, 74]  # the tagline's black bar (both halves side by side)
SPECS["55_0a"] = {
    "en": "FEATURING KNUCKLES THE ECHIDNA. / WELCOME TO THE NEXT LEVEL / IN 32X WORLD / PUSH START (logo, left half)",
    "zh": "主演：納克魯斯／歡迎來到 32X 的全新境界／請按 START",
    "join": "0b", "canvas": "orig",
    "rects": [TAG[:4] + [0x56]],
    "fill_rows": [[106, 85, 189, 94, 95]],
    "layers": [
        {"zh": "主演：納克魯斯", "font": "fusion8", "scale": 1, "gap": 1, "style": "title_tag", "y": 56,
         "align": "center", "region": [0, 292], "colmap": {"rect": TAG, "bg": [0x56], "fill": 0x7f}},
        {"zh": "歡迎來到 32X 的全新境界", "font": "fusion8", "scale": 1, "gap": 1, "style": "title_tag", "y": 66,
         "align": "center", "region": [0, 292], "colmap": {"rect": TAG, "bg": [0x56], "fill": 0x7f}},
        {"zh": "請按 START", "font": "fusion8", "scale": 1, "gap": 1, "space": 4, "style": "title_blue", "y": 86,
         "align": "center", "region": [106, 189]},
    ]}
SPECS["55_0b"] = {"en": "(logo, right half)", "zh": "(drawn with 55_0a)", "joined": "55_0a"}
SPECS["55_09"] = {"en": "PUSH START", "zh": "請按 START", "layers": [
    {"zh": "請按 START", "font": "fusion8", "scale": 1, "gap": 1, "space": 4, "style": "title_push", "y": 0,
     "align": "center"}]}

# ---------------------------------------------------------------- goal, AA, TT
SPECS["23_06"] = {"en": "CLEAR (goal sign)", "zh": "過關", "canvas": "orig",
                  "rects": [[1, 1, 73, 17, 0x12]],
                  "unletter": [{"rect": [1, 17, 73, 25], "idx": [0x01, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d,
                                                             0x0f, 0x10], "only": [0x02, 0x03, 0x04, 0x05, 0x12]}],
                  "layers": [
                      {"zh": "過", "font": TTF_BLOCK, "size": 21, "thresh": 128, "style": "goal_yellow", "y": 1, "x": 15},
                      {"zh": "關", "font": TTF_BLOCK, "size": 21, "thresh": 128, "style": "goal_blue", "y": 1, "x": 39}]}
SPECS["3d_03"] = {"en": "(dot) NO CLEAR (dot)", "zh": "未過關", "canvas": "orig", "erase": [[7, 0, 93, 23]],
                  "layers": [{"zh": "未過關", "font": TTF_BLOCK, "size": 21, "thresh": 128, "gap": 3,
                              "style": "aa_noclear", "valign": [1, 22], "align": "center"}]}
SPECS["29_23"] = {"en": "(arrow) CHALLENGE AGAIN!! (arrow)", "zh": "再挑戰一次！！", "canvas": "orig",
                  "erase": [[7, 0, 121, 10]],
                  "layers": [{"zh": "再挑戰一次！！", "font": "fusion8", "scale": 1, "gap": 2, "style": "aa_again",
                              "y": 1, "align": "center"}]}
SPECS["2d_02"] = {"en": "LOCK ON", "zh": "鎖定", "canvas": "orig", "erase": [[0, 0, 20, 10]],
                  "layers": [{"zh": "鎖定", "font": "fusion8", "scale": 1, "gap": 1, "style": "tt_lock",
                              "y": 1, "align": "center"}]}

# ---------------------------------------------------------------- bonus stage 26
SPECS["26_01"] = {"en": "500 PTS.", "zh": "500 分", "canvas": "orig", "rects": [[11, 17, 29, 26, 0x09]],
                  "layers": [{"zh": "分", "font": "fusion8", "scale": 1, "style": "bonus_pts", "y": 18,
                              "align": "center", "region": [11, 29]}]}
for ff, st, bg in (("1a", "bonus_exit1", 0x02), ("1b", "bonus_exit2", 0x12), ("1c", "bonus_exit3", 0x12)):
    SPECS["26_" + ff] = {"en": "EXIT (block)", "zh": "出口", "canvas": "orig", "rects": [[5, 9, 27, 23, bg]],
                         "layers": [{"zh": "出口", "font": TTF_BLOCK, "size": 13, "thresh": 128, "gap": 1,
                                     "style": st, "valign": [9, 23], "align": "center", "region": [4, 28]}]}
SPECS["26_20"] = {"en": "UP (block)", "zh": "上", "canvas": "orig", "rects": [[3, 11, 29, 21, 0x01]],
                  "layers": [{"zh": "上", "font": TTF_BLOCK, "size": 12, "thresh": 128, "style": "bonus_up",
                              "valign": [10, 22], "align": "center"}]}
SPECS["26_21"] = {"en": "DOWN (block)", "zh": "下", "canvas": "orig", "rects": [[3, 11, 29, 21, 0x01]],
                  "layers": [{"zh": "下", "font": TTF_BLOCK, "size": 12, "thresh": 128, "style": "bonus_down",
                              "valign": [10, 22], "align": "center"}]}

# ---------------------------------------------------------------- lobby 58, 59, 5e
SIGN_LETTERS = [0x42, 0x43, 0x3d, 0x3c]
SPECS["59_00"] = {"en": "EXIT (sign)", "zh": "出口", "canvas": "orig",
                  "unletter": [{"rect": [2, 24, 50, 36], "idx": SIGN_LETTERS, "only": [0x41]}],
                  "layers": [dict(WORD, zh="出口", style="lobby_sign", valign=[23, 37], align="center", region=[2, 52])]}
SPECS["59_01"] = {"en": "PLAY (sign)", "zh": "開始", "canvas": "orig",
                  "unletter": [{"rect": [2, 22, 50, 34], "idx": SIGN_LETTERS, "only": [0x41]}],
                  "layers": [dict(WORD, zh="開始", style="lobby_sign", valign=[21, 35], align="center", region=[2, 52])]}
SPECS["58_00"] = {"en": "COMBI / CATCHER (alternating sign)", "zh": "搭檔／抓抓機", "canvas": "orig",
                  "cycle": {"rect": [6, 6, 53, 14], "bg": 0x60, "both": 0x6c,
                            "a": {"zh": "抓抓機", "idx": 0x6e, "gap": 1, "y": 1},
                            "b": {"zh": "搭檔", "idx": 0x6d, "gap": 1, "y": 1}}}
SPECS["5e_00"] = {"en": "NEWTROGIC HIGH ZONE / ATTRACTION INFORMATION", "zh": "紐托吉克高地／設施導覽",
                  "canvas": "orig",
                  "fill_rows": [[21, 5, 72, 11, 10], [18, 11, 74, 17, 17]],
                  "erase": [[0, 25, 92, 46]],
                  "layers": [
                      {"zh": "紐托吉克", "font": "fusion8", "scale": 1, "gap": 1, "style": "lobby_banner", "y": 4, "align": "center"},
                      {"zh": "高地", "font": "fusion8", "scale": 1, "gap": 1, "style": "lobby_banner", "y": 11, "align": "center"},
                      dict(WORD, zh="設施導覽", style="lobby_info", valign=[26, 45], align="center")]}
SPECS["5e_01"] = {"en": "CLEAR (attraction board)", "zh": "過關", "layers": [
    {"zh": "過關", "font": "fusion8", "scale": 1, "gap": 1, "style": "lobby_grey", "y": 0, "align": "center"}]}
SPECS["5e_02"] = {"en": "LEVEL (attraction board)", "zh": "關卡", "layers": [
    {"zh": "關卡", "font": "fusion8", "scale": 1, "gap": 1, "style": "lobby_grey", "y": 0, "align": "center"}]}

# ---------------------------------------------------------------- misc
SPECS["24_1a"] = keep("Test", "debug graphic")
SPECS["24_19"] = keep("skull with text", "debug graphic")
SPECS["55_0d"] = keep("(c)SEGA ENTERPRISES,LTD.1995", "copyright line stays as it is")


def main():
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "_styles.json"), "w", encoding="utf8") as f:
        json.dump(STYLES, f, ensure_ascii=False, indent=1)
    for k, v in sorted(SPECS.items()):
        with open(os.path.join(OUT, k + ".json"), "w", encoding="utf8") as f:
            json.dump(v, f, ensure_ascii=False, indent=1)
            f.write("\n")
    print("%d specs written" % len(SPECS))


if __name__ == "__main__":
    main()
