"""Package the mod: release/ChaotixRecompiled-zhTW-<version>.zip.

    python tools/package.py

The zip holds the mod pack Mods/ChaotixZhTW/ (mod/Mods/Textures and
mod/mod.ini), README_zhTW.txt and licenses/ (mod/), with
fixed timestamps and sorted entries so that the same files give the same
zip. The version is read from mod/README_zhTW.txt ("Version X.Y.Z").
Run tools/build.py first.
"""
import os
import re
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOD = os.path.join(ROOT, "mod")
# The pack's folder in the game's Mods folder (Knuckles' Chaotix Recompiled
# 0.9.0 mod packs). Keep it the same in every version, so players keep their
# order and on/off setting.
PACK = "ChaotixZhTW"


def zip_name(f):
    """Where a file of mod/ goes in the zip."""
    if f == "mod.ini":
        return "Mods/%s/mod.ini" % PACK
    if f.startswith("Mods/"):
        return "Mods/%s/%s" % (PACK, f[len("Mods/"):])
    return f


def main():
    readme = open(os.path.join(MOD, "README_zhTW.txt"), encoding="utf8").read()
    version = re.search(r"^Version (\d+\.\d+\.\d+)", readme, re.M).group(1)
    files = ["README_zhTW.txt", "mod.ini"]
    for top in ("Mods", "licenses"):
        for d, _, fs in os.walk(os.path.join(MOD, top)):
            files += [os.path.relpath(os.path.join(d, f), MOD).replace(os.sep, "/") for f in fs]
    files.sort(key=zip_name)
    os.makedirs(os.path.join(ROOT, "release"), exist_ok=True)
    out = os.path.join(ROOT, "release", "ChaotixRecompiled-zhTW-%s.zip" % version)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for f in files:
            data = open(os.path.join(MOD, f), "rb").read()
            if f.endswith((".txt", ".ini")):
                data = data.replace(b"\r\n", b"\n")
            info = zipfile.ZipInfo(zip_name(f), date_time=(2026, 10, 23, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, data)
    print("%s: %d files, %d bytes" % (out, len(files), os.path.getsize(out)))


if __name__ == "__main__":
    main()
