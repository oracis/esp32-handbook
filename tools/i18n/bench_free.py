# -*- coding: utf-8 -*-
"""实测本机各 free LLM 端点做翻译的延迟与质量（同一批真实课标题 → 日语）。

用法：python tools/i18n/bench_free.py
"""
import json
import os
import re
import time

import requests

TEXTS = [
    "RFID 入门：13.56 MHz 与 MFRC522",
    "读卡：卡片没有电池，怎么回话",
    "防冲突：多张卡同时在场上",
    "写卡与钱包：块写入与值块加减",
    "聆听：INMP441 I2S 数字麦克风",
    "分贝：从采样值算响度",
    "频谱：FFT 把声音拆成柱子",
    "语音特效：实时变声与回声",
]
SYS = ("你是专业的技术文档翻译。把用户给的 JSON 字符串数组逐条译成日语，"
       "只输出 JSON 数组，条数与顺序严格一致，不要任何解释。"
       "型号、引脚名、库名、数字、域名保持原文（如 MFRC522、INMP441、GPIO4）。")
KANA = re.compile(r"[\u3040-\u30ff]")


def models():
    p = os.path.expanduser("~/.workbuddy/models.json")
    d = json.load(open(p, encoding="utf-8"))
    for m in d:
        yield m["id"], m["url"], m.get("apiKey", "")


def proxies():
    """给需要出国的端点用系统代理；国内端点直连。"""
    for px in ("http://127.0.0.1:9935", "http://127.0.0.1:1114"):
        yield {"http": px, "https": px}


def call(url, key, timeout=40, px=None):
    s = requests.Session()
    s.trust_env = False
    body = {
        "model": None,
        "messages": [
            {"role": "system", "content": SYS},
            {"role": "user", "content": json.dumps(TEXTS, ensure_ascii=False)},
        ],
        "temperature": 0.2,
        "stream": False,
    }
    return s, body


def run(mid, url, key, px):
    s = requests.Session()
    s.trust_env = False
    body = {
        "model": mid,
        "messages": [
            {"role": "system", "content": SYS},
            {"role": "user", "content": json.dumps(TEXTS, ensure_ascii=False)},
        ],
        "temperature": 0.2,
    }
    hdr = {"Content-Type": "application/json"}
    if key and key != "anonymous":
        hdr["Authorization"] = "Bearer " + key
    t0 = time.time()
    try:
        r = s.post(url, json=body, timeout=45, headers=hdr,
                   proxies=px if px else None)
    except Exception as e:
        return {"id": mid, "err": type(e).__name__ + ":" + str(e)[:60],
                "sec": round(time.time() - t0, 1)}
    dt = round(time.time() - t0, 1)
    if r.status_code != 200:
        return {"id": mid, "http": r.status_code, "sec": dt,
                "err": r.text[:90].replace("\n", " ")}
    try:
        txt = r.json()["choices"][0]["message"]["content"]
    except Exception:
        return {"id": mid, "http": r.status_code, "sec": dt, "err": "非标准响应"}
    m = re.search(r"\[.*\]", txt, re.S)
    arr = None
    if m:
        try:
            arr = json.loads(m.group(0))
        except Exception:
            arr = None
    if not isinstance(arr, list) or len(arr) != len(TEXTS):
        return {"id": mid, "http": 200, "sec": dt, "err": "条数%s" % (len(arr) if isinstance(arr, list) else "解析失败"),
                "raw": txt[:80].replace("\n", " ")}
    ja = sum(1 for a in arr if isinstance(a, str) and KANA.search(a))
    return {"id": mid, "http": 200, "sec": dt, "kana": "%d/%d" % (ja, len(TEXTS)),
            "sample": arr[0][:40]}


def main():
    rows = []
    for mid, url, key in models():
        if mid in ("deepseek-v4-flash", "glm-4v-flash"):
            continue                      # 付费 / 读图模型，跳过
        if "intern-ai" in url or "bigmodel" in url:
            rows.append(run(mid, url, key, None))      # 国内直连
        else:
            got = run(mid, url, key, None)
            if got.get("err"):
                for px in proxies():
                    got = run(mid, url, key, px)
                    if not got.get("err"):
                        got["via"] = px
                        break
            rows.append(got)
    rows.sort(key=lambda r: (r.get("err") is not None, r.get("sec", 999)))
    print("%-26s %-6s %-6s %-7s %s" % ("模型", "耗时s", "HTTP", "假名", "首条译文/错误"))
    for r in rows:
        print("%-26s %-6s %-6s %-7s %s" % (
            r["id"], r.get("sec"), r.get("http", "-"), r.get("kana", "-"),
            r.get("err") or (r.get("sample", "") + (" via " + r["via"] if r.get("via") else ""))))


if __name__ == "__main__":
    main()
