#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验收主站 9 语言 LBWHOLE 块：卡片数、链接规范、外链残留、译文完整度。"""
import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent.parent
SITE = ROOT / "index.html"
LAB = ROOT / "lab" / "index.html"
CJK = re.compile(r"[\u4e00-\u9fff]")


def grab(src, marker):
    a = src.index(marker) + len(marker)
    depth, ins, esc = 0, False, False
    for j in range(a, len(src)):
        c = src[j]
        if ins:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                ins = False
        else:
            if c == '"':
                ins = True
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    return json.loads(src[a:j + 1])
    raise AssertionError(marker)


def nos_of_lab():
    s = LAB.read_text(encoding="utf-8")
    i = s.index("const LESSONS = [")
    j = s.index("\n];", i)
    return re.findall(r'no:"([^"]+)"', s[i:j])


def check_block(lang, html, nos, expect_cjk=False):
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("a.lab-item")
    hrefs = [c.get("href", "") for c in cards]
    want = ["https://lab.ydtgo.top/#/lessons/%s" % n for n in nos]
    text = soup.get_text(" ")
    cjk = len(CJK.findall(text))
    issues = []
    if len(cards) != len(nos):
        issues.append("卡片 %d != %d" % (len(cards), len(nos)))
    if hrefs != want:
        bad = [(i, h) for i, h in enumerate(hrefs) if i >= len(want) or h != want[i]][:3]
        issues.append("href 异常 %d 处，首例 %s" % (len([1 for i, h in enumerate(hrefs)
                                                       if i >= len(want) or h != want[i]]), bad))
    if "esp-labs-web" in html or "pages.dev" in html:
        issues.append("仍有外链")
    if text.count("ZZ") or "ZZCODE" in html or "ZZBRZZ" in html:
        issues.append("残留占位符")
    if not expect_cjk and len(CJK.findall(text)) > len(text) * 0.02:
        issues.append("中文残留 %d 字" % cjk)
    return len(cards), cjk, issues


def main():
    src = SITE.read_text(encoding="utf-8")
    nos = nos_of_lab()
    print("实验室课程数:", len(nos))
    ok = True

    i18n = grab(src, "window.I18N = ")
    zh_html = BeautifulSoup(src, "html.parser").select_one('#labs [data-l10n="LBWHOLE"]')
    zh_html = zh_html.decode_contents() if zh_html else ""
    for tag, html, cjk_ok in [("zh(页面)", zh_html, True),
                              ("en(I18N.b)", i18n["b"].get("LBWHOLE", ""), False)]:
        n, cjk, iss = check_block(tag, html, nos, cjk_ok)
        print("  %-12s 卡片 %d 中文 %d %s" % (tag, n, cjk, "OK" if not iss else "!! " + "; ".join(iss)))
        ok &= not iss

    multi = grab(src, "window.I18N.MULTI = ")
    for lang, obj in multi.items():
        html = obj.get("b", {}).get("LBWHOLE", "")
        n, cjk, iss = check_block(lang, html, nos)
        print("  %-12s 卡片 %d 中文 %d %s" % (lang, n, cjk, "OK" if not iss else "!! " + "; ".join(iss)))
        ok &= not iss

    total = src.count("esp-labs-web") + src.count("pages.dev")
    print("全页外链残留:", total)
    ok &= total == 0
    print("结论:", "全部通过" if ok else "有问题")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
