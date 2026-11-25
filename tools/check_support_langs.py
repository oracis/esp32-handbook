# -*- coding: utf-8 -*-
"""验收：支持区块与页脚在 9 种语言下是否真的被替换。

做法：复制一份 index.html，把初始化语言写死成目标语言，用 Chrome --dump-dom
跑完 JS 后取渲染结果，只截取 section#support 与 footer 的文本做断言。
比读 JSON 字典更可信——它验的是浏览器里实际看到的字。

用法：python tools/check_support_langs.py
"""
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "index.html")
LANGS = ["en", "zh-TW", "ja", "ko", "es", "pt", "fr", "ru"]
CHROME = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
]
CJK = re.compile(r"[\u4e00-\u9fff]")
KANA = re.compile(r"[\u3040-\u30ff]")
HANGUL = re.compile(r"[\uac00-\ud7af]")


def chrome_bin():
    for p in CHROME:
        if os.path.exists(p):
            return p
    sys.exit("找不到 Chrome")


def dump(src, lang, tmpdir):
    html = src.replace(
        "var saved='zh-CN';\n  try{ saved=localStorage.getItem(KEY)||'zh-CN'; }catch(e){}",
        "var saved='%s';" % lang, 1)
    assert "var saved='%s';" % lang in html, "初始化语言钩子没找到，index.html 结构变了？"
    f = os.path.join(tmpdir, "_lang_%s.html" % lang.replace("/", "_"))
    open(f, "w", encoding="utf-8", newline="\n").write(html)
    out = subprocess.run([chrome_bin(), "--headless=new", "--disable-gpu",
                          "--virtual-time-budget=4000", "--dump-dom",
                          "file:///" + f.replace("\\", "/")],
                         capture_output=True, timeout=180)
    return out.stdout.decode("utf-8", "replace")


def text_of(dom, tag_start, tag_end):
    i = dom.find(tag_start)
    if i < 0:
        return ""
    j = dom.find(tag_end, i)
    seg = dom[i:j]
    seg = re.sub(r"<[^>]+>", " ", seg)
    import html as h
    return re.sub(r"\s+", " ", h.unescape(seg)).strip()


def main():
    src = open(SITE, encoding="utf-8").read()
    tmp = tempfile.mkdtemp(prefix="langcheck_")
    bad = 0
    for lang in LANGS:
        dom = dump(src, lang, tmp)
        sup = text_of(dom, '<section id="support"', "</section>")
        foot = text_of(dom, "<footer", "</footer>")
        head = sup[:64]
        err = []
        if not sup or "支持这个项目" in sup:
            err.append("支持区仍是中文")
        if lang == "ja" and not KANA.search(sup):
            err.append("日语区无假名")
        if lang == "ko" and (not HANGUL.search(sup) or CJK.search(sup)):
            err.append("韩语区字形异常")
        if lang in ("en", "es", "pt", "fr", "ru") and CJK.search(sup + foot):
            err.append("残留汉字: %s" % CJK.search(sup + foot).group(0))
        mark = "OK " if not err else "BAD"
        if err:
            bad += 1
        print("[%s] %-6s %s" % (mark, lang, head))
        print("        页脚: %s" % foot[:110])
        for e in err:
            print("        !! %s" % e)
    print("\n%d/%d 语言通过" % (len(LANGS) - bad, len(LANGS)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
