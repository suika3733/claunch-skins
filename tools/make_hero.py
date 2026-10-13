# -*- coding: utf-8 -*-
"""Compose a hero preview image for the README using the skin's real parts."""
import os
from PIL import Image, ImageDraw, ImageFont
from verify_render import render_window, L

BASE = os.path.dirname(os.path.abspath(__file__))
S = os.path.join(BASE, "macOS Sonoma")
OUT = os.path.join(BASE, "preview.png")

W, H = 1000, 470
BG = (42, 42, 46, 255)
ACCENT = (10, 132, 255)
C_T1, C_T2, C_T3 = (29, 29, 31), (110, 110, 115), (134, 134, 139)

fp = "C:/Windows/Fonts/msyh.ttc"
f_lab = ImageFont.truetype(fp, 13)
f_tab = ImageFont.truetype(fp, 13)
f_cap = ImageFont.truetype(fp, 15)
f_men = ImageFont.truetype(fp, 14)

img = Image.new("RGBA", (W, H), BG)

WIN_W, WIN_H = 470, 252
WX, WY = 56, 64
win = render_window(WIN_W, WIN_H, 0)
win.alpha_composite(Image.new("RGBA", (WIN_W - 24, WIN_H - 34 - 20), (247, 247, 249, 255)), (12, 34))

# ---- tab strip ----
tab_src = L("tab.png")
TAB_W, TAB_H, TX0, TY0 = 74, 24, 10, 43
tabs = [("常用", 2), ("工具", 0), ("网络", 0), ("开发", 0)]
tx = TX0
for name, state in tabs:
    win.alpha_composite(tab_src.crop((0, state * 24, 80, state * 24 + 24))
                        .resize((TAB_W, TAB_H), Image.Resampling.LANCZOS), (tx, TY0))
    tw = win.resize((1, 1))  # no-op keeps PIL quiet
    d = ImageDraw.Draw(win)
    d.text((tx + (TAB_W - d.textlength(name, font=f_tab)) / 2, TY0 + 4), name,
           font=f_tab, fill=C_T1 if state == 2 else C_T2)
    tx += TAB_W + 2

# ---- illustrative icon placeholders ----
ICONS = [
    ((74, 144, 217), "doc", "文件"), ((94, 92, 230), "note", "笔记"),
    ((52, 199, 89), "grid", "表格"), ((255, 159, 10), "globe", "浏览器"),
    ((255, 55, 95), "mail", "邮件"), ((142, 142, 147), "term", "终端"),
    ((175, 82, 222), "tri", "演示"), ((10, 132, 255), "check", "任务"),
    ((48, 209, 88), "square", "便签"), ((255, 214, 10), "lines", "下载"),
    ((100, 210, 255), "circle", "云盘"), ((191, 90, 242), "book", "词典"),
]
CELL, COLS, GX, GY = 76, 6, 10, 74
V = 160
W_ = (255, 255, 255, 255)


def glyph(pd, k):
    if k == "doc":
        pd.rounded_rectangle([46, 34, 114, 126], radius=8, outline=W_, width=10)
    elif k == "note":
        pd.rectangle([44, 44, 116, 116], outline=W_, width=10)
    elif k == "grid":
        pd.line([40, 58, 120, 58], fill=W_, width=10)
        pd.line([40, 82, 120, 82], fill=W_, width=10)
        pd.line([40, 106, 120, 106], fill=W_, width=10)
    elif k == "globe":
        pd.ellipse([42, 42, 118, 118], outline=W_, width=10)
        pd.line([42, 80, 118, 80], fill=W_, width=8)
    elif k == "mail":
        pd.rounded_rectangle([40, 50, 120, 110], radius=8, outline=W_, width=10)
        pd.line([44, 58, 80, 86, 116, 58], fill=W_, width=8)
    elif k == "term":
        pd.line([44, 54, 68, 80, 44, 106], fill=W_, width=10)
        pd.line([78, 106, 116, 106], fill=W_, width=10)
    elif k == "tri":
        pd.polygon([80, 40, 124, 120, 36, 120], outline=W_, width=10)
    elif k == "check":
        pd.line([40, 82, 68, 110, 122, 52], fill=W_, width=12)
    elif k == "square":
        pd.rounded_rectangle([44, 44, 116, 116], radius=12, outline=W_, width=10)
    elif k == "lines":
        for y in (52, 80, 108):
            pd.rounded_rectangle([40, y - 5, 120, y + 5], radius=5, fill=W_)
    elif k == "circle":
        pd.ellipse([44, 44, 116, 116], outline=W_, width=11)
    else:
        pd.rounded_rectangle([40, 46, 120, 114], radius=6, outline=W_, width=10)
        pd.line([80, 46, 80, 114], fill=W_, width=8)


