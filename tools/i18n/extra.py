#!/usr/bin/env python3
"""补翻界面新增的硬编码提示文案（9 条），并同步英文主字典。"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build

ROOT = HERE.parents[1]
LAB = ROOT / "lab/index.html"
KEYS = [
    "怎么看效果：",
    "点左下「▶ 运行」，盯住板子图上的",
    "蓝色 LED",
    "和下方",
    "串口监视器 · 115200 baud",
    "——时间轴驱动的仿真播放，不是真编译。",
    "仿真说明：",
    "虚拟板子按接线状态自动呈现，你不需要真的插线。外接 LED 的课在现实里记得串",
    "电阻。",
    "这课的四个要点",
]
START, END = "<!-- I18N_EXTRA:START -->", "<!-- I18N_EXTRA:END -->"


def main():
    lab = json.loads((HERE / "dicts/lab.json").read_text(encoding="utf-8"))
    for lang in ["en"] + list(build.LANGS):
        target = {} if lang == "en" else lab[lang]["t"]
        for k in KEYS:
            if k in target:
                continue
            try:
                target[k] = build.translate_one(k, lang)
                print(lang, "OK", k[:20], "->", target[k][:45], flush=True)
            except Exception as e:
                print(lang, "FAIL", k[:20], str(e)[:70], flush=True)
                target[k] = k
        if lang != "en":
            lab[lang]["t"] = target
    (HERE / "dicts/lab.json").write_text(json.dumps(lab, ensure_ascii=False), encoding="utf-8")

    # 英文补进主字典（en 走 window.I18N.t 回退，不在 MULTI 中）
    en = build.translate_one  # noqa
    en_map = {k: build.translate_one(k, "en") for k in KEYS}
    # 插在主脚本内部：先闭合当前 script，独立补充后再重新打开，保持后续代码仍在同一逻辑脚本中
    block = (START + "\n</script><script>Object.assign(window.I18N.t, " +
             json.dumps(en_map, ensure_ascii=False).replace("</", "<\\/") +
             ");</script><script>\n" + END)
    src = LAB.read_text(encoding="utf-8")
    anchor = "/* I18N_MULTI:START */"
    if START in src and END in src:
        a = src.index(START); b = src.index(END) + len(END)
        src = src[:a] + block + src[b:]
    else:
        i = src.index(anchor)
        src = src[:i] + block + "\n" + src[i:]
    with open(LAB, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("lab extra inserted", flush=True)


if __name__ == "__main__":
    main()
