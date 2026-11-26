# -*- coding: utf-8 -*-
"""把支持区/页脚的 8 条长句用免费 LLM 机翻一遍，与现有人工译文并列，供人工挑拣。

只产出对照表，不改站点文件。挑好的候选用 support_review.py 填 *_new 导入。

用法：
    python tools/support_mt_compare.py            # 默认 glm + ernie
    python tools/support_mt_compare.py glm        # 只跑一个引擎
"""
import importlib.util
import io
import json
import re
import sys
import time

sys.path.insert(0, "tools/i18n")
from llm_translate import LLM  # noqa: E402

KEYS = ["SP2", "SP4", "SP7", "SP9", "SP10", "SP11", "FT7", "FT8"]
LANGS = ["es", "pt", "fr", "ru"]
LANG_LABEL = {"es": "西班牙语", "pt": "葡萄牙语", "fr": "法语", "ru": "俄语"}

SYS = (
    "你是嵌入式教学网站的专业本地化译者。把用户给的这一条中文译成%s。\n"
    "只输出译文本身：不要引号包裹、不要解释、不要前后缀、不要保留中文。\n"
    "以下必须原样保留：<b> 与 </b> 标签、ESP32、GitHub、Star、Discussions、datasheet、"
    "型号名、域名、数字。\n"
    "术语口径：「板子」指开发板（board），不是表格；「打赏」指自愿打赏（tip / donation），"
    "不是订阅或收藏；「实验」指动手做的 lab / experiment。\n"
    "中文标点换成目标语言习惯；句末不加句号以外的装饰。不要扩写，不要补解释。"
)

CJK = re.compile(r"[\u4e00-\u9fff]")
TAG = re.compile(r"</?b>")

# 人工判读结果：(语言, 键) -> (采用来源, 理由)。keep 表示现译更好，不改。
PICKS = {
    ("es", "SP2"): ("sage", "补出「算作支持」——cuenta como apoyo 比现译光秃秃的 cuenta 完整"),
    ("es", "SP4"): ("sage", "「GitHub 首页」写成 página de inicio de GitHub 更明确；pulsar Star 更常用"),
    ("es", "SP7"): ("keep", "现译一句三顿更利落，且保留了 placa 这个开发板说法"),
    ("es", "SP9"): ("sage", "「能点」译成 hacer clic，现译 recorrer（走一遍）偏了"),
    ("es", "SP10"): ("sage", "「一直在线」是 siempre está en línea，现译 sigue 弱化了「一直」"),
    ("es", "SP11"): ("sage", "补出「比打赏更有用」的比较对象；Star 用阳性 un Star 前后一致"),
    ("es", "FT7"): ("sage", "sin afiliación / se rigen por 比 sin relación / siguen 更像法律声明"),
    ("es", "FT8"): ("keep", "现译短句有标语感；只把 placa 改成复数 Las placas 更自然"),

    ("pt", "SP2"): ("keep", "现译更紧凑；只把句尾改成 conta como apoio"),
    ("pt", "SP4"): ("sage", "página inicial 比 início 明确；clicar em Star 自然"),
    ("pt", "SP7"): ("keep", "现译「Um dado errado…: diga」更有力，sage 版偏冗长"),
    ("pt", "SP9"): ("sage", "clicáveis / podem ser pulados 准确；现译 percorrer 是「游走」"),
    ("pt", "SP10"): ("sage", "está sempre online 贴合「一直在线」；原句缺句末句号，补上"),
    ("pt", "SP11"): ("sage", "canal 用单数、补出「比打赏更有用」的比较"),
    ("pt", "FT7"): ("sage", "prevalece o datasheet oficial 正是「以…为准」的法律语"),
    ("pt", "FT8"): ("keep", "现译短句更像标语；placa 改复数 placas"),

    ("fr", "SP2"): ("sage", "gestes ci-dessous comptent comme un soutien 比 l'une ou l'autre…compte 精确"),
    ("fr", "SP4"): ("sage", "C'est gratuit… détermine si… 比 Avec une Star 通顺"),
    ("fr", "SP7"): ("keep", "现译「Une valeur fausse, un lien mort…: dites-le」更利落"),
    ("fr", "SP9"): ("sage", "cliquables 纠正了现译 parcourir（游走）对「能点」的误译"),
    ("fr", "SP10"): ("keep", "现译已准确；sage 的 reste toujours 语义重复"),
    ("fr", "SP11"): ("keep", "现译 quand ils le seront 比 sage 的 dès qu'il le sera 少一处重复"),
    ("fr", "FT7"): ("sage", "seul le datasheet officiel fait foi 是法语法律惯用；补句号"),
    ("fr", "FT8"): ("keep", "现译保留标语节奏；carte 改复数 cartes"),

    ("ru", "SP2"): ("sage", "стена входа 是照字面造的，обязательная регистрация 才是俄语自然说法"),
    ("ru", "SP4"): ("sage", "现译「После Star」过于电报式，sage 补全了主谓"),
    ("ru", "SP7"): ("keep", "现译更紧凑，битая ссылка 是俄语口语里地道的说法"),
    ("ru", "SP9"): ("sage", "「能点」= запустить кликом，现译 пройти 只表示「走完」"),
    ("ru", "SP10"): ("sage", "всегда онлайн 贴合「一直在线」，现译 остаётся 只是「仍然」"),
    ("ru", "SP11"): ("sage", "「挂在这里」→ ссылка появится здесь 更具体；逗号改分号"),
    ("ru", "FT7"): ("keep", "现译已准确；glm 的 Ненавязчивый 把「非官方」译成「不打扰」是错译"),
    ("ru", "FT8"): ("keep", "现译短句贴合标语；плата 改复数 Платы"),
}

