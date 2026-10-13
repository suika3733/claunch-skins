# -*- coding: utf-8 -*-
"""
Regenerate skin.xml in the exact structure CLaunch 4.23 expects
(validated against the bundled official skin "Glass.zip"), then pack a
FLAT zip: skin.xml + PNGs at the archive root, no wrapping folder.
"""
import os, zipfile

BASE = os.path.dirname(os.path.abspath(__file__))
SKIN = os.path.join(BASE, "macOS Sonoma")

FONT = "Microsoft YaHei UI"

# --- palette mirrored from the artwork ---
C_TITLE  = "#6E6E73"
C_TEXT   = "#1D1D1F"
C_MUTED  = "#6E6E73"
C_ACCENT = "#0A84FF"
C_WHITE  = "#FFFFFF"
C_DIS    = "#B4B4B9"

T = "\t"


def dec(shadow, color, sc="#FFFFFF", sa="255", sw="1"):
    return f'shadow="{shadow}" color="{color}" shadowColor="{sc}" shadowAlpha="{sa}" shadowWidth="{sw}"'


def button_states(name, img, col, offset, rows=3):
    """window system button: normal / hover / down [/ downhover]"""
    out = [f"{T}<{name}>"]
    seq = [("normal", 0), ("hover", 1), ("down", 2)]
    if rows == 4:
        seq.append(("downhover", 2))
    for st, r in seq:
        out.append(
            f'{T}{T}<{st} image="{img}" left="{col * 12}" top="{r * 12}" '
            f'width="12" height="12" method="stretch" border="0, 0, 0, 0" />'
        )
    out += [
        f"{T}{T}<arrangement>",
        f'{T}{T}{T}<left base="TopFrame" side="left" offset="{offset}" />',
        f'{T}{T}{T}<top base="TopFrame" side="top" offset="11" />',
        f'{T}{T}{T}<right width="ImageSize" />',
        f'{T}{T}{T}<bottom height="ImageSize" />',
        f"{T}{T}</arrangement>",
        f"{T}</{name}>",
    ]
    return "\n".join(out)


X = []
X += ['<?xml version="1.0" encoding="UTF-16" standalone="yes" ?>', "",
      "<!-- CLaunch Skin : macOS Sonoma (light) -->", "",
      '<skin title="macOS Sonoma" author="UI Designer" version="4.20">', ""]

X.append("""<comment>macOS Sonoma 風格皮膚。

* 需要 32bpp 顯示模式與 Unicode 版 CLaunch 4.20 以上
* 視窗列左側為關閉(紅)／鎖定(黃)／模式(綠)三個圓鈕，滑過顯示 mac 字形
* 分頁為分段控制器膠囊樣式，選中頁白色
* 圖示按鈕常規無底色，滑過為淺灰圓角塊，文字轉系統藍
* 右鍵子選單選中項為 macOS 系統藍 #0A84FF 白字
</comment>""")

X += ["",
      f'{T}<general tabPosition="top" alphaChannel="true" clippingColor="#FF00FF" '
      f'sizeArea="6, 6, 6, 6" shadowArea="0, 0, 0, 0" />', ""]

# ---- background / frames (9-slice from one image) ----
X += [f'{T}<background image="window.png" left="0" top="0" width="1/1" height="1/1" '
      f'method="stretch" border="12, 34, 12, 20">',
      f'{T}{T}<arrangement offset="0, 0, 0, 0" />',
      f"{T}</background>", ""]

X += [f"{T}<frame>",
      f'{T}{T}<top image="window.png" left="0" top="0" width="1/1" height="34" '
      f'method="tile" border="12, 0, 12, 0">',
      f'{T}{T}{T}<arrangement height="ImageSize" />', f"{T}{T}</top>",
      f'{T}{T}<left image="window.png" left="0" top="34" width="12" height="26" '
      f'method="tile" border="0, 0, 0, 0">',
      f'{T}{T}{T}<arrangement width="ImageSize" />', f"{T}{T}</left>",
      f'{T}{T}<right image="window.png" left="36" top="34" width="12" height="26" '
      f'method="tile" border="0, 0, 0, 0">',
      f'{T}{T}{T}<arrangement width="ImageSize" />', f"{T}{T}</right>",
      f'{T}{T}<bottom image="window.png" left="0" top="60" width="1/1" height="20" '
      f'method="tile" border="12, 0, 12, 0">',
      f'{T}{T}{T}<arrangement height="ImageSize" />', f"{T}{T}</bottom>",
      f"{T}</frame>", ""]

# ---- traffic lights ----
X += [T + button_states("closebutton", "win_buttons.png", 0, 13).replace("\n", "\n" + T), ""]
X += [T + button_states("pinbutton", "win_buttons.png", 1, 33, 4).replace("\n", "\n" + T), ""]
X += [T + button_states("modebutton", "win_buttons.png", 2, 53, 4).replace("\n", "\n" + T), ""]

