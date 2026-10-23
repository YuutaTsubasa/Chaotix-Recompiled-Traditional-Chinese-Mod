"""Showcase screenshots for the mod page from preview/showcase (tools/render_showcase.sh).

    python tools/showcase.py   -> release/screenshots/NN_<name>.png

Each 426x224 widescreen shot (a wider one is cropped to the centre) is
scaled 3x nearest-neighbour and centred on a 1280x720 black picture.
The screenshots contain the game's art (gitignored, for the mod page only).
"""
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "preview", "showcase")
OUT = os.path.join(ROOT, "release", "screenshots")
PICK = [("title", 1760), ("menu", 1890), ("card", 640), ("hud", 1100), ("results", 3900), ("special", 600),
        ("lobby", 1000), ("dataload", 2240), ("playersel", 2500), ("options", 2140)]


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith(".png"):
            os.remove(os.path.join(OUT, f))
    for k, (name, frame) in enumerate(PICK, 1):
        im = Image.open(os.path.join(SRC, name, "frame_%05d.png" % frame)).convert("RGB")
        if im.width > 426:
            x = (im.width - 426) // 2
            im = im.crop((x, 0, x + 426, im.height))
        im = im.resize((im.width * 3, im.height * 3), Image.NEAREST)
        out = Image.new("RGB", (1280, 720), (0, 0, 0))
        out.paste(im, ((1280 - im.width) // 2, (720 - im.height) // 2))
        p = os.path.join(OUT, "%02d_%s.png" % (k, name))
        out.save(p, optimize=True)
        print(p)


if __name__ == "__main__":
    main()
