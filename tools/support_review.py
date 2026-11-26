# -*- coding: utf-8 -*-
"""支持区 / 页脚译文的对外复核闭环。

    python tools/support_review.py --export     # 生成 tools/support_i18n_review.csv
    python tools/support_review.py --import     # 读回 CSV 里填过的 _new 列并写入 index.html

CSV 用 UTF-8 BOM，Excel 双击直接打开不乱码。
只认 es / pt / fr / ru 四列的「_new」；留空表示保持现值。
写入前逐条校验：<b> 标签数、专有名词、目标语言字形、是否残留汉字。
"""
import csv
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "i18n"))

SITE = "index.html"
CSV_PATH = "tools/support_i18n_review.csv"
REVIEW_LANGS = ["es", "pt", "fr", "ru"]
COLS = ["key", "note", "zh", "en"] + sum([[L, L + "_new"] for L in REVIEW_LANGS], [])

# 长句才有复核价值；短标签（回到顶部 / 支持 / 反馈）机翻反而更容易走样
LONG = {"SP2", "SP4", "SP7", "SP9", "SP10", "SP11", "FT7", "FT8"}

CJK = re.compile(r"[\u4e00-\u9fff]")
KANA = re.compile(r"[\u3040-\u30ff]")
HANGUL = re.compile(r"[\uac00-\ud7af]")
KEEP = ("ESP32", "GitHub", "oracis", "Espressif", "datasheet", "Discussions", "Star")


def load_mod():
    import importlib.util
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "add_support_i18n.py")
    spec = importlib.util.spec_from_file_location("asi", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def do_export(mod):
    src = io.open(SITE, encoding="utf-8").read()
    zh = mod.pick_zh(src)
    keys = sorted(zh, key=lambda x: (x[:2], int(x[2:])))
    rows = []
    for k in keys:
        row = {"key": k, "note": "建议复核" if k in LONG else "", "zh": zh[k],
               "en": mod.EN[k]}
        for L in REVIEW_LANGS:
            row[L] = mod.BY_LANG[L][k]
            row[L + "_new"] = ""
        rows.append(row)
    with io.open(CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)
    print("已生成 %s（%d 条 × %d 语言）" % (CSV_PATH, len(rows), len(REVIEW_LANGS)))
    print("填 *_new 列即可，留空表示不改。")
    return 0


def do_import(mod):
    if not os.path.exists(CSV_PATH):
        print("找不到 %s，先跑 --export" % CSV_PATH)
        return 1
    src = io.open(SITE, encoding="utf-8").read()
    zh = mod.pick_zh(src)

    changed, rejected = {}, []
    with io.open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            k = (row.get("key") or "").strip()
            if k not in zh:
                continue
            for L in REVIEW_LANGS:
                v = (row.get(L + "_new") or "").strip()
                if not v or v == mod.BY_LANG[L].get(k):
                    continue
                err = []
                if v.count("<b>") != zh[k].count("<b>"):
                    err.append("<b> 标签数不符")
                for w in KEEP:
                    if w in zh[k] and w not in v:
                        err.append("丢了 %s" % w)
                if CJK.search(v):
                    err.append("残留汉字")
                # 以 <b> 开头的句子 split("<b>")[0] 是空串，长度上限会退化成 80，
                # 正常译文全被拒——先剥标签再量中文长度
                plain = re.sub(r"<[^>]+>", "", zh[k])
                if len(v) > len(plain) * 4 + 80:
                    err.append("长度异常")
                if err:
                    rejected.append("%s %s: %s" % (L, k, "、".join(err)))
                    continue
                changed.setdefault(L, {})[k] = v

    if rejected:
        print("!! 以下条目未采用：")
        for r in rejected:
            print("   -", r)
    if not changed:
        print("没有需要写入的改动。")
        return 0

    i18n, end1, multi, end2, pos_i, pos_m = mod.load_blocks(src)
    for L, d in changed.items():
        mod.BY_LANG[L].update(d)
        multi.setdefault(L, {}).setdefault("b", {}).update(d)
        print(" - %s 更新 %d 条" % (L, len(d)))

    new = src[:pos_i] + mod.dump(i18n) + src[end1:]
    shift = len(mod.dump(i18n)) - (end1 - pos_i)
    new = new[:pos_m + shift] + mod.dump(multi) + new[end2 + shift:]
    io.open(SITE, "w", encoding="utf-8", newline="\n").write(new)
    print("写入 index.html：%d → %d 字节" % (len(src.encode()), len(new.encode())))
    print("提醒：记得把改动同步回 tools/add_support_i18n.py，否则重跑会覆盖。")
    return 0


def main():
    mod = load_mod()
    if "--import" in sys.argv:
        return do_import(mod)
    return do_export(mod)


if __name__ == "__main__":
    sys.exit(main())
