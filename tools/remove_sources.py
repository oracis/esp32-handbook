#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""删除主站「资料来源」相关区块（用户指令）。

- <section id="src"> 整节（含 10 条外部来源链接）
- 实验区 .lab-credit 署名行
- 页脚 ESP32 Labs 致谢行
- 不再使用的 .lab-credit CSS
- window.I18N.t 里只被这些区块使用的键
幂等：重复运行无副作用。
"""
import html as html_mod
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "index.html"

STALE_KEYS = [
    "资料来源",
    "版本号与参数以这些来源为准。本页整理于 2026-11-24。",
    "实验台主题编排参考开源项目 ",
    "（by Abderrehmen Gharsallah，MIT License）；本站 46 课的讲解、代码与仿真均为原创，不转载原文。",
]


def grab_json_span(src, marker="window.I18N = "):
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
    report = []

    # 1) <section id="src"> 整节（连注释一起）
    m = re.search(r'\n  <!-- ============ 来源 ============ -->\n  <section id="src">.*?</section>\n',
                  s, flags=re.S)
    if m:
        s = s[:m.start()] + "\n" + s[m.end():]
        report.append("删除 #src 整节 (%d 字符)" % (m.end() - m.start()))

    # 2) 实验区署名行
    m = re.search(r'\n *<div class="lab-credit">.*?</div>', s, flags=re.S)
    if m:
        s = s[:m.start()] + s[m.end():]
        report.append("删除实验区 .lab-credit 署名行")

    # 3) 页脚致谢行
    m = re.search(r'\n *<div style="font-size:12px;[^"]*">实验台主题编排参考开源项目 .*?</div>', s)
    if m:
        s = s[:m.start()] + s[m.end():]
        report.append("删除页脚 ESP32 Labs 致谢行")

    # 4) 板块注释里的「署名见…」
    s2 = s.replace(
        "<!-- ============ 延伸：ESP32 Labs 实验台（MIT · 署名见板块内与页脚） ============ -->",
        "<!-- ============ 延伸：ESP32 实验台（本站 46 课原创） ============ -->")
    if s2 != s:
        s = s2
        report.append("更新板块注释")

    # 5) 失效 CSS
    css = ('  .lab-credit{margin-top:18px;border-top:1px dashed var(--line);'
           'padding-top:14px;font-size:12.5px;color:var(--muted);line-height:1.8}\n'
           '  .lab-credit a{color:var(--text-2)}\n'
           '  .lab-credit a:hover{color:var(--amber)}\n')
    if css in s:
        s = s.replace(css, "")
        report.append("删除 .lab-credit CSS（3 行）")

    # 6) 清理 window.I18N.t 里已不在页面文本中的失效键（与 test_t_keys_appear_in_document 同口径）
    def norm(x):
        return re.sub(r"\s+", " ", x).strip()

    doc = html_mod.unescape(re.sub(r"<script.*?</script>", "", s, flags=re.S))
    nodes = {norm(c) for c in re.split(r"<[^>]+>", doc) if norm(c)}
    a, b = grab_json_span(s)
    dic = json.loads(s[a:b])
    dropped = [k for k in list(dic["t"]) if norm(k) not in nodes]
    for k in dropped:
        del dic["t"][k]
    s = s[:a] + json.dumps(dic, ensure_ascii=False,
                           separators=(",", ":")).replace("</", "<\\/") + s[b:]
    if dropped:
        report.append("清理失效 t 键 %d 个：%s" % (len(dropped), [d[:18] for d in dropped[:6]]))

    SITE.write_text(s, encoding="utf-8", newline="")
    for r in report:
        print(" -", r)
    print("页面 %d 字节；esp-labs-web 残留 %d 处" % (len(s.encode("utf-8")), s.count("esp-labs-web")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
