# -*- coding: utf-8 -*-
"""通用免费 LLM 翻译后端（OpenAI 兼容），与 Zhipu 同接口，可直接替换。

已实测（同一批 8 条真实课标题 → 日语，本机 2026-11-26）：

    baidu/ernie-5.5-flash-preview:free   2.3s   ← Kilo 网关，免 key
    glm-4-flash                          4.5s   ← 智谱，国内直连
    Sage-S2.1-Flash                      5.6s   ← 上海 AI 实验室，国内直连
    inclusionai/ling-3.2-flash:free     10.2s   ← Kilo 网关
    Atria-Dawn                          28.8s   ← 上海 AI 实验室
    kilo-auto/free                      29.6s   ← Kilo 网关
    openrouter/free                     34.0s   ← Kilo 网关

用法：
    from llm_translate import LLM
    llm = LLM("ernie")        # 或 "sage" / "glm" / "ling"
    llm.translate(["中文一", "中文二"], "ja")
"""
import json
import os
import time

import requests

from zhipu_translate import Zhipu

KILO = "https://api.kilo.ai/api/gateway/v1/chat/completions"

# 出国代理候选（本机切换器会换端口，按顺序探测）
PROXIES = ["socks5h://127.0.0.1:10808",
           "http://127.0.0.1:9935",
           "http://127.0.0.1:1114",
           "http://127.0.0.1:7897"]

ENGINES = {
    "ernie": {"api": KILO, "model": "baidu/ernie-5.5-flash-preview:free",
              "key": "anonymous", "abroad": True},
    "ling":  {"api": KILO, "model": "inclusionai/ling-3.2-flash:free",
              "key": "anonymous", "abroad": True},
    "kilo":  {"api": KILO, "model": "kilo-auto/free",
              "key": "anonymous", "abroad": True},
    "glm":   {"api": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
              "model": "glm-4-flash",
              "key": "c1127ca59f80474480c2cb64473b8de1.OdkFiOCFunDjiCSW",
              "abroad": False},
    "sage":  {"api": "https://discovery-api.intern-ai.org.cn/v1/chat/completions",
              "model": "Sage-S2.1-Flash", "key": None, "abroad": False},
}

_PICKED = {}


def _models_json():
    p = os.path.expanduser("~/.workbuddy/models.json")
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return []


def _probe(api, model, key, timeout=25):
    """发一条最小请求，返回可用代理（None 表示直连可用），失败返回 False。"""
    hdr = {"Content-Type": "application/json"}
    if key and key != "anonymous":
        hdr["Authorization"] = "Bearer " + key
    body = {"model": model, "messages": [{"role": "user", "content": "hi"}],
            "max_tokens": 8}
    s = requests.Session()
    s.trust_env = False
    for px in [None] + PROXIES:
        if px is None and _PICKED.get((api, model)) is not None:
            continue                                   # 已知需要代理就跳过直连
        p = {"http": px, "https": px} if px else None
        try:
            r = s.post(api, json=body, timeout=timeout, headers=hdr, proxies=p)
            if r.status_code == 200:
                return px
        except Exception:
            continue
    return False


class LLM(Zhipu):
    """与 Zhipu 完全同接口（translate / translate_raw / chat）。"""

    def __init__(self, engine="ernie", timeout=60):
        cfg = ENGINES.get(engine)
        if not cfg:
            raise ValueError("未知引擎 %s，可选：%s" % (engine, list(ENGINES)))
        key = cfg["key"]
        if engine == "sage":                           # 从 models.json 取 key
            for m in _models_json():
                if m.get("id") == cfg["model"]:
                    key = m.get("apiKey", "")
                    break
        self.engine = engine
        px = None
        if cfg["abroad"]:
            hit = _PICKED.get((cfg["api"], cfg["model"]), "unset")
            px = hit if hit != "unset" else _probe(cfg["api"], cfg["model"], key)
            if px is False:
                raise RuntimeError("%s 连不通（代理全失败）" % engine)
            _PICKED[(cfg["api"], cfg["model"])] = px
        super().__init__(key=key, model=cfg["model"], proxy=px,
                         timeout=timeout, api=cfg["api"])


if __name__ == "__main__":
    import sys
    eng = sys.argv[1] if len(sys.argv) > 1 else "ernie"
    lang = sys.argv[2] if len(sys.argv) > 2 else "ja"
    t0 = time.time()
    llm = LLM(eng)
    print("引擎 %s / 模型 %s / 代理 %s（探测 %.1fs）"
          % (eng, llm.model, llm.proxy, time.time() - t0))
    t0 = time.time()
    out = llm.translate(["RFID 入门：13.56 MHz 与 MFRC522",
                         "分贝：从采样值算响度",
                         "拍手控制：阈值、去抖与误触发"], lang)
    print("翻译 3 条耗时 %.1fs：" % (time.time() - t0))
    for x in out:
        print("   ", x)
