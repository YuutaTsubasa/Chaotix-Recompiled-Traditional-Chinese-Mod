"""Build the zh-TW Mega Drive plane text replacements from text/mdtext/*.json.

    python tools/build_mdtext.py [--preview] [NAME ...]

For every spec text/mdtext/<name>.json this writes
mod/Mods/Textures/mdtext_<name>.txt (the tile pattern: plane, align,
palette, rows of tile hashes) and mdtext_<name>.png (the Chinese, palette-
indexed, 8 px high per row), as docs/TEXTURE_MODS.md of the game repo
(Knuckles' Chaotix Recompiled 0.7.0 or later) describes. The pattern rows
were copied from the game's DUMP GRAPHICS text lists (Dump/Text, kept in
work/, see `source`); the picture is drawn from the spec alone, so the
build needs no game data and is deterministic.

Spec keys:
  en, zh, screen        documentation (zh is checked by check_text.py)
  source                where the rows came from (dump, plane, cell rect)
  plane, align          pattern options (palette: 0-3, optional)
  rows                  the pattern, top row first: "hash[:h|:v|:hv] ..."
  size: [w, h]          picture size (default: 8 x tiles by 8 x rows)
  preview_palette       16 RGB colours sampled from a screenshot, only so
                        that the PNG looks right in a viewer: the game draws
                        the indices with the palette line of the run's first
                        tile (so the highlighted entry still changes colour)
  rects: [[x0,y0,x1,y1,idx], ...]   filled first
  layers                as in build_sprites.py (font, zh, size/scale, style,
                        align + region, valign, x, y); styles are in
                        text/mdtext/_styles.json; "cast": {idx, dx, dy, y0, grow}
                        adds the text's shadow cast on the panel below
  checker: [[x0,y0,x1,y1,idx,parity], ...]  dithered areas, after rects
  layers                ... or {"art": ["..#", ".##", ...], style, x, y}: a
                        hand-drawn shape ('#' = ink) instead of text
  pixels: [[x,y,idx], ...]          single pixels set last
"""
import glob
import json
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_sprites as B  # noqa: E402
import sprlib as L  # noqa: E402

SPECS = os.path.join(L.ROOT, "text", "mdtext")
OUT = os.path.join(L.ROOT, "mod", "Mods", "Textures")
PREVIEW = os.path.join(L.ROOT, "preview")


def draw(spec, styles, size=None):
    """The spec's picture (indices) and a list of problems. `size` is given
    by build_mdsprite.py; a plane text pattern is 8 px per row and tile."""
    if size is None:
        rows = [r.split() for r in spec["rows"]]
        assert all(len(r) == len(rows[0]) for r in rows), "rows of different lengths"
        W, H = spec.get("size", [8 * len(rows[0]), 8 * len(rows)])
        assert H == 8 * len(rows), "the picture must be 8 px high per row"
    else:
        W, H = size
    canvas = np.zeros((H, W), np.uint8)
    for x0, y0, x1, y1, idx in spec.get("rects", []):
        canvas[y0:y1, x0:x1] = idx
    for x0, y0, x1, y1, idx, par in spec.get("checker", []):
        # a dithered (every second pixel) area, as the menus' drop shadows
        yy, xx = np.mgrid[y0:y1, x0:x1]
        sel = (xx + yy) % 2 == par
        canvas[y0:y1, x0:x1][sel] = idx
    problems = []
    for layer in spec.get("layers", []):
        st = dict(styles[layer["style"]]) if isinstance(layer["style"], str) else dict(layer["style"])
        st.update(layer.get("style_over", {}))
        if "art" in layer:
            # a small hand-drawn shape ('#' = ink), e.g. the selectors' arrows
            m = np.array([[c == "#" for c in r] for r in layer["art"]], bool)
        else:
            m = B.text_mask(layer)
        img, ox, oy = B.stylise(m, st)
        mw, mh = m.shape[1], m.shape[0]
        if "x" in layer:
            x = layer["x"]
        else:
            r0, r1 = layer.get("region", [0, W])
            a = layer.get("align", "center")
            x = r0 if a == "left" else r1 - mw if a == "right" else r0 + (r1 - r0 - mw) // 2
        if "y" in layer:
            y = layer["y"]
        else:
            r0, r1 = layer.get("valign", [0, H])
            y = r0 + (r1 - r0 - mh) // 2
        X, Y = x - ox, y - oy
        if X < 0 or Y < 0 or X + img.shape[1] > W or Y + img.shape[0] > H:
            problems.append("%r does not fit: %dx%d at %d,%d in %dx%d" % (layer.get("zh", "art"), img.shape[1], img.shape[0], X, Y, W, H))
            x0, y0 = max(0, -X), max(0, -Y)
            img = img[y0:, x0:]
            X, Y = max(X, 0), max(Y, 0)
            img = img[:H - Y, :W - X]
        sel = img != 0
        if "cast" in layer:
            # the text's shadow cast on the panel under it (DATA LOAD slot
            # headers): the mask moved by dx,dy, only from line y0 down,
            # where the picture is still transparent
            c = layer["cast"]
            full = np.zeros((H, W), bool)
            mx, my = x + c["dx"], y + c["dy"]
            cm = L.dilate(L.pad(m, 1, 1, 1, 1)) if c.get("grow") else m
            if c.get("grow"):
                mx, my = mx - 1, my - 1
            sub = cm[max(0, -my):H - my, max(0, -mx):W - mx]
            full[max(my, 0):max(my, 0) + sub.shape[0], max(mx, 0):max(mx, 0) + sub.shape[1]] = sub
            full[:c.get("y0", 0)] = False
            canvas[full & (canvas == 0)] = c["idx"]
        canvas[Y:Y + img.shape[0], X:X + img.shape[1]][sel] = img[sel]
    for x, y, idx in spec.get("pixels", []):
        canvas[y, x] = idx
    if canvas.max() > 15:
        problems.append("index above 15")
    return canvas, problems