# ---- search button ----
X += [f"{T}<searchbutton>"]
for st, r in (("normal", 0), ("hover", 1), ("down", 2), ("downhover", 2)):
    X.append(f'{T}{T}<{st} image="search.png" left="0" top="{r * 20}" width="20" '
             f'height="20" method="stretch" border="0, 0, 0, 0" />')
X += [f"{T}{T}<arrangement>",
      f'{T}{T}{T}<left base="TopFrame" side="right" offset="-31" />',
      f'{T}{T}{T}<top base="TopFrame" side="top" offset="7" />',
      f'{T}{T}{T}<right width="ImageSize" />',
      f'{T}{T}{T}<bottom height="ImageSize" />',
      f"{T}{T}</arrangement>", f"{T}</searchbutton>", ""]

# ---- caption ----
X += [f"{T}<caption>",
      f"{T}{T}<arrangement>",
      f'{T}{T}{T}<left base="TopFrame" side="left" offset="76" />',
      f'{T}{T}{T}<top base="TopFrame" side="top" offset="0" />',
      f'{T}{T}{T}<right width="Variable" base="SearchButton" side="left" offset="-6" />',
      f'{T}{T}{T}<bottom height="Variable" base="TopFrame" side="bottom" offset="0" />',
      f"{T}{T}</arrangement>",
      f"{T}{T}<text>",
      f'{T}{T}{T}<font face="{FONT}" size="10" style="normal" antiAlias="true" />',
      f'{T}{T}{T}<decoration {dec("none", C_TITLE)} />',
      f"{T}{T}</text>", f"{T}</caption>", ""]

# ---- tab area ----
X += [f"{T}<tabarea>",
      f'{T}{T}<arrangement offset="0, 0, 0, 0" margin="10, 9, 10, 6" />',
      f'{T}{T}<tab image="tab.png" method="stretch" border="10, 4, 10, 4" designs="1">',
      f'{T}{T}{T}<arrangement pitch="2, 0" />',
      f"{T}{T}{T}<text>",
      f"{T}{T}{T}{T}<font>",
      f'{T}{T}{T}{T}{T}<active face="{FONT}" size="10" style="bold" antiAlias="true" />',
      f'{T}{T}{T}{T}{T}<inactive face="{FONT}" size="10" style="normal" antiAlias="true" />',
      f"{T}{T}{T}{T}</font>",
      f"{T}{T}{T}{T}<decoration>",
      f'{T}{T}{T}{T}{T}<normal {dec("none", C_MUTED)} />',
      f'{T}{T}{T}{T}{T}<hover {dec("none", C_TEXT)} />',
      f'{T}{T}{T}{T}{T}<active {dec("none", C_TEXT)} />',
      f"{T}{T}{T}{T}</decoration>",
      f"{T}{T}{T}</text>",
      f"{T}{T}</tab>", f"{T}</tabarea>", ""]

# ---- button area ----
X += [f"{T}<buttonarea>",
      f'{T}{T}<arrangement offset="0, 0, 0, 0" margin="10, 6, 10, 12" />',
      f'{T}{T}<button image="button.png" method="stretch" border="12, 12, 12, 12" designs="1">',
      f'{T}{T}{T}<arrangement pitch="2, 2" shiftHover="-1, -1" shiftDown="1, 1" />',
      f"{T}{T}{T}<text>",
      f'{T}{T}{T}{T}<font face="{FONT}" size="9" style="normal" antiAlias="true" />',
      f"{T}{T}{T}{T}<decoration>",
      f'{T}{T}{T}{T}{T}<normal {dec("lower", C_TEXT, sa="220")} />',
      f'{T}{T}{T}{T}{T}<hover {dec("lower", C_ACCENT, sa="220")} />',
      f'{T}{T}{T}{T}{T}<down {dec("lower", C_ACCENT, sa="220")} />',
      f"{T}{T}{T}{T}</decoration>",
      f"{T}{T}{T}</text>",
      f"{T}{T}</button>",
      f'{T}{T}<lockmarker image="lockmarker.png" left="0" top="0" width="1/1" height="1/1" '
      f'method="stretch" border="0, 0, 0, 0">',
      f'{T}{T}{T}<arrangement offset="-1, -1, 1, 1" zOrder="bottom" />',
      f"{T}{T}</lockmarker>",
      f"{T}</buttonarea>", ""]

