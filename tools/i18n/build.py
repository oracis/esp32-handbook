#!/usr/bin/env python3
"""构建主站/实验室的多语言字典（构建期翻译，运行时零外部请求）。

用法：
  python tools/i18n/build.py --lang ja        # 只跑一种语言
  python tools/i18n/build.py --all            # 跑全部 7 种语言
  python tools/i18n/build.py --report         # 查看覆盖率

翻译后端：智谱 glm-4-flash（永久免费、国内直连，不受 Google 出口 IP 封禁影响）。
一次请求提交一个 JSON 数组批量翻译，失败自动二分拆批。
结果缓存在 cache.json，可断点续传。输出 dicts/site.json 与 dicts/lab.json。
"""
import argparse
import json
import re
import time
from pathlib import Path

from bs4 import BeautifulSoup

from zhipu_translate import Zhipu

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SITE_HTML = ROOT / "index.html"
LAB_HTML = ROOT / "lab/index.html"
CACHE = HERE / "cache.json"
DICT_DIR = HERE / "dicts"

LANGS = {
    "zh-TW": "繁體中文", "ja": "日本語", "ko": "한국어", "es": "Español",
    "pt": "Português", "fr": "Français", "ru": "Русский",
}
NL = "ZZBRZZ"
_Z = None

# 超过单次输出上限的大块不走机翻：LBWHOLE（13.5KB 的 46 课卡片 HTML）
# 由 tools/i18n/labs_section_multi.py 按结构化数据逐语言渲染，避免截断与 href 被译坏。
SKIP_BLOCKS = {"LBWHOLE"}
MAX_ITEM_CHARS = 3000


def engine():
    global _Z
    if _Z is None:
        _Z = Zhipu()
    return _Z


def grab_json(path, marker="window.I18N = "):
    s = path.read_text(encoding="utf-8")
    a = s.index(marker) + len(marker)
    d = 0; ins = False; esc = False
    for j in range(a, len(s)):
        c = s[j]
        if ins:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == '"': ins = False
        else:
            if c == '"': ins = True
            elif c in "[{": d += 1
            elif c in "]}":
                d -= 1
                if d == 0: break
    return json.loads(s[a:j + 1])


def site_blocks():
    """从主站原始 HTML 取出每个 data-l10n 块的中文 innerHTML。"""
    soup = BeautifulSoup(SITE_HTML.read_text(encoding="utf-8"), "html.parser")
    out = {}
    for el in soup.select("[data-l10n]"):
        key = el.get("data-l10n")
        if key not in out:
            out[key] = el.decode_contents()
    return out


def code_mask(text):
    """保护 <code> 片段不被翻译（Arduino 代码 / 型号 / 引脚名保留原文）。"""
    saved = []
    def sub(m):
        saved.append(m.group(0))
        return "ZZCODE%dZZ" % (len(saved) - 1)
    return re.sub(r"<code\b[^>]*>.*?</code>", sub, text, flags=re.S), saved


def code_unmask(text, saved):
    for i, frag in enumerate(saved):
        text = text.replace("ZZCODE%dZZ" % i, frag)
        text = text.replace(("ZZCODE%dZZ" % i).upper(), frag)
    return text


def curl_json(q, lang):
    raise NotImplementedError  # 已由智谱后端取代


def translate_one(text, lang):
    return translate_batch([text], lang)[0]


def translate_batch(texts, lang, depth=0):
    """批量翻译；整批失败时二分拆批重试。texts: list[str] -> list[str]"""
    masked = [code_mask(t.replace("\n", NL)) for t in texts]
    try:
        got = engine().translate([m[0] for m in masked], lang)
    except Exception:
        if len(texts) == 1 or depth >= 3:
            raise
        mid = len(texts) // 2
        return (translate_batch(texts[:mid], lang, depth + 1)
                + translate_batch(texts[mid:], lang, depth + 1))
    return [code_unmask(g.replace(NL, "\n"), m[1]).strip()
            for g, m in zip(got, masked)]


def load_cache():
    return json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}


