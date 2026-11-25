# -*- coding: utf-8 -*-
"""从 index.html 已渲染的 MULTI 块反解出 labs_i18n.json。

为什么反解：labs_i18n.json 在 23:52 的回滚里丢了，但这些译文早已渲染进
MULTI[*].b.LBWHOLE（含人工修正过的术语），反解比重新机翻更准、零配额。
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SITE = ROOT / "index.html"
OUT = HERE / "labs_i18n.json"
NATIVE = "简体中文 · English · 繁體中文 · 日本語 · 한국어 · Español · Português · Français · Русский"


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
                    return json.loads(src[a:j + 1]), a, j + 1
    raise AssertionError(marker)


def text_of(frag):
    """取 HTML 片段里的纯文本（保留内部标签结构交给调用方决定）。"""
    return frag.strip()


def main():
    src = SITE.read_text(encoding="utf-8")
    multi, _, _ = grab(src, "window.I18N.MULTI = ")

    out = {}
    for lang, obj in multi.items():
        html = obj.get("b", {}).get("LBWHOLE", "")
        if not html:
            print("跳过 %s：无 LBWHOLE" % lang)
            continue
        d = {}
        m = re.search(r"<h2>(.*?)</h2>", html, re.S)
        d["head"] = m.group(1).strip() if m else ""
        m = re.search(r'<p class="sec-sub">(.*?)</p>', html, re.S)
        d["sub"] = m.group(1).strip() if m else ""

        # 6 组：组名 / 组描述 / 计数格式
        heads = re.findall(
            r'<div class="lab-track-head"><div><b>(.*?)</b><span class="lab-td">(.*?)</span></div>'
            r'<span class="lab-count">(.*?)</span>', html, re.S)
        if len(heads) != 6:
            print("%s 分组解析异常：%d 组" % (lang, len(heads)))
            continue
        for i, (nm, desc, cnt) in enumerate(heads):
            d["t%dn" % i] = nm.strip()
            d["t%dd" % i] = desc.strip()
            if i == 0:
                # 把计数字里的数字替换成 %d
                d["cnt"] = re.sub(r"\d+", "%d", cnt.strip(), count=1)

        m = re.search(r'<div class="lab-hint">(.*?)</div>', html, re.S)
        d["hint"] = m.group(1).strip() if m else ""

        # 语言清单：块尾 "xx 简体中文 · English · ..."
        tail = html.rsplit('<p class="sec-sub"', 1)[-1]
        m = re.search(r">(.*?)</p>", tail, re.S)
        if m and NATIVE in m.group(1):
            d["langs"] = m.group(1).replace(NATIVE, "").strip()
        else:
            d["langs"] = ""

        out[lang] = d

    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("反解完成：%d 语言 -> %s" % (len(out), OUT))
    for lang, d in out.items():
        missing = [k for k in ("head", "sub", "hint", "cnt", "langs") if not d.get(k)]
        bad = ["t%d%s" % (i, s) for i in range(6) for s in "nd"
               if not d.get("t%d%s" % (i, s))]
        print("  %-6s %s%s" % (lang, "OK" if not (missing + bad) else "缺 " + str(missing + bad),
                               "" if not d.get("cnt") else ""))


if __name__ == "__main__":
    sys.exit(main())
