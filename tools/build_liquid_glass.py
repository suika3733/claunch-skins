# -*- coding: utf-8 -*-
"""
CLaunch skin generator — iPhone "Liquid Glass" style (iOS 26 inspired).

Builds two variants (light / dark) from one palette table:
  Liquid Glass/       Liquid Glass Dark/
  ├── skin.xml        (UTF-16 LE, 4.20 spec, validated against official Glass.zip)
  └── part PNGs       (4x supersampled, LANCZOS downscaled)

NOTE ON TRANSLUCENCY: CLaunch skins cannot blur the desktop behind them —
that is a DWM/compositor feature the skin format does not expose. The glass
look here is simulated with translucency + a specular inner rim + a soft top
sheen. Alpha is kept fairly high (~80%) so text stays legible on any wallpaper.
"""
import os, zipfile
from PIL import Image, ImageDraw, ImageFilter, ImageChops

SS = 4  # supersample

# ---------------------------------------------------------------- geometry
WIN_W, WIN_H = 64, 98      # 9-slice source: border must be >= corner radius
R            = 26          # window corner radius (Liquid Glass = big, soft corners)
SIDE         = 28          # >= R
BAR_H        = 42
BOT_H        = 28
MID_Y0, MID_Y1 = BAR_H, WIN_H - BOT_H

SYSBTN       = 16          # circular glass window buttons
BTN_OFF      = (14, 36, 58)
SRCH         = 20
TAB_W, TAB_H, TAB_R = 84, 26, 13
BTN_W, BTN_H, BTN_R, BTN_B = 72, 72, 20, 24
MENU_W, MENU_H, MENU_R, MENU_B = 72, 72, 20, 24
ITEM_W, ITEM_H, ITEM_R = 48, 24, 7
ARROW        = 16

FONT = "Microsoft YaHei UI"


def C(hexs, a=255):
    hexs = hexs.lstrip("#")
    return (int(hexs[0:2], 16), int(hexs[2:4], 16), int(hexs[4:6], 16), a)


# ---------------------------------------------------------------- palettes
PALETTES = {
    "light": dict(
        skin_title="Liquid Glass",
        folder="Liquid Glass",
        comment="iPhone 液態玻璃（Liquid Glass）風格皮膚。\n\n"
                "* 需要 32bpp 顯示模式與 Unicode 版 CLaunch 4.20 以上\n"
                "* 半透明玻璃面板：鏡面高光內緣 + 頂部柔光澤\n"
                "* 分頁為玻璃膠囊，選中頁為不透明白\n"
                "* 圓形玻璃視窗鈕（關閉／鎖定／模式），滑過增亮\n"
                "* 右鍵子選單為玻璃面板，選中項為 iOS 系統藍 #007AFF\n"
                "* 注意：CLaunch 皮膚無法對桌面做即時模糊，通透感以半透明模擬",
        glass=(252, 253, 255, 205),      # window fill (rgba)
        glass_edge=(252, 253, 255, 205),
        rim_hi=245, rim_lo=178, rim_bot=215,
        hairline=(0, 0, 0, 26),
        sheen=44,
        sysbtn_fill=(255, 255, 255, 110),
        sysbtn_hover=(255, 255, 255, 205),
        sysbtn_down=(255, 255, 255, 240),
        sysbtn_glyph=(142, 142, 147),
        sysbtn_glyph_hover=(60, 60, 67),
        close_glyph_hover=(255, 59, 48),
        tab_off=(255, 255, 255, 78),
        tab_hover=(255, 255, 255, 140),
        tab_on=(255, 255, 255, 243),
        btn_hover=(255, 255, 255, 98),
        btn_down=(255, 255, 255, 140),
        menu_fill=(252, 253, 255, 222),
        item_sel=C("#007AFF", 242),
        item_multisel=C("#007AFF", 115),
        text_1="#1C1C1E", text_2="#6C6C70", text_3="#8E8E93",
        text_dis="#C7C7CC", text_on_sel="#FFFFFF",
        accent="#007AFF", sel_color="#1C1C1E",
        lock_badge=(28, 28, 30, 190),
        arrow=(142, 142, 147), arrow_hi=(60, 60, 67), arrow_dis=(199, 199, 204),
        scroll_fill=(255, 255, 255, 90), scroll_hov=(255, 255, 255, 165),
        scroll_down=(255, 255, 255, 205),
    ),
    "dark": dict(
        skin_title="Liquid Glass Dark",
        folder="Liquid Glass Dark",
        comment="iPhone 液態玻璃（Liquid Glass）深色版皮膚。\n\n"
                "* 需要 32bpp 顯示模式與 Unicode 版 CLaunch 4.20 以上\n"
                "* 深色半透明玻璃面板：鏡面高光內緣 + 頂部柔光澤\n"
                "* 分頁為玻璃膠囊，選中頁為亮玻璃\n"
                "* 圓形玻璃視窗鈕（關閉／鎖定／模式），滑過增亮\n"
                "* 右鍵子選單為深色玻璃面板，選中項為 iOS 系統藍 #0A84FF",
        glass=(24, 24, 27, 210),
        glass_edge=(24, 24, 27, 210),
        rim_hi=170, rim_lo=82, rim_bot=125,
        hairline=(255, 255, 255, 34),
        sheen=30,
        sysbtn_fill=(255, 255, 255, 40),
        sysbtn_hover=(255, 255, 255, 105),
        sysbtn_down=(255, 255, 255, 150),
        sysbtn_glyph=(174, 174, 178),
        sysbtn_glyph_hover=(245, 245, 247),
        close_glyph_hover=(255, 69, 58),
        tab_off=(255, 255, 255, 34),
        tab_hover=(255, 255, 255, 72),
        tab_on=(255, 255, 255, 168),
        btn_hover=(255, 255, 255, 48),
        btn_down=(255, 255, 255, 78),
        menu_fill=(32, 32, 36, 228),
        item_sel=C("#0A84FF", 242),
        item_multisel=C("#0A84FF", 115),
        text_1="#F2F2F7", text_2="#AEAEB2", text_3="#98989F",
        text_dis="#5A5A5E", text_on_sel="#FFFFFF",
        accent="#0A84FF", sel_color="#3A3A3C",
        lock_badge=(255, 255, 255, 200),
        arrow=(174, 174, 178), arrow_hi=(245, 245, 247), arrow_dis=(90, 90, 94),
        scroll_fill=(255, 255, 255, 30), scroll_hov=(255, 255, 255, 66),
        scroll_down=(255, 255, 255, 100),
    ),
}


