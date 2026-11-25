#!/usr/bin/env python3
"""把生成好的多语言字典注入两个单文件页面（可重复运行）。

用法：python tools/i18n/inject.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SITE = ROOT / "index.html"
LAB = ROOT / "lab/index.html"

S_START, S_END = "<!-- I18N_MULTI:START -->", "<!-- I18N_MULTI:END -->"
L_START, L_END = "/* I18N_MULTI:START */", "/* I18N_MULTI:END */"


def js(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def replace_block(src, start, end, block, anchor=None):
    if start in src and end in src:
        a = src.index(start)
        b = src.index(end) + len(end)
        return src[:a] + block + src[b:], "replaced"
    if anchor is None:
        raise SystemExit("anchor missing")
    i = src.index(anchor)
    return src[:i] + block + "\n" + src[i:], "inserted"


def main():
    site = json.loads((HERE / "dicts/site.json").read_text(encoding="utf-8"))
    lab = json.loads((HERE / "dicts/lab.json").read_text(encoding="utf-8"))
    langs = list(site.keys())
    print("languages:", ", ".join(langs))

    s_block = (S_START + "\n<script>window.I18N.MULTI = " + js(site) +
               ";</script>\n" + S_END)
    src = SITE.read_text(encoding="utf-8")
    src, act = replace_block(src, S_START, S_END, s_block,
                             "<script>\n/* ---------- 多语言切换（9 种） ---------- */")
    with open(SITE, "w", encoding="utf-8", newline="") as f: f.write(src)
    print("site:", act, SITE.stat().st_size, "bytes")

    l_block = (L_START + "\nwindow.I18N.MULTI = " + js(lab) + ";\n" + L_END)
    src = LAB.read_text(encoding="utf-8")
    src, act = replace_block(src, L_START, L_END, l_block, "const LAB_LANGS = [")
    with open(LAB, "w", encoding="utf-8", newline="") as f: f.write(src)
    print("lab:", act, LAB.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
