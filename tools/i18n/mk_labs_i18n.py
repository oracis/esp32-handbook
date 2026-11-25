#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""翻译主站实验区（LBWHOLE）的「结构性短文案」，产出 labs_i18n.json。

只翻短串（标题/说明段/提示段/分组名与描述/计数模板），
46 张卡片的标题与一句话说明来自 dicts/lab.json，无需重复翻。

带 <b> 强调的段落拆成纯文本片段翻译，拼装时由代码补回标签——
机翻不会挪动或吃掉标签，结构永远合法。
"""
import json
from pathlib import Path

from zhipu_translate import Zhipu

HERE = Path(__file__).resolve().parent
OUT = HERE / "labs_i18n.json"

TRACK_ZH = [
    ("入门与基础", "工具链、点灯、按键、串口"),
    ("显示与通信", "SPI/I²C 屏幕、HTTP、WebSocket、MQTT、BLE"),
    ("传感与执行", "蜂鸣器、舵机、超声波、温湿度、红外、触摸"),
    ("系统与进阶", "millis、FreeRTOS、NVS、OTA、看门狗、综合项目"),
    ("RFID 与 NFC", "13.56 MHz、MIFARE、防冲突、写卡、门禁"),
    ("声音与音频", "I2S 麦克风、分贝、录音、FFT、功放、变声"),
]

# 纯文本键：直接翻译
PLAIN = {
    "head": "动手实验台：46 个能跟着做的 ESP32 实验",
    "langs": "站内支持 9 种语言（在实验室顶栏切换）：",
    "cnt": "%d 课",
}
for _i, (_n, _d) in enumerate(TRACK_ZH):
    PLAIN["t%dn" % _i] = _n
    PLAIN["t%dd" % _i] = _d

# 整段文案：外语版按整段翻译，不塞行内 <b>。
# 理由：片段翻译会出现「…实验室</b>里（lab.ydtgo.top）」这种断句残留；
# 整段翻虽然少了两个加粗高亮，但句子语法正确、不会粘连，也没有标签错位风险。
PARAGRAPHS = {
    "sub": ("上面是「怎么选、怎么学」，这里是「直接上手做」。46 课全部跑在我们自己的虚拟实验室里"
            "（lab.ydtgo.top）：接线、可复制代码、串口输出、时间轴仿真和真 3D 开发板都在浏览器里，"
            "点任一课直接进对应实验，不出站、零外链。课程与仿真均为本站原创，"
            "主题编排参考过开源项目 ESP32 Labs（MIT）。"),
    "hint": ("前提硬件：一块 ESP32 开发板 + 一根 USB-C 数据线。前 10 课只需板子；"
             "显示与通信要加 ST7789/SSD1306 屏；RFID 8 课要 MFRC522 + MIFARE 卡；"
             "声音 8 课要 INMP441 麦克风 + MAX98357A 功放。"),
}

NATIVE = "简体中文 · English · 繁體中文 · 日本語 · 한국어 · Español · Português · Français · Русский"


def main():
    data = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    z = Zhipu()
    for lang in ["zh-TW", "ja", "ko", "es", "pt", "fr", "ru"]:
        got = data.setdefault(lang, {})

        # 1) 纯文本键
        todo = [k for k in PLAIN if k not in got or not got.get(k)]
        if todo:
            if len(todo) == 1:
                # 单条走纯文本：JSON 数组里只有一条带顿号的串时，模型会按顿号拆成多条
                got[todo[0]] = z.translate_raw(PLAIN[todo[0]], lang)
            else:
                vals = z.translate([PLAIN[k] for k in todo], lang)
                for k, v in zip(todo, vals):
                    got[k] = v.strip()
            print("%s 纯文本 +%d" % (lang, len(todo)), flush=True)

        # 2) 整段文案：整段翻，避免片段断句残留
        for key, text in PARAGRAPHS.items():
            cur = got.get(key)
            if isinstance(cur, str) and cur.strip() and cur.strip() != text:
                continue
            got[key] = z.translate_raw(text, lang)
            print("%s 段落 %s 已翻" % (lang, key), flush=True)

        OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

    print("\n抽查：")
    for lang in ["ja", "es", "ru"]:
        d = data[lang]
        print("  %-5s %s" % (lang, d["head"]))
        print("        %s" % d["sub"][:120])
    print("输出:", OUT)


if __name__ == "__main__":
    main()