def palette(spec):
    pal = spec.get("preview_palette") or [[i * 16] * 3 for i in range(16)]
    flat = [c for rgb in pal for c in rgb]
    return flat + [0] * (768 - len(flat))


def pattern_text(name, spec):
    out = ["# %s: %s -> %s (zh-TW translation mod)" % (spec.get("screen", ""), spec["en"], spec["zh"]),
           "# built by tools/build_mdtext.py from text/mdtext/%s.json" % name,
           "plane %s" % spec.get("plane", "any"),
           "align %s" % spec.get("align", "left")]
    if "palette" in spec:
        out.append("palette %s" % spec["palette"])
    out += ["row " + r for r in spec["rows"]]
    return "\n".join(out) + "\n"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    want_preview = "--preview" in sys.argv
    styles = json.load(open(os.path.join(SPECS, "_styles.json"), encoding="utf8"))
    os.makedirs(OUT, exist_ok=True)
    if not args:
        for old in glob.glob(os.path.join(OUT, "mdtext_*")):
            os.remove(old)
    n = bad = 0
    shown = []
    for p in sorted(glob.glob(os.path.join(SPECS, "[a-z0-9]*.json"))):
        name = os.path.basename(p)[:-5]
        if args and name not in args:
            continue
        spec = json.load(open(p, encoding="utf8"))
        canvas, problems = draw(spec, styles)
        for pr in problems:
            print("%s: %s" % (name, pr))
            bad += 1
        L.save_indexed(canvas, palette(spec), os.path.join(OUT, "mdtext_%s.png" % name))
        with open(os.path.join(OUT, "mdtext_%s.txt" % name), "w", encoding="utf8", newline="\n") as f:
            f.write(pattern_text(name, spec))
        n += 1
        shown.append((name, spec, canvas))
    print("%d text pattern(s) written to %s%s" % (n, OUT, ", %d problem(s)" % bad if bad else ""))
    if want_preview and shown:
        from PIL import ImageDraw
        s = 4
        tiles = []
        for name, spec, canvas in shown:
            im = L.preview(canvas, palette(spec), s, bg=(40, 40, 48))
            t = Image.new("RGB", (max(im.width, 300), im.height + 14), (20, 20, 24))
            ImageDraw.Draw(t).text((2, 0), "%s  %s" % (name, spec["en"]), fill=(255, 255, 0))
            t.paste(im, (0, 14))
            tiles.append(t)
        Wp = max(t.width for t in tiles)
        page = Image.new("RGB", (Wp, sum(t.height + 6 for t in tiles)), (20, 20, 24))
        y = 0
        for t in tiles:
            page.paste(t, (0, y))
            y += t.height + 6
        os.makedirs(PREVIEW, exist_ok=True)
        page.save(os.path.join(PREVIEW, "mdtext.png"))
        print("preview: %s" % os.path.join(PREVIEW, "mdtext.png"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
