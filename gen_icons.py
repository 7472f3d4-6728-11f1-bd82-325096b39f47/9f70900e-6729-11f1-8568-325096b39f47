# -*- coding: utf-8 -*-
"""
gen_icons.py — 科目別 PWA アイコン生成。
 - 192px / 512px
 - maskable 対応（フルブリード背景＋数字は中央の安全領域[直径80%]内に配置）
 - 科目ごとに別アイコン: 無機=1(シアン) / 有機=2(ブルー) / 高分子=3(グリーン)
"""
import os, sys, io
from PIL import Image, ImageDraw, ImageFont
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# (number, top color, bottom color = accent-deep), white digit
SUBJECTS = {
    "muki":     ("1", (124,231,237), (0,170,180)),   # cyan
    "yuki":     ("2", (151,174,252), (73,102,216)),  # blue
    "kobunshi": ("3", (155,222,64),  (90,150,28)),   # green
}
SIZES = [192, 512]

FONT_CANDIDATES = [
    "C:/Windows/Fonts/ariblk.ttf",   # Arial Black
    "C:/Windows/Fonts/arialbd.ttf",  # Arial Bold
    "C:/Windows/Fonts/segoeuib.ttf", # Segoe UI Bold
]

def load_font(px):
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            return ImageFont.truetype(p, px)
    return ImageFont.load_default()

def vgrad(size, top, bot):
    img = Image.new("RGB", (size, size), bot)
    px = img.load()
    for y in range(size):
        t = y / (size - 1)
        r = int(top[0] + (bot[0]-top[0])*t)
        g = int(top[1] + (bot[1]-top[1])*t)
        b = int(top[2] + (bot[2]-top[2])*t)
        for x in range(size):
            px[x, y] = (r, g, b)
    return img.convert("RGBA")

def make(num, top, bot, size):
    img = vgrad(size, top, bot)               # full-bleed background (maskable-safe)
    d = ImageDraw.Draw(img)
    # digit sized to ~58% of canvas -> well inside the 80% maskable safe circle
    font = load_font(int(size*0.60))
    bb = d.textbbox((0,0), num, font=font)
    w, h = bb[2]-bb[0], bb[3]-bb[1]
    x = (size - w)/2 - bb[0]
    y = (size - h)/2 - bb[1]
    # soft shadow then white digit
    sh = max(1, size//110)
    d.text((x+sh, y+sh), num, font=font, fill=(0,0,0,70))
    d.text((x, y), num, font=font, fill=(255,255,255,255))
    return img

count = 0
for name, (num, top, bot) in SUBJECTS.items():
    for s in SIZES:
        img = make(num, top, bot, s)
        out = f"{name}-icon-{s}.png"
        img.save(out, "PNG")
        count += 1
        print(f"wrote {out}  ({img.size[0]}x{img.size[1]}, digit '{num}')")
print(f"done. {count} icons.")