# ---- submenu ----
X += [f'{T}<submenu image="menuframe.png" left="0" top="0" width="1/1" height="1/1" '
      f'method="stretch" border="12, 12, 12, 12">',
      f'{T}{T}<arrangement shadowArea="0, 0, 0, 0" />',
      f"{T}{T}<frame>",
      f'{T}{T}{T}<top image="menuframe.png" left="0" top="0" width="1/1" height="12" '
      f'method="tile" border="12, 0, 12, 0">',
      f'{T}{T}{T}{T}<arrangement height="ImageSize" />', f"{T}{T}{T}</top>",
      f'{T}{T}{T}<left image="menuframe.png" left="0" top="12" width="12" height="24" '
      f'method="tile" border="0, 0, 0, 0">',
      f'{T}{T}{T}{T}<arrangement width="ImageSize" />', f"{T}{T}{T}</left>",
      f'{T}{T}{T}<right image="menuframe.png" left="36" top="12" width="12" height="24" '
      f'method="tile" border="0, 0, 0, 0">',
      f'{T}{T}{T}{T}<arrangement width="ImageSize" />', f"{T}{T}{T}</right>",
      f'{T}{T}{T}<bottom image="menuframe.png" left="0" top="36" width="1/1" height="12" '
      f'method="tile" border="12, 0, 12, 0">',
      f'{T}{T}{T}{T}<arrangement height="ImageSize" />', f"{T}{T}{T}</bottom>",
      f"{T}{T}</frame>",
      f"{T}{T}<item>",
      f'{T}{T}{T}<normal image="menu_item.png" left="0" top="0" width="1/1" height="22" '
      f'method="stretch" border="0, 0, 0, 0" />',
      f'{T}{T}{T}<selected image="menu_item.png" left="0" top="22" width="1/1" height="22" '
      f'method="stretch" border="8, 0, 8, 0" />',
      f'{T}{T}{T}<multisel image="menu_item.png" left="0" top="44" width="1/1" height="22" '
      f'method="stretch" border="8, 0, 8, 0" />',
      f'{T}{T}{T}<arrangement margin="4, 3, 4, 3" interval="0, 0" />',
      f"{T}{T}{T}<text>",
      f'{T}{T}{T}{T}<font face="{FONT}" size="10" style="normal" antiAlias="true" />',
      f"{T}{T}{T}{T}<decoration>",
      f'{T}{T}{T}{T}{T}<normal {dec("none", C_TEXT)} />',
      f'{T}{T}{T}{T}{T}<selected {dec("none", C_WHITE)} />',
      f'{T}{T}{T}{T}{T}<disabled {dec("none", C_DIS)} />',
      f"{T}{T}{T}{T}</decoration>",
      f"{T}{T}{T}</text>",
      f"{T}{T}</item>"]

X += [f"{T}{T}<scrollbutton>"]
for st, r in (("normal", 0), ("hover", 1), ("down", 2), ("disabled", 3)):
    X.append(f'{T}{T}{T}<{st} image="scroll_btn.png" left="0" top="{r * 16}" width="16" '
             f'height="16" method="stretch" border="0, 0, 0, 0" />')
X += [f'{T}{T}{T}<arrangement width="16" height="16" interval="0, 0" />']
for i, nm in enumerate(("uparrow", "downarrow", "leftarrow", "rightarrow")):
    X.append(f"{T}{T}{T}<{nm}>")
    for st, r in (("normal", 0), ("hover", 1), ("down", 2), ("disabled", 3)):
        X.append(f'{T}{T}{T}{T}<{st} image="arrows.png" left="{i * 16}" top="{r * 16}" '
                 f'width="16" height="16" />')
    X.append(f"{T}{T}{T}</{nm}>")
X += [f"{T}{T}</scrollbutton>", f"{T}</submenu>", ""]

# ---- recommended ----
X += [f"{T}<recommended>"]
for mode, count in (("mode1", "6, 3"), ("mode2", "6, 6")):
    X += [f"{T}{T}<{mode}>",
          f'{T}{T}{T}<caption textMargin="0, 0, 0, 0" centerText="true" multiLine="false" />',
          f'{T}{T}{T}<tab size="74, 24" textMargin="2, 0, 2, 0" fixedWidth="true" '
          f'multiLine="false" leftText="false" />',
          f'{T}{T}{T}<button size="76, 76" count="{count}" iconSize="40" '
          f'iconMargin="0, 8, 0, 0" textMargin="1, 4, 1, 0" leftIcon="false" '
          f'text="true" singleLine="true" leftText="false" />',
          f"{T}{T}</{mode}>"]
X += [f"{T}</recommended>"]

X += ["", "</skin>", ""]

xml = "\n".join(X)
with open(os.path.join(SKIN, "skin.xml"), "w", encoding="utf-16") as f:
    f.write(xml)
print("skin.xml rewritten (UTF-16 LE,", len(xml), "chars )")

# ---- flat zip: no wrapping folder ----
zip_path = os.path.join(BASE, "macOS Sonoma.zip")
names = ["skin.xml"] + sorted(n for n in os.listdir(SKIN) if n.lower().endswith(".png"))
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for n in names:
        z.write(os.path.join(SKIN, n), n)
print("packed:", zip_path)
print("zip root:", zipfile.ZipFile(zip_path).namelist())
