#!/bin/bash
# cap.sh NAME FRAME [headless args...]: full/md/32x shots at FRAME, dump + sheets
. /c/Users/User/Repo/ChaotixRecompiled-zhTW/work/env.sh
N=$1; F=$2; shift 2
D=/c/Users/User/Repo/ChaotixRecompiled-zhTW/work/scenes/$N
rm -rf $D; mkdir -p $D/full $D/md $D/32x
$H --rom "$R" --frames $((F+1)) --shot $F --out $W/scenes/$N/full --dump-graphics $W/scenes/$N/dump --export-sheets $W/scenes/$N/sheets "$@" >/dev/null 2>&1
$H --rom "$R" --frames $((F+1)) --shot $F --out $W/scenes/$N/md --layer md "$@" >/dev/null 2>&1
$H --rom "$R" --frames $((F+1)) --shot $F --out $W/scenes/$N/32x --layer 32x "$@" >/dev/null 2>&1
mv $D/full/*.png $D/full.png; mv $D/md/*.png $D/md.png; mv $D/32x/*.png $D/32x.png; rmdir $D/full $D/md $D/32x
