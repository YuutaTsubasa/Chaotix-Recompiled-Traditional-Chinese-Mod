"""Helpers for the zh-TW sprite replacements (phase 2).

- Reading the game's exported sprite sheets (work/, not committed): a frame's
  original pixels, its box around the hotspot and the sheet's palette.
- The Fusion Pixel 8px BDF font and OFL TrueType fonts as 1-bit glyph masks.
- Small raster operations on numpy masks (scale, outline, shadow).

Run with the Windows Python that has Pillow and numpy.
"""
import json
import os
import re

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, "work")
FUSION_BDF = "C:/Users/User/Repo/Translations/fonts/fusion-pixel-8px/fusion-pixel-8px-monospaced-zh_tw.bdf"
USER_FONTS = os.path.expanduser("~/AppData/Local/Microsoft/Windows/Fonts")

# Where each bank's sheet was exported (phase 1 scenes).
SHEETS = {
    "13": "tc/sheets/32x_13",
    "23": "scenes/results3/sheets/32x_23",
    "26": "z9/sheets/32x_26",
    "29": "z2/sheets/32x_29",
    "2d": "tt1/sheets/32x_2d",
    "3d": "z2/sheets/32x_3d",
    "40": "tc/sheets/32x_40",
    "4a": "scenes/results3/sheets/32x_4a",
    "4d": "z10/sheets/32x_4d",
    "55": "title/sheets/32x_55",
    "58": "lobby2/sheets/32x_58",
    "59": "lobby2/sheets/32x_59",
    "5e": "lobby2/sheets/32x_5e",
}


class Sheet:
    def __init__(self, bank):
        base = os.path.join(WORK, SHEETS[bank])
        self.bank = bank
        self.img = Image.open(base + ".png")
        assert self.img.mode == "P", base
        self.px = np.array(self.img)
        self.palette = self.img.getpalette()
        self.frames = {}
        for line in open(base + ".txt", encoding="utf8"):
            line = line.split("#")[0].split()
            if not line:
                continue
            if line[0] == "hotspot":
                self.hot = (int(line[1]), int(line[2]))
            elif line[0] == "frame" and len(line) >= 10 and line[6] not in ("empty", "same"):
                ff = line[1]
                X, Y, W, H, x0, x1, y0, y1 = map(int, line[2:10])
                self.frames[ff] = dict(X=X, Y=Y, x0=x0, x1=x1, y0=y0, y1=y1)

    def frame(self, ff):
        """(pixels HxW uint8, box dict) of frame ff's box."""
        f = self.frames[ff]
        bx = f["X"] + self.hot[0] + f["x0"]
        by = f["Y"] + self.hot[1] + f["y0"]
        w = f["x1"] - f["x0"]
        h = f["y1"] - f["y0"] + 1
        return self.px[by:by + h, bx:bx + w].copy(), f

    def rgb(self, idx):
        p = self.palette
        return tuple(p[3 * idx:3 * idx + 3])


_sheets = {}


def sheet(bank):
    if bank not in _sheets:
        _sheets[bank] = Sheet(bank)
    return _sheets[bank]


# ---------------------------------------------------------------- fonts

class BDF:
    def __init__(self, path):
        self.glyphs = {}
        cur = None
        bitmap = None
        for line in open(path, encoding="utf8"):
            t = line.split()
            if not t:
                continue
            if t[0] == "ENCODING":
                cur = {"cp": int(t[1])}
            elif t[0] == "DWIDTH" and cur is not None:
                cur["dw"] = int(t[1])
            elif t[0] == "BBX" and cur is not None:
                cur["bbx"] = tuple(map(int, t[1:5]))
            elif t[0] == "BITMAP":
                bitmap = []
            elif t[0] == "ENDCHAR":
                cur["rows"] = bitmap
                self.glyphs[cur["cp"]] = cur
                cur = None
                bitmap = None
            elif bitmap is not None:
                bitmap.append(int(t[0], 16))
        self.ascent = 7

    def has(self, ch):
        return ord(ch) in self.glyphs

    def glyph(self, ch):
        """8-row mask (rows = ascent 7 + descent 1), width = advance."""
        g = self.glyphs[ord(ch)]
        bw, bh, bx, by = g["bbx"]
        dw = g["dw"]
        m = np.zeros((8, dw), bool)
        nbytes = (bw + 7) // 8
        top = self.ascent - (by + bh)
        for r, v in enumerate(g["rows"]):
            for c in range(bw):
                if v >> (nbytes * 8 - 1 - c) & 1:
                    y, x = top + r, bx + c
                    if 0 <= y < 8 and 0 <= x < dw:
                        m[y, x] = True
        return m


_bdf = None


def fusion():
    global _bdf
    if _bdf is None:
        _bdf = BDF(FUSION_BDF)
    return _bdf


def trim_cols(m):
    cols = np.where(m.any(0))[0]
    if len(cols) == 0:
        return m[:, :0]
    return m[:, cols[0]:cols[-1] + 1]


