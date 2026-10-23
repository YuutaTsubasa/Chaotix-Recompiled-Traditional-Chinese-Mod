#!/bin/bash
# render_preview.sh [SCENE...]: screenshots of the game with the mod's sprites
# (mod/Mods/Textures) into preview/scenes/<scene>/ (gitignored: game art).
# Then: python tools/contact.py  (Windows Python with Pillow)
. "$(dirname "$0")/env.sh"
M=C:/Users/User/Repo/ChaotixRecompiled-zhTW
TX=$M/mod/Mods/Textures
REC=C:/Users/User/Repo/KnucklesChaotixRecompiledClaude/tests/recordings/finished_run.txt

scene() {  # NAME "FRAMES" ARGS...
    local n=$1 f=$2; shift 2
    local last=${f##*,}
    rm -rf "$M/preview/scenes/$n"; mkdir -p "$M/preview/scenes/$n"
    $H --rom "$R" --tiles $TX --frames $((last + 1)) --shot "$f" --out $M/preview/scenes/$n "$@" 2>&1 | grep -E "^sprites: [0-9]+ repl|refus|too large|original is drawn" | head -5
    echo "$n done"
}

ALL="$*"
run() { if [ -z "$ALL" ] || [[ " $ALL " == *" $1 "* ]]; then scene "$@"; fi; }

run title 1650,1700,1760
run card_bb 600,640 --stage 300:0:1:0:2:7:0
run card_ss 600,640 --stage 300:1:1:0:2:7:0
run card_aa 600,640 --stage 300:2:1:0:2:7:0
run card_tt 600,640 --stage 300:3:1:0:2:7:0
run card_mm 600,640 --stage 300:4:1:0:2:7:0
run card_ii 600,640,700 --stage 300:6:0:0:2:7:0
run card_tr 600,640,700 --stage 300:5:0:0:2:7:0
run hud 900,1200 --stage 300:0:1:0:2:7:0
run pause 1000,1010 --stage 300:0:1:0:2:7:0 --press 990:start:5
run results 3700,3900,4100 --replay-input $REC
run special 440,460,600 --stage 300:10:0:0:2:7:0
run bonus 450,700,1100 --stage 300:9:0:0:2:7:0
run lobby 700,1000,1300 --stage 300:7:0:0:2:7:0
run lobby_board 785,850,866 --stage 300:7:0:0:2:7:0 --press 450:right:2000
run special_end 12750,12900 --stage 300:10:0:0:2:7:0
run aa 700,1100 --stage 300:2:1:0:2:7:0
run tt 400,600,800 --stage 300:3:1:0:2:7:0
# Mega Drive plane text (mdtext_, phase 3): title menu, OPTIONS, DATA LOAD
run menu 1890,1920,1960,2000 --press 1800:start:6 --press 1900:down:4 --press 1930:down:4
run options 2040,2140,2240 --press 1800:start:6 --press 1900:down:4 --press 1930:down:4 --press 1980:start:6 --press 2050:right:4 --press 2150:right:4 --press 2200:down:4
run dataload 2140,2240,2340,2440,2540 --press 1800:start:6 --press 1950:start:6 --press 2150:down:6 --press 2250:down:6 --press 2350:down:6 --press 2450:up:6
run training 2150 --press 1800:start:6 --press 1900:down:4 --press 1960:start:6
# Mega Drive sprite text (mdsprite_, phase 4)
D="--press 1800:start:6 --press 1950:start:6"
T="--press 1800:start:6 --press 1900:down:4 --press 1960:start:6"
O="--press 1800:start:6 --press 1900:down:4 --press 1930:down:4 --press 1980:start:6 --press 2050:down:4 --press 2200:start:6"
run dl_banners 2038,2100,2152,2168 $D --press 2150:down:6
run savemode 2258,2264,2270,2300,2400 $D --press 2150:down:6 --press 2250:start:6 --press 2350:down:6
SR=$M/work/p4/t2.srm  # a save with cleared zones (python tools/make_sram.py)
[ -f $SR ] && run used_slot 2200,2300,2400,2500 $D --sram $SR --press 2150:down:6 --press 2250:right:6 --press 2350:start:6 --press 2450:down:6
run tr_banners 2150,2300,2260,2276 $T --press 2200:right:6 --press 2240:left:6 --press 2250:start:6
run playstyle 2262,2270,2300,2560,2580,2620 $T --press 2250:start:6 --press 2550:down:6
run playersel 2405,2500,2600,2700,2800,2900,3000,3100 $T --press 2250:start:6 --press 2350:start:6 $(for i in 0 1 2 3 4 5 6; do echo --press $((2550 + i * 100)):down:6; done)
run combi 2545,2600,2700,2800 $T --press 2250:start:6 --press 2350:start:6 --press 2450:start:6 --press 2650:down:6
run soundtest 2300,2430,2470,2550,2710,3230,3990,4030,4070 $O $(for i in $(seq 0 43); do echo --press $((2400 + i * 40)):right:4; done)
# the top banners sliding (whole-banner patterns, matched partly off the
# screen by Knuckles' Chaotix Recompiled 0.7.1): TRAINING out, PLAY STYLE in
run tr_slide $(seq -s, 2250 2 2290) $T --press 2200:right:6 --press 2240:left:6 --press 2250:start:6
run dl_slide $(seq -s, 2000 3 2050) $D
