"""Build the zh-TW 32X sprite replacements from text/sprites/*.json.

    python tools/build_sprites.py [--preview] [ID ...]

For every spec text/sprites/<bb>_<ff>.json this writes
mod/Mods/Textures/32x_<bb>_<ff>.png: a single-frame replacement, palette-
indexed with the bank's palette (docs/TEXTURE_MODS.md in the game repo), the
same size as the original or larger towards the right and down. The original
frames are read from the sheets the game exported (work/, not committed), so
the output is deterministic given those and the specs.

Spec keys:
  en, zh                 the English text and its translation (documentation)
  keep: true             not replaced (English kept); `why` says why
  blank: true            replaced by a fully transparent frame (a word whose
                         phrase is drawn by another frame)
  canvas: "blank"|"orig" start from transparency (default) or from the
                         original pixels (for pictures holding art besides
                         the text), then `erase` rectangles [x0,y0,x1,y1)
                         are set to `erase_idx` (default 0)
  copy: [[x0,y0,x1,y1,dx,dy], ...]  copy original pixels (art pieces) to
                         dx,dy before drawing the text
  size: [w,h]            minimum canvas size (default: the original's)
  layers: [ {zh, font, scale|size, gap, style, x, y, align, region}, ... ]
     font "fusion8": Fusion Pixel 8px (scale = integer zoom)
     font "<file>.ttf/.otf": an OFL font, rendered at `size` px, `thresh`
     x: left of the text's ink; or align left/right/center in region [x0,x1)
     y: top of the text's ink
  pixels: [[x,y,idx], ...]  single pixels set last (hand touch-ups)

Styles (text/sprites/_styles.json) turn a 1-bit text mask into indices:
  fill: idx, or bands [[row, idx], ...] by row from the ink top
  shadow: {idx, offsets: [[dx,dy],...]}   drawn under the fill
  outline: {idx, mode: "8"|"4"}           drawn under the fill and shadow
  edge: {br: idx, tl: idx}                recolours the fill's edge pixels
"""
import glob
import json
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprlib as L  # noqa: E402

SPECS = os.path.join(L.ROOT, "text", "sprites")
OUT = os.path.join(L.ROOT, "mod", "Mods", "Textures")
PREVIEW = os.path.join(L.ROOT, "preview")


def load_styles():
    return json.load(open(os.path.join(SPECS, "_styles.json"), encoding="utf8"))


def text_mask(layer):
    font = layer.get("font", "fusion8")
    zh = layer["zh"]
    gap = layer.get("gap", None)
    if font == "fusion8":
        s = layer.get("scale", 1)
        f = L.fusion()
        parts = []
        for c in zh:
            if c == " ":
                parts.append(np.zeros((8 * s, layer.get("space", 3) * s), bool))
                continue
            if not f.has(c):
                raise KeyError("%s: Fusion Pixel 8px has no glyph for %r" % (zh, c))
            g = f.glyph(c)
            if not layer.get("mono"):
                g = L.trim_cols(g)
            parts.append(L.scale(g, s))
        m = L.hcat(parts, gap=s if gap is None else gap)
    else:
        m = L.ttf_text(zh, font, layer["size"], thresh=layer.get("thresh", 128),
                       gap=2 if gap is None else gap, space=layer.get("space"))
    if layer.get("squeeze"):
        w = int(round(m.shape[1] * layer["squeeze"]))
        m = L.fit(m, w, m.shape[0])
    # trim empty rows at top/bottom (keep columns: spaces matter)
    rows = np.where(m.any(1))[0]
    return m[rows[0]:rows[-1] + 1]


def stylise(m, st):
    """Index image of the mask with a style; returns (img, ox, oy) where
    (ox, oy) is where the mask's top-left lands in img."""
    padl = padt = 1 if "outline" in st else 0
    padr = padb = 1 if "outline" in st else 0
    if "shadow" in st:
        for dx, dy in st["shadow"]["offsets"]:
            padr = max(padr, dx)
            padb = max(padb, dy)
            padl = max(padl, -dx)
            padt = max(padt, -dy)
    M = L.pad(m, padl, padt, padr, padb)
    img = np.zeros(M.shape, np.uint8)
    if "outline" in st:
        o = L.dilate(M, st["outline"].get("mode", "8")) & ~M
        img[o] = st["outline"]["idx"]
        if "outline2" in st:
            o2 = L.dilate(M | o, st["outline2"].get("mode", "8")) & ~(M | o)
            # outline2 only where it fits (no padding added for it)
            img[o2] = st["outline2"]["idx"]
    if "shadow" in st:
        sh = np.zeros_like(M)
        for dx, dy in st["shadow"]["offsets"]:
            sh |= L.shift(M, dx, dy)
        sh &= ~M
        img[sh] = st["shadow"]["idx"]
    f = st["fill"]
    if isinstance(f, int):
        img[M] = f
    else:
        rows = np.arange(M.shape[0]) - padt
        for r0, idx in f["bands"]:
            sel = M & (rows >= r0)[:, None]
            img[sel] = idx
    if "edge" in st:
        e = st["edge"]
        if "br" in e:
            br = M & (~L.shift(M, -1, 0) | ~L.shift(M, 0, -1))
            img[br] = e["br"]
        if "tl" in e:
            tl = M & (~L.shift(M, 1, 0) | ~L.shift(M, 0, 1))
            img[tl] = e["tl"]
    return img, padl, padt