def trim(m):
    rows = np.where(m.any(1))[0]
    cols = np.where(m.any(0))[0]
    if len(rows) == 0:
        return m[:0, :0]
    return m[rows[0]:rows[-1] + 1, cols[0]:cols[-1] + 1]


def fusion_text(text, gap=1, trim_glyphs=True):
    """Mask of text in Fusion Pixel 8px; each glyph trimmed to its ink and
    separated by `gap` columns (spaces give 3 columns)."""
    f = fusion()
    parts = []
    for ch in text:
        if ch == " ":
            parts.append(np.zeros((8, 3), bool))
            continue
        if not f.has(ch):
            raise KeyError("Fusion Pixel 8px has no glyph for %r" % ch)
        g = f.glyph(ch)
        if trim_glyphs:
            g = trim_cols(g)
        parts.append(g)
    out = []
    for i, p in enumerate(parts):
        if i:
            out.append(np.zeros((8, gap), bool))
        out.append(p)
    return np.concatenate(out, 1)


def scale(m, s):
    return np.kron(m, np.ones((s, s), bool)).astype(bool)


def ttf_path(name):
    for d in (USER_FONTS, "C:/Windows/Fonts"):
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    raise FileNotFoundError(name)


def ttf_glyph(ch, font, size, thresh=128, ss=1):
    """1-bit mask of one character rendered with a TrueType font."""
    f = ImageFont.truetype(ttf_path(font), size * ss)
    l, t, r, b = f.getbbox(ch)
    im = Image.new("L", (r - l + 4 * ss, b - t + 4 * ss), 0)
    ImageDraw.Draw(im).text((2 * ss - l, 2 * ss - t), ch, font=f, fill=255)
    if ss > 1:
        im = im.resize((im.width // ss, im.height // ss), Image.BOX)
    return trim(np.array(im) >= thresh)


def ttf_text(text, font, size, thresh=128, gap=1, ss=4, space=None):
    """1-bit mask of a string in a TrueType font: glyphs on one baseline,
    each trimmed to its ink columns and `gap` columns apart."""
    f = ImageFont.truetype(ttf_path(font), size * ss)
    l, top, r, b = f.getbbox("國")
    H = (b - top) + 8 * ss
    parts = []
    for ch in text:
        if ch == " ":
            parts.append(np.zeros((H // ss, space if space is not None else max(2, size // 4)), bool))
            continue
        gl, gt, gr, gb = f.getbbox(ch)
        im = Image.new("L", (gr - gl + 4 * ss, H), 0)
        ImageDraw.Draw(im).text((2 * ss - gl, 4 * ss - top), ch, font=f, fill=255)
        im = im.resize((im.width // ss, im.height // ss), Image.BOX)
        parts.append(trim_cols(np.array(im) >= thresh))
    return hcat(parts, gap=gap)


def fit(m, w, h):
    """Nearest-neighbour resize of a mask to w x h."""
    im = Image.fromarray(m.astype(np.uint8) * 255).resize((w, h), Image.NEAREST)
    return np.array(im) > 127


def hcat(parts, gap=1, h=None):
    h = h or max(p.shape[0] for p in parts)
    out = []
    for i, p in enumerate(parts):
        if i:
            out.append(np.zeros((h, gap), bool))
        q = np.zeros((h, p.shape[1]), bool)
        q[:p.shape[0]] = p
        out.append(q)
    return np.concatenate(out, 1)


def dilate(m, mode="8"):
    p = np.pad(m, 1)
    o = p.copy()
    H, W = p.shape
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if mode == "4" and dx and dy:
                continue
            o[1:-1, 1:-1] |= p[1 + dy:H - 1 + dy, 1 + dx:W - 1 + dx]
    return o[1:-1, 1:-1]


def shift(m, dx, dy):
    o = np.zeros_like(m)
    H, W = m.shape
    ys, yd = (slice(0, H - dy), slice(dy, H)) if dy >= 0 else (slice(-dy, H), slice(0, H + dy))
    xs, xd = (slice(0, W - dx), slice(dx, W)) if dx >= 0 else (slice(-dx, W), slice(0, W + dx))
    o[yd, xd] = m[ys, xs]
    return o


def pad(m, l=0, t=0, r=0, b=0):
    return np.pad(m, ((t, b), (l, r)))


def save_indexed(arr, palette, path):
    im = Image.fromarray(arr.astype(np.uint8), "P")
    im.putpalette(palette)
    im.save(path, optimize=False)


def preview(arr, palette, s=3, bg=(40, 40, 48)):
    """RGB preview of an indexed array, 0 shown as bg."""
    pal = np.array(palette, np.uint8).reshape(-1, 3)
    rgb = pal[arr]
    rgb[arr == 0] = bg
    im = Image.fromarray(rgb, "RGB")
    return im.resize((im.width * s, im.height * s), Image.NEAREST)
