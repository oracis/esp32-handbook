#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按结构化数据渲染主站 7 个外语版本的实验区卡片块（LBWHOLE）。

为什么不用机翻整块：LBWHOLE 是 13.5KB 的 HTML，整块送去翻译必然被截断，
而且模型会「顺手改写」href，历史上就是这样把 46 个链接译成了第三方站点。
这里改成：文案来自 labs_i18n.json（已翻好），卡片标题来自 dicts/lab.json，
HTML 与 href 全部由代码拼装 —— 结构不可能坏，链接不可能跑偏。

运行顺序：build.py → inject.py → labs_section_multi.py → check_labs_i18n.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SITE = ROOT / "index.html"
LAB = ROOT / "lab" / "index.html"
DICTS = HERE / "dicts" / "lab.json"
LABELS = HERE / "labs_i18n.json"

# (中文名, 中文描述, 起始课号, 结束课号) —— 与 tools/labs_section.py 的 TRACKS 保持一致
RANGES = [("01", "10"), ("11", "18"), ("19", "24"),
          ("25", "30"), ("31", "38"), ("39", "46")]
NATIVE = "简体中文 · English · 繁體中文 · 日本語 · 한국어 · Español · Português · Français · Русский"
CJK = re.compile(r"[\u4e00-\u9fff]")
KANA = re.compile(r"[\u3040-\u30ff]")
HANGUL = re.compile(r"[\uac00-\ud7af]")


def grab_lessons():
    s = LAB.read_text(encoding="utf-8")
    i = s.index("const LESSONS = [")
    seg = s[i:s.index("\n];", i)]
    out = []
    for m in re.finditer(r'id:(\d+),\s*no:"([^"]+)",\s*title:"([^"]+)",\s*meta:"([^"]+)"', seg):
        out.append({"no": m.group(2), "title": m.group(3), "meta": m.group(4)})
    return out


def grab_tag(src, marker):
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


def pieces(v):
    """把 [[flag, text], ...] 或纯字符串还原成带 <b> 的 HTML。"""
    if isinstance(v, str):
        return v
    return "".join(("<b>%s</b>" % t) if f else t for f, t in v)


def grab_en():
    """lab/index.html 的 window.I18N.t：中文 → 英文，作为译文缺失时的兜底。"""
    s = LAB.read_text(encoding="utf-8")
    a = s.index("window.I18N = ") + len("window.I18N = ")
    depth, ins, esc = 0, False, False
    for j in range(a, len(s)):
        c = s[j]
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
                    return json.loads(s[a:j + 1])["t"]
    raise AssertionError("I18N")


def render(lessons, tmap, en, T, lang):
    """生成某一语言的 LBWHOLE innerHTML。

    译文回退顺序：目标语言 → 英文 → 中文（宁可显示英文，也不在日语页里留汉字）。
    判定必须按语言：日语/繁中本来就用汉字，不能「含汉字即判为没翻」。
    """
    def good(v):
        if not v:
            return False
        if lang in ("zh-TW", "ja"):
            return True                    # 本身就用汉字，有值即可用
        if lang == "ko":
            return bool(HANGUL.search(v)) and not CJK.search(v)
        return not CJK.search(v)

    def tr(zh):
        v = tmap.get(zh)
        if good(v):
            return v
        v = en.get(zh)
        if v and (lang in ("zh-TW", "ja") or not CJK.search(v)):
            return v
        return zh

    h = ['<div class="sec-head"><span class="sec-num" style="color:var(--amber)">＋</span><h2>%s</h2></div>'
         % T["head"]]
    h.append('<p class="sec-sub">%s</p>' % pieces(T["sub"]))
    h.append('<div class="lab-hint">%s</div>' % pieces(T["hint"]))
    h.append('<div class="lab-tracks">')
    for idx, (lo, hi) in enumerate(RANGES):
        items = [L for L in lessons if lo <= L["no"] <= hi]
        h.append('  <div class="lab-track">')
        h.append('    <div class="lab-track-head"><div><b>%s</b><span class="lab-td">%s</span></div>'
                 '<span class="lab-count">%s</span></div>'
                 % (T["t%dn" % idx], T["t%dd" % idx], T["cnt"] % len(items)))
        h.append('    <div class="lab-list">')
        for L in items:
            h.append('      <a class="lab-item" href="https://lab.ydtgo.top/#/lessons/%s" '
                     'target="_blank" rel="noopener"><span class="lab-id">%s</span>'
                     '<span class="lab-body"><b>%s</b><span class="lab-goal">%s</span></span>'
                     '<span class="lab-arrow">→</span></a>'
                     % (L["no"], L["no"], tr(L["title"]), tr(L["meta"])))
        h.append('    </div>')
        h.append('  </div>')
    h.append('</div>')
    h.append('<p class="sec-sub" style="margin-top:14px">%s %s</p>' % (T["langs"], NATIVE))
    return "\n".join(h)


def main():
    lessons = grab_lessons()
    if len(lessons) != 46:
        print("课程数不是 46，实际 %d" % len(lessons))
        return 1
    dicts = json.loads(DICTS.read_text(encoding="utf-8"))
    labels = json.loads(LABELS.read_text(encoding="utf-8"))
    en = grab_en()

    src = SITE.read_text(encoding="utf-8")
    a, b = grab_tag(src, "window.I18N.MULTI = ")
    multi = json.loads(src[a:b])

    report = []
    for lang, obj in multi.items():
        T = labels.get(lang)
        if not T:
            report.append((lang, "缺 labs_i18n", 0))
            continue
        tmap = dict(dicts.get(lang, {}).get("t", {}))
        html = render(lessons, tmap, en, T, lang)
        obj.setdefault("b", {})["LBWHOLE"] = html
        cards = html.count('class="lab-item"')
        report.append((lang, "OK", cards))

    src = src[:a] + json.dumps(multi, ensure_ascii=False,
                               separators=(",", ":")).replace("</", "<\\/") + src[b:]
    SITE.write_text(src, encoding="utf-8", newline="")
    for lang, st, n in report:
        print("  %-6s %-12s 卡片 %d" % (lang, st, n))
    print("MULTI 实验区渲染完成，页面 %d 字节" % len(src.encode("utf-8")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
