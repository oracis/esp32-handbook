# -*- coding: utf-8 -*-
"""页脚署名改版后，同步 window.I18N.t 的键：删失效键、登记新键。幂等。"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "index.html"

OLD_KEYS = [
    "实验台内容整理自",
    "by Abderrehmen Gharsallah（MIT License）。本站仅作中文摘要与导航；课程原文与模拟器归原作者所有。",
    "内容整理自",
    "另有独立许可。",
    "by Abderrehmen Gharsallah，依 MIT License 复用。本站仅做中文摘要与导航，课程原文与交互模拟器归原作者所有。固件仓库",
]
NEW = [
    ("实验台主题编排参考开源项目 ",
     "Lab topic outline references the open-source project "),
    ("（by Abderrehmen Gharsallah，MIT License）；本站 46 课的讲解、代码与仿真均为原创，不转载原文。",
     " (by Abderrehmen Gharsallah, MIT License). All 46 lessons on this site - explanations, "
     "code and simulations - are original; no source text is reproduced."),
]


def grab_json(src, marker="window.I18N = "):
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
                    return a, j + 1
    raise AssertionError(marker)


def main():
    s = SITE.read_text(encoding="utf-8")
    a, b = grab_json(s)
    dic = json.loads(s[a:b])
    t = dic["t"]
    removed = [k for k in OLD_KEYS if k in t]
    for k in removed:
        del t[k]
    added = 0
    for zh, en in NEW:
        if t.get(zh) != en:
            t[zh] = en
            added += 1
    # 排序保持稳定（按插入序即可，这里直接重写）
    out = json.dumps(dic, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    s = s[:a] + out + s[b:]
    SITE.write_text(s, encoding="utf-8", newline="")
    print("删除失效键 %d 个：%s" % (len(removed), removed))
    print("登记新键 %d 个" % added)
    print("页面 %d 字节" % len(s.encode("utf-8")))


if __name__ == "__main__":
    sys.exit(main())