# ---------------------------------------------------------------- helpers
def canvas(w, h, bg=(255, 255, 255, 0)):
    return Image.new("RGBA", (w * SS, h * SS), bg)


def rr(d, box, radius, **kw):
    d.rounded_rectangle([v * SS for v in box], radius=radius * SS, **kw)


def emit(img, w, h, path):
    img.resize((w, h), Image.Resampling.LANCZOS).save(path)


def alpha_ramp(h_px, stops):
    """stops: [(fraction, alpha)] -> L image 1 x h*SS"""
    H = h_px * SS
    im = Image.new("L", (1, H))
    p = im.load()
    st = sorted(stops)
    for y in range(H):
        f = y / max(1, H - 1)
        for i in range(len(st) - 1):
            f0, a0 = st[i]
            f1, a1 = st[i + 1]
            if f0 <= f <= f1:
                t = 0 if f1 == f0 else (f - f0) / (f1 - f0)
                p[0, y] = int(a0 + (a1 - a0) * t)
                break
        else:
            p[0, y] = st[-1][1] if f > st[-1][0] else st[0][1]
    return im


def rim_layer(w, h, radius, inset, width, stops, color=(255, 255, 255)):
    """1px specular inner rim, alpha varying vertically"""
    mask = Image.new("L", (w * SS, h * SS), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([inset * SS, inset * SS, (w - inset) * SS - 1, (h - inset) * SS - 1],
                         radius=radius * SS, outline=255, width=max(1, int(width * SS)))
    ramp = alpha_ramp(h, stops).resize((w * SS, h * SS), Image.Resampling.NEAREST)
    a = ImageChops.multiply(mask, ramp)
    lay = Image.new("RGBA", (w * SS, h * SS), color + (0,))
    lay.putalpha(a)
    return lay


def hairline_layer(w, h, radius, inset, color, width=1.0):
    mask = Image.new("L", (w * SS, h * SS), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([inset * SS, inset * SS, (w - inset) * SS - 1, (h - inset) * SS - 1],
                         radius=radius * SS, outline=color[3], width=max(1, int(width * SS)))
    lay = Image.new("RGBA", (w * SS, h * SS), color[:3] + (0,))
    lay.putalpha(mask)
    return lay


def pill(w, h, radius, fill, rim_stops, hairline, badge=None):
    """a glass capsule / squircle used by tabs, buttons, menus"""
    img = canvas(w, h)
    d = ImageDraw.Draw(img)
    rr(d, (0, 0, w - 1, h - 1), radius, fill=fill)
    if hairline:
        img.alpha_composite(hairline_layer(w, h, radius, 0.5, hairline))
    img.alpha_composite(rim_layer(w, h, radius, 0.7, 1.1, rim_stops))
    return img


# ---------------------------------------------------------------- window
def build_window(P, out):
    W, H = WIN_W, WIN_H
    img = canvas(W, H)
    d = ImageDraw.Draw(img)

    rr(d, (0, 0, W - 1, H - 1), R, fill=P["glass"])

    # top sheen: brighter toward the top edge (lives in the fixed-height top band)
    sheen = Image.new("RGBA", (W * SS, H * SS), (255, 255, 255, 0))
    sa = alpha_ramp(H, [(0.0, P["sheen"]), (0.30, 0), (1.0, 0)]).resize(
        (W * SS, H * SS), Image.Resampling.NEAREST)
    sa = ImageChops.multiply(sa, rounded_fill_mask(W, H, R))
    sheen.putalpha(sa)
    img.alpha_composite(sheen)

    # toolbar hairline divider (full width -> survives horizontal stretch)
    dl = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dl)
    dd.rectangle([0, (BAR_H - 1) * SS, W * SS, BAR_H * SS - 1], fill=(255, 255, 255, 66))
    dd.rectangle([0, BAR_H * SS, W * SS, BAR_H * SS + SS - 1], fill=(0, 0, 0, 22))
    img.alpha_composite(dl)

    # specular rim: bright at the top, dimmer down the sides, bright again at the bottom
    # (the middle band is uniform so vertical stretching stays seamless)
    f_bar, f_mid, f_bot = BAR_H / H, MID_Y1 / H, 1.0
    stops = [(0.0, P["rim_hi"]), (0.10, P["rim_hi"] - 20),
             (f_bar, P["rim_lo"]), (f_mid, P["rim_lo"]),
             (f_bot - 0.06, P["rim_bot"]), (1.0, P["rim_bot"])]
    img.alpha_composite(rim_layer(W, H, R, 0.7, 1.2, stops))
    img.alpha_composite(hairline_layer(W, H, R, 0.5, P["hairline"]))

    # soft inner shadow just inside the bottom edge (depth)
    sh = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.rectangle([SIDE * SS, (H - BOT_H - 5) * SS, (W - SIDE) * SS, (H - BOT_H + 1) * SS],
                 fill=(0, 0, 0, 16))
    sh = sh.filter(ImageFilter.GaussianBlur(4 * SS))
    sh = ImageChops.multiply(sh, sh) if False else sh
    m = Image.new("L", (W * SS, H * SS), 0)
    ImageDraw.Draw(m).rounded_rectangle([SS, SS, (W - 1) * SS, (H - 1) * SS],
                                        radius=R * SS, fill=255)
    sh.putalpha(ImageChops.multiply(sh.getchannel("A"), m))
    img.alpha_composite(sh)
    emit(img, W, H, out)


def rounded_fill_mask(w, h, radius):
    m = Image.new("L", (w * SS, h * SS), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w * SS - 1, h * SS - 1],
                                        radius=radius * SS, fill=255)
    return m


