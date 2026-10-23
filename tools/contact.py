"""Contact sheet of the verification screenshots (preview/scenes/*/*.png).

    python tools/contact.py [--name NAME] [SCENE ...]   -> preview/<NAME>_<n>.png
                                                       (default NAME: contact)

The screenshots contain the game's art: preview/ is gitignored.
"""
import glob
import os
import sys

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "preview")


def main():
    want = sys.argv[1:]
    name = "contact"
    if want[:1] == ["--name"]:
        name, want = want[1], want[2:]
    files = []
    for d in sorted(glob.glob(os.path.join(P, "scenes", "*"))):
        if want and os.path.basename(d) not in want:
            continue
        files += sorted(glob.glob(os.path.join(d, "*.png")))
    cols, per_page = 3, 12
    for page in range(0, len(files), per_page):
        chunk = files[page:page + per_page]
        ims = [Image.open(f).convert("RGB") for f in chunk]
        w = max(i.width for i in ims)
        h = max(i.height for i in ims)
        rows = (len(ims) + cols - 1) // cols
        M = Image.new("RGB", (cols * w, rows * (h + 12)), (40, 40, 40))
        d = ImageDraw.Draw(M)
        for k, (f, im) in enumerate(zip(chunk, ims)):
            x, y = (k % cols) * w, (k // cols) * (h + 12)
            M.paste(im, (x, y + 12))
            d.text((x + 2, y), os.path.basename(os.path.dirname(f)) + "/" + os.path.basename(f), fill=(255, 255, 0))
        out = os.path.join(P, "%s_%d.png" % (name, page // per_page))
        M.save(out)
        print(out)


if __name__ == "__main__":
    main()
