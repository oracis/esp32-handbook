# -*- coding: utf-8 -*-
"""实验室页脚接入「支持这个项目」入口。

结构保持原样：一条 30px 的细状态栏，末尾追加分隔点 + 链接，
指向主站的 #support（lab 跑在独立子域，必须用绝对地址）。
MIT 署名原样保留——它是合规项，不能动。

同时把词条写进 lab 自己的 i18n：window.I18N.t（en）与 MULTI[lang].t。
幂等：重复执行不会重复追加链接。
"""
import io
import json
import re

SITE = "lab/index.html"
KEY = "支持这个项目"
EN = "Support this project"
MAIN = "https://esp32.ydtgo.top/#support"
BY_LANG = {
    "zh-TW": "支持這個專案",
    "ja": "このプロジェクトを支援する",
    "ko": "이 프로젝트 후원하기",
    "es": "Apoya este proyecto",
    "pt": "Apoie este projeto",
    "fr": "Soutenez ce projet",
    "ru": "Поддержать проект",
}

LINK = ('<span class="foot-sep"> · </span>'
        '<a href="%s" target="_blank" rel="noopener" data-i18n="%s">%s</a>' % (MAIN, KEY, KEY))


def dump(o):
    return json.dumps(o, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def main():
    s = io.open(SITE, encoding="utf-8").read()
    orig = s

    # 1. 页脚链接
    if 'href="%s"' % MAIN in s:
        print(" - 页脚链接已存在，跳过")
    else:
        m = re.search(r'(<footer id="labFoot">)([\s\S]*?)(</footer>)', s)
        assert m, "找不到 #labFoot"
        body = m.group(2)
        assert "MIT" in body, "页脚已不含 MIT 署名，先确认合规"
        s = s[:m.start(2)] + body.rstrip() + LINK + s[m.end(2):]
        print(" - 页脚链接已追加")

    # 2. CSS 里的分隔点
    if ".foot-sep" not in s:
        s = s.replace("#labFoot a{color:var(--teal);text-decoration:none}",
                      "#labFoot .foot-sep{opacity:.5}\n#labFoot a{color:var(--teal);text-decoration:none}", 1)

    # 3. i18n 词条
    dec = json.JSONDecoder()
    i = s.index("window.I18N = ") + len("window.I18N = ")
    obj, e1 = dec.raw_decode(s, i)
    k = s.index("window.I18N.MULTI = ") + len("window.I18N.MULTI = ")
    mobj, e2 = dec.raw_decode(s, k)

    obj.setdefault("t", {})[KEY] = EN
    for L, v in BY_LANG.items():
        if L not in mobj:
            print(" !! MULTI 缺语言", L)
            continue
        mobj[L].setdefault("t", {})[KEY] = v

    new = s[:i] + dump(obj) + s[e1:]
    shift = len(dump(obj)) - (e1 - i)
    new = new[:k + shift] + dump(mobj) + new[e2 + shift:]

    io.open(SITE, "w", encoding="utf-8", newline="\n").write(new)
    print("写入：%d → %d 字节（页脚 %s）" % (len(orig.encode()), len(new.encode()),
                                          "有改动" if new != orig else "无改动"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
