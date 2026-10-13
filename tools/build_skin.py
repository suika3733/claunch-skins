# -*- coding: utf-8 -*-
"""
CLaunch skin builder — macOS Sonoma style
Outputs a CLaunch (Ver 4.20+) skin folder: skin.xml (UTF-16 LE) + part PNGs.
All artwork is drawn from scratch; 4x supersampled then LANCZOS-downscaled.
"""
import os, struct, zlib
from PIL import Image, ImageDraw, ImageFilter

SS = 4  # supersample factor

# ---------- macOS Sonoma light palette ----------
TOOLBAR      = (237, 237, 240, 255)   # #EDEDF0
BODY         = (247, 247, 249, 255)   # #F7F7F9
OUTER        = (201, 201, 207, 255)   # #C9C9CF  window hairline
BAR_LINE     = (214, 214, 219, 255)   # #D6D6DB  toolbar separator
TEXT1        = (29, 29, 31, 255)      # #1D1D1F
TEXT2        = (110, 110, 115, 255)   # #6E6E73
TEXT3        = (134, 134, 139, 255)   # #86868B
ACCENT       = (10, 132, 255, 255)    # #0A84FF
SEG_NORMAL   = (237, 237, 240, 255)
SEG_HOVER    = (227, 227, 233, 255)
SEG_SEL      = (255, 255, 255, 255)
SEG_SEL_LINE = (207, 207, 213, 255)
BTN_HOVER    = (233, 233, 238, 255)
BTN_DOWN     = (222, 222, 229, 255)
DISABLED     = (199, 199, 204, 255)

CLEAR = (BODY[0], BODY[1], BODY[2], 0)   # opaque-ish clear, avoids dark fringing

# ---------- geometry ----------
WIN_W, WIN_H = 48, 80
R            = 11          # window corner radius
BAR_H        = 34          # toolbar height
SIDE         = 12          # left/right frame thickness
BOT_H        = 20          # bottom frame height
MID_Y0, MID_Y1 = BAR_H, WIN_H - BOT_H     # 34 .. 60

TAB_W, TAB_H = 80, 24
BTN_W, BTN_H = 72, 72
SYSBTN       = 12          # traffic light diameter
SRCH         = 20          # search button box
MENU_W, MENU_H, MENU_R, MENU_BAND = 48, 48, 10, 12
ITEM_H       = 22
ARROW        = 16


def canvas(w, h, bg=CLEAR):
    return Image.new("RGBA", (w * SS, h * SS), bg)


def emit(img, w, h, path):
    img.resize((w, h), Image.Resampling.LANCZOS).save(path)
    print("  wrote", os.path.basename(path), f"{w}x{h}")


def rr(d, box, radius, **kw):
    """rounded rect in SS space"""
    d.rounded_rectangle([v * SS for v in box], radius=radius * SS, **kw)


def circle(d, cx, cy, r, **kw):
    d.ellipse([(cx - r) * SS, (cy - r) * SS, (cx + r) * SS, (cy + r) * SS], **kw)


def line(d, x1, y1, x2, y2, w=1.0, **kw):
    d.line([x1 * SS, y1 * SS, x2 * SS, y2 * SS], width=max(1, int(w * SS)), **kw)