for i, (rgb, kind, label) in enumerate(ICONS):
    cx = GX + (i % COLS) * (CELL + 2)
    cy = GY + (i // COLS) * (CELL + 2)
    if cy + CELL > WIN_H - 20:
        break
    plate = Image.new("RGBA", (V, V), (0, 0, 0, 0))
    pd = ImageDraw.Draw(plate)
    pd.rounded_rectangle([0, 0, V - 1, V - 1], radius=36, fill=rgb + (255,))
    glyph(pd, kind)
    win.alpha_composite(plate.resize((40, 40), Image.Resampling.LANCZOS),
                        (cx + (CELL - 40) // 2, cy + 8))
    d = ImageDraw.Draw(win)
    d.text((cx + (CELL - d.textlength(label, font=f_lab)) / 2, cy + 52), label,
           font=f_lab, fill=C_T1)

img.alpha_composite(win, (WX, WY))

# ---- submenu card ----
MW, MR = 216, 10
rows = [("打开", "Enter", "n"), ("以管理员身份运行", "", "n"),
        ("打开所在文件夹", "", "sep"), ("锁定项目", "", "sel"),
        ("属性", "Alt+Enter", "n"), ("重命名", "F2", "n"), ("删除", "Del", "dis")]
ROW_H, PAD = 26, 5
CARD_H = PAD * 2 + len(rows) * ROW_H
card = Image.new("RGBA", (MW + 60, CARD_H + 60), (0, 0, 0, 0))
cd = ImageDraw.Draw(card)
for i in range(16, 0, -1):
    cd.rounded_rectangle([30 - i, 30 - i, 30 + MW + i, 30 + CARD_H + i],
                         radius=MR + i // 2, fill=(0, 0, 0, 7))
cd.rounded_rectangle([30, 30, 30 + MW, 30 + CARD_H], radius=MR,
                     fill=(247, 247, 249, 255), outline=(201, 201, 207, 255), width=1)
y = 30 + PAD
for text, key, kind in rows:
    if kind == "sep":
        cd.line([38, y + ROW_H // 2, 30 + MW - 8, y + ROW_H // 2],
                fill=(221, 221, 226, 255), width=1)
    elif kind == "sel":
        cd.rounded_rectangle([34, y, 30 + MW - 4, y + ROW_H - 2], radius=4, fill=ACCENT + (255,))
        cd.text((44, y + 3), text, font=f_men, fill=(255, 255, 255, 255))
    else:
        col = C_T1 if kind == "n" else (180, 180, 185)
        cd.text((44, y + 3), text, font=f_men, fill=col + (255,))
    if key:
        cd.text((30 + MW - 12 - cd.textlength(key, font=f_men), y + 3), key,
                font=f_men, fill=(255, 255, 255, 255) if kind == "sel" else (134, 134, 139, 255))
    y += ROW_H
img.alpha_composite(card, (566, 96))

# ---- captions ----
d = ImageDraw.Draw(img)
d.text((WX, WY - 30), "窗口 · 工具栏 · 分段控制分页 · 图标按钮", font=f_cap, fill=(212, 214, 222, 255))
d.text((566, 66), "右键子菜单（选中项为系统蓝）", font=f_cap, fill=(212, 214, 222, 255))

img.convert("RGB").save(OUT)
print("wrote", OUT, img.size)
