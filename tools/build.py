"""Build the whole mod: mod/Mods/Textures from text/.

    python tools/build.py

Runs build_sprites.py (32x_*), build_mdtext.py (mdtext_*) and
build_mdsprite.py (mdsprite_*); each removes its own old files first, and
anything else left in mod/Mods/Textures (not made by these builds) is
removed here, so the folder holds exactly what the specs describe. The
builds use no game data and are deterministic.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "mod", "Mods", "Textures")


def main():
    bad = 0
    for tool in ("build_sprites.py", "build_mdtext.py", "build_mdsprite.py"):
        bad |= subprocess.call([sys.executable, os.path.join(HERE, tool)])
    for f in sorted(os.listdir(OUT)):
        if not f.startswith(("32x_", "mdtext_", "mdsprite_")):
            print("removing stray %s" % f)
            os.remove(os.path.join(OUT, f))
    print("%d file(s) in %s" % (len(os.listdir(OUT)), OUT))
    return bad


if __name__ == "__main__":
    sys.exit(main())
