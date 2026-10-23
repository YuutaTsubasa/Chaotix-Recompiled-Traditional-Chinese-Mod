#!/bin/bash
# cap_text.sh NAME LASTFRAME SHOTS [args...]: screenshots and the game's
# DUMP GRAPHICS (with Text/text_<n>.txt, the plane text runs) of a menu into
# work/p3/NAME (not committed). The captures used for text/mdtext (phase 3):
#   tr    2600 1950       --press 1800:start:6 --press 1900:down:4 --press 1960:start:6   (title menu, TRAINING)
#   opt   2600 2100       --press 1800:start:6 --press 1900:down:4 --press 1930:down:4 --press 1980:start:6
#   opt2  2700 2190       (opt) --press 2050:right:4 --press 2150:right:4                 (TYPE 3: HOLD&JUMP)
#   dl    2500 2499       --press 1800:start:6 --press 1950:start:6                       (DATA LOAD)
#   dl2   2900 2300       (dl) --press 2150:down:6                                        (DATA 1)
#   slots 3000 2340       (dl2) --press 2250:down:6                                       (DATA 2, 3)
. "$(dirname "$0")/env.sh"
W=C:/Users/User/Repo/ChaotixRecompiled-zhTW/work
N=$1; F=$2; S=$3; shift 3
D=/c/Users/User/Repo/ChaotixRecompiled-zhTW/work/p3/$N
rm -rf $D; mkdir -p $D
$H --rom "$R" --frames $F --shot $S --out $W/p3/$N --dump-graphics $W/p3/$N/dump "$@" >$D/log.txt 2>&1
ls $D/dump/Text 2>/dev/null | grep txt | tr '\n' ' '; echo