# =========================================================
# 1. window.png  — window body + toolbar (9-slice source, 4 slices)
# =========================================================
def build_window(out):
    W, H = WIN_W, WIN_H
    img = canvas(W, H)
    d = ImageDraw.Draw(img)

    # body
    rr(d, (0, 0, W - 1, H - 1), R, fill=BODY)

    # toolbar (rounded top only -> draw tall then square the bottom off)
    bar = canvas(W, H)
    bd = ImageDraw.Draw(bar)
    rr(bd, (0, 0, W - 1, H * 2), R, fill=TOOLBAR)
    bd.rectangle([0, BAR_H * SS, W * SS, H * 2 * SS], fill=TOOLBAR)
    # re-apply body below the bar so the toolbar only occupies the top band
    cut = Image.new("L", img.size, 255)
    cd = ImageDraw.Draw(cut)
    cd.rectangle([0, BAR_H * SS, img.size[0], img.size[1]], fill=0)
    bar.putalpha(Image.composite(bar.getchannel("A"),
                                 Image.new("L", img.size, 0), cut))
    img = Image.alpha_composite(img, bar)

    d = ImageDraw.Draw(img)
    # separator under toolbar (spans tiled middle -> stays crisp)
    d.rectangle([0, BAR_H * SS - SS, W * SS, BAR_H * SS - 1], fill=BAR_LINE)
    # outer hairline
    rr(d, (0, 0, W - 1, H - 1), R, outline=OUTER, width=SS)
    emit(img, W, H, out)


# =========================================================
# 2. win_buttons.png — traffic lights: 3 cols x 3 rows of 12x12
# =========================================================
def build_win_buttons(out):
    cols = [(255, 95, 87), (254, 188, 46), (40, 200, 64)]        # close / pin / mode
    dark = [(224, 68, 62), (222, 161, 31), (30, 175, 53)]
    hovr = [(255, 113, 106), (255, 200, 76), (66, 209, 88)]
    glyph = [(124, 26, 22), (140, 95, 10), (15, 95, 25)]

    W, H = SYSBTN * 3, SYSBTN * 3
    img = canvas(W, H)

    def draw_glyph(idx, cx, cy, col):
        g = ImageDraw.Draw(img)
        if idx == 0:      # close: x
            line(g, cx - 2.6, cy - 2.6, cx + 2.6, cy + 2.6, 1.15, fill=col)
            line(g, cx + 2.6, cy - 2.6, cx - 2.6, cy + 2.6, 1.15, fill=col)
        elif idx == 1:    # pin: minus
            line(g, cx - 2.6, cy, cx + 2.6, cy, 1.25, fill=col)
        else:             # mode: expand (two corner triangles)
            g.polygon([(cx - 3.2) * SS, (cy - 3.2) * SS, (cx - 0.7) * SS, (cy - 3.2) * SS,
                       (cx - 3.2) * SS, (cy - 0.7) * SS], fill=col)
            g.polygon([(cx + 3.2) * SS, (cy + 3.2) * SS, (cx + 0.7) * SS, (cy + 3.2) * SS,
                       (cx + 3.2) * SS, (cy + 0.7) * SS], fill=col)

    for row in range(3):
        for col in range(3):
            cx = col * SYSBTN + SYSBTN / 2
            cy = row * SYSBTN + SYSBTN / 2
            fill = [cols, hovr, dark][row][col]
            edge = dark[col] if row == 0 else fill
            g = ImageDraw.Draw(img)
            circle(g, cx, cy, SYSBTN / 2 - 0.2, fill=fill)
            circ = Image.new("RGBA", img.size, (0, 0, 0, 0))
            cd = ImageDraw.Draw(circ)
            circle(cd, cx, cy, SYSBTN / 2 - 0.7, outline=edge, width=max(1, int(0.55 * SS)))
            img.alpha_composite(circ)
            if row >= 1:
                draw_glyph(col, cx, cy, glyph[col])
    emit(img, W, H, out)


