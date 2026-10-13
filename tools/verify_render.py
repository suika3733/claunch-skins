# -*- coding: utf-8 -*-
"""Render the skin exactly as CLaunch interprets it (border-aware tiling)."""
import os
from PIL import Image, ImageDraw

BASE = os.path.dirname(os.path.abspath(__file__))
S = os.path.join(BASE, "macOS Sonoma")
L = lambda n: Image.open(os.path.join(S, n)).convert("RGBA")


def nine_slice(img, box, ow, oh, border):
    l, t, r, b = border
    x0, y0, x1, y1 = box
    src = img.crop((x0, y0, x1, y1))
    sw, sh = src.size
    out = Image.new("RGBA", (ow, oh), (0, 0, 0, 0))
    ocw, och = ow - l - r, oh - t - b

    def put(region, size, pos):
        if size[0] <= 0 or size[1] <= 0:
            return
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
    """method=tile + horizontal border: fixed ends, tiled middle"""
    l, t, r, b = border
    x0, y0, x1, y1 = box
    src = img.crop((x0, y0, x1, y1))
    sw, sh = src.size
    out = Image.new("RGBA", (ow, oh), (0, 0, 0, 0))
    out.alpha_composite(src.crop((0, 0, l, sh)), (0, 0))
    out.alpha_composite(src.crop((sw - r, 0, sw, sh)), (ow - r, 0))
    mid = src.crop((l, 0, sw - r, sh))
    for x in range(l, ow - r, mid.width):
        out.alpha_composite(mid, (x, 0))
    return out.crop((0, 0, ow, oh))


def tile(img, box, ow, oh):
    src = img.crop(box)
    out = Image.new("RGBA", (ow, oh), (0, 0, 0, 0))
    for y in range(0, oh, src.height):
        for x in range(0, ow, src.width):
            out.alpha_composite(src, (x, y))
    return out


def render_window(w, h, hover_row=0):
    win = L("window.png")
    layer = nine_slice(win, (0, 0, 48, 80), w, h, (12, 34, 12, 20))
    layer.alpha_composite(h_band(win, (0, 0, 48, 34), w, 34, (12, 0, 12, 0)), (0, 0))
    layer.alpha_composite(h_band(win, (0, 60, 48, 80), w, 20, (12, 0, 12, 0)), (0, h - 20))
    layer.alpha_composite(tile(win, (0, 34, 12, 60), 12, h - 54), (0, 34))
    layer.alpha_composite(tile(win, (36, 34, 48, 60), 12, h - 54), (w - 12, 34))

    wb = L("win_buttons.png")
    for col, x in enumerate((13, 33, 53)):
        layer.alpha_composite(wb.crop((col * 12, hover_row * 12,
                                       col * 12 + 12, hover_row * 12 + 12)), (x, 11))
    sr = L("search.png")
    layer.alpha_composite(sr.crop((0, hover_row * 20, 20, hover_row * 20 + 20)), (w - 31, 7))
    return layer


def checker(w, h, a=(138, 138, 143), b=(120, 120, 125), s=8):
    im = Image.new("RGB", (w, h), a)
    d = ImageDraw.Draw(im)
    for y in range(0, h, s):
        for x in range(0, w, s):
            if (x // s + y // s) % 2:
                d.rectangle([x, y, x + s - 1, y + s - 1], fill=b)
    return im.convert("RGBA")


# normal state
W, H = 420, 250
sheet = checker(W + 60, H + 60)
sheet.alpha_composite(render_window(W, H, 0), (30, 30))
# hover state, half overlapping for comparison
sheet.alpha_composite(render_window(300, 160, 1), (90, 150))
sheet.convert("RGB").save(os.path.join(BASE, "verify-window.png"))
print("wrote verify-window.png")