def build_background(P, out):
    """uniform translucent pane that fills the area inside the frames"""
    img = Image.new("RGBA", (16 * SS, 16 * SS), P["glass"])
    emit(img, 16, 16, out)


# ---------------------------------------------------------------- window buttons
GLYPH = {"close": "x", "pin": "minus", "mode": "expand"}


def draw_glyph(d, kind, cx, cy, color):
    lw = max(1, int(1.25 * SS))
    if kind == "x":
        d.line([(cx - 3) * SS, (cy - 3) * SS, (cx + 3) * SS, (cy + 3) * SS], fill=color, width=lw)
        d.line([(cx + 3) * SS, (cy - 3) * SS, (cx - 3) * SS, (cy + 3) * SS], fill=color, width=lw)
    elif kind == "minus":
        d.line([(cx - 3.2) * SS, cy * SS, (cx + 3.2) * SS, cy * SS], fill=color, width=lw + 1)
    else:  # expand (two corner chevrons, iOS-ish)
        d.line([(cx - 3.4) * SS, (cy - 1.2) * SS, (cx - 3.4) * SS, (cy - 3.4) * SS], fill=color, width=lw)
        d.line([(cx - 3.4) * SS, (cy - 3.4) * SS, (cx - 1.2) * SS, (cy - 3.4) * SS], fill=color, width=lw)
        d.line([(cx + 3.4) * SS, (cy + 1.2) * SS, (cx + 3.4) * SS, (cy + 3.4) * SS], fill=color, width=lw)
        d.line([(cx + 3.4) * SS, (cy + 3.4) * SS, (cx + 1.2) * SS, (cy + 3.4) * SS], fill=color, width=lw)


def build_win_buttons(P, out):
    cols = ["close", "pin", "mode"]
    W, H = SYSBTN * 3, SYSBTN * 3
    img = canvas(W, H)
    for row, (fill, glyph_col) in enumerate([
            (P["sysbtn_fill"], P["sysbtn_glyph"]),
            (P["sysbtn_hover"], P["sysbtn_glyph_hover"]),
            (P["sysbtn_down"], P["sysbtn_glyph_hover"])]):
        for ci, kind in enumerate(cols):
            cx = ci * SYSBTN + SYSBTN / 2
            cy = row * SYSBTN + SYSBTN / 2
            cell = canvas(SYSBTN, SYSBTN)
            d = ImageDraw.Draw(cell)
            r = SYSBTN / 2 - 0.5
            d.ellipse([SS, SS, (SYSBTN - 1) * SS, (SYSBTN - 1) * SS], fill=fill)
            cell.alpha_composite(rim_layer(SYSBTN, SYSBTN, SYSBTN / 2 - 0.5, 0.8, 1.1,
                                           [(0.0, 190), (1.0, 90)]))
            gcol = P["close_glyph_hover"] if (kind == "close" and row >= 1) else glyph_col
            draw_glyph(ImageDraw.Draw(cell), GLYPH[kind], cx - ci * SYSBTN, cy - row * SYSBTN,
                       gcol + (255,))
            img.alpha_composite(cell, (ci * SYSBTN * SS, row * SYSBTN * SS))
    emit(img, W, H, out)


