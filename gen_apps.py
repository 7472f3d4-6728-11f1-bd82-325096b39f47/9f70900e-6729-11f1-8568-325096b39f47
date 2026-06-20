# -*- coding: utf-8 -*-
"""
gen_apps.py — 無機版(muki.html)を唯一の雛形として、
有機版/高分子版を「データ以外は完全に同一」で再生成する。

方針:
 1) 雛形を MASTER_DATA ブロックの前後で分割する（pre / post）。
 2) データ(JSON)以外の差し替えは pre/post の「シェル部分」だけに適用する
    → 問題文に含まれる文字（例: 「無機化合物」）を誤置換しない。
 3) MASTER_DATA はマスタJSON（questionIds形式・共有問題を保持）をそのまま埋め込む。
学習ロジック・UI・統計・おさらい確認画面などは雛形からそのままコピーされる。
"""
import json, sys, re, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

TPL = "muki.html"

# 無機(雛形)側の「置換元」トークン
MUKI = {
    "title":   "<title>無機化学</title>",
    "apple":   '<meta name="apple-mobile-web-app-title" content="無機化学">',
    "theme":   '<meta name="theme-color" content="#00c1cc">',
    "manifest":'<link rel="manifest" href="manifest.json">',
    "accent":  "--accent:#7ce7ed; --accent2:#29f4ff; --accent-deep:#00c1cc; --accent-soft:#e0fdff; --accent-ink:#005257; --accent-glow:rgba(0,193,204,0.30);",
    "kicker":  ">Inorganic Chemistry<",
    "h1":      "<h1>無機化学</h1>",
    "lsp":     '"muki"',
    "suffix":  '"-muki-v4"',
    "dk":      '"muki_dark"',
    "sw":      '"./sw.js"',
}

SUBJECTS = {
  "yuki": {
    "master": "_yuki_master.json", "out": "yuki.html",
    "title":  "<title>有機化学</title>",
    "apple":  '<meta name="apple-mobile-web-app-title" content="有機化学">',
    "theme":  '<meta name="theme-color" content="#4966d8">',   # = accent-deep（muki と同じ規則）
    "manifest":'<link rel="manifest" href="yuki_manifest.json">',
    "accent": "--accent:#97AEFC; --accent2:#b0c5ff; --accent-deep:#4966d8; --accent-soft:#eef1ff; --accent-ink:#1a2e7a; --accent-glow:rgba(73,102,216,0.25);",
    "kicker": ">Organic Chemistry<",
    "h1":     "<h1>有機化学</h1>",
    "lsp":    '"yuki"',
    "suffix": '"-yuki-v4"',
    "dk":     '"yuki_dark"',
    "sw":     '"./yuki_sw.js"',
  },
  "kobunshi": {
    "master": "_kobunshi_master.json", "out": "kobunshi.html",
    "title":  "<title>高分子化学</title>",
    "apple":  '<meta name="apple-mobile-web-app-title" content="高分子化学">',
    "theme":  '<meta name="theme-color" content="#6db020">',
    "manifest":'<link rel="manifest" href="kobunshi_manifest.json">',
    "accent": "--accent:#9BDE40; --accent2:#b8ef60; --accent-deep:#6db020; --accent-soft:#f0fce0; --accent-ink:#2d5010; --accent-glow:rgba(109,176,32,0.25);",
    "kicker": ">Polymer Chemistry<",
    "h1":     "<h1>高分子化学</h1>",
    "lsp":    '"kobunshi"',
    "suffix": '"-kobun-v4"',
    "dk":     '"kobunshi_dark"',
    "sw":     '"./kobunshi_sw.js"',
  },
}

def split_template(s):
    a = s.find("const MASTER_DATA = {")
    b = s.find("const _qMap", a)
    if a < 0 or b < 0:
        raise SystemExit("MASTER_DATA block not found")
    return s[:a], s[b:]   # pre, post  (data block is dropped/rebuilt)

PRE_KEYS  = ["title","apple","theme","manifest","accent","kicker","h1"]
POST_KEYS = ["lsp","suffix","dk","sw"]

def replace_tokens(text, keys, cfg):
    for k in keys:
        src, dst = MUKI[k], cfg[k]
        cnt = text.count(src)
        if cnt != 1:
            raise SystemExit(f"token {k!r}: expected exactly 1 occurrence, found {cnt}")
        text = text.replace(src, dst)
    return text

def build(name, cfg):
    tpl = open(TPL, encoding="utf-8").read()
    pre, post = split_template(tpl)
    pre  = replace_tokens(pre,  PRE_KEYS,  cfg)
    post = replace_tokens(post, POST_KEYS, cfg)
    master = json.load(open(cfg["master"], encoding="utf-8"))
    data_js = "const MASTER_DATA = " + json.dumps(master, ensure_ascii=False, separators=(",",":")) + ";\n"
    out = pre + data_js + post
    open(cfg["out"], "w", encoding="utf-8").write(out)
    # quick self-audit
    chs = master["chapters"]; qs = master["questions"]
    refs = sum(len(c.get("questionIds", [])) for c in chs)
    print(f"[{name}] -> {cfg['out']}  bytes={len(out):,}  chapters={len(chs)} questions={len(qs)} qIdRefs={refs}")

if __name__ == "__main__":
    for name, cfg in SUBJECTS.items():
        build(name, cfg)
    print("done.")
