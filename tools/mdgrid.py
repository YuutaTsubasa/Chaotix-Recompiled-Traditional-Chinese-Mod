"""Mega Drive plane text dumps (phase 3): read `Dump/Text/text_<n>.txt`.

The game's DUMP GRAPHICS writes, per menu screen, the runs of tiles each
plane shows (`plane A|B|W`, `row <hash>[:h|:v|:hv] ...`, the run's plane cell
and palette lines). This module turns a dump into a grid per plane, cell ->
token, so that a pattern can be any rectangle of cells (a banner's letters
span several rows), and renders cells from the dumped `md_<hash>.png` tiles
for inspection (work/, never shipped).

Run with the Windows Python that has Pillow and numpy.
"""
import os
import re

import numpy as np
from PIL import Image

RUN = re.compile(r"# run (\d+): screen x (-?\d+) y (-?\d+), (\d+) tiles? .*plane cell (\d+),(\d+), palette line ([\d,]+)")


class Dump:
    """One text_<n>.txt: runs and the grid {(plane, cx, cy): (token, lines, sx, sy)}."""

    def __init__(self, path):
        self.path = path
        self.dir = os.path.dirname(os.path.dirname(path))  # the Dump folder (md_ tiles)
        self.runs = []
        self.grid = {}
        cur = None
        for line in open(path, encoding="utf8"):
            m = RUN.match(line)
            if m:
                cur = dict(id=int(m.group(1)), sx=int(m.group(2)), sy=int(m.group(3)), n=int(m.group(4)),
                           cx=int(m.group(5)), cy=int(m.group(6)), lines=m.group(7))
                continue
            if cur is None:
                continue
            t = line.split()
            if t and t[0] == "plane":
                cur["plane"] = t[1]
            elif t and t[0] == "row":
                cur["tokens"] = t[1:]
                self.runs.append(cur)
                for k, tok in enumerate(cur["tokens"]):
                    self.grid[(cur["plane"], cur["cx"] + k, cur["cy"])] = (tok, cur["lines"], cur["sx"] + 8 * k, cur["sy"])
                cur = None

    def rect(self, plane, cx, cy, w, h):
        """Rows of tokens of a rectangle of cells (KeyError if a cell is not in a run)."""
        return [[self.grid[(plane, cx + i, cy + j)][0] for i in range(w)] for j in range(h)]

    def tile(self, tok):
        """(8x8 indices, palette) of a token, flipped as the token says."""
        h, _, fl = tok.partition(":")
        f = os.path.join(self.dir, "md_%s.png" % h)
        if not os.path.exists(f):  # not dumped (drawn behind something): grey
            return np.full((8, 8), 15, np.uint8), [128] * 768
        im = Image.open(f)
        a = np.array(im)
        if "h" in fl:
            a = a[:, ::-1]
        if "v" in fl:
            a = a[::-1]
        return a, im.getpalette()

    def render(self, plane, cx, cy, w, h, scale=1):
        """RGB picture of a rectangle (missing cells grey), for inspection."""
        out = np.full((h * 8, w * 8, 3), 60, np.uint8)
        for j in range(h):
            for i in range(w):
                g = self.grid.get((plane, cx + i, cy + j))
                if not g:
                    continue
                a, pal = self.tile(g[0])
                p = np.array(pal[:48], np.uint8).reshape(16, 3)
                rgb = p[a]
                rgb[a == 0] = (255, 0, 255)
                out[j * 8:j * 8 + 8, i * 8:i * 8 + 8] = rgb
        im = Image.fromarray(out)
        return im.resize((im.width * scale, im.height * scale), Image.NEAREST)

    def indices(self, plane, cx, cy, w, h):
        """Indices of a rectangle (-1 where a cell is missing)."""
        out = np.full((h * 8, w * 8), -1, np.int16)
        for j in range(h):
            for i in range(w):
                g = self.grid.get((plane, cx + i, cy + j))
                if g:
                    out[j * 8:j * 8 + 8, i * 8:i * 8 + 8] = self.tile(g[0])[0]
        return out

    def sample_palette(self, shot, plane, cx, cy, w, h):
        """16 RGB colours of the rectangle's palette line, read off a
        screenshot taken while the screen looked as in the dump (index ->
        the most common screen colour where the tiles use it); unknown
        indices stay grey. Only for the PNG's palette (previews): the game
        draws the indices with the line's own colours."""
        im = np.array(Image.open(shot).convert("RGB"))
        votes = {}
        for j in range(h):
            for i in range(w):
                g = self.grid.get((plane, cx + i, cy + j))
                if not g:
                    continue
                a, _ = self.tile(g[0])
                sx, sy = g[2], g[3]
                for y in range(8):
                    for x in range(8):
                        v = int(a[y, x])
                        if v and 0 <= sy + y < im.shape[0] and 0 <= sx + x < im.shape[1]:
                            c = tuple(int(t) for t in im[sy + y, sx + x])
                            votes.setdefault(v, {}).setdefault(c, 0)
                            votes[v][c] += 1
        pal = [[128, 128, 128] for _ in range(16)]
        pal[0] = [0, 0, 0]
        for v, cs in votes.items():
            pal[v] = list(max(cs.items(), key=lambda kv: kv[1])[0])
        return pal


def main():
    """python tools/mdgrid.py DUMP PLANE CX CY W H [SHOT]: the rectangle's
    rows of tokens (and its palette from SHOT) as JSON for a spec."""
    import json
    import sys
    d = Dump(sys.argv[1])
    pl = sys.argv[2]
    cx, cy, w, h = map(int, sys.argv[3:7])
    out = {"plane": pl, "rows": [" ".join(r) for r in d.rect(pl, cx, cy, w, h)]}
    lines = sorted({d.grid[(pl, cx + i, cy + j)][1] for i in range(w) for j in range(h)})
    out["lines_seen"] = lines
    if len(sys.argv) > 7:
        out["preview_palette"] = d.sample_palette(sys.argv[7], pl, cx, cy, w, h)
    print(json.dumps(out))


if __name__ == "__main__":
    main()