def build_search(P, out):
    W, H = SRCH, SRCH * 3
    img = canvas(W, H)
    for row, fill in enumerate([P["sysbtn_fill"], P["sysbtn_hover"], P["sysbtn_down"]]):
        cell = canvas(SRCH, SRCH)
        d = ImageDraw.Draw(cell)
        d.ellipse([SS, SS, (SRCH - 1) * SS, (SRCH - 1) * SS], fill=fill)
        cell.alpha_composite(rim_layer(SRCH, SRCH, SRCH / 2 - 0.5, 0.8, 1.1,
                                       [(0.0, 200), (1.0, 95)]))
        g = (P["sysbtn_glyph"] if row == 0 else P["sysbtn_glyph_hover"]) + (255,)
        gg = ImageDraw.Draw(cell)
        gg.ellipse([5.4 * SS, 5.4 * SS, 11 * SS, 11 * SS], outline=g, width=max(1, int(1.3 * SS)))
        gg.line([10.2 * SS, 10.2 * SS, 13.4 * SS, 13.4 * SS], fill=g, width=max(1, int(1.3 * SS)))
        img.alpha_composite(cell, (0, row * SRCH * SS))
    emit(img, W, H, out)


# ---------------------------------------------------------------- tabs / buttons
def build_tab(P, out):
    W, H = TAB_W, TAB_H * 3
    img = canvas(W, H)
    states = [(P["tab_off"], [(0.0, 120), (1.0, 55)], P["hairline"]),
              (P["tab_hover"], [(0.0, 175), (1.0, 80)], P["hairline"]),
              (P["tab_on"], [(0.0, 235), (1.0, 120)], P["hairline"])]
    for row, (fill, stops, hl) in enumerate(states):
        cell = pill(TAB_W, TAB_H, TAB_R, fill, stops, hl)
        img.alpha_composite(cell, (0, row * TAB_H * SS))
    emit(img, W, H, out)


def build_button(P, out):
    W, H = BTN_W, BTN_H * 3
    img = canvas(W, H)
    # normal: alpha=1 so the cell still accepts clicks (alpha=0 cells don't)
    d = ImageDraw.Draw(img)
    rr(d, (0, 0, W - 1, BTN_H - 1), BTN_R, fill=(255, 255, 255, 1))
    for row, (fill, stops) in enumerate([(P["btn_hover"], [(0.0, 150), (1.0, 70)]),
                                         (P["btn_down"], [(0.0, 190), (1.0, 95)])], start=1):
        cell = pill(W, H, BTN_R, fill, stops, P["hairline"])
        img.alpha_composite(cell, (0, row * BTN_H * SS))
    emit(img, W, H, out)


def build_menu(P, out):
    img = canvas(MENU_W, MENU_H)
    d = ImageDraw.Draw(img)
    rr(d, (0, 0, MENU_W - 1, MENU_H - 1), MENU_R, fill=P["menu_fill"])
    img.alpha_composite(rim_layer(MENU_W, MENU_H, MENU_R, 0.7, 1.2,
                                  [(0.0, 150), (0.5, 80), (1.0, 105)]))
    img.alpha_composite(hairline_layer(MENU_W, MENU_H, MENU_R, 0.5, P["hairline"]))
    emit(img, MENU_W, MENU_H, out)


def build_menu_item(P, out):
    W, H = ITEM_W, ITEM_H * 3
    img = canvas(W, H)
    d = ImageDraw.Draw(img)
    rr(d, (0, 0, W - 1, ITEM_H - 1), 0, fill=(255, 255, 255, 1))
    for row, fill in enumerate([P["item_sel"], P["item_multisel"]], start=1):
        cell = canvas(W, ITEM_H)
        d = ImageDraw.Draw(cell)
        rr(d, (2.5, 1.5, W - 3.5, ITEM_H - 2.5), ITEM_R, fill=fill)
        cell.alpha_composite(rim_layer(W, ITEM_H, ITEM_R, 3.0, 1.0,
                                       [(0.0, 120), (1.0, 50)]))
        img.alpha_composite(cell, (0, row * ITEM_H * SS))
    emit(img, W, H, out)


