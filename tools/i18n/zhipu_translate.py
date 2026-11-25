# -*- coding: utf-8 -*-
"""智谱 glm-4-flash 翻译客户端（永久免费，国内直连，不受 IP 封禁影响）。

用法：作为模块被补翻脚本 import。
"""
import json
import time

import requests

API = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
KEY = "c1127ca59f80474480c2cb64473b8de1.OdkFiOCFunDjiCSW"
MODEL = "glm-4-flash"

LANG_NAME = {
    "ja": "日语（日本語）",
    "ko": "韩语（한국어）",
    "es": "西班牙语（Español）",
    "pt": "葡萄牙语（Português）",
    "fr": "法语（Français）",
    "ru": "俄语（Русский）",
    "zh-TW": "繁体中文（台湾用语）",
    "en": "英语",
}

SYS = (
    "你是嵌入式教学网站的专业本地化译者。用户会给你一个 JSON 数组，元素是中文字符串。"
    "请把它们逐条翻译成目标语言，输出一个严格合法的 JSON 数组，长度与输入完全一致，顺序不变。\n"
    "硬性规则：\n"
    "1. 只输出 JSON 数组本身，不要代码块、不要解释、不要任何前后缀文字。\n"
    "2. 代码标识符、函数名、型号（如 MFRC522、INMP441、MAX98357A、ESP32、I2S、FFT、WAV）、"
    "引脚名（如 SDA、SCK、MOSI、MISO、RST、3.3V、GND）、数字与单位保持原样不译。\n"
    "3. 中文标点换成目标语言习惯的标点；不要保留中文全角引号。\n"
    "4. 术语前后一致：例如「接线」统一当地用语、「串口」= serial port 的对应词。\n"
    "5. 语气保持简洁的教程口吻，不要添加解释或扩写。\n"
    "6. 若某条是纯符号或纯数字，原样返回。\n"
    "7. 除型号/引脚名/域名/数字外，任何中文词（含「串口」「接线」「卡片」「分贝」这类常见术语）"
    "都必须译出，不允许在译文里残留汉字。\n"
    "参考译法（按目标语言自然表达，不要照搬英文）：点灯=点亮/闪烁 LED、串口=serial port、"
    "接线=wiring、按键=button、写卡=writing a card、防冲突=anti-collision、"
    "分贝=decibel、功放=amplifier、门禁=access control、变声=voice changing。\n"
)


class Zhipu:
    def __init__(self, key=KEY, model=MODEL, proxy=None, timeout=120, api=None):
        self.key = key
        self.model = model
        self.timeout = timeout
        self.proxy = proxy
        self.api = api or API
        self.s = requests.Session()
        self.s.trust_env = False
        if proxy:
            self.s.proxies.update({"http": proxy, "https": proxy})
        self.calls = 0

    def chat(self, messages, temperature=0.2, retries=3):
        body = {"model": self.model, "messages": messages,
                "temperature": temperature, "stream": False}
        last = None
        for i in range(retries):
            try:
                r = self.s.post(self.api, json=body, timeout=self.timeout,
                                headers={"Authorization": "Bearer " + self.key,
                                         "Content-Type": "application/json"})
                self.calls += 1
                if r.status_code == 200:
                    return r.json()["choices"][0]["message"]["content"]
                if r.status_code in (429, 500, 502, 503, 504):
                    last = "HTTP %d %s" % (r.status_code, r.text[:100])
                    time.sleep(2 + i * 3)
                    continue
                raise RuntimeError("HTTP %d: %s" % (r.status_code, r.text[:200]))
            except requests.RequestException as e:
                last = "%s: %s" % (type(e).__name__, str(e)[:100])
                time.sleep(2 + i * 3)
        raise RuntimeError("重试耗尽: %s" % last)

    def translate_raw(self, text, lang):
        """单条整段翻译：直接输出译文纯文本。

        不走 JSON 数组协议——整段译文里难免出现引号（俄语 «…»、法语 “…”），
        塞进 JSON 字符串一旦没转义就会整条解析失败。
        """
        name = LANG_NAME.get(lang, lang)
        msg = [
            {"role": "system", "content":
                "你是嵌入式教学网站的专业本地化译者。把用户给的中文整段译成%s。\n"
                "只输出译文本身：不要 JSON、不要引号包裹、不要解释、不要前后缀。\n"
                "代码标识符、型号（MFRC522、INMP441、MAX98357A、ESP32、I2S、FFT、WAV、"
                "ST7789、SSD1306、MIFARE、USB-C、3D）、域名（lab.ydtgo.top）与数字保持原样。\n"
                "中文标点换成目标语言习惯；语气保持简洁教程口吻，不扩写、不加解释。\n"
                "除上述原文保留项外，任何中文词（含「串口」「接线」「卡片」「分贝」这类常见术语）"
                "都必须译出，译文里不允许残留汉字。"
                % name},
            {"role": "user", "content": text},
        ]
        out = self.chat(msg, temperature=0.15).strip()
        if out.startswith("```"):
            out = out.strip("`").strip()
        return out

    def translate(self, texts, lang, retries=3):
        """texts: list[str] -> list[str]，长度一致。"""
        name = LANG_NAME.get(lang, lang)
        msg = [
            {"role": "system", "content": SYS},
            {"role": "user", "content": "目标语言：%s\n\n输入：\n%s"
             % (name, json.dumps(list(texts), ensure_ascii=False))},
        ]
        raw = self.chat(msg, retries=retries)
        out = parse_json_array(raw)
        if out is None or len(out) != len(texts):
            # 重试一次，强制强调条数
            msg2 = msg + [
                {"role": "assistant", "content": raw[:2000]},
                {"role": "user", "content": "上面输出不是合法 JSON 数组或条数不对。"
                 "请重新只输出一个 JSON 数组，必须正好 %d 条，顺序与输入一致。"
                 % len(texts)},
            ]
            raw = self.chat(msg2, retries=retries)
            out = parse_json_array(raw)
        if out is None:
            raise RuntimeError("解析失败: %s" % raw[:200])
        if len(out) != len(texts):
            raise RuntimeError("条数不符 %d != %d" % (len(out), len(texts)))
        return [("" if v is None else str(v)) for v in out]


def parse_json_array(raw):
    if not isinstance(raw, str):
        return None
    t = raw.strip()
    if t.startswith("```"):
        t = t.split("```")[1] if len(t.split("```")) > 1 else t
        if t.lstrip().startswith("json"):
            t = t.lstrip()[4:]
    i, j = t.find("["), t.rfind("]")
    if i < 0 or j <= i:
        return None
    try:
        v = json.loads(t[i:j + 1])
        return v if isinstance(v, list) else None
    except Exception:
        return None


if __name__ == "__main__":
    import sys
    z = Zhipu()
    sample = ["RFID 与 NFC", "接线：MFRC522 六根线，只能 3.3V",
              "读卡：卡片没有电池，怎么回话", "短按一次，串口打印一行"]
    lang = sys.argv[1] if len(sys.argv) > 1 else "ja"
    for x in z.translate(sample, lang):
        print("  ", x)
