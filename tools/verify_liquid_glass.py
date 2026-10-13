# -*- coding: utf-8 -*-
"""Verify the Liquid Glass skins: XML structure vs the official Glass.zip,
and a faithful render of the window using CLaunch's 9-slice rules."""
import os, re, zipfile, difflib
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw

BASE = os.path.dirname(os.path.abspath(__file__))
SS = 4
WIN_W, WIN_H, R, SIDE, BAR_H, BOT_H = 64, 98, 26, 28, 42, 28
MID_Y0, MID_Y1 = BAR_H, WIN_H - BOT_H
SYSBTN, BTN_OFF, SRCH = 16, (14, 36, 58), 20
TAB_W, TAB_H = 84, 26


def tree(d):
    """nested (tag, children) structure via a real XML parser.
    <br/> inside <comment> is pure text formatting, so drop it."""
    root = ET.fromstring(d)

    def walk(e):
        return (e.tag, [walk(c) for c in e if c.tag != "br"])

    return walk(root)


def drop_block(node, *tags):
    """remove entire <tag>...</tag> subtrees anywhere in the tree"""
    name, kids = node
    return (name, [drop_block(k, *tags) for k in kids if k[0] not in tags])


def fingerprint(node, depth=0):
    out = ["  " * depth + node[0]]
    for c in node[1]:
        out += fingerprint(c, depth + 1)
    return out


def check_xml(folder):
    p = os.path.join(BASE, folder, "skin.xml")
    raw = open(p, "rb").read()
    assert raw[:2] == b"\xff\xfe", "not UTF-16 LE with BOM"
    txt = raw.decode("utf-16")
    ET.fromstring(txt)                       # well-formed?
    ref = tree(zipfile.ZipFile(r"C:\Program Files\CLaunch\Skins\Glass.zip")
               .read("skin.xml").decode("utf-16"))
    mine = tree(txt)
    # strict: our skin must mirror the official block-for-block
    # (only <br/> inside <comment> is normalised away as text formatting)
    a, b = fingerprint(ref), fingerprint(mine)
    same = a == b
    print(f"[{folder}] xml OK, {len(txt)} chars, elements {len(b)}  "
          f"structure {'== official Glass.zip' if same else 'DIFFERS'}")
    if not same:
        d = [l for l in difflib.unified_diff(a, b, "official", "mine", lineterm="")][:30]
        print("\n".join(d))
    # every referenced image must exist
    refs = sorted(set(re.findall(r'image="([^"]+)"', txt)))
    missing = [r for r in refs if not os.path.exists(os.path.join(BASE, folder, r))]
    print(f"   images referenced: {len(refs)}, missing: {missing or 'none'}")
    return same and not missing


# ---------------------------------------------------------------- render
def L(folder, n):
    return Image.open(os.path.join(BASE, folder, n)).convert("RGBA")


def nine_slice(img, box, ow, oh, border):
    l, t, r, b = border
    src = img.crop(box)
    sw, sh = src.size
    out = Image.new("RGBA", (ow, oh), (0, 0, 0, 0))
    ocw, och = ow - l - r, oh - t - b

    def put(region, size, pos):
        if size[0] > 0 and size[1] > 0:
            out.alpha_composite(region.resize(size, Image.Resampling.LANCZOS), pos)

    put(src.crop((0, 0, l, t)), (l, t), (0, 0))
    put(src.crop((sw - r, 0, sw, t)), (r, t), (ow - r, 0))
    put(src.crop((0, sh - b, l, sh)), (l, b), (0, oh - b))
    put(src.crop((sw - r, sh - b, sw, sh)), (r, b), (ow - r, oh - b))
    put(src.crop((l, 0, sw - r, t)), (ocw, t), (l, 0))
    put(src.crop((l, sh - b, sw - r, sh)), (ocw, b), (l, oh - b))
    put(src.crop((0, t, l, sh - b)), (l, och), (0, t))
    put(src.crop((sw - r, t, sw, sh - b)), (r, och), (ow - r, t))
    put(src.crop((l, t, sw - r, sh - b)), (ocw, och), (l, t))
    return out


