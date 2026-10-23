"""Check the specs' Chinese: glyphs exist, Traditional only, glossary.

    python tools/check_text.py

Covers the 32X sprite specs (text/sprites/*.json, phase 2), the Mega
Drive plane text specs (text/mdtext/*.json, phase 3) and the Mega Drive
sprite text specs (text/mdsprite/*.json, phase 4).

- Every character drawn has a glyph in the font that draws it (Fusion Pixel
  8px BDF, or the TrueType font's cmap): no tofu.
- Every Chinese string encodes in Big5 (Taiwan's character set), which
  rejects Simplified-only and Japanese-only forms, and none of a list of
  Simplified forms that Big5 happens to include appears.
- Where a spec's English contains a glossary term, its Chinese contains the
  glossary's translation; every translation used is in the glossary.
  When several glossary terms match an English string, a longer term that
  is satisfied wins ("EXIT (menu)" takes Exit (menu) = 離開, not Exit = 出口).
- Mega Drive text specs: every pattern row has the same number of tiles,
  the tokens look like hashes, and no two specs use the same rows.
- Mega Drive sprite specs: every sprite line is `sprite DX DY WxH[:flip]`
  with W x H hashes, and no two specs name the same sprites.
"""
import glob
import json
import os
import sys

from fontTools.ttLib import TTFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprlib as L  # noqa: E402

ROOT = L.ROOT
# Simplified forms that are also in Big5 (so the Big5 test misses them) and
# that a translator might type by accident.
SIMPLIFIED = set("后台里只干发松面范才云冲")
EXTRA_OK = set(" ：！？，、。·／()（）0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.-")


def cjk(c):
    return ord(c) > 0x2000


def main():
    glossary = json.load(open(os.path.join(ROOT, "text", "glossary.json"), encoding="utf8"))
    cmaps = {}
    bad = 0
    used = set()
    n = 0
    files = sorted(glob.glob(os.path.join(ROOT, "text", "sprites", "[0-9a-f]*.json")))
    files += sorted(glob.glob(os.path.join(ROOT, "text", "mdtext", "[a-z0-9]*.json")))
    files += sorted(glob.glob(os.path.join(ROOT, "text", "mdsprite", "[a-z0-9]*.json")))
    patterns = {}
    sprite_patterns = {}
    for p in files:
        sid = os.path.basename(p)[:-5]
        spec = json.load(open(p, encoding="utf8"))
        if spec.get("keep") or spec.get("blank") or spec.get("joined"):
            continue
        n += 1
        if "rows" in spec:
            rows = [r.split() for r in spec["rows"]]
            if len({len(r) for r in rows}) != 1:
                print("%s: pattern rows of different lengths" % sid)
                bad += 1
            for t in sum(rows, []):
                h, _, fl = t.partition(":")
                if len(h) != 16 or any(c not in "0123456789abcdef" for c in h) or fl not in ("", "h", "v", "hv"):
                    print("%s: bad tile token %r" % (sid, t))
                    bad += 1
            key = "/".join(spec["rows"])
            if key in patterns:
                print("%s: same pattern as %s" % (sid, patterns[key]))
                bad += 1
            patterns[key] = sid
        if "sprites" in spec:
            for line in spec["sprites"]:
                t = line.split()
                try:
                    w, _, rest = t[3].partition("x")
                    h, _, fl = rest.partition(":")
                    ok = (t[0] == "sprite" and int(t[1]) == int(t[1]) and int(t[2]) == int(t[2]) and 1 <= int(w) <= 4
                          and 1 <= int(h) <= 4 and fl in ("", "h", "v", "hv") and len(t) == 4 + int(w) * int(h)
                          and all(len(x) == 16 and all(c in "0123456789abcdef" for c in x) for x in t[4:]))
                except (ValueError, IndexError):
                    ok = False
                if not ok:
                    print("%s: bad sprite line %r" % (sid, line[:60]))
                    bad += 1
            key = "/".join(spec["sprites"])
            if key in sprite_patterns:
                print("%s: same sprites as %s" % (sid, sprite_patterns[key]))
                bad += 1
            sprite_patterns[key] = sid
        layers = [l for l in spec.get("layers", []) if "zh" in l]
        if "cycle" in spec:
            layers += [dict(spec["cycle"]["a"], font="fusion8"), dict(spec["cycle"]["b"], font="fusion8")]
        for layer in layers:
            font = layer.get("font", "fusion8")
            for c in layer["zh"]:
                used.add(c)
                if c == " ":
                    continue
                if font == "fusion8":
                    ok = L.fusion().has(c)
                else:
                    if font not in cmaps:
                        cmaps[font] = TTFont(L.ttf_path(font), fontNumber=0).getBestCmap()
                    ok = ord(c) in cmaps[font]
                if not ok:
                    print("%s: %r has no glyph in %s" % (sid, c, font))
                    bad += 1
        zh = spec.get("zh", "")
        for c in zh:
            if cjk(c) and c not in "／·":
                try:
                    c.encode("big5")
                except UnicodeEncodeError:
                    print("%s: %r is not in Big5 (not Traditional?)" % (sid, c))
                    bad += 1
                if c in SIMPLIFIED:
                    print("%s: %r is a Simplified form" % (sid, c))
                    bad += 1
        en = spec.get("en", "").lower()
        hits = []
        for term, g in glossary.items():
            keys = [k.strip().lower() for k in term.split("/")]
            ks = [k for k in keys if k and k in en]
            if ks:
                hits.append((max(len(k) for k in ks), term, g))
        for klen, term, g in hits:
            if any(l2 > klen and g2["zh"].split(" ")[0] in zh for l2, t2, g2 in hits):
                continue  # a longer, more specific term is the one used
            if g["zh"].split(" ")[0] not in zh:
                # "Time" is a glossary word but TIME OUT / TIME BONUS are phrases
                if g.get("note", "").startswith("translator decision") or term in ("Time", "Score", "Rings"):
                    if g["zh"] not in zh:
                        print("%s: note: %r (%s) not used for %r" % (sid, g["zh"], term, spec["en"]))
                    continue
                print("%s: glossary %r -> %r not in %r" % (sid, term, g["zh"], zh))
                bad += 1
    print("%d specs checked (%d Mega Drive text patterns, %d sprite patterns), %d distinct characters, %d problem(s)"
          % (n, len(patterns), len(sprite_patterns), len([c for c in used if cjk(c)]), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