def save_cache(c):
    tmp = CACHE.with_suffix(".tmp")
    tmp.write_text(json.dumps(c, ensure_ascii=False), encoding="utf-8")
    tmp.replace(CACHE)


def collect():
    site = grab_json(SITE_HTML)
    lab = grab_json(LAB_HTML)
    blocks = site_blocks()
    items = []
    for k in site["t"]:
        items.append(("t", k, k))
    for k in site["b"]:
        if k in SKIP_BLOCKS:
            continue
        if k in blocks and re.search(r"[\u4e00-\u9fff]", blocks[k]):
            items.append(("b", k, blocks[k]))
    for k, obj in site["meta"].items():
        items.append(("meta", k, obj["zh"]))
    for k in lab["t"]:
        items.append(("lab", k, k))
    return site, lab, items


def make_batches(todo, max_chars=2000, max_n=24):
    batches, cur, size = [], [], 0
    for item in todo:
        text = item[2]
        n = len(text) + 1
        if cur and (size + n > max_chars or len(cur) >= max_n):
            batches.append(cur); cur, size = [], 0
        cur.append(item); size += n
    if cur: batches.append(cur)
    return batches


def write_dicts(cache, site, lab):
    blocks = site_blocks()
    out_site, out_lab = {}, {}
    for lang in LANGS:
        c = cache.get(lang, {})
        sd = {"meta": {}, "t": {}, "b": {}}
        for k, obj in site["meta"].items():
            sd["meta"][k] = c.get(obj["zh"], obj["en"])
        for k in site["t"]:
            sd["t"][k] = c.get(k, site["t"][k])
        for k in site["b"]:
            zh = blocks.get(k, "")
            sd["b"][k] = c.get(zh, site["b"][k]) if zh else site["b"][k]
        out_site[lang] = sd
        out_lab[lang] = {"t": {k: c.get(k, lab["t"][k]) for k in lab["t"]}}
    DICT_DIR.mkdir(parents=True, exist_ok=True)
    (DICT_DIR / "site.json").write_text(json.dumps(out_site, ensure_ascii=False), encoding="utf-8")
    (DICT_DIR / "lab.json").write_text(json.dumps(out_lab, ensure_ascii=False), encoding="utf-8")


def run_lang(lang, offline=False):
    site, lab, items = collect()
    cache = load_cache()
    bucket = cache.setdefault(lang, {})
    todo = [x for x in items if x[2] not in bucket]
    print("%s: total=%d cached=%d todo=%d" % (lang, len(items), len(bucket), len(todo)), flush=True)
    if offline:
        print("  offline: 跳过网络，未命中项回退英文", flush=True)
        write_dicts(cache, site, lab)
        return
    batches = make_batches(todo)
    done = 0
    failed = 0
    for bi, batch in enumerate(batches, 1):
        try:
            values = translate_batch([x[2] for x in batch], lang)
            for (kind, key, text), val in zip(batch, values):
                bucket[text] = val or text
        except Exception as e:
            failed += len(batch)
            print("  BATCH FAIL %d 条: %s %s" % (len(batch), type(e).__name__,
                                                 str(e)[:120]), flush=True)
        done += len(batch)
        if bi % 5 == 0 or bi == len(batches):
            save_cache(cache)
            print("  %d/%d (fail %d)" % (done, len(todo), failed), flush=True)
    save_cache(cache)
    write_dicts(cache, site, lab)
    print("%s done: %d/%d" % (lang, len(bucket), len(items)), flush=True)


def report():
    _, _, items = collect()
    cache = load_cache()
    print("items:", len(items))
    for lang in LANGS:
        c = cache.get(lang, {})
        got = sum(1 for _, _, t in items if t in c)
        print("  %-5s %s  %d/%d" % (lang, LANGS[lang], got, len(items)))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", choices=list(LANGS))
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--offline", action="store_true", help="只从缓存写字典，不联网")
    args = ap.parse_args()
    if args.report: report()
    elif args.all:
        for l in LANGS: run_lang(l, offline=args.offline)
    elif args.lang: run_lang(args.lang, offline=args.offline)
    else: ap.print_help()