def h_band(img, box, ow, oh, border):
    """method=stretch + horizontal border: fixed ends, stretched middle"""
    l, t, r, b = border
    src = img.crop(box)
    sw, sh = src.size
    out = Image.new("RGBA", (ow, oh), (0, 0, 0, 0))
    out.alpha_composite(src.crop((0, 0, l, sh)).resize((l, oh), Image.Resampling.LANCZOS), (0, 0))
    out.alpha_composite(src.crop((sw - r, 0, sw, sh)).resize((r, oh), Image.Resampling.LANCZOS),
                        (ow - r, 0))
    mid = src.crop((l, 0, sw - r, sh)).resize((ow - l - r, oh), Image.Resampling.LANCZOS)
    out.alpha_composite(mid, (l, 0))
    return out


def render(folder, w, h, hover=False):
    win = L(folder, "window.png")
    bg = L(folder, "background.png")
    # CLaunch frames are ONLY four bands (no centre fill) — the interior comes
    # from <background>, which fills the area enclosed by the frames.
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    lay.alpha_composite(h_band(win, (0, 0, WIN_W, BAR_H), w, BAR_H, (SIDE, 0, SIDE, 0)), (0, 0))
    lay.alpha_composite(h_band(win, (0, MID_Y1, WIN_W, WIN_H), w, BOT_H, (SIDE, 0, SIDE, 0)),
                        (0, h - BOT_H))
    lay.alpha_composite(win.crop((0, MID_Y0, SIDE, MID_Y1)).resize(
        (SIDE, h - BAR_H - BOT_H), Image.Resampling.LANCZOS), (0, BAR_H))
    lay.alpha_composite(win.crop((WIN_W - SIDE, MID_Y0, WIN_W, MID_Y1)).resize(
        (SIDE, h - BAR_H - BOT_H), Image.Resampling.LANCZOS), (w - SIDE, BAR_H))
    lay.alpha_composite(bg.resize((w - SIDE * 2, h - BAR_H - BOT_H), Image.Resampling.LANCZOS),
                        (SIDE, BAR_H))
    wb = L(folder, "win_buttons.png")
    row = 1 if hover else 0
    for ci, x in enumerate(BTN_OFF):
        lay.alpha_composite(wb.crop((ci * SYSBTN, row * SYSBTN,
                                     ci * SYSBTN + SYSBTN, row * SYSBTN + SYSBTN)),
                            (x, (BAR_H - SYSBTN) // 2))
    sr = L(folder, "search.png")
    lay.alpha_composite(sr.crop((0, row * SRCH, SRCH, row * SRCH + SRCH)),
                        (w - SRCH - 12, (BAR_H - SRCH) // 2))
    return lay


def checker(w, h, a=(96, 104, 118), b=(74, 82, 96), s=10):
    im = Image.new("RGB", (w, h), a)
    d = ImageDraw.Draw(im)
    for y in range(0, h, s):
        for x in range(0, w, s):
            if (x // s + y // s) % 2:
                d.rectangle([x, y, x + s - 1, y + s - 1], fill=b)
    return im.convert("RGBA")


if __name__ == "__main__":
    ok = all(check_xml(f) for f in ("Liquid Glass", "Liquid Glass Dark"))
    print("XML check:", "PASS" if ok else "FAIL")

    W, H = 430, 270
    sheet = checker(W + 80, H * 2 + 140)
    for i, folder in enumerate(("Liquid Glass", "Liquid Glass Dark")):
        sheet.alpha_composite(render(folder, W, H, False), (30, 30 + i * (H + 60)))
        sheet.alpha_composite(render(folder, 260, 150, True), (150, 190 + i * (H + 60)))
    sheet.convert("RGB").save(os.path.join(BASE, "verify-liquid-glass.png"))
    print("wrote verify-liquid-glass.png", sheet.size)
