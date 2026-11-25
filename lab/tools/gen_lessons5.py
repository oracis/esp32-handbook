#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 lessons_m5_data.py 的第 31-46 课注入 lab/index.html（幂等）。

做的事：
  1. 纯 C++ 源码 → 与现有课程一致的 span 高亮 HTML
  2. 16 个课程对象追加进 LESSONS 数组
  3. 所有中英字符串汇总进 window.I18N.t
  4. 顶栏课程计数 30 → 46
  5. 第 30 课收尾文案改成「本组完成」，不再说「完成 30 课」
  6. 追加 e2e=m5 / e2e=route 自检分支（46 课渲染 + 课级深链）
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_lessons import highlight, js, scan  # noqa: E402
from lessons_m5_data import COURSES  # noqa: E402

PAGE = Path(__file__).resolve().parent.parent / "index.html"

OLD_END = "恭喜完成 30 课！你现在可以独立开新项目了"
NEW_END = "系统与项目完成 · 下一组是 RFID 与声音"
NEW_END_EN = "Systems track done · next up: RFID and audio"

E2E = '''      } else if (mode === "m5"){
        /* M5：46 课全渲染 + 新两组 + 末课代码 */
        R.count = document.querySelectorAll("#lsnList .lsn").length;
        R.groups = document.querySelectorAll("#lsnList .grp").length;
        R.no31 = document.querySelectorAll(".lsn .no")[30].textContent;
        R.no46 = document.querySelectorAll(".lsn .no")[45].textContent;
        R.head = document.querySelector(".hstat span").textContent;
        const gs = Array.prototype.map.call(document.querySelectorAll("#lsnList .grp"), g => g.textContent);
        R.hasRfid = gs.some(g => g.indexOf("RFID") >= 0);
        R.hasSound = gs.some(g => g.indexOf("声音") >= 0);
        cur = 30; renderLesson();
        R.fn31 = document.querySelector("#codeFn").textContent;
        R.code31 = document.querySelector("#codeOut").textContent.indexOf("MFRC522") >= 0;
        cur = 45; renderLesson();
        R.fn46 = document.querySelector("#codeFn").textContent;
        R.code46 = document.querySelector("#codeOut").textContent.indexOf("echoMix") >= 0;
        setLang("en"); await sleep(120);
        R.en46 = document.querySelectorAll(".lsn .tt")[45].textContent;
        R.enGroup = document.querySelectorAll("#lsnList .grp")[7].textContent;
        setLang("zh"); await sleep(100);
      } else if (mode === "route"){
        /* 课级深链：#/lessons/39 与 #/lessons/31?lang=en */
        cur = 0; renderList(); renderLesson();
        location.hash = "#/lessons/39";
        window.dispatchEvent(new HashChangeEvent("hashchange"));
        await sleep(250);
        R.title39 = (document.querySelector("#body h3") || {}).textContent || "";
        R.hashAfter = location.hash;
        location.hash = "#/lessons/31?lang=en";
        window.dispatchEvent(new HashChangeEvent("hashchange"));
        await sleep(350);
        R.title31en = (document.querySelector("#body h3") || {}).textContent || "";
        R.lang31 = document.documentElement.lang;
        R.listMarked = !!document.querySelector("#lsnList .lsn.on");

'''


def main():
    src = PAGE.read_text(encoding="utf-8")
    if 'no:"46"' in src or 'no: "46"' in src:
        print("已注入过第 46 课，拒绝重复执行")
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
            tl.append({k: v for k, v in e.items() if k != "en"})

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
        objs.append("\n{" + ",".join("%s:%s" % (k, js(v)) for k, v in fields) + "}")

    trans[NEW_END] = NEW_END_EN

    # 1) i18n 字典
    a, b = scan(src, "window.I18N = ", "{", "}")
    dic = json.loads(src[a:b])
    merged = {k.replace('\\\\n', '\\n'): v for k, v in dic["t"].items()}
    for k, v in trans.items():
        merged.setdefault(k, v)
    dic["t"] = merged
    src = src[:a] + json.dumps(dic, ensure_ascii=False).replace("</", "<\\/") + src[b:]

    # 2) LESSONS 追加
    a, b = scan(src, "const LESSONS = ", "[", "]")
    src = src[:b - 1] + ",\n" + ",".join(objs) + "\n" + src[b - 1:]

    # 3) 顶栏计数 30 -> 46
    assert '<b>30</b> <i data-i18n="课">课</i>' in src, "未找到顶栏课程计数"
    src = src.replace('<b>30</b> <i data-i18n="课">课</i>', '<b>46</b> <i data-i18n="课">课</i>', 1)

    # 4) 第 30 课收尾文案（只在课程数据里改，字典旧键保留无副作用）
    assert OLD_END in src
    src = src.replace(OLD_END, NEW_END)

    # 5) e2e 分支
    anchor = '''      } else if (mode === "l1"){'''
    assert anchor in src, "未找到 e2e 锚点"
    src = src.replace(anchor, E2E + anchor, 1)

    with open(PAGE, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("注入完成：%d 门课 / %d 条译文 / 页面 %d 字节" %
          (len(COURSES), len(trans), len(src.encode("utf-8"))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