def build_lockmarker(P, out):
    W = H = 12
    img = canvas(W, H)
    d = ImageDraw.Draw(img)
    rr(d, (0, 0, W - 1, H - 1), 4, fill=P["lock_badge"])
    img.alpha_composite(rim_layer(W, H, 4, 0.7, 1.0, [(0.0, 120), (1.0, 60)]))
    g = ImageDraw.Draw(img)
    w = (255, 255, 255, 255) if P["lock_badge"][0] < 128 else (28, 28, 30, 255)
    g.arc([3.4 * SS, 1.6 * SS, 8.6 * SS, 7.0 * SS], start=180, end=360,
          fill=w, width=max(1, int(1.0 * SS)))
    rr(g, (2.8, 5.0, 9.2, 9.6), 1, fill=w)
    emit(img, W, H, out)


def build_scroll(P, out_btn, out_arrow):
    img = canvas(ARROW, ARROW * 4)
    for row, fill in enumerate([P["scroll_fill"], P["scroll_hov"], P["scroll_down"],
                                (255, 255, 255, 1)]):
        cell = pill(ARROW, ARROW, 5, fill, [(0.0, 150), (1.0, 70)], None)
        img.alpha_composite(cell, (0, row * ARROW * SS))
    emit(img, ARROW, ARROW * 4, out_btn)

    dirs = ["up", "down", "left", "right"]
    cols = [P["arrow"], P["arrow_hi"], P["arrow_hi"], P["arrow_dis"]]
    W2, H2 = ARROW * 4, ARROW * 4
    img = canvas(W2, H2)
    for ci, name in enumerate(dirs):
        for ri, col in enumerate(cols):
            cx = ci * ARROW + ARROW / 2
            cy = ri * ARROW + ARROW / 2
            s = 3.2
            pts = {"up": [(cx, cy - s), (cx - s, cy + s * .7), (cx + s, cy + s * .7)],
                   "down": [(cx, cy + s), (cx - s, cy - s * .7), (cx + s, cy - s * .7)],
                   "left": [(cx - s, cy), (cx + s * .7, cy - s), (cx + s * .7, cy + s)],
                   "right": [(cx + s, cy), (cx - s * .7, cy - s), (cx - s * .7, cy + s)]}[name]
            d = ImageDraw.Draw(img)
            d.polygon([(px * SS, py * SS) for px, py in pts], fill=col + (255,))
    emit(img, W2, H2, out_arrow)


# ---------------------------------------------------------------- skin.xml
T = "\t"


def dec(shadow, color, sc="#FFFFFF", sa="255", sw="1"):
    return f'shadow="{shadow}" color="{color}" shadowColor="{sc}" shadowAlpha="{sa}" shadowWidth="{sw}"'


def sysbutton_xml(name, col, offset, rows=3):
    o = [f"{T}<{name}>"]
    seq = [("normal", 0), ("hover", 1), ("down", 2)] + ([("downhover", 2)] if rows == 4 else [])
    for st, r in seq:
        o.append(f'{T}{T}<{st} image="win_buttons.png" left="{col * SYSBTN}" top="{r * SYSBTN}" '
                 f'width="{SYSBTN}" height="{SYSBTN}" method="stretch" border="0, 0, 0, 0" />')
    o += [f"{T}{T}<arrangement>",
          f'{T}{T}{T}<left base="TopFrame" side="left" offset="{offset}" />',
          f'{T}{T}{T}<top base="TopFrame" side="top" offset="{(BAR_H - SYSBTN) // 2}" />',
          f'{T}{T}{T}<right width="ImageSize" />',
          f'{T}{T}{T}<bottom height="ImageSize" />',
          f"{T}{T}</arrangement>", f"{T}</{name}>"]
    return "\n".join(o)


