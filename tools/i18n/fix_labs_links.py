#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把主站 9 语言 LBWHOLE 块里的课程卡链接规范化。

机翻有可能改动 href（或漏译整块导致顺序错位），这里按 DOM 顺序把
第 1..46 个 .lab-item 的 href 强制写回 https://lab.ydtgo.top/#/lessons/<no>。
运行顺序：inject.py 之后。
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "index.html"
LAB = ROOT / "lab" / "index.html"

CARD = re.compile(r'<a class="lab-item" href="[^"]*"')


def lesson_numbers():
    s = LAB.read_text(encoding="utf-8")
    i = s.index("const LESSONS = [")
    j = s.index("\n];", i)
    return re.findall(r'no:"([^"]+)"', s[i:j])


def fix_block(html, nos):
    idx = {"i": 0}
    miss = []

    def sub(m):
        k = idx["i"]
        idx["i"] = k + 1
        if k >= len(nos):
            miss.append(k)
            return m.group(0)
        return '<a class="lab-item" href="https://lab.ydtgo.top/#/lessons/%s"' % nos[k]

    out = CARD.sub(sub, html)
    return out, idx["i"]


def grab_json(src, marker, open_ch="{", close_ch="}"):
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
            elif c == open_ch:
                depth += 1
            elif c == close_ch:
                depth -= 1
                if depth == 0:
                    return a, j + 1
    raise AssertionError(marker)


def main():
    nos = lesson_numbers()
    if len(nos) != 46:
        print("课程号不是 46 个：%d" % len(nos))
        return 1

    s = SITE.read_text(encoding="utf-8")
    report = []

    # 1) 英文块：window.I18N.b.LBWHOLE
    a, b = grab_json(s, "window.I18N = ")
    dic = json.loads(s[a:b])
    if "LBWHOLE" in dic.get("b", {}):
        dic["b"]["LBWHOLE"], n = fix_block(dic["b"]["LBWHOLE"], nos)
        report.append(("en", n))
    s = s[:a] + json.dumps(dic, ensure_ascii=False).replace("</", "<\\/") + s[b:]

    # 2) 其余 7 语言：window.I18N.MULTI[lang].b.LBWHOLE
    marker = "window.I18N.MULTI = "
    if marker in s:
        a, b = grab_json(s, marker)
        multi = json.loads(s[a:b])
        for lang, obj in multi.items():
            blk = obj.get("b", {}).get("LBWHOLE")
            if blk is None:
                report.append((lang, -1))
                continue
            obj["b"]["LBWHOLE"], n = fix_block(blk, nos)
            report.append((lang, n))
        s = s[:a] + json.dumps(multi, ensure_ascii=False).replace("</", "<\\/") + s[b:]

    SITE.write_text(s, encoding="utf-8", newline="")
    for lang, n in report:
        flag = "OK" if n == 46 else "注意：卡片数 %d" % n
        print("  %-6s %s" % (lang, flag))
    print("链接规范化完成，页面 %d 字节" % len(s.encode("utf-8")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
