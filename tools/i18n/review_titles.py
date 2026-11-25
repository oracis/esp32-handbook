# -*- coding: utf-8 -*-
"""抽查各语言 46 课标题与分组名，输出对照表供人工校对。"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/i18n"))
import build

LANGS = ["zh-TW", "ja", "ko", "es", "pt", "fr", "ru"]
cache = json.loads((ROOT / "tools/i18n/cache.json").read_text(encoding="utf-8"))
lab_src = (ROOT / "lab/index.html").read_text(encoding="utf-8")
i = lab_src.index("const LESSONS = [")
seg = lab_src[i:lab_src.index("\n];", i)]
titles = [(m.group(1), m.group(2)) for m in
          re.finditer(r'no:"(\d+)",\s*title:"([^"]+)"', seg)]

CJK = re.compile(r"[\u4e00-\u9fff]")
args = sys.argv[1:] or LANGS
for lang in args:
    c = cache.get(lang, {})
    miss = [no for no, t in titles if t not in c]
    resid = [no for no, t in titles if t in c and lang != "zh-TW" and CJK.search(c[t])]
    print("=== %s  缺 %d  残留汉字 %d" % (lang, len(miss), len(resid)))
    if miss:
        print("  缺失课号:", " ".join(miss))
    if resid:
        print("  汉字残留:", " ".join(resid))
    for no, t in titles:
        if no in ("31", "32", "34", "36", "39", "40", "42", "44", "46"):
            print("  %s  %-34s -> %s" % (no, t[:32], c.get(t, "(缺)")))