def build_xml(P, path):
    X = ['<?xml version="1.0" encoding="UTF-16" standalone="yes" ?>', "",
         "<!-- CLaunch Skin : iPhone Liquid Glass -->", "",
         f'<skin title="{P["skin_title"]}" author="UI Designer" version="4.20">', "",
         f'<comment>{P["comment"]}\n</comment>', "",
         f'{T}<general tabPosition="top" alphaChannel="true" clippingColor="#FF00FF" '
         f'sizeArea="6, 6, 6, 6" shadowArea="0, 0, 0, 0" />', ""]

    X += [f'{T}<background image="background.png" left="0" top="0" width="1/1" height="1/1" '
          f'method="stretch" border="0, 0, 0, 0">',
          f'{T}{T}<arrangement offset="0, 0, 0, 0" />', f"{T}</background>", ""]
    X += [f"{T}<frame>",
          f'{T}{T}<top image="window.png" left="0" top="0" width="1/1" height="{BAR_H}" '
          f'method="stretch" border="{SIDE}, 0, {SIDE}, 0">',
          f'{T}{T}{T}<arrangement height="ImageSize" />', f"{T}{T}</top>",
          f'{T}{T}<left image="window.png" left="0" top="{MID_Y0}" width="{SIDE}" '
          f'height="{MID_Y1 - MID_Y0}" method="stretch" border="0, 0, 0, 0">',
          f'{T}{T}{T}<arrangement width="ImageSize" />', f"{T}{T}</left>",
          f'{T}{T}<right image="window.png" left="{WIN_W - SIDE}" top="{MID_Y0}" width="{SIDE}" '
          f'height="{MID_Y1 - MID_Y0}" method="stretch" border="0, 0, 0, 0">',
          f'{T}{T}{T}<arrangement width="ImageSize" />', f"{T}{T}</right>",
          f'{T}{T}<bottom image="window.png" left="0" top="{MID_Y1}" width="1/1" height="{BOT_H}" '
          f'method="stretch" border="{SIDE}, 0, {SIDE}, 0">',
          f'{T}{T}{T}<arrangement height="ImageSize" />', f"{T}{T}</bottom>",
          f"{T}</frame>", ""]

    for name, col, off, rows in (("closebutton", 0, BTN_OFF[0], 3),
                                 ("pinbutton", 1, BTN_OFF[1], 4),
                                 ("modebutton", 2, BTN_OFF[2], 4)):
        X += [T + sysbutton_xml(name, col, off, rows).replace("\n", "\n" + T), ""]

    X += [f"{T}<searchbutton>"]
    for st, r in (("normal", 0), ("hover", 1), ("down", 2), ("downhover", 2)):
        X.append(f'{T}{T}<{st} image="search.png" left="0" top="{r * SRCH}" width="{SRCH}" '
                 f'height="{SRCH}" method="stretch" border="0, 0, 0, 0" />')
    X += [f"{T}{T}<arrangement>",
          f'{T}{T}{T}<left base="TopFrame" side="right" offset="{-SRCH - 12}" />',
          f'{T}{T}{T}<top base="TopFrame" side="top" offset="{(BAR_H - SRCH) // 2}" />',
          f'{T}{T}{T}<right width="ImageSize" />', f'{T}{T}{T}<bottom height="ImageSize" />',
          f"{T}{T}</arrangement>", f"{T}</searchbutton>", ""]

    X += [f"{T}<caption>", f"{T}{T}<arrangement>",
          f'{T}{T}{T}<left base="TopFrame" side="left" offset="{BTN_OFF[2] + SYSBTN + 10}" />',
          f'{T}{T}{T}<top base="TopFrame" side="top" offset="0" />',
          f'{T}{T}{T}<right width="Variable" base="SearchButton" side="left" offset="-8" />',
          f'{T}{T}{T}<bottom height="Variable" base="TopFrame" side="bottom" offset="0" />',
          f"{T}{T}</arrangement>", f"{T}{T}<text>",
          f'{T}{T}{T}<font face="{FONT}" size="10" style="normal" antiAlias="true" />',
          f'{T}{T}{T}<decoration {dec("none", P["text_3"])} />',
          f"{T}{T}</text>", f"{T}</caption>", ""]

    X += [f"{T}<tabarea>", f'{T}{T}<arrangement offset="0, 0, 0, 0" margin="{SIDE}, 10, {SIDE}, 6" />',
          f'{T}{T}<tab image="tab.png" method="stretch" border="16, 6, 16, 6" designs="1">',
          f'{T}{T}{T}<arrangement pitch="4, 0" />', f"{T}{T}{T}<text>", f"{T}{T}{T}{T}<font>",
          f'{T}{T}{T}{T}{T}<active face="{FONT}" size="10" style="bold" antiAlias="true" />',
          f'{T}{T}{T}{T}{T}<inactive face="{FONT}" size="10" style="normal" antiAlias="true" />',
          f"{T}{T}{T}{T}</font>", f"{T}{T}{T}{T}<decoration>",
          f'{T}{T}{T}{T}{T}<normal {dec("none", P["text_2"])} />',
          f'{T}{T}{T}{T}{T}<hover {dec("none", P["text_1"])} />',
          f'{T}{T}{T}{T}{T}<active {dec("none", P["sel_color"])} />',
          f"{T}{T}{T}{T}</decoration>", f"{T}{T}{T}</text>", f"{T}{T}</tab>", f"{T}</tabarea>", ""]

    X += [f"{T}<buttonarea>",
          f'{T}{T}<arrangement offset="0, 0, 0, 0" margin="{SIDE}, 6, {SIDE}, 16" />',
          f'{T}{T}<button image="button.png" method="stretch" border="28, 28, 28, 28" designs="1">',
          f'{T}{T}{T}<arrangement pitch="4, 4" shiftHover="0, -1" shiftDown="0, 1" />',
          f"{T}{T}{T}<text>",
          f'{T}{T}{T}{T}<font face="{FONT}" size="9" style="normal" antiAlias="true" />',
          f"{T}{T}{T}{T}<decoration>",
          f'{T}{T}{T}{T}{T}<normal {dec("lower", P["text_1"], sc="#FFFFFF", sa="200")} />',
          f'{T}{T}{T}{T}{T}<hover {dec("lower", P["accent"], sc="#FFFFFF", sa="200")} />',
          f'{T}{T}{T}{T}{T}<down {dec("lower", P["accent"], sc="#FFFFFF", sa="200")} />',
          f"{T}{T}{T}{T}</decoration>", f"{T}{T}{T}</text>", f"{T}{T}</button>",
          f'{T}{T}<lockmarker image="lockmarker.png" left="0" top="0" width="1/1" height="1/1" '
          f'method="stretch" border="0, 0, 0, 0">',
          f'{T}{T}{T}<arrangement offset="-1, -1, 1, 1" zOrder="bottom" />',
          f"{T}{T}</lockmarker>", f"{T}</buttonarea>", ""]

    X += [f'{T}<submenu image="menuframe.png" left="0" top="0" width="1/1" height="1/1" '
          f'method="stretch" border="{MENU_B}, {MENU_B}, {MENU_B}, {MENU_B}">',
          f'{T}{T}<arrangement shadowArea="0, 0, 0, 0" />', f"{T}{T}<frame>",
          f'{T}{T}{T}<top image="menuframe.png" left="0" top="0" width="1/1" height="{MENU_B}" '
          f'method="stretch" border="{MENU_B}, 0, {MENU_B}, 0">',
          f'{T}{T}{T}{T}<arrangement height="ImageSize" />', f"{T}{T}{T}</top>",
          f'{T}{T}{T}<left image="menuframe.png" left="0" top="{MENU_B}" width="{MENU_B}" '
          f'height="{MENU_H - MENU_B * 2}" method="stretch" border="0, 0, 0, 0">',
          f'{T}{T}{T}{T}<arrangement width="ImageSize" />', f"{T}{T}{T}</left>",
          f'{T}{T}{T}<right image="menuframe.png" left="{MENU_W - MENU_B}" top="{MENU_B}" '
          f'width="{MENU_B}" height="{MENU_H - MENU_B * 2}" method="stretch" border="0, 0, 0, 0">',
          f'{T}{T}{T}{T}<arrangement width="ImageSize" />', f"{T}{T}{T}</right>",
          f'{T}{T}{T}<bottom image="menuframe.png" left="0" top="{MENU_H - MENU_B}" width="1/1" '
          f'height="{MENU_B}" method="stretch" border="{MENU_B}, 0, {MENU_B}, 0">',
          f'{T}{T}{T}{T}<arrangement height="ImageSize" />', f"{T}{T}{T}</bottom>",
          f"{T}{T}</frame>", f"{T}{T}<item>",
          f'{T}{T}{T}<normal image="menu_item.png" left="0" top="0" width="1/1" height="{ITEM_H}" '
          f'method="stretch" border="0, 0, 0, 0" />',
          f'{T}{T}{T}<selected image="menu_item.png" left="0" top="{ITEM_H}" width="1/1" '
          f'height="{ITEM_H}" method="stretch" border="10, 0, 10, 0" />',
          f'{T}{T}{T}<multisel image="menu_item.png" left="0" top="{ITEM_H * 2}" width="1/1" '
          f'height="{ITEM_H}" method="stretch" border="10, 0, 10, 0" />',
          f'{T}{T}{T}<arrangement margin="5, 4, 5, 4" interval="0, 0" />',
          f"{T}{T}{T}<text>",
          f'{T}{T}{T}{T}<font face="{FONT}" size="10" style="normal" antiAlias="true" />',
          f"{T}{T}{T}{T}<decoration>",
          f'{T}{T}{T}{T}{T}<normal {dec("none", P["text_1"])} />',
          f'{T}{T}{T}{T}{T}<selected {dec("none", P["text_on_sel"])} />',
          f'{T}{T}{T}{T}{T}<disabled {dec("none", P["text_dis"])} />',
          f"{T}{T}{T}{T}</decoration>", f"{T}{T}{T}</text>", f"{T}{T}</item>"]
    X += [f"{T}{T}<scrollbutton>"]
    for st, r in (("normal", 0), ("hover", 1), ("down", 2), ("disabled", 3)):
        X.append(f'{T}{T}{T}<{st} image="scroll_btn.png" left="0" top="{r * ARROW}" '
                 f'width="{ARROW}" height="{ARROW}" method="stretch" border="0, 0, 0, 0" />')
    X += [f'{T}{T}{T}<arrangement width="{ARROW}" height="{ARROW}" interval="0, 0" />']
    for i, nm in enumerate(("uparrow", "downarrow", "leftarrow", "rightarrow")):
        X.append(f"{T}{T}{T}<{nm}>")
        for st, r in (("normal", 0), ("hover", 1), ("down", 2), ("disabled", 3)):
            X.append(f'{T}{T}{T}{T}<{st} image="arrows.png" left="{i * ARROW}" top="{r * ARROW}" '
                     f'width="{ARROW}" height="{ARROW}" />')
        X.append(f"{T}{T}{T}</{nm}>")
    X += [f"{T}{T}</scrollbutton>", f"{T}</submenu>", ""]

    # ---- search result window (same glass panel as the submenu) ----
    X += [f'{T}<searchwindow image="menuframe.png" left="0" top="0" width="1/1" height="1/1" '
          f'method="stretch" border="{MENU_B}, {MENU_B}, {MENU_B}, {MENU_B}">',
          f'{T}{T}<arrangement sizeArea="6, 0, 6, 0" shadowArea="0, 0, 0, 0" />',
          f"{T}{T}<frame>",
          f'{T}{T}{T}<top image="menuframe.png" left="0" top="0" width="1/1" height="{MENU_B}" '
          f'method="stretch" border="{MENU_B}, 0, {MENU_B}, 0">',
          f'{T}{T}{T}{T}<arrangement height="ImageSize" />', f"{T}{T}{T}</top>",
          f'{T}{T}{T}<left image="menuframe.png" left="0" top="{MENU_B}" width="{MENU_B}" '
          f'height="{MENU_H - MENU_B * 2}" method="stretch" border="0, 0, 0, 0">',
          f'{T}{T}{T}{T}<arrangement width="ImageSize" />', f"{T}{T}{T}</left>",
          f'{T}{T}{T}<right image="menuframe.png" left="{MENU_W - MENU_B}" top="{MENU_B}" '
          f'width="{MENU_B}" height="{MENU_H - MENU_B * 2}" method="stretch" border="0, 0, 0, 0">',
          f'{T}{T}{T}{T}<arrangement width="ImageSize" />', f"{T}{T}{T}</right>",
          f'{T}{T}{T}<bottom image="menuframe.png" left="0" top="{MENU_H - MENU_B}" width="1/1" '
          f'height="{MENU_B}" method="stretch" border="{MENU_B}, 0, {MENU_B}, 0">',
          f'{T}{T}{T}{T}<arrangement height="ImageSize" />', f"{T}{T}{T}</bottom>",
          f"{T}{T}</frame>",
          # font + alignment are inherited from the submenu item settings,
          # exactly as the official Glass.zip does it
          f"{T}{T}<item>",
          f'{T}{T}{T}<normal image="menu_item.png" left="0" top="0" width="1/1" height="{ITEM_H}" '
          f'method="stretch" border="0, 0, 0, 0" />',
          f'{T}{T}{T}<selected image="menu_item.png" left="0" top="{ITEM_H}" width="1/1" '
          f'height="{ITEM_H}" method="stretch" border="10, 0, 10, 0" />',
          f"{T}{T}{T}<text>",
          f"{T}{T}{T}{T}<decoration>",
          f'{T}{T}{T}{T}{T}<normal {dec("none", P["text_1"])} />',
          f'{T}{T}{T}{T}{T}<selected {dec("none", P["text_on_sel"])} />',
          f"{T}{T}{T}{T}</decoration>", f"{T}{T}{T}</text>", f"{T}{T}</item>",
          f"{T}</searchwindow>", ""]

    X += [f"{T}<recommended>"]
    for mode, count in (("mode1", "6, 3"), ("mode2", "6, 6")):
        X += [f"{T}{T}<{mode}>",
              f'{T}{T}{T}<caption textMargin="0, 0, 0, 0" centerText="true" multiLine="false" />',
              f'{T}{T}{T}<tab size="{TAB_W}, {TAB_H}" textMargin="2, 0, 2, 0" fixedWidth="true" '
              f'multiLine="false" leftText="false" />',
              f'{T}{T}{T}<button size="{BTN_W}, {BTN_H}" count="{count}" iconSize="38" '
              f'iconMargin="0, 8, 0, 0" textMargin="1, 4, 1, 0" leftIcon="false" '
              f'text="true" singleLine="true" leftText="false" />',
              f"{T}{T}</{mode}>"]
    X += [f"{T}</recommended>", "", "</skin>", ""]

    with open(path, "w", encoding="utf-16") as f:
        f.write("\n".join(X))


