# -*- coding: utf-8 -*-
"""免费 LLM 补翻器（后端可切换）：只补 cache 里缺失的条目，小批 + 每批落盘。

后端用 --engine 选，实测速度（8 条课标题→日语）：
  ernie 2.3s（Kilo 网关，免 key，默认） / glm 4.5s / sage 5.6s / ling 10.2s


- 409 条课文短句走 LLM 批量翻译（3 线程，失败自动二分到单条）
- SIMCARD 这类 HTML 块不机翻：只翻其中的纯文案，标记结构由代码重建，href 零风险
- 每批成功立即写 cache.json，断点续传；日志逐批输出带 ETA
"""
import json
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

import build
from llm_translate import LLM

LANGS = ["zh-TW", "ja", "ko", "es", "pt", "fr", "ru"]
BATCH_N = 8
BATCH_CHARS = 600
WORKERS = 2
CJK = re.compile(r"[\u4e00-\u9fff]")
KANA = re.compile(r"[\u3040-\u30ff]")
HANGUL = re.compile(r"[\uac00-\ud7af]")


def valid(lang, text, v):
    """按语言判定译文是否合格。

    关键是别把「正常的译文」判成失败：
    - 源串本来就没有汉字（型号/引脚/代号）→ 不翻译才是对的
    - 日语的纯汉字词（開発環境、高性能）是正常译文，不要求必须有假名
    - 只有「目标语言里夹着大段汉字」才是真没翻
    """
    if not v:
        return False
    if text.startswith("<"):
        return True
    if not CJK.search(text):          # 源串无汉字，无需翻译
        return True
    if lang in ("zh-TW", "ja"):
        return True                   # 繁中/日文都用汉字
    if lang == "ko":
        return bool(HANGUL.search(v)) or v == text
    # 拉丁/西里尔语系：译文里混进成串汉字说明没翻完
    return len(CJK.findall(v)) <= 2

lock = threading.Lock()
cache = build.load_cache()
done = [0]
fail = []
t0 = time.time()
_tl = threading.local()


ENGINE = "ernie"


def z_of():
    """每个线程一个独立客户端：requests.Session 不是线程安全的，
    多线程共用一个 Session 会在连接池上死锁（表现为跑一阵后静默卡死）。"""
    if not hasattr(_tl, "z"):
        _tl.z = LLM(ENGINE, timeout=45)
    return _tl.z


def log(msg):
    with lock:
        print("[%s] %s" % (time.strftime("%H:%M:%S"), msg), flush=True)


def save():
    build.save_cache(cache)


def translate_batch(z, texts, lang, depth=0):
    """失败二分；到单条仍失败则抛错（由调用方记入失败清单）。"""
    masked = [build.code_mask(t)[0] if "<code" in t else t for t in texts]
    saved = [build.code_mask(t)[1] if "<code" in t else [] for t in texts]
    try:
        got = z.translate(masked, lang, retries=1)
    except Exception:
        if len(texts) == 1 or depth >= 3:
            raise
        mid = len(texts) // 2
        return (translate_batch(z, texts[:mid], lang, depth + 1)
                + translate_batch(z, texts[mid:], lang, depth + 1))
    return [build.code_unmask(g, s) for g, s in zip(got, saved)]


def run_batch(lang, batch):
    z = z_of()
    texts = [x[2] for x in batch]
    log("  · %s 批开跑 %d 条" % (lang, len(texts)))
    try:
        vals = translate_batch(z, texts, lang, 0)
    except Exception as e:
        with lock:
            fail.extend([(lang, t) for t in texts])
        log("  ✗ %s 批失败(%s)，%d 条转单条待跑" % (lang, type(e).__name__, len(texts)))
        return
    with lock:
        bucket = cache.setdefault(lang, {})
        bad = []
        for (kind, key, text), val in zip(batch, vals):
            v = (val or "").strip()
            if valid(lang, text, v):
                bucket[text] = v
            else:
                bad.append((lang, text, v[:40]))
        fail.extend(bad)
        done[0] += len(batch)
        save()
        el = time.time() - t0
        rate = done[0] / el if el else 0
        left = TOTAL - done[0]
        eta = left / rate / 60 if rate else 0
        print("[%s] %-6s +%d 累计 %d/%d (%.1f/s, 剩约 %.0f 分)"
              % (time.strftime("%H:%M:%S"), lang, len(batch), done[0], TOTAL, rate, eta),
              flush=True)


def simcard(lang):
    z = z_of()
    """SIMCARD 块：只翻 4 条文案，结构由代码重建。"""
    src = build.site_blocks()["SIMCARD"]
    if src in cache.get(lang, {}):
        return
    strings = ["🌱 进入零基础",
               "46 课引导式仿真：拆解开发板、看串口输出、跑示例代码，零门槛上手。",
               "🔧 进入进阶工作台",
               "在编辑器里真写 Arduino 代码，自由挂载外设，引脚与 3D 板实时联动。"]
    vals = translate_batch(z, strings, lang)
    html = ('<div class="entry-cards">\n'
            '<a class="entry-card" href="https://lab.ydtgo.top/" rel="noopener" target="_blank">'
            '<b>%s</b><span>%s</span><span class="go">lab.ydtgo.top →</span></a>\n'
            '<a class="entry-card hot" href="https://lab.ydtgo.top/?mode=wb" rel="noopener" target="_blank">'
            '<b>%s</b><span>%s</span><span class="go">lab.ydtgo.top/?mode=wb →</span></a>\n'
            '</div>') % tuple(vals)
    with lock:
        cache.setdefault(lang, {})[src] = html
        save()
    log("%s SIMCARD 结构重建完成" % lang)


def wanted(it):
    """要翻译的条目：排除 HTML 块（只翻其中纯文案），保留以 <b>/<code> 开头的句子。"""
    kind, key, text = it
    if kind == "b" and text.startswith("<"):
        return False
    return True


def main():
    global TOTAL
    _, _, items = build.collect()
    TOTAL = sum(1 for L in LANGS for it in items
                if it[2] not in cache.get(L, {}) and wanted(it))
    log("待补 %d 条（不含 HTML 块）" % TOTAL)
    if TOTAL == 0:
        log("无事可做")
        return

    jobs = []
    for lang in LANGS:
        bucket = cache.setdefault(lang, {})
        todo = [it for it in items if it[2] not in bucket and wanted(it)]
        for batch in build.make_batches(todo, max_chars=BATCH_CHARS, max_n=BATCH_N):
            jobs.append((lang, batch))

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = [ex.submit(run_batch, lang, b) for lang, b in jobs]
        for f in as_completed(futs):
            f.result()

    for lang in LANGS:
        simcard(lang)

    log("完成 %d 条；失败 %d 条" % (done[0], len(fail)))
    if fail:
        (HERE / "_fail.json").write_text(
            json.dumps(fail, ensure_ascii=False, indent=1), encoding="utf-8")
        log("失败清单已写 _fail.json")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", default="ernie",
                    help="翻译后端：ernie(默认,最快) / glm / sage / ling / kilo")
    a = ap.parse_args()
    ENGINE = a.engine
    TOTAL = 0
    print("翻译后端:", ENGINE, "| 模型:", LLM(ENGINE).model, flush=True)
    main()
