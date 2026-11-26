# -*- coding: utf-8 -*-
"""把复核表里填好的 *_new 译文写进 index.html，并同步回 tools/add_support_i18n.py。

support_review.py --import 只改 index.html，重跑 add_support_i18n.py 会把手改成
机翻稿覆盖回去，所以这里多做一步：把 ES/PT/FR/RU 字典里的对应行原地替换。

用法：
    python tools/apply_mt_picks.py            # 写入
    python tools/apply_mt_picks.py --dry      # 只报告将要改哪些
"""
import csv
import importlib.util
import io
import os
import re
import sys

SITE = "index.html"
MOD = "tools/add_support_i18n.py"
CSV_PATH = "tools/support_i18n_review.csv"
LANGS = ["es", "pt", "fr", "ru"]
KEEP = ("ESP32", "GitHub", "oracis", "Espressif", "datasheet", "Discussions", "Star")
CJK = re.compile(r"[\u4e00-\u9fff]")


def load_mod():
    spec = importlib.util.spec_from_file_location("asi", MOD)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def collect(m, zh):
    """读 CSV 的 *_new 列，返回 {lang: {key: text}} 与拒绝清单。"""
    changed, rejected = {}, []
    with io.open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            k = (row.get("key") or "").strip()
            if k not in zh:
                continue
            for L in LANGS:
                v = (row.get(L + "_new") or "").strip()
                if not v or v == m.BY_LANG[L].get(k):
                    continue
                err = []
                if v.count("<b>") != zh[k].count("<b>"):
                    err.append("<b> 标签数不符")
                for w in KEEP:
                    if w in zh[k] and w not in v:
                        err.append("丢了 %s" % w)
                if CJK.search(v):
                    err.append("残留汉字")
                if len(v) > len(re.sub(r"<[^>]+>", "", zh[k])) * 4 + 80:
                    err.append("长度异常")
                if err:
                    rejected.append("%s %s: %s" % (L, k, "、".join(err)))
                    continue
                changed.setdefault(L, {})[k] = v
    return changed, rejected


def main():
    dry = "--dry" in sys.argv
    m = load_mod()
    src = io.open(SITE, encoding="utf-8").read()
    zh = m.pick_zh(src)
    changed, rejected = collect(m, zh)

    if rejected:
        print("!! 未采用：")
        for r in rejected:
            print("   -", r)
    if not changed:
        print("没有需要写入的改动。")
        return 0

    total = sum(len(d) for d in changed.values())
    print("待写入 %d 条：%s" % (total, {L: len(d) for L, d in changed.items()}))
    if dry:
        for L, d in changed.items():
            for k in d:
                print("  %-3s %-5s %s" % (L, k, d[k][:80]))
        return 0

    # 1) index.html 的两处 JSON 块
    i18n, end1, multi, end2, pos_i, pos_m = m.load_blocks(src)
    for L, d in changed.items():
        multi.setdefault(L, {}).setdefault("b", {}).update(d)
    new = src[:pos_i] + m.dump(i18n) + src[end1:]
    shift = len(m.dump(i18n)) - (end1 - pos_i)
    new = new[:pos_m + shift] + m.dump(multi) + new[end2 + shift:]
    io.open(SITE, "w", encoding="utf-8", newline="\n").write(new)
    print("index.html：%d → %d 字节" % (len(src.encode()), len(new.encode())))

    # 2) 同步 add_support_i18n.py，否则重跑脚本会覆盖回去
    py = io.open(MOD, encoding="utf-8").read()
    patched = 0
    for L, d in changed.items():
        var = L.upper()                                  # BY_LANG 的键是小写，模块变量是大写
        a = py.index("\n%s = {\n" % var) + 1
        b = py.index("\n}\n", a) + 3
        blk = py[a:b]
        for k, v in d.items():
            old = m.BY_LANG[L][k]
            old_line = '    "%s": "%s",' % (k, old)
            new_line = '    "%s": "%s",' % (k, v)
            if blk.count(old_line) != 1:
                print("  !! %s %s 在 %s 里找不到唯一原文，跳过" % (L, k, MOD))
                continue
            blk = blk.replace(old_line, new_line)
            patched += 1
        py = py[:a] + blk + py[b:]
    io.open(MOD, "w", encoding="utf-8", newline="\n").write(py)
    print("%s：原地替换 %d 行" % (MOD, patched))

    # 3) 回读校验：模块里的值与 index.html 必须一致
    m2 = load_mod()
    s2 = io.open(SITE, encoding="utf-8").read()
    _, _, m2multi, _, _, _ = m2.load_blocks(s2)
    bad = []
    for L, d in changed.items():
        for k, v in d.items():
            if m2.BY_LANG[L][k] != v:
                bad.append("%s %s 脚本未同步" % (L, k))
            if m2multi[L]["b"].get(k) != v:
                bad.append("%s %s 站点未写入" % (L, k))
    if bad:
        print("!! 回读不一致：")
        for x in bad:
            print("   -", x)
        return 1
    print("回读一致：%d 条在脚本与站点两侧都已更新。" % total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