def build(spec, styles):
    bank, frame = spec["id"].split("_")
    sh = L.sheet(bank)
    orig, box = sh.frame(frame)
    if "join" in spec:
        # two frames drawn side by side (the title logo's halves): drawn as
        # one picture, split again in main()
        o2, _ = sh.frame(spec["join"])
        assert o2.shape[0] == orig.shape[0]
        orig = np.concatenate([orig, o2], 1)
    oh, ow = orig.shape
    w, h = spec.get("size", [ow, oh])
    w, h = max(w, ow), max(h, oh)
    canvas = np.zeros((h, w), np.uint8)
    if spec.get("canvas") == "orig":
        canvas[:oh, :ow] = orig
    for x0, y0, x1, y1 in spec.get("erase", []):
        canvas[y0:y1, x0:x1] = spec.get("erase_idx", 0)
    for x0, y0, x1, y1, src in spec.get("fill_rows", []):
        # erase with the picture's own row `src` (a background gradient)
        canvas[y0:y1, x0:x1] = orig[src, x0:x1][None, :]
    for u in spec.get("unletter", []):
        # remove letters: each pixel of the letters' indices takes the
        # nearest other non-transparent pixel of its row (the background)
        x0, y0, x1, y1 = u["rect"]
        letters = set(u["idx"])
        for yy in range(y0, y1):
            row = canvas[yy].copy()
            only = set(u.get("only", []))
            cand = [xx for xx in range(len(row)) if row[xx] and row[xx] not in letters
                    and (not only or row[xx] in only)]
            for xx in range(x0, x1):
                if row[xx] in letters:
                    if cand:
                        k = min(cand, key=lambda k: (abs(k - xx), k))
                        canvas[yy, xx] = row[k]
                    else:
                        canvas[yy, xx] = u.get("default", 0)
    for x0, y0, x1, y1, idx in spec.get("rects", []):
        canvas[y0:y1, x0:x1] = idx
    for x0, y0, x1, y1, dx, dy in spec.get("copy", []):
        piece = orig[y0:y1, x0:x1]
        sel = piece != 0
        canvas[dy:dy + piece.shape[0], dx:dx + piece.shape[1]][sel] = piece[sel]
    placed = []
    for layer in spec.get("layers", []):
        st = dict(styles[layer["style"]]) if isinstance(layer["style"], str) else layer["style"]
        st.update(layer.get("style_over", {}))
        m = text_mask(layer)
        if layer.get("bold"):
            m = L.pad(m, 0, 0, 1, 0)
            m = m | L.shift(m, 1, 0)
        img, ox, oy = stylise(m, st)
        mw = m.shape[1]
        if "x" in layer:
            x = layer["x"]
        else:
            r0, r1 = layer.get("region", [0, ow])
            a = layer.get("align", "center")
            x = r0 if a == "left" else r1 - mw if a == "right" else r0 + (r1 - r0 - mw) // 2
        y = layer.get("y", 0)
        if "valign" in layer:
            r0, r1 = layer["valign"]
            y = r0 + (r1 - r0 - m.shape[0]) // 2
        X, Y = x - ox, y - oy
        if X < 0 or Y < 0:
            # clip what would fall left of / above the box (it cannot grow there)
            img = img[max(0, -Y):, max(0, -X):]
            X, Y = max(X, 0), max(Y, 0)
        need_w, need_h = X + img.shape[1], Y + img.shape[0]
        if need_w > canvas.shape[1] or need_h > canvas.shape[0]:
            c2 = np.zeros((max(need_h, canvas.shape[0]), max(need_w, canvas.shape[1])), np.uint8)
            c2[:canvas.shape[0], :canvas.shape[1]] = canvas
            canvas = c2
        if "colmap" in layer:
            # the fill takes, per column, the index the original's text uses
            # in that column (the title tagline's colour bands)
            cx0, cy0, cx1, cy1 = layer["colmap"]["rect"]
            bg = set(layer["colmap"].get("bg", []))
            cmap = {}
            for cx in range(cx0, cx1):
                col = [v for v in orig[cy0:cy1, cx] if v and v not in bg]
                if col:
                    cmap[cx] = max(set(col), key=col.count)
            keys = sorted(cmap)
            fidx = layer["colmap"]["fill"]
            for iy, ix in zip(*np.where(img == fidx)):
                cx = X + ix
                near = min(keys, key=lambda k: abs(k - cx))
                img[iy, ix] = cmap[near]
        sel = img != 0
        canvas[Y:Y + img.shape[0], X:X + img.shape[1]][sel] = img[sel]
        placed.append((x, y, mw, m.shape[0]))
    if "cycle" in spec:
        # two words in one place, shown alternately by palette cycling:
        # pixels of word A only, word B only, and both, each their own index
        c = spec["cycle"]
        x0, y0, x1, y1 = c["rect"]
        canvas[y0:y1, x0:x1] = c["bg"]
        masks = []
        for w in (c["a"], c["b"]):
            m = text_mask(dict(w, font=w.get("font", "fusion8")))
            full = np.zeros((y1 - y0, x1 - x0), bool)
            mx = (x1 - x0 - m.shape[1]) // 2
            my = w.get("y", (y1 - y0 - m.shape[0]) // 2)
            full[my:my + m.shape[0], mx:mx + m.shape[1]] = m
            masks.append(full)
        a, b = masks
        reg = canvas[y0:y1, x0:x1]
        reg[a & ~b] = c["a"]["idx"]
        reg[b & ~a] = c["b"]["idx"]
        reg[a & b] = c["both"]
    for x, y, idx in spec.get("pixels", []):
        canvas[y, x] = idx
    # limits: grows right/down only, within -128..127 of the hotspot
    H, W = canvas.shape
    if "join" in spec:
        W = sh.frame(frame)[0].shape[1]
    nx1 = box["x0"] + ((W + 1) & ~1)
    ny1 = box["y0"] + H - 1
    problems = []
    if nx1 > 127 or ny1 > 127:
        problems.append("too large: x1 %d y1 %d (max 127)" % (nx1, ny1))
    if canvas.max() >= 0x80:
        problems.append("pixel values >= 0x80")
    return canvas, orig, problems, placed


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    want_preview = "--preview" in sys.argv
    styles = load_styles()
    os.makedirs(OUT, exist_ok=True)
    specs = []
    for p in sorted(glob.glob(os.path.join(SPECS, "[0-9a-f][0-9a-f]_[0-9a-f][0-9a-f].json"))):
        spec = json.load(open(p, encoding="utf8"))
        spec["id"] = os.path.basename(p)[:-5]
        if args and spec["id"] not in args:
            continue
        specs.append(spec)
    if not args:
        for old in glob.glob(os.path.join(OUT, "32x_*.png")):
            os.remove(old)
    rows = []
    n = 0
    bad = 0
    for spec in specs:
        if spec.get("keep") or spec.get("joined"):
            continue
        bank, frame = spec["id"].split("_")
        sh = L.sheet(bank)
        if spec.get("blank"):
            orig, _ = sh.frame(frame)
            canvas, problems = np.zeros_like(orig), []
        else:
            canvas, orig, problems, _ = build(spec, styles)
        for pr in problems:
            print("%s: %s" % (spec["id"], pr))
            bad += 1
        if "join" in spec:
            ow = sh.frame(frame)[0].shape[1]
            right = canvas[:, ow:]
            canvas = canvas[:, :ow]
            L.save_indexed(right, sh.palette, os.path.join(OUT, "32x_%s_%s.png" % (bank, spec["join"])))
            n += 1
        L.save_indexed(canvas, sh.palette, os.path.join(OUT, "32x_%s_%s.png" % (bank, frame)))
        n += 1
        if want_preview:
            rows.append((spec, orig, canvas, sh.palette))
    print("%d sprite(s) written to %s%s" % (n, OUT, ", %d problem(s)" % bad if bad else ""))
    if want_preview and rows:
        contact(rows)


def contact(rows):
    """Original and replacement side by side, 3x, one row per sprite."""
    from PIL import ImageDraw
    s = 3
    tiles = []
    for spec, orig, canvas, pal in rows:
        a = L.preview(orig, pal, s)
        b = L.preview(canvas, pal, s)
        w = a.width + b.width + 30
        h = max(a.height, b.height) + 14
        t = Image.new("RGB", (w, h), (20, 20, 24))
        ImageDraw.Draw(t).text((2, 0), spec["id"] + " " + spec.get("en", "")[:40], fill=(255, 255, 0))
        t.paste(a, (0, 14))
        t.paste(b, (a.width + 30, 14))
        tiles.append(t)
    # pack into pages of width 1400
    W = 1400
    pages = []
    cur = []
    x = y = rowh = 0
    pos = []
    for t in tiles:
        if x + t.width > W:
            x = 0
            y += rowh + 6
            rowh = 0
        if y + t.height > 1800 and pos:
            pages.append(pos)
            pos = []
            x = y = rowh = 0
        pos.append((t, x, y))
        x += t.width + 10
        rowh = max(rowh, t.height)
    if pos:
        pages.append(pos)
    os.makedirs(PREVIEW, exist_ok=True)
    for i, pos in enumerate(pages):
        H = max(y + t.height for t, x, y in pos)
        page = Image.new("RGB", (W, H), (20, 20, 24))
        for t, x, y in pos:
            page.paste(t, (x, y))
        page.save(os.path.join(PREVIEW, "sprites_%d.png" % i))
    print("preview: %d page(s) in %s" % (len(pages), PREVIEW))


if __name__ == "__main__":
    main()
