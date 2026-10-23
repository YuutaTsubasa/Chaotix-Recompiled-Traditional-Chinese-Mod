"""Mega Drive sprite dumps (phase 4): read `Dump/Text/sprites_<n>.txt`.

The game's DUMP GRAPHICS writes, per menu screen, the sprites on screen
grouped into suggested patterns (`# group n: screen x X y Y, ...`, then one
`sprite DX DY WxH[:flip] hash...` line per sprite, tiles column by column).
This module reads the groups and renders a group (or any list of sprite
lines) from the dumped `md_<hash>.png` tiles, as palette indices, for
inspection and to measure the letters (work/, never shipped).

    python tools/mdspr.py DUMP.txt [GROUP ...]   -> list the groups / write
                                                    work/p4/_g<group>.png (4x)

Run with the Windows Python that has Pillow and numpy.
"""
import os
import re
import sys

import numpy as np
from PIL import Image

GROUP = re.compile(r"# group (\d+): screen x (-?\d+) y (-?\d+), (\d+) sprites?, (\d+) tiles?, (\d+)x(\d+) pixels, palette line (\d), priority (\d)")
ENTRY = re.compile(r"#\s+entry (\d+) \(list place (\d+)\) at (-?\d+),(-?\d+), tile ([0-9a-f]+)")


def parse_sprite(line):
    """'sprite DX DY WxH[:f] h...' -> dict(dx, dy, w, h, flip, tiles)."""
    t = line.split()
    assert t[0] == "sprite", line
    size, _, flip = t[3].partition(":")
    w, h = map(int, size.split("x"))
    tiles = t[4:]
    assert len(tiles) == w * h, line
    return dict(dx=int(t[1]), dy=int(t[2]), w=w, h=h, flip=flip, tiles=tiles)


def sprite_line(s):
    return "sprite %d %d %dx%d%s %s" % (s["dx"], s["dy"], s["w"], s["h"], ":" + s["flip"] if s["flip"] else "", " ".join(s["tiles"]))


class Dump:
    def __init__(self, path):
        self.path = path
        self.dir = os.path.dirname(os.path.dirname(path))
        self.groups = {}
        cur = None
        for line in open(path, encoding="utf8"):
            m = GROUP.match(line)
            if m:
                g = dict(id=int(m.group(1)), x=int(m.group(2)), y=int(m.group(3)), w=int(m.group(6)),
                         h=int(m.group(7)), pal=int(m.group(8)), pri=int(m.group(9)), sprites=[], entries=[])
                self.groups[g["id"]] = cur = g
                continue
            m = ENTRY.match(line)
            if m and cur:
                cur["entries"].append(dict(entry=int(m.group(1)), x=int(m.group(3)), y=int(m.group(4)), tile=m.group(5)))
                continue
            if line.startswith("sprite") and cur:
                cur["sprites"].append(parse_sprite(line))

    def tile(self, h):
        f = os.path.join(self.dir, "md_%s.png" % h)
        if not os.path.exists(f):
            return np.full((8, 8), 15, np.uint8), None
        im = Image.open(f)
        return np.array(im), im.getpalette()

    def render(self, sprites):
        """(indices HxW, palette, x0, y0) of sprites laid out at their DX DY
        (-1 where no sprite), flipped as they say."""
        x0 = min(s["dx"] for s in sprites)
        y0 = min(s["dy"] for s in sprites)
        x1 = max(s["dx"] + 8 * s["w"] for s in sprites)
        y1 = max(s["dy"] + 8 * s["h"] for s in sprites)
        out = np.full((y1 - y0, x1 - x0), -1, np.int16)
        pal = None
        for s in sprites:
            blk = np.zeros((8 * s["h"], 8 * s["w"]), np.int16)
            for k, h in enumerate(s["tiles"]):
                cx, cy = k // s["h"], k % s["h"]
                a, p = self.tile(h)
                pal = pal or p
                blk[8 * cy:8 * cy + 8, 8 * cx:8 * cx + 8] = a
            if "h" in s["flip"]:
                blk = blk[:, ::-1]
            if "v" in s["flip"]:
                blk = blk[::-1]
            X, Y = s["dx"] - x0, s["dy"] - y0
            reg = out[Y:Y + blk.shape[0], X:X + blk.shape[1]]
            sel = (blk != 0) | (reg < 0)
            reg[sel] = blk[sel]
        return out, pal, x0, y0


def to_rgb(ind, pal, s=4, bg=(255, 0, 255)):
    p = np.array((pal or [128] * 48)[:48], np.uint8).reshape(16, 3)
    rgb = p[np.clip(ind, 0, 15)]
    rgb[ind <= 0] = bg
    im = Image.fromarray(rgb, "RGB")
    return im.resize((im.width * s, im.height * s), Image.NEAREST)


def main():
    d = Dump(sys.argv[1])
    want = [int(a) for a in sys.argv[2:]]
    for gid, g in sorted(d.groups.items()):
        if want and gid not in want:
            continue
        print("group %d at %d,%d %dx%d line %d, %d sprites" % (gid, g["x"], g["y"], g["w"], g["h"], g["pal"], len(g["sprites"])))
        if want:
            ind, pal, _, _ = d.render(g["sprites"])
            out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "work", "p4", "_g%d.png" % gid)
            to_rgb(ind, pal).save(out)
            print(out)
            for row in ind:
                print("".join(" .123456789abcdef"[v + 1] for v in row))


if __name__ == "__main__":
    main()
