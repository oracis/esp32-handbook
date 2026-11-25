#!/usr/bin/env python3
"""补齐 lab 多语言字典：扫描页面里所有 tr("...") / data-i18n / data-i18n-ph 的中文键，
   对比 dicts/lab.json 各语言 t 字典，缺失的用翻译端点补齐并写回。
   用法：python tools/i18n/patch_lab.py
"""
import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import build  # noqa: E402

LAB = ROOT / "lab" / "index.html"
DICTS = HERE / "dicts" / "lab.json"
CJK = re.compile(r"[\u4e00-\u9fff]")


def page_keys():
    s = LAB.read_text(encoding="utf-8")
    keys = set()
    for m in re.finditer(r'''\btr\(\s*(['"])(.*?)\1\s*\)''', s, re.S):
        v = m.group(2)
        if CJK.search(v) and "\n" not in v and len(v) < 200:
            keys.add(v)
    soup = BeautifulSoup(s, "html.parser")
    for el in soup.select("[data-i18n]"):
        k = el.get("data-i18n", "")
        if CJK.search(k):
            keys.add(k)
    for el in soup.select("[data-i18n-ph]"):
        k = el.get("data-i18n-ph", "")
        if CJK.search(k):
            keys.add(k)
    # 工作台外观文案（顶栏/按钮/示例选项）也用 data-i18n 标记，已被上面覆盖
    return keys


def main():
    keys = sorted(page_keys())
    d = json.loads(DICTS.read_text(encoding="utf-8"))
    cache = build.load_cache()
    print("page CJK keys:", len(keys), "| langs:", list(d.keys()))
    added_total = 0
    for lang, obj in d.items():
        t = obj["t"]
        missing = [k for k in keys if k not in t]
        print(f"  {lang}: missing {len(missing)}")
        if not missing:
            continue
        bucket = cache.setdefault(lang, {})
        for k in missing:
            try:
                if k in bucket:
                    val = bucket[k]
                else:
                    val = build.translate_one(k, lang)
                    bucket[k] = val
                t[k] = val
            except Exception as e:
                print(f"    FAIL {k[:20]}: {str(e)[:60]}")
                t[k] = k  # 退化：保留原文，不阻断
        added_total += len(missing)
    build.save_cache(cache)
    DICTS.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    print("added entries:", added_total)


if __name__ == "__main__":
    main()
