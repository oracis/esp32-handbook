#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 lessons_m4_data.py 的第 11-30 课注入 lab/index.html（幂等，重复运行会拒绝二次注入）。

做的事：
  1. 纯 C++ 源码 → 与现有课程一致的 span 高亮 HTML
  2. 20 个课程对象追加进 LESSONS 数组
  3. 所有中文字符串汇总进 window.I18N.t（tr() 精确整串翻译）
  4. 顶栏课程计数 10 → 30
  5. 追加 e2e=m4 自检分支（前 10 课仍由 m3 覆盖）
 注：e2e=all / e2e=m4p 两个全量分支在生成后追加于 index.html，重跑时需一并保留
"""
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lessons_m4_data import COURSES  # noqa: E402

PAGE = Path(__file__).resolve().parent.parent / "index.html"

_pp = re.compile(r'^[ \t]*#[^\n]*', re.M)
_tok = re.compile(
    r'(?P<comment>//[^\n]*|/\*[\s\S]*?\*/)|'
    r'(?P<str>"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')|'
    r'(?P<kw>\b(?:void|const|int|char|byte|float|double|bool|unsigned|long|short|'
    r'static|volatile|if|else|for|while|return|struct|class|public|private|'
    r'new|delete|true|false|NULL|nullptr|sizeof|String|uint8_t|uint16_t|'
    r'uint32_t|size_t|TaskHandle_t|SemaphoreHandle_t|ota_error_t|'
    r'decode_results|define|include)\b)|'
    r'(?P<num>\b0x[0-9A-Fa-f]+\b|\b\d+(?:\.\d+)?\b)|'
    r'(?P<fn>\b[A-Za-z_]\w*(?=\s*\())'
)
_CLS = {"comment": "c", "str": "s", "kw": "k", "num": "n", "fn": "f"}


def highlight(src):
    s = html.escape(src, quote=False)
    # 预处理行先占位，否则 _tok 会把刚生成的 <span class="c"> 二次高亮、破坏标签
    held = []

    def hold(m):
        held.append('<span class="c">%s</span>' % m.group(0))
        return '\x00PP%d\x00' % (len(held) - 1)

    s = _pp.sub(hold, s)

    def sub(m):
        kind = m.lastgroup
        if kind is None:
            return m.group(0)
        return '<span class="%s">%s</span>' % (_CLS[kind], m.group(0))

    s = _tok.sub(sub, s)
    for i, val in enumerate(held):
        s = s.replace('\x00PP%d\x00' % i, val)
    return s


def js(v):
    """JSON 字符串字面量兼容 JS，且避免 </script> 截断。"""
    return json.dumps(v, ensure_ascii=False).replace("</", "<\\/")


def scan(src, marker, open_ch, close_ch):
    """从 marker 后定位完整 JSON 对象/数组的 [start, end)。"""
    i = src.index(marker) + len(marker)
    while i < len(src) and src[i].isspace():
        i += 1
    assert src[i] == open_ch, (marker, src[i:i + 20])
    depth, in_str, esc = 0, False, False
    for j in range(i, len(src)):
        c = src[j]
        if in_str:
            if esc:
                esc = False
            elif c == '\\':
                esc = True
            elif c == '"':
                in_str = False
        else:
            if c == '"':
                in_str = True
            elif c == open_ch:
                depth += 1
            elif c == close_ch:
                depth -= 1
                if depth == 0:
                    return i, j + 1
    raise AssertionError("未找到匹配的 %s" % marker)


def main():
    src = PAGE.read_text(encoding="utf-8")
    if 'no:"30"' in src or 'no: "30"' in src:
        print("已注入过第 30 课，拒绝重复执行")
        return 1

    trans = {}

    def put(zh, en):
        assert isinstance(zh, str) and isinstance(en, str) and zh and en
        if zh in trans and trans[zh] != en:
            raise AssertionError("译文冲突: %r -> %r / %r" % (zh, trans[zh], en))
        trans[zh] = en

    objs = []
    for c in COURSES:
        put(c["title"], c["titleEn"])
        put(c["meta"], c["metaEn"])
        put(c["group"], c["groupEn"])
        put(c["wiringHd"], c["wiringHdEn"])
        put(c["wiring"], c["wiringEn"])
        for pin, zh, en in c["pins"]:
            put(zh, en)
        for zh, en in c["overview"]:
            put(zh, en)
        for kzh, vzh, ken, ven in c["points"]:
            put(kzh, ken)
            put(vzh, ven)
        tl = []
        for e in c["tl"]:
            put(e["serial"], e["en"])
            item = {k: v for k, v in e.items() if k != "en"}
            tl.append(item)

        fields = [
            ("id", int(c["no"])),
            ("no", c["no"]),
            ("title", c["title"]),
            ("meta", c["meta"]),
            ("group", c["group"]),
            ("wiringHd", c["wiringHd"]),
            ("wiring", c["wiring"]),
            ("pins", c["pins"]),
            ("overview", c["overview"]),
            ("points", c["points"]),
            ("code", highlight(c["code"])),
            ("tl", tl),
            ("input", False),
        ]
        parts = ["{" + ",".join("%s:%s" % (k, js(v)) for k, v in fields) + "}"]
        objs.append("\n" + parts[0])

    # 1) i18n 字典
    a, b = scan(src, "window.I18N = ", "{", "}")
    dic = json.loads(src[a:b])
    merged = dict(dic["t"])
    # 旧字典里 readStringUntil('\\n') 的键多了一层反斜杠，tr() 永远命中不了，先归一
    merged = {k.replace('\\\\n', '\\n'): v for k, v in merged.items()}
    overlap = set(merged) & set(trans)
    if overlap:
        print("注意：%d 条译文键已存在，保持原值" % len(overlap))
    for k, v in trans.items():
        merged.setdefault(k, v)
    dic["t"] = merged
    new_dic = json.dumps(dic, ensure_ascii=False).replace("</", "<\\/")
    src = src[:a] + new_dic + src[b:]

    # 2) LESSONS 数组追加
    a, b = scan(src, "const LESSONS = ", "[", "]")
    src = src[:b - 1] + ",\n" + ",".join(objs) + "\n" + src[b - 1:]

    # 3) 顶栏计数
    before = '<b>10</b> <i data-i18n="课">课</i>'
    assert before in src, "未找到顶栏课程计数"
    src = src.replace(before, '<b>30</b> <i data-i18n="课">课</i>', 1)

    # 4) e2e=m4：覆盖 20 门新课的渲染、双语、分组与末课代码
    anchor = '''      } else if (mode === "l1"){'''
    assert anchor in src, "未找到 e2e 钩子锚点"
    m4 = '''      } else if (mode === "m4"){
        /* M4：30 课全渲染 + 第 11-30 课双语 + 末课代码与分组 */
        R.count = document.querySelectorAll("#lsnList .lsn").length;
        R.groups = document.querySelectorAll("#lsnList .grp").length;
        R.no11 = document.querySelectorAll(".lsn .no")[10].textContent;
        R.no30 = document.querySelectorAll(".lsn .no")[29].textContent;
        R.zh30 = document.querySelectorAll(".lsn .tt")[29].textContent;
        R.en11 = null;
        setLang("en"); await sleep(120);
        R.en11 = document.querySelectorAll(".lsn .tt")[10].textContent;
        R.en30 = document.querySelectorAll(".lsn .tt")[29].textContent;
        R.enGroup = document.querySelectorAll("#lsnList .grp")[4].textContent;
        R.enHead = document.querySelector(".hstat span").textContent;
        cur = 29; renderLesson();
        R.fn30 = document.querySelector("#codeFn").textContent;
        R.code30 = document.querySelector("#codeOut").textContent.indexOf("WebServer") >= 0;
        setLang("zh"); await sleep(100);
'''
    src = src.replace(anchor, m4 + anchor, 1)

    with open(PAGE, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("注入完成：%d 门课 / %d 条译文 / 页面 %d 字节" %
          (len(COURSES), len(trans), len(src.encode("utf-8"))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