# ---------------------------------------------------------------- main
def main():
    base = os.path.dirname(os.path.abspath(__file__))
    for key, P in PALETTES.items():
        out = os.path.join(base, P["folder"])
        os.makedirs(out, exist_ok=True)
        p = lambda n: os.path.join(out, n)
        print(f"[{key}] building -> {P['folder']}")
        build_window(P, p("window.png"))
        build_background(P, p("background.png"))
        build_win_buttons(P, p("win_buttons.png"))
        build_search(P, p("search.png"))
        build_tab(P, p("tab.png"))
        build_button(P, p("button.png"))
        build_menu(P, p("menuframe.png"))
        build_menu_item(P, p("menu_item.png"))
        build_lockmarker(P, p("lockmarker.png"))
        build_scroll(P, p("scroll_btn.png"), p("arrows.png"))
        build_xml(P, p("skin.xml"))

        names = ["skin.xml"] + sorted(n for n in os.listdir(out) if n.lower().endswith(".png"))
        with zipfile.ZipFile(os.path.join(base, P["folder"] + ".zip"), "w",
                             zipfile.ZIP_DEFLATED) as z:
            for n in names:
                z.write(os.path.join(out, n), n)
        print("   zipped:", P["folder"] + ".zip", "->", names)


if __name__ == "__main__":
    main()
