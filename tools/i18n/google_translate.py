# -*- coding: utf-8 -*-
"""Google gtx 免费翻译端点后端（与 zhipu_translate.Zhipu 同接口）。

接口：
    translate(texts, lang) -> list[str]   # texts 为单行文本（换行已替换为 ZZBRZZ）
    translate_raw(text, lang) -> str       # 整段原文翻译（labs 区段落用）

特点：
- 经 SOCKS5 出口（当前节点下 Google 返回 200，此前被封 IP 已解除）
- 批量按行提交，单次请求打包多行以降低请求数
- 429/失败按指数退避重试，行数不匹配时自动二分拆批
"""
import time

import requests

ENDPOINT = "https://translate.googleapis.com/translate_a/single"
PROXY = "socks5h://127.0.0.1:10808"
PROXIES = {"http": PROXY, "https": PROXY}
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
NL = "ZZBRZZ"


class RateLimited(Exception):
    pass


def _call(q, lang, timeout=25):
    r = requests.get(
        ENDPOINT,
        params={"client": "gtx", "sl": "zh-CN", "tl": lang, "dt": "t", "q": q},
        proxies=PROXIES, timeout=timeout, headers={"User-Agent": UA})
    if r.status_code == 429:
        raise RateLimited("gtx 429")
    r.raise_for_status()
    data = r.json()
    return "".join(seg[0] for seg in data[0] if seg and seg[0])


class Google:
    def __init__(self, max_retry=5):
        self.max_retry = max_retry

    def _call_retry(self, q, lang):
        delay = 2.0
        for attempt in range(self.max_retry):
            try:
                return _call(q, lang)
            except RateLimited:
                if attempt == self.max_retry - 1:
                    raise
                time.sleep(delay)
                delay *= 2          # 2s 4s 8s 16s 32s
            except Exception:
                if attempt == self.max_retry - 1:
                    raise
                time.sleep(1.0)

    def translate(self, texts, lang):
        """批量翻译。texts: 单行文本列表 -> list[str]。行数不匹配自动二分。"""
        if not texts:
            return []
        q = "\n".join(texts)
        out = self._call_retry(q, lang)
        lines = out.split("\n")
        if len(lines) == len(texts):
            return [ln.strip() for ln in lines]
        if len(texts) == 1:
            # 单行也可能被拆行：合并即可
            return [out.strip()]
        mid = len(texts) // 2
        return (self.translate(texts[:mid], lang)
                + self.translate(texts[mid:], lang))

    def translate_raw(self, text, lang):
        """整段翻译，保留内部换行结构（NL 占位符换回换行）。"""
        masked = text.replace("\n", NL)
        out = self._call_retry(masked, lang)
        return out.replace(NL, "\n").strip()


if __name__ == "__main__":
    g = Google()
    print(g.translate(["你好，世界", "串口通信的波特率是 115200",
                       "RFID 与 NFC 入门：13.56 MHz 与 MFRC522"], "ja"))
    print(g.translate_raw("46 课全部跑在我们自己的虚拟实验室里，点任一课直接进对应实验。", "ja"))
