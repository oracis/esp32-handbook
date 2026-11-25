#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把主站 #labs 区块重写为「本站实验室 46 课目录」。

- 课程数据从 lab/index.html 的 LESSONS 读取（保证与实验室一致，不手抄）
- 卡片链接改为 https://lab.ydtgo.top/#/lessons/NN，零外链
- 同时生成中文块（HTML）与英文块（window.I18N.b.LBWHOLE），其余 7 语言交给 tools/i18n
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "index.html"
LAB = ROOT / "lab" / "index.html"

TRACKS = [
    ("入门与基础", "工具链、点灯、按键、串口", "01", "10",
     "Getting started", "Toolchain, blink, buttons, serial"),
    ("显示与通信", "SPI/I²C 屏幕、HTTP、WebSocket、MQTT、BLE", "11", "18",
     "Displays and networking", "SPI/I2C screens, HTTP, WebSocket, MQTT, BLE"),
    ("传感与执行", "蜂鸣器、舵机、超声波、温湿度、红外、触摸", "19", "24",
     "Sensing and actuation", "Buzzer, servo, ultrasonic, DHT11, IR, touch"),
    ("系统与进阶", "millis、FreeRTOS、NVS、OTA、看门狗、综合项目", "25", "30",
     "Systems and projects", "millis, FreeRTOS, NVS, OTA, watchdog, capstone"),
    ("RFID 与 NFC", "13.56 MHz、MIFARE、防冲突、写卡、门禁", "31", "38",
     "RFID and NFC", "13.56 MHz, MIFARE, anti-collision, writes, access control"),
    ("声音与音频", "I2S 麦克风、分贝、录音、FFT、功放、变声", "39", "46",
     "Sound and audio", "I2S mic, decibels, recording, FFT, amp, voice effects"),
]


def grab_lessons():
    s = LAB.read_text(encoding="utf-8")
    i = s.index("const LESSONS = [")
    j = s.index("\n];", i)
    seg = s[i:j]
    out = []
    for m in re.finditer(r'id:(\d+),\s*no:"([^"]+)",\s*title:"([^"]+)",\s*meta:"([^"]+)",\s*group:"([^"]+)"', seg):
        out.append({"id": int(m.group(1)), "no": m.group(2), "title": m.group(3),
                    "meta": m.group(4), "group": m.group(5)})
    return out


def grab_map():
    """lab 的中文 → 英文对照表（window.I18N.t）"""
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
                    break
    return json.loads(s[a:j + 1])["t"]


def card_html(L, en, tmap):
    title = tmap.get(L["title"], L["title"]) if en else L["title"]
    meta = tmap.get(L["meta"], L["meta"]) if en else L["meta"]
    return ('<a class="lab-item" href="https://lab.ydtgo.top/#/lessons/%s" target="_blank" rel="noopener">'
            '<span class="lab-id">%s</span><span class="lab-body"><b>%s</b>'
            '<span class="lab-goal">%s</span></span><span class="lab-arrow">→</span></a>'
            % (L["no"], L["no"], title, meta))


