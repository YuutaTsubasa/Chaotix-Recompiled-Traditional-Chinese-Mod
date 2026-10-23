"""Build the zh-TW Mega Drive sprite text replacements from text/mdsprite/*.json.

    python tools/build_mdsprite.py [--preview] [NAME ...]

For every spec text/mdsprite/<name>.json this writes
mod/Mods/Textures/mdsprite_<name>.txt (the sprite pattern: align, palette,
offset, one `sprite DX DY WxH[:flip] hash...` line per sprite) and
mdsprite_<name>.png (the Chinese, palette-indexed), as the section "Mega
Drive text by sprite" of docs/TEXTURE_MODS.md in the game repo describes
(Knuckles' Chaotix Recompiled 0.7.1 or later). The sprite lines were copied
from the game's DUMP GRAPHICS sprite lists (Dump/Text/sprites_<n>.txt, kept
in work/p4, see `source`) or put together from the 8x16 game font's tile
hashes (inventory/inventory.json) by tools/make_mdsprite_specs.py; the
picture is drawn from the spec alone, so the build needs no game data and is
deterministic.

Spec keys (besides those of build_mdtext.py: en, zh, screen, source,
preview_palette, rects, checker, layers, pixels):
  sprites               the pattern's sprite lines, the first is the anchor
  align, offset, palette pattern options (offset: [x, y])
  size: [w, h]          picture size (default: the sprites' bounding box);
                        its top-left is the bounding box's top-left (moved
                        by align / offset), so a larger picture reaches
                        right and down
The indices are those of the first sprite's palette line (as the game draws
the line), 0 transparent; styles are in text/mdsprite/_styles.json.
"""
import glob
import json
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_mdtext as T  # noqa: E402
import mdspr  # noqa: E402
import sprlib as L  # noqa: E402

SPECS = os.path.join(L.ROOT, "text", "mdsprite")
OUT = os.path.join(L.ROOT, "mod", "Mods", "Textures")
PREVIEW = os.path.join(L.ROOT, "preview")


def bbox(spec):
    sp = [mdspr.parse_sprite(s) for s in spec["sprites"]]
    x0 = min(s["dx"] for s in sp)
    y0 = min(s["dy"] for s in sp)
    x1 = max(s["dx"] + 8 * s["w"] for s in sp)
    y1 = max(s["dy"] + 8 * s["h"] for s in sp)
    return x1 - x0, y1 - y0


def pattern_text(name, spec):
    out = ["# %s: %s -> %s (zh-TW translation mod)" % (spec.get("screen", ""), spec["en"], spec["zh"]),
           "# built by tools/build_mdsprite.py from text/mdsprite/%s.json" % name,
           "align %s" % spec.get("align", "left")]
    if "palette" in spec:
        out.append("palette %s" % spec["palette"])
    if "offset" in spec:
        out.append("offset %d %d" % tuple(spec["offset"]))
    out += spec["sprites"]
    return "\n".join(out) + "\n"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    want_preview = "--preview" in sys.argv
    styles = json.load(open(os.path.join(SPECS, "_styles.json"), encoding="utf8"))
    os.makedirs(OUT, exist_ok=True)
    if not args:
        for old in glob.glob(os.path.join(OUT, "mdsprite_*")):
            os.remove(old)
    n = bad = 0
    shown = []
    for p in sorted(glob.glob(os.path.join(SPECS, "[a-z0-9]*.json"))):
        name = os.path.basename(p)[:-5]
        if args and name not in args:
            continue
        spec = json.load(open(p, encoding="utf8"))
        for s in spec["sprites"]:
            mdspr.parse_sprite(s)  # checks the tile count
        size = spec.get("size") or list(bbox(spec))
        canvas, problems = T.draw(spec, styles, size=size)
        for pr in problems:
            print("%s: %s" % (name, pr))
            bad += 1
        L.save_indexed(canvas, T.palette(spec), os.path.join(OUT, "mdsprite_%s.png" % name))
        with open(os.path.join(OUT, "mdsprite_%s.txt" % name), "w", encoding="utf8", newline="\n") as f:
            f.write(pattern_text(name, spec))
        n += 1
        shown.append((name, spec, canvas))
    print("%d sprite pattern(s) written to %s%s" % (n, OUT, ", %d problem(s)" % bad if bad else ""))
    if want_preview and shown:
        s = 3
        tiles = []
        for name, spec, canvas in shown:
            im = L.preview(canvas, T.palette(spec), s, bg=(40, 90, 60))
            t = Image.new("RGB", (max(im.width, 330), im.height + 14), (20, 20, 24))
            ImageDraw.Draw(t).text((2, 0), "%s  %s" % (name, spec["en"]), fill=(255, 255, 0))
            t.paste(im, (0, 14))
            tiles.append(t)
        cols = 3
        Wp = max(t.width for t in tiles)
        rows = [tiles[i:i + cols] for i in range(0, len(tiles), cols)]
        page = Image.new("RGB", (Wp * cols, sum(max(t.height for t in r) + 6 for r in rows)), (20, 20, 24))
        y = 0
        for r in rows:
            for k, t in enumerate(r):
                page.paste(t, (k * Wp, y))
            y += max(t.height for t in r) + 6
        os.makedirs(PREVIEW, exist_ok=True)
        page.save(os.path.join(PREVIEW, "mdsprite.png"))
        print("preview: %s" % os.path.join(PREVIEW, "mdsprite.png"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
