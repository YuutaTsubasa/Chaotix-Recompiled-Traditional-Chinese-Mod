#!/bin/bash
# cap_sprites.sh NAME LASTFRAME SHOTS [args...]: screenshots and the game's
# DUMP GRAPHICS (Text/sprites_<n>.txt: the sprite groups, phase 4) of a menu
# into work/p4/NAME (not committed). The captures used for text/mdsprite are
# listed in tools/make_mdsprite_specs.py.
. "$(dirname "$0")/env.sh"
N=$1; F=$2; S=$3; shift 3
D=/c/Users/User/Repo/ChaotixRecompiled-zhTW/work/p4/$N
rm -rf $D; mkdir -p $D
$H --rom "$R" --frames $F --shot $S --out $W/p4/$N --dump-graphics $W/p4/$N/dump "$@" >$D/log.txt 2>&1
ls $D/dump/Text 2>/dev/null | grep sprites_.*txt | tr '\n' ' '; echo
