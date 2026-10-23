#!/bin/bash
# render_showcase.sh: widescreen (--wide 53, 426x224) screenshots for the mod
# page into preview/showcase/<name>/ (gitignored: game art); then
#   python tools/showcase.py   -> release/screenshots/*.png (3x, nearest)
. "$(dirname "$0")/env.sh"
M=C:/Users/User/Repo/ChaotixRecompiled-zhTW
TX=$M/mod/Mods/Textures
REC=C:/Users/User/Repo/KnucklesChaotixRecompiledClaude/tests/recordings/finished_run.txt
WIDE="--wide 53 --wide-everywhere"
shot() {  # NAME "FRAMES" ARGS...
    local n=$1 f=$2; shift 2
    local last=${f##*,}
    rm -rf "$M/preview/showcase/$n"; mkdir -p "$M/preview/showcase/$n"
    $H --rom "$R" --tiles $TX $WIDE --frames $((last + 1)) --shot "$f" --out $M/preview/showcase/$n "$@" >/dev/null 2>&1
    echo "$n: $(ls $M/preview/showcase/$n | tr '\n' ' ')"
}
ALL="$*"
run() { if [ -z "$ALL" ] || [[ " $ALL " == *" $1 "* ]]; then shot "$@"; fi; }
D="--press 1800:start:6 --press 1950:start:6"
T="--press 1800:start:6 --press 1900:down:4 --press 1960:start:6"
run title 1700,1760
run menu 1890,1920 --press 1800:start:6 --press 1900:down:4
run card 600,640 --stage 300:0:1:0:2:7:0
run hud 900,1100,1200 --stage 300:0:1:0:2:7:0
run aa 700,1100 --stage 300:2:1:0:2:7:0
run results 3900,4100 --replay-input $REC
run special 600 --stage 300:10:0:0:2:7:0
run lobby 1000,1300 --stage 300:7:0:0:2:7:0
run lobby_board 785 --stage 300:7:0:0:2:7:0 --press 450:right:2000
run dataload 2240,2340 $D --press 2150:down:6 --press 2250:down:6
run savemode 2300 $D --press 2150:down:6 --press 2250:start:6
run playersel 2500,2600 $T --press 2250:start:6 --press 2350:start:6 --press 2550:down:6
run playstyle 2300 $T --press 2250:start:6
run options 2140 --press 1800:start:6 --press 1900:down:4 --press 1930:down:4 --press 1980:start:6 --press 2050:right:4
run training 2150 $T