# 采用机翻时补的标点/复数微调，避免把模型的疏漏带进站点
FIXES = {
    ("pt", "SP10"): [("internet fraca", "internet fraca.")],
    ("fr", "FT7"): [("fait foi", "fait foi.")],
    ("ru", "SP11"): [(", когда откроется", "; когда откроется")],
}


def load_module():
    spec = importlib.util.spec_from_file_location("sup", "tools/add_support_i18n.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def translate_one(llm, text, lang, engine):
    """单条整段翻译：条数少，走 raw 比 JSON 数组更不容易被标签/引号搞坏。"""
    name = LANG_LABEL[lang]
    msg = [{"role": "system", "content": SYS % name},
           {"role": "user", "content": text}]
    out = llm.chat(msg, temperature=0.1).strip()
    if out.startswith("```"):
        out = out.strip("`").strip()
    out = out.split("\n\n")[0].strip() if "\n\n" in out else out
    return out


def issues(zh, cur, mt):
    """返回这条机翻的问题清单，空列表表示可直接用。长度以现译为基准——
    拿中文长度当基准没有意义，中文比任何目标语言都紧凑。"""
    bad = []
    if not mt:
        return ["空输出"]
    if len(TAG.findall(mt)) != len(TAG.findall(zh)):
        bad.append("<b> 标签数不对")
    if CJK.search(mt):
        bad.append("残留汉字：%s" % "".join(sorted(set(CJK.findall(mt)))))
    if "Star" in zh and "Star" not in mt:
        bad.append("Star 被译走")
    if cur and not 0.6 <= len(mt) / len(cur) <= 1.7:
        bad.append("长度偏离现译 %.2fx" % (len(mt) / len(cur)))
    if cur and mt.strip() == cur.strip():
        bad.append("与现译相同")
    return bad


RAW = "tools/support_mt_raw.json"
PICK_CSV = "tools/support_i18n_review.csv"


def load_raw():
    try:
        return json.load(io.open(RAW, encoding="utf-8"))
    except Exception:
        return {}


def save_raw(o):
    io.open(RAW, "w", encoding="utf-8", newline="\n").write(
        json.dumps(o, ensure_ascii=False, indent=1))


def adopted(lang, k, cur, out):
    """按人工判读给出建议落地文本（机翻原文 + 必要标点微调）。"""
    src, _reason = PICKS.get((lang, k), ("keep", ""))
    if src == "keep":
        return cur, src
    v = out.get(lang, {}).get(k, {}).get(src, "")
    if not v:
        return cur, "keep"
    for a, b in FIXES.get((lang, k), []):
        v = v.replace(a, b)
    return v, src


def main():
    engines = sys.argv[1:] or ["glm", "sage"]
    m = load_module()
    src = io.open("index.html", encoding="utf-8").read()
    zh = m.pick_zh(src)

    out = load_raw()
    for eng in engines:
        print("=== 引擎 %s ===" % eng, flush=True)
        try:
            llm = LLM(eng, timeout=45)
        except Exception as e:
            print("  连不通，跳过：%s" % e, flush=True)
            continue
        for lang in LANGS:
            for k in KEYS:
                slot = out.setdefault(lang, {}).setdefault(k, {})
                if slot.get(eng):                      # 断点续跑：已有就不重复烧配额
                    continue
                t0 = time.time()
                try:
                    v = translate_one(llm, zh[k], lang, eng)
                except Exception as e:
                    v = ""
                    print("  %s/%s 失败 %s" % (lang, k, str(e)[:80]), flush=True)
                slot[eng] = v
                save_raw(out)                          # 每条落盘，被杀也不丢
                print("  %-4s %-5s %4.1fs %s" % (lang, k, time.time() - t0, v[:60]), flush=True)

    # ---------- 对照表（Markdown，给人读） ----------
    lines = ["# 支持区文案机翻对照（8 条长句 × 4 语言）", "",
             "现译 = 当前线上的人工译文；glm / sage = 两个免费模型的机翻结果。",
             "标 ⚠ 的是自动校验没过（标签数、汉字残留、长度偏离、Star 被译走）。"]
    stats = {"sage": 0, "keep": 0, "glm": 0}
    for lang in LANGS:
        lines += ["", "## %s `%s`" % (LANG_LABEL[lang], lang), ""]
        for k in KEYS:
            cur = m.BY_LANG[lang][k]
            new, src_used = adopted(lang, k, cur, out)
            stats[src_used] = stats.get(src_used, 0) + 1
            lines.append("**%s** · %s" % (k, zh[k]))
            lines.append("")
            lines.append("- 现译：%s" % cur)
            for eng in engines:
                mt = out.get(lang, {}).get(k, {}).get(eng, "")
                if not mt:
                    continue
                bad = issues(zh[k], cur, mt)
                lines.append("- %s：%s%s" % (eng, mt, " ⚠ " + "；".join(bad) if bad else ""))
            tag = "采用 sage" if src_used == "sage" else "保持现译"
            lines.append("- **建议：%s** — %s" % (tag, PICKS.get((lang, k), ("", ""))[1]))
            if src_used == "sage":
                lines.append("- → 定稿：%s" % new)
            lines.append("")
    lines += ["---", "",
              "判读结果：采用 sage %d 条，保持现译 %d 条；glm 有硬伤（SP10 四语全英文、"
              "FT7 西语混汉字、SP4 俄语混中文），一条未采用。"
              % (stats["sage"], stats["keep"])]
    io.open("tools/support_mt_compare.md", "w", encoding="utf-8", newline="\n").write(
        "\n".join(lines) + "\n")

    # ---------- 回填复核表的 *_new 列，用户可直接 --import ----------
    import csv
    rows = list(csv.DictReader(io.open(PICK_CSV, encoding="utf-8-sig")))
    for r in rows:
        k = (r.get("key") or "").strip()
        for lang in LANGS:
            r[lang + "_new"] = ""
            if k in KEYS:
                new, src_used = adopted(lang, k, m.BY_LANG[lang][k], out)
                if src_used != "keep":
                    r[lang + "_new"] = new
    cols = list(rows[0].keys())
    with io.open(PICK_CSV, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    print("\n对照表：tools/support_mt_compare.md")
    print("复核表：%s（已把建议文本填进 *_new 列，留空即不改）" % PICK_CSV)
    print("判读：sage %d 条 / 保持现译 %d 条" % (stats["sage"], stats["keep"]))


if __name__ == "__main__":
    main()
