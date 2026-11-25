#!/usr/bin/env python3
"""构建主站/实验室的多语言字典（构建期翻译，运行时零外部请求）。

用法：
  python tools/i18n/build.py --lang ja        # 只跑一种语言
  python tools/i18n/build.py --all            # 跑全部 7 种语言
  python tools/i18n/build.py --report         # 查看覆盖率

翻译走 curl + 本机 SOCKS5 + Google 免费 gtx 端点，按行批量提交以减少请求数。
结果缓存在 cache.json，可断点续传。输出 dicts/site.json 与 dicts/lab.json。
"""
import argparse
import json
import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from bs4 import BeautifulSoup

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
ENDPOINT = "https://translate.google.com/translate_a/single"
NL = "ZZBRZZ"


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
    cmd = ["curl", "-s", "--max-time", "25", "--socks5", "127.0.0.1:10808",
           "--get", ENDPOINT,
           "--data-urlencode", "client=gtx", "--data-urlencode", "sl=zh-CN",
           "--data-urlencode", "tl=" + lang, "--data-urlencode", "dt=t",
           "--data-urlencode", "q=" + q]
    r = subprocess.run(cmd, capture_output=True, timeout=35)
    if r.returncode:
        raise RuntimeError("curl exit %d" % r.returncode)
    return json.loads(r.stdout.decode("utf-8", "ignore"))


def translate_one(text, lang):
    masked, saved = code_mask(text.replace("\n", NL))
    data = curl_json(masked, lang)
    out = "".join(seg[0] for seg in data[0] if seg and seg[0])
    return code_unmask(out.replace(NL, "\n"), saved)


def translate_batch(texts, lang):
    """批量翻译；行数不匹配时自动回退逐条。texts: list[str] -> list[str]"""
    masked = [code_mask(t.replace("\n", NL)) for t in texts]
    q = "\n".join(m[0] for m in masked)
    data = curl_json(q, lang)
    out = "".join(seg[0] for seg in data[0] if seg and seg[0])
    lines = out.split("\n")
    if len(lines) != len(texts):
        return [translate_one(t, lang) for t in texts]
    return [code_unmask(line.replace(NL, "\n"), m[1]).strip()
            for line, m in zip(lines, masked)]


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
        if k in blocks and re.search(r"[\u4e00-\u9fff]", blocks[k]):
            items.append(("b", k, blocks[k]))
    for k, obj in site["meta"].items():
        items.append(("meta", k, obj["zh"]))
    for k in lab["t"]:
        items.append(("lab", k, k))
    return site, lab, items


def make_batches(todo, max_chars=1500, max_n=16):
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


def run_lang(lang):
    site, lab, items = collect()
    cache = load_cache()
    bucket = cache.setdefault(lang, {})
    todo = [x for x in items if x[2] not in bucket]
    print("%s: total=%d cached=%d todo=%d" % (lang, len(items), len(bucket), len(todo)), flush=True)
    batches = make_batches(todo)
    done = 0
    for batch in batches:
        for attempt in range(3):
            try:
                values = translate_batch([x[2] for x in batch], lang)
                for (kind, key, text), val in zip(batch, values):
                    bucket[text] = val or text
                done += len(batch)
                break
            except Exception as e:
                if attempt == 2:
                    print("  BATCH FAIL", len(batch), type(e).__name__, str(e)[:100], flush=True)
                    done += len(batch)
                else:
                    time.sleep(1.5 * (attempt + 1))
        if done % 160 < len(batch):
            save_cache(cache)
            print("  %d/%d" % (done, len(todo)), flush=True)
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
    args = ap.parse_args()
    if args.report: report()
    elif args.all:
        for l in LANGS: run_lang(l)
    elif args.lang: run_lang(args.lang)
    else: ap.print_help()