# =========================================================
# 3. search.png — magnifier, 1 col x 3 rows of 20x20
# =========================================================
def build_search(out):
    W, H = SRCH, SRCH * 3
    img = canvas(W, H)

    def magnifier(cx, cy, col, flip):
        g = ImageDraw.Draw(img)
        circ = Image.new("RGBA", img.size, (0, 0, 0, 0))
        cd = ImageDraw.Draw(circ)
        cd.ellipse([(cx - 4) * SS, (cy - 4) * SS, (cx + 2) * SS, (cy + 2) * SS],
                   outline=col, width=max(1, int(1.35 * SS)))
        cd.line([(cx + 1.1) * SS, (cy + 1.1) * SS, (cx + 4.3) * SS, (cy + 4.3) * SS],
                fill=col, width=max(1, int(1.35 * SS)))
        img.alpha_composite(circ)

    for row in range(3):
        y0 = row * SRCH
        if row == 0:
            d = ImageDraw.Draw(img)
            rr(d, (0, y0, SRCH - 1, y0 + SRCH - 1), 0, fill=(BODY[0], BODY[1], BODY[2], 1))
            magnifier(SRCH / 2 - 1.2, y0 + SRCH / 2 - 1.2, TEXT3, 0)
        else:
            d = ImageDraw.Draw(img)
            rr(d, (0.5, y0 + 0.5, SRCH - 1.5, y0 + SRCH - 1.5), 5,
               fill=(SEG_HOVER if row == 1 else BTN_DOWN))
            magnifier(SRCH / 2 - 1.2, y0 + SRCH / 2 - 1.2, TEXT1, 0)
    emit(img, W, H, out)