def build_inner(lessons, tmap, en):
    pick = lambda i: TRACKS[i] if not en else TRACKS[i]
    head = ("Hands-on lab: 46 ESP32 experiments you can follow" if en
            else "动手实验台：46 个能跟着做的 ESP32 实验")
    sub = ("Above is how to choose and learn; here is how to build. All 46 lessons run inside "
           "<b>our own virtual lab</b> at lab.ydtgo.top: wiring, code, serial output, a timeline "
           "simulation and a 3D board, all in the browser. Click any lesson to open it directly — "
           "<b>no external links</b>. Lessons and simulations are original to this site; the topic "
           "outline was inspired by the open-source ESP32 Labs (MIT)." if en else
           "上面是「怎么选、怎么学」，这里是「直接上手做」。46 课全部跑在<b>我们自己的虚拟实验室</b>里"
           "（lab.ydtgo.top）：接线、可复制代码、串口输出、时间轴仿真和真 3D 开发板都在浏览器里，"
           "点任一课直接进对应实验，<b>不出站、零外链</b>。课程与仿真均为本站原创，主题编排参考过"
           "开源项目 ESP32 Labs（MIT）。")
    hint = ("Hardware you need: one ESP32 board plus a USB-C <b>data cable</b>. The first 10 lessons "
            "need the board alone; displays and networking add a ST7789/SSD1306 panel; the 8 RFID "
            "lessons need an MFRC522 and a MIFARE card; the 8 audio lessons need an INMP441 mic and a "
            "MAX98357A amp." if en else
            "前提硬件：一块 ESP32 开发板 + 一根 USB-C <b>数据线</b>。前 10 课只需板子；显示与通信要加 "
            "ST7789/SSD1306 屏；RFID 8 课要 MFRC522 + MIFARE 卡；声音 8 课要 INMP441 麦克风 + MAX98357A 功放。")
    langs = ("Available in 9 languages: 简体中文 · English · 繁體中文 · 日本語 · 한국어 · Español · "
             "Português · Français · Русский. Switch inside the lab." if en else
             "站内支持 9 种语言：简体中文 · English · 繁體中文 · 日本語 · 한국어 · Español · Português · "
             "Français · Русский，在实验室顶栏切换。")

    h = ['<div class="sec-head"><span class="sec-num" style="color:var(--amber)">＋</span><h2>%s</h2></div>' % head]
    h.append('<p class="sec-sub">%s</p>' % sub)
    h.append('<div class="lab-hint">%s</div>' % hint)
    h.append('<div class="lab-tracks">')
    for idx, tr in enumerate(TRACKS):
        name, td, lo, hi = (tr[4], tr[5], tr[2], tr[3]) if en else (tr[0], tr[1], tr[2], tr[3])
        items = [L for L in lessons if lo <= L["no"] <= hi]
        cnt = "%d lessons" % len(items) if en else "%d 课" % len(items)
        h.append('  <div class="lab-track">')
        h.append('    <div class="lab-track-head"><div><b>%s</b><span class="lab-td">%s</span></div>'
                 '<span class="lab-count">%s</span></div>' % (name, td, cnt))
        h.append('    <div class="lab-list">')
        for L in items:
            h.append("      " + card_html(L, en, tmap))
        h.append('    </div>')
        h.append('  </div>')
    h.append('</div>')
    h.append('<p class="sec-sub" style="margin-top:14px">%s</p>' % langs)
    return "\n".join(h)


def main():
    lessons = grab_lessons()
    tmap = grab_map()
    if len(lessons) != 46:
        print("课程数不是 46，实际 %d，停止" % len(lessons))
        return 1

    zh = build_inner(lessons, tmap, False)
    en = build_inner(lessons, tmap, True)

    s = SITE.read_text(encoding="utf-8")
    i = s.index('<section id="labs">')
    j = s.index('</section>', i)
    # SIMCARD 双入口卡与署名都在 LBWHOLE 之外，原样保留，只改文案
    k = s.index('<div class="lab-hint" data-l10n="SIMCARD">', i)
    assert k < j, "SIMCARD 不在 labs 区块内"
    tail = s[k:j]
    tail = tail.replace("30 课引导式仿真", "46 课引导式仿真")
    tail = re.sub(r'<div class="lab-credit">.*?</div>',
                  '<div class="lab-credit">主题编排参考开源项目 ESP32 Labs（by Abderrehmen Gharsallah，'
                  'MIT License）；本站 46 课的讲解、代码与仿真均为原创，不转载原文。</div>',
                  tail, flags=re.S)
    section = ('<section id="labs">\n    <div data-l10n="LBWHOLE">\n' + zh + '\n    </div>\n    '
               + tail + '\n  ')
    s = s[:i] + section + s[j:]

    # 英文块 LBWHOLE
    key = '"LBWHOLE":"'
    k = s.index(key)
    p = k + len(key)
    esc = False
    while p < len(s):
        c = s[p]
        if esc:
            esc = False
        elif c == "\\":
            esc = True
        elif c == '"':
            break
        p += 1
    # 注意：key 已包含值的前引号，json.dumps 自带引号，故去掉一个
    s = s[:k] + key + json.dumps(en, ensure_ascii=False).replace("</", "<\\/")[1:] + s[p + 1:]

    s = s.replace("30 guided simulation lessons", "46 guided simulation lessons")

    SITE.write_text(s, encoding="utf-8", newline="")
    print("主站实验区已重写：%d 课 / 中文块 %d 字节 / 英文块 %d 字节 / 页面 %d 字节"
          % (len(lessons), len(zh.encode()), len(en.encode()), len(s.encode())))
    print("外链数（esp-labs-web）：", s.count("esp-labs-web"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