# =========================================================
# 4. tab.png — page tabs, 1 design x 3 states, 80x24 each
# =========================================================
def build_tab(out):
    W, H = TAB_W, TAB_H * 3
    img = canvas(W, H)
    states = [(SEG_NORMAL, (220, 220, 226)),
              (SEG_HOVER, (207, 207, 214)),
              (SEG_SEL, SEG_SEL_LINE)]
    for row, (fill, edge) in enumerate(states):
        y0 = row * TAB_H
        d = ImageDraw.Draw(img)
        rr(d, (0.5, y0 + 0.5, W - 1.5, y0 + TAB_H - 1.5), 6, fill=fill)
        rr(d, (0.5, y0 + 0.5, W - 1.5, y0 + TAB_H - 1.5), 6,
           outline=(edge[0], edge[1], edge[2], 255), width=SS)
        if row == 2:  # selected chip: subtle inner top highlight
            hl = Image.new("RGBA", img.size, (0, 0, 0, 0))
            hd = ImageDraw.Draw(hl)
            rr(hd, (1.5, y0 + 1.5, W - 2.5, y0 + TAB_H - 2.5), 5, outline=(255, 255, 255, 170), width=SS)
            hd.rectangle([0, y0 * SS + TAB_H * SS // 2, W * SS, (y0 + TAB_H) * SS], fill=(0, 0, 0, 0))
            img.alpha_composite(hl)
    emit(img, W, H, out)


# =========================================================
# 5. button.png — icon buttons, 1 design x 3 states, 72x72 each
# =========================================================
def build_button(out):
    W, H = BTN_W, BTN_H * 3
    img = canvas(W, H)
    # normal state: alpha=1 so the cell still accepts clicks
    d = ImageDraw.Draw(img)
    rr(d, (0, 0, W - 1, BTN_H - 1), 10, fill=(BODY[0], BODY[1], BODY[2], 1))
    for row, fill in enumerate([BTN_HOVER, BTN_DOWN], start=1):
        y0 = row * BTN_H
        d = ImageDraw.Draw(img)
        rr(d, (0.5, y0 + 0.5, W - 1.5, y0 + BTN_H - 1.5), 10, fill=fill)
    emit(img, W, H, out)


# =========================================================
# 6. lockmarker.png — badge on locked buttons
# =========================================================
def build_lockmarker(out):
    W = H = 12
    img = canvas(W, H)
    d = ImageDraw.Draw(img)
    rr(d, (0, 0, W - 1, H - 1), 3, fill=(29, 29, 31, 219))
    g = ImageDraw.Draw(img)
    g.arc([3.2 * SS, 1.6 * SS, 8.8 * SS, 7.2 * SS], start=180, end=360,
          fill=(255, 255, 255, 255), width=max(1, int(1.0 * SS)))
    rr(g, (2.6, 5.0, 9.4, 9.6), 1, fill=(255, 255, 255, 255))
    emit(img, W, H, out)


# =========================================================
# 7. menuframe.png — submenu body + frames
# =========================================================
def build_menu(out):
    W, H = MENU_W, MENU_H
    img = canvas(W, H)
    d = ImageDraw.Draw(img)
    rr(d, (0, 0, W - 1, H - 1), MENU_R, fill=BODY)
    rr(d, (0, 0, W - 1, H - 1), MENU_R, outline=OUTER, width=SS)
    emit(img, W, H, out)


# =========================================================
# 8. menu_item.png — item bg, 1 design x 3 states, 48x22 each
# =========================================================
def build_menu_item(out):
    W, H = MENU_W, ITEM_H * 3
    img = canvas(W, H)
    d = ImageDraw.Draw(img)
    rr(d, (0, 0, W - 1, ITEM_H - 1), 0, fill=(BODY[0], BODY[1], BODY[2], 1))
    y0 = ITEM_H
    d = ImageDraw.Draw(img)
    rr(d, (2.5, y0 + 1.5, W - 3.5, y0 + ITEM_H - 2.5), 4, fill=ACCENT)
    y0 = ITEM_H * 2
    d = ImageDraw.Draw(img)
    rr(d, (2.5, y0 + 1.5, W - 3.5, y0 + ITEM_H - 2.5), 4, fill=(10, 132, 255, 120))
    emit(img, W, H, out)


# =========================================================
# 9. scroll_btn.png (4 states) + arrows.png (4 dirs x 4 states)
# =========================================================
def build_scroll(out_btn, out_arrow):
    W, H = ARROW, ARROW * 4
    img = canvas(W, H)
    fills = [(BODY[0], BODY[1], BODY[2], 1), SEG_HOVER, BTN_DOWN, (BODY[0], BODY[1], BODY[2], 1)]
    for row, fill in enumerate(fills):
        y0 = row * ARROW
        d = ImageDraw.Draw(img)
        rr(d, (0, y0, W - 1, y0 + ARROW - 1), 4, fill=fill)
    emit(img, W, H, out_btn)

    cols = {"up": 0, "down": 1, "left": 2, "right": 3}
    rows = [TEXT2, TEXT1, TEXT1, DISABLED]
    W2, H2 = ARROW * 4, ARROW * 4
    img = canvas(W2, H2)
    for name, col in cols.items():
        for row, col_ in enumerate(rows):
            cx = col * ARROW + ARROW / 2
            cy = row * ARROW + ARROW / 2
            s = 3.2
            pts = {
                "up":    [(cx, cy - s), (cx - s, cy + s * 0.7), (cx + s, cy + s * 0.7)],
                "down":  [(cx, cy + s), (cx - s, cy - s * 0.7), (cx + s, cy - s * 0.7)],
                "left":  [(cx - s, cy), (cx + s * 0.7, cy - s), (cx + s * 0.7, cy + s)],
                "right": [(cx + s, cy), (cx - s * 0.7, cy - s), (cx - s * 0.7, cy + s)],
            }[name]
            d = ImageDraw.Draw(img)
            d.polygon([(px * SS, py * SS) for px, py in pts], fill=col_)
    emit(img, W2, H2, out_arrow)


# =========================================================
# skin.xml
# =========================================================
def sysbutton(name, img, col, rows, extra=""):
    """emit normal/hover/down[/downhover] for a window button"""
    out = []
    seq = ["normal", "hover", "down"] + (["downhover"] if rows == 4 else [])
    seen = {"normal": 0, "hover": 1, "down": 2, "downhover": 2}
    for st in seq:
        r = seen[st]
        out.append(
            f'\t\t<{st} image="{img}" left="{col * SYSBTN}" top="{r * SYSBTN}" '
            f'width="{SYSBTN}" height="{SYSBTN}" method="stretch" border="0, 0, 0, 0" />'
        )
    arr = f"""\t\t<arrangement>
\t\t\t<left base="TopFrame" side="left" offset="{extra}" />
\t\t\t<top base="TopFrame" side="top" offset="{(BAR_H - SYSBTN) // 2}" />
\t\t\t<right width="ImageSize" />
\t\t\t<bottom height="ImageSize" />
\t\t</arrangement>"""
    return "<" + name + ">\n" + "\n".join(out) + "\n" + arr + f"\n\t</{name}>"


def build_xml(path, font="Microsoft YaHei UI"):
    S = "\t"
    parts = []
    parts.append('<?xml version="1.0" encoding="UTF-16" standalone="yes" ?>')
    parts.append("")
    parts.append("<!-- CLaunch Skin : macOS Sonoma -->")
    parts.append("")
    parts.append('<skin title="macOS Sonoma" author="UI Designer" version="4.20">')
    parts.append("")
    parts.append("<comment>macOS 風格皮膚（Sonoma / Big Sur 風）。")
    parts.append("")
    parts.append("* 需要 32bpp 顯示模式，Unicode 版 CLaunch 4.20 以上")
    parts.append("* 視窗列左側為紅／黃／綠三個圓形按鈕（關閉／鎖定／模式切換）")
    parts.append("* 分頁為 macOS 分段控制器膠囊樣式，選中頁為白色")
    parts.append("* 子選單選中項為 macOS 系統藍 #0A84FF")
    parts.append("</comment>")
    parts.append("")

    # ---- general ----
    parts.append(f'{S}<general tabPosition="top" alphaChannel="true" clippingColor="#FF00FF" '
                 f'sizeArea="6, 6, 6, 6" shadowArea="0, 0, 0, 0" />')
    parts.append("")

    # ---- background : full window, 9-slice so the corners stay round ----
    parts.append(f'{S}<background image="window.png" left="0" top="0" width="1/1" height="1/1" '
                 f'method="stretch" border="{SIDE}, {BAR_H}, {SIDE}, {BOT_H}">')
    parts.append(f'{S}{S}<arrangement offset="0, 0, 0, 0" />')
    parts.append(f"{S}</background>")
    parts.append("")

    # ---- frames ----
    parts.append(f"{S}<frame>")
    parts.append(f'{S}{S}<top image="window.png" left="0" top="0" width="1/1" height="{BAR_H}" '
                 f'method="tile" border="{SIDE}, 0, {SIDE}, 0">')
    parts.append(f'{S}{S}{S}<arrangement height="ImageSize" />')
    parts.append(f"{S}{S}</top>")
    parts.append(f'{S}{S}<left image="window.png" left="0" top="{MID_Y0}" width="{SIDE}" '
                 f'height="{MID_Y1 - MID_Y0}" method="tile" border="0, 0, 0, 0">')
    parts.append(f'{S}{S}{S}<arrangement width="ImageSize" />')
    parts.append(f"{S}{S}</left>")
    parts.append(f'{S}{S}<right image="window.png" left="{WIN_W - SIDE}" top="{MID_Y0}" '
                 f'width="{SIDE}" height="{MID_Y1 - MID_Y0}" method="tile" border="0, 0, 0, 0">')
    parts.append(f'{S}{S}{S}<arrangement width="ImageSize" />')
    parts.append(f"{S}{S}</right>")
    parts.append(f'{S}{S}<bottom image="window.png" left="0" top="{MID_Y1}" width="1/1" '
                 f'height="{BOT_H}" method="tile" border="{SIDE}, 0, {SIDE}, 0">')
    parts.append(f'{S}{S}{S}<arrangement height="ImageSize" />')
    parts.append(f"{S}{S}</bottom>")
    parts.append(f"{S}</frame>")
    parts.append("")

    # ---- traffic lights ----
    parts.append(S + sysbutton("closebutton", "win_buttons.png", 0, 3, 13).replace("\n", "\n" + S))
    parts.append("")
    parts.append(S + sysbutton("pinbutton", "win_buttons.png", 1, 4, 33).replace("\n", "\n" + S))
    parts.append("")
    parts.append(S + sysbutton("modebutton", "win_buttons.png", 2, 4, 53).replace("\n", "\n" + S))
    parts.append("")

    # ---- search button (right side of toolbar) ----
    parts.append(f"{S}<searchbutton>")
    for st, r in (("normal", 0), ("hover", 1), ("down", 2), ("downhover", 2)):
        parts.append(f'{S}{S}<{st} image="search.png" left="0" top="{r * SRCH}" width="{SRCH}" '
                     f'height="{SRCH}" method="stretch" border="0, 0, 0, 0" />')
    parts.append(f"{S}{S}<arrangement>")
    parts.append(f'{S}{S}{S}<left base="TopFrame" side="right" offset="{-SRCH - 11}" />')
    parts.append(f'{S}{S}{S}<top base="TopFrame" side="top" offset="{(BAR_H - SRCH) // 2}" />')
    parts.append(f'{S}{S}{S}<right width="ImageSize" />')
    parts.append(f'{S}{S}{S}<bottom height="ImageSize" />')
    parts.append(f"{S}{S}</arrangement>")
    parts.append(f"{S}</searchbutton>")
    parts.append("")

    # ---- caption (window title, centred like macOS) ----
    parts.append(f"{S}<caption>")
    parts.append(f"{S}{S}<arrangement>")
    parts.append(f'{S}{S}{S}<left base="TopFrame" side="left" offset="76" />')
    parts.append(f'{S}{S}{S}<top base="TopFrame" side="top" offset="0" />')
    parts.append(f'{S}{S}{S}<right width="Variable" base="TopFrame" side="right" offset="-76" />')
    parts.append(f'{S}{S}{S}<bottom height="Variable" base="TopFrame" side="top" offset="{BAR_H}" />')
    parts.append(f"{S}{S}</arrangement>")
    parts.append(f'{S}{S}<text fontFace="{font}" fontSize="10" fontStyle="normal" antiAlias="true" '
                 f'color="#6E6E73" shadow="none" shadowColor="#FFFFFF" shadowAlpha="120" shadowWidth="1" />')
    parts.append(f"{S}</caption>")
    parts.append("")

    # ---- tab area ----
    parts.append(f"{S}<tabarea>")
    parts.append(f'{S}{S}<arrangement offset="0, 0, 0, 0" margin="10, 9, 10, 6" />')
    parts.append(f'{S}{S}<tab image="tab.png" method="stretch" border="10, 0, 10, 0">')
    parts.append(f'{S}{S}{S}<arrangement pitch="2, 0" />')
    parts.append(f"{S}{S}{S}<text>")
    parts.append(f'{S}{S}{S}{S}<font>')
    parts.append(f'{S}{S}{S}{S}{S}<active face="{font}" size="10" style="bold" antiAlias="true" />')
    parts.append(f'{S}{S}{S}{S}{S}<inactive face="{font}" size="10" style="normal" antiAlias="true" />')
    parts.append(f"{S}{S}{S}{S}</font>")
    parts.append(f'{S}{S}{S}{S}<decoration shadow="none" color="#6E6E73" shadowColor="#FFFFFF" '
                 f'shadowAlpha="160" shadowWidth="1">')
    parts.append(f'{S}{S}{S}{S}{S}<active color="#1D1D1F" />')
    parts.append(f'{S}{S}{S}{S}{S}<inactive color="#6E6E73">')
    parts.append(f'{S}{S}{S}{S}{S}{S}<hover color="#1D1D1F" />')
    parts.append(f"{S}{S}{S}{S}{S}</inactive>")
    parts.append(f"{S}{S}{S}{S}</decoration>")
    parts.append(f"{S}{S}{S}</text>")
    parts.append(f"{S}{S}</tab>")
    parts.append(f"{S}</tabarea>")
    parts.append("")

    # ---- button area ----
    parts.append(f"{S}<buttonarea>")
    parts.append(f'{S}{S}<arrangement offset="0, 0, 0, 0" margin="10, 6, 10, 12" />')
    parts.append(f'{S}{S}<button image="button.png" method="stretch" border="12, 12, 12, 12">')
    parts.append(f'{S}{S}{S}<arrangement pitch="2, 2" shiftHover="-1, -1" shiftDown="1, 1" />')
    parts.append(f'{S}{S}{S}<text fontFace="{font}" fontSize="9" fontStyle="normal" antiAlias="true" '
                 f'color="#1D1D1F" shadow="lower" shadowColor="#FFFFFF" shadowAlpha="220" shadowWidth="1">')
    parts.append(f'{S}{S}{S}{S}<hover color="#0A84FF" />')
    parts.append(f"{S}{S}{S}</text>")
    parts.append(f"{S}{S}</button>")
    parts.append(f'{S}{S}<lockmarker image="lockmarker.png" left="0" top="0" width="1/1" height="1/1" '
                 f'method="stretch" border="0, 0, 0, 0">')
    parts.append(f'{S}{S}{S}<arrangement zOrder="0" />')
    parts.append(f"{S}{S}</lockmarker>")
    parts.append(f"{S}</buttonarea>")
    parts.append("")

    # ---- submenu (also used by the search window) ----
    parts.append(f'{S}<submenu image="menuframe.png" left="0" top="0" width="1/1" height="1/1" '
                 f'method="stretch" border="{MENU_BAND}, {MENU_BAND}, {MENU_BAND}, {MENU_BAND}">')
    parts.append(f'{S}{S}<arrangement shadowArea="0, 0, 0, 0" />')
    parts.append(f"{S}{S}<frame>")
    parts.append(f'{S}{S}{S}<top image="menuframe.png" left="0" top="0" width="1/1" height="{MENU_BAND}" '
                 f'method="tile" border="{MENU_BAND}, 0, {MENU_BAND}, 0">')
    parts.append(f'{S}{S}{S}{S}<arrangement height="ImageSize" />')
    parts.append(f"{S}{S}{S}</top>")
    parts.append(f'{S}{S}{S}<left image="menuframe.png" left="0" top="{MENU_BAND}" width="{MENU_BAND}" '
                 f'height="{MENU_H - MENU_BAND * 2}" method="tile" border="0, 0, 0, 0">')
    parts.append(f'{S}{S}{S}{S}<arrangement width="ImageSize" />')
    parts.append(f"{S}{S}{S}</left>")
    parts.append(f'{S}{S}{S}<right image="menuframe.png" left="{MENU_W - MENU_BAND}" top="{MENU_BAND}" '
                 f'width="{MENU_BAND}" height="{MENU_H - MENU_BAND * 2}" method="tile" border="0, 0, 0, 0">')
    parts.append(f'{S}{S}{S}{S}<arrangement width="ImageSize" />')
    parts.append(f"{S}{S}{S}</right>")
    parts.append(f'{S}{S}{S}<bottom image="menuframe.png" left="0" top="{MENU_H - MENU_BAND}" width="1/1" '
                 f'height="{MENU_BAND}" method="tile" border="{MENU_BAND}, 0, {MENU_BAND}, 0">')
    parts.append(f'{S}{S}{S}{S}<arrangement height="ImageSize" />')
    parts.append(f"{S}{S}{S}</bottom>")
    parts.append(f"{S}{S}</frame>")
    parts.append(f"{S}{S}<item>")
    parts.append(f'{S}{S}{S}<normal image="menu_item.png" left="0" top="0" width="1/1" height="{ITEM_H}" '
                 f'method="stretch" border="0, 0, 0, 0" />')
    parts.append(f'{S}{S}{S}<selected image="menu_item.png" left="0" top="{ITEM_H}" width="1/1" '
                 f'height="{ITEM_H}" method="stretch" border="8, 0, 8, 0" />')
    parts.append(f'{S}{S}{S}<multisel image="menu_item.png" left="0" top="{ITEM_H * 2}" width="1/1" '
                 f'height="{ITEM_H}" method="stretch" border="8, 0, 8, 0" />')
    parts.append(f'{S}{S}{S}<arrangement margin="4, 3, 4, 3" interval="0, 0" />')
    parts.append(f'{S}{S}{S}<text fontFace="{font}" fontSize="10" fontStyle="normal" antiAlias="true" '
                 f'color="#1D1D1F" shadow="none" shadowColor="#FFFFFF" shadowAlpha="120" shadowWidth="1">')
    parts.append(f'{S}{S}{S}{S}<selected color="#FFFFFF" />')
    parts.append(f'{S}{S}{S}{S}<disabled color="#B4B4B9" />')
    parts.append(f"{S}{S}{S}</text>")
    parts.append(f"{S}{S}</item>")
    # scroll buttons
    parts.append(f"{S}{S}<scrollbutton>")
    for st, r in (("normal", 0), ("hover", 1), ("down", 2), ("disabled", 3)):
        parts.append(f'{S}{S}{S}<{st} image="scroll_btn.png" left="0" top="{r * ARROW}" width="{ARROW}" '
                     f'height="{ARROW}" method="stretch" border="0, 0, 0, 0" />')
    parts.append(f'{S}{S}{S}<arrangement width="{ARROW}" height="{ARROW}" interval="0, 0" />')
    for i, name in enumerate(("uparrow", "downarrow", "leftarrow", "rightarrow")):
        parts.append(f"{S}{S}{S}<{name}>")
        for st, r in (("normal", 0), ("hover", 1), ("down", 2), ("disabled", 3)):
            parts.append(f'{S}{S}{S}{S}<{st} image="arrows.png" left="{i * ARROW}" top="{r * ARROW}" '
                         f'width="{ARROW}" height="{ARROW}" />')
        parts.append(f"{S}{S}{S}</{name}>")
    parts.append(f"{S}{S}</scrollbutton>")
    parts.append(f"{S}</submenu>")
    parts.append("")

    # ---- recommended settings ----
    parts.append(f"{S}<recommended>")
    for mode, count in (("mode1", "6, 3"), ("mode2", "6, 6")):
        parts.append(f"{S}{S}<{mode}>")
        parts.append(f'{S}{S}{S}<caption textMargin="0, 0, 0, 0" centerText="true" multiLine="false" />')
        parts.append(f'{S}{S}{S}<tab size="74, 24" textMargin="2, 0, 2, 0" fixedWidth="true" '
                     f'multiLine="false" leftText="false" />')
        parts.append(f'{S}{S}{S}<button size="76, 76" count="{count}" iconSize="40" '
                     f'iconMargin="0, 8, 0, 0" textMargin="1, 4, 1, 0" leftIcon="false" '
                     f'text="true" singleLine="true" leftText="false" />')
        parts.append(f"{S}{S}</{mode}>")
    parts.append(f"{S}</recommended>")
    parts.append("")
    parts.append("</skin>")
    parts.append("")

    with open(path, "w", encoding="utf-16") as f:
        f.write("\n".join(parts))
    print("  wrote skin.xml (UTF-16 LE with BOM)")


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(base, "macOS Sonoma")
    os.makedirs(out, exist_ok=True)
    p = lambda n: os.path.join(out, n)

    print("building parts ->", out)
    build_window(p("window.png"))
    build_win_buttons(p("win_buttons.png"))
    build_search(p("search.png"))
    build_tab(p("tab.png"))
    build_button(p("button.png"))
    build_lockmarker(p("lockmarker.png"))
    build_menu(p("menuframe.png"))
    build_menu_item(p("menu_item.png"))
    build_scroll(p("scroll_btn.png"), p("arrows.png"))
    build_xml(p("skin.xml"))
    print("done.")


if __name__ == "__main__":
    main()
