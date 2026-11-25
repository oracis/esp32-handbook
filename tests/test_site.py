#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ESP32 全景手册站点全量测试套件。

三层：
  A. 静态结构/契约测试 —— 纯 stdlib 解析 index.html，不联网不跑浏览器
  B. 运行时测试 —— headless Chrome 加载 tests/harness.html，驱动 iframe 里的
     真实页面跑全部交互（语言切换/决策器/筛选/搜索/复制/溢出/滚动显现），
     结果 JSON 写入 #PROBE，这里逐项断言
  C. 在线冒烟（--live 或 ALIYUN_LIVE=1）—— 线上站点 HTTPS/字节一致/语义标记

用法：
  python tests/test_site.py            # A + B
  python tests/test_site.py --live     # A + B + C
依赖：requests（仅 --live 用到）、本机 Chrome（B 层用，缺失则 SKIP）。
"""
import html as html_mod
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "index.html"
HARNESS = ROOT / "tests" / "harness.html"
LIVE_URL = "https://esp32.ydtgo.top/"

SRC = SITE.read_text(encoding="utf-8")
EXPECT_SECTIONS = ["ai", "chips", "env", "wizard", "path", "labs", "video",
                   "cases", "code", "res", "buy", "pit", "gloss", "src"]

CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
]


def chrome_path():
    for p in CHROME_CANDIDATES:
        if os.path.exists(p):
            return p
    return shutil.which("chrome") or shutil.which("chrome.exe")


# ---------------------------------------------------------------- 工具

class _StackParser(HTMLParser):
    """带栈的解析器：检出未闭合标签、.rv 嵌套在 data-l10n 内、data-l10n 嵌套。"""

    VOID = {"br", "img", "meta", "link", "input", "hr", "source", "area",
            "base", "col", "embed", "track", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.unclosed = []
        self.rv_in_l10n = []
        self.l10n_nested = []
        self.texts = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = (a.get("class") or "").split()
        if "rv" in cls:
            for _t, aa in self.stack:
                if "data-l10n" in aa:
                    self.rv_in_l10n.append((tag, a.get("data-l10n")))
                    break
        if "data-l10n" in a:
            for _t, aa in self.stack:
                if "data-l10n" in aa:
                    self.l10n_nested.append(a.get("data-l10n"))
                    break
        if tag not in self.VOID:
            self.stack.append((tag, a))

    def handle_startendtag(self, tag, attrs):
        pass  # 自闭合不进栈

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                # 只记真正悬空的（i+1 之后），别把匹配到的自己记进去
                for t, _a in self.stack[i + 1:]:
                    if t not in self.VOID:
                        self.unclosed.append(t)
                del self.stack[i:]
                return
        # 多余的闭合标签不记（HTML 容错）

    def handle_data(self, data):
        self.texts.append(data)


def parse_stack():
    p = _StackParser()
    p.feed(SRC)
    return p


def get_i18n():
    """括号计数提取 window.I18N 的 JSON——字典里可能含 '};' 序列，
    non-greedy 正则会提前截断（英文块里带 CSS 时触发）。"""
    key = "window.I18N = "
    i = SRC.find(key)
    assert i >= 0, "window.I18N 字典未找到"
    i += len(key)
    depth = 0; in_str = False; esc = False; end = None
    for k in range(i, len(SRC)):
        c = SRC[k]
        if in_str:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == '"': in_str = False
            continue
        if c == '"': in_str = True
        elif c == "{": depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                end = k + 1
                break
    assert end, "I18N JSON 括号未闭合"
    return json.loads(SRC[i:end])


def script_blocks():
    return re.findall(r"<script[^>]*>(.*?)</script>", SRC, re.S)


# ================================================================ A. 静态

class TestStructure(unittest.TestCase):
    def test_file_exists_and_size(self):
        self.assertTrue(SITE.exists())
        self.assertGreater(SITE.stat().st_size, 150_000)

    def test_sections_order(self):
        secs = re.findall(r'<section id="([^"]+)"', SRC)
        self.assertEqual(secs, EXPECT_SECTIONS)

    def test_single_h1(self):
        self.assertEqual(len(re.findall(r"<h1[\s>]", SRC)), 1)

    def test_title_and_meta_desc(self):
        self.assertIn("ESP32 全景手册", re.search(r"<title>(.*?)</title>", SRC).group(1))
        self.assertTrue(re.search(r'<meta name="description" content=".{20,}"', SRC))

    def test_lang_attr_default(self):
        m = re.search(r'<html[^>]*lang="([^"]+)"', SRC)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), "zh-CN")

    def test_nav_anchors_resolve(self):
        secs = set(EXPECT_SECTIONS)
        anchors = set(re.findall(r'href="#([a-zA-Z-]+)"', SRC))
        dead = anchors - secs - {"top"}
        self.assertEqual(dead, set(), f"死锚点: {dead}")

    def test_no_javascript_hrefs(self):
        self.assertNotRe = None  # noqa
        bad = [h for h in re.findall(r'href="javascript:[^"]*"', SRC)]
        self.assertEqual(bad, [])

    def test_i18n_toggle_button_present(self):
        self.assertIn('id="langSw"', SRC)

    def test_search_input_present(self):
        self.assertIn('id="resSearch"', SRC)


class TestI18NStatic(unittest.TestCase):
    """i18n 字典完整性与实现契约（脚本 2 的真实逻辑）。"""

    def setUp(self):
        self.d = get_i18n()

    def test_meta_bilingual(self):
        for k in ("title", "desc", "ph"):
            self.assertIn(k, self.d["meta"])
            self.assertIn("zh", self.d["meta"][k])
            self.assertIn("en", self.d["meta"][k])

    def test_t_b_dicts_exist(self):
        self.assertIn("t", self.d)
        self.assertIn("b", self.d)
        self.assertGreater(len(self.d["t"]), 100)
        self.assertGreater(len(self.d["b"]), 50)

    def test_every_l10n_key_in_b(self):
        keys = set(re.findall(r'data-l10n="([^"]+)"', SRC))
        missing = keys - set(self.d["b"])
        self.assertEqual(missing, set(),
                         f"data-l10n 键缺 en 块翻译（切换英文会永久停留在中文）: {missing}")

    def test_no_orphan_b_keys(self):
        keys = set(re.findall(r'data-l10n="([^"]+)"', SRC))
        orphan = set(self.d["b"]) - keys
        self.assertEqual(orphan, set(), f"b 字典多余键（从未被用到）: {orphan}")

    def test_en_values_contain_no_cjk(self):
        def cjk(s):
            return re.search(r"[\u4e00-\u9fff]", s)
        bad_t = [k for k, v in self.d["t"].items() if cjk(v)]
        bad_b = [k for k, v in self.d["b"].items() if cjk(v)]
        self.assertEqual(bad_t, [], f"t 英文译文含中文: {bad_t[:5]}")
        self.assertEqual(bad_b, [], f"b 英文译文含中文: {bad_b[:5]}")

    def test_t_keys_all_contain_cjk(self):
        """TreeWalker 只匹配含 CJK 的文本节点，不含中文的 t 键永远命中不了。"""
        dead = [k for k, v in self.d["t"].items()
                if not re.search(r"[\u4e00-\u9fff]", k)]
        self.assertEqual(dead, [], f"永远不会命中的 t 键: {dead[:5]}")

    def test_t_keys_appear_in_document(self):
        """t 键必须以纯文本形式出现在 HTML 里（TreeWalker 按整段文本匹配）。
        按标签切块重建候选文本节点（键可跨行），比对时折叠空白。"""
        text = html_mod.unescape(re.sub(r"<script.*?</script>", "", SRC, flags=re.S))

        def norm(s):
            return re.sub(r"\s+", " ", s).strip()

        nodes = {norm(c) for c in re.split(r"<[^>]+>", text) if norm(c)}
        miss = [k for k in self.d["t"] if norm(k) not in nodes]
        self.assertEqual(miss, [], f"t 键在页面文本中找不到（按节点匹配不到）: {miss[:5]}")


class TestRvPitfall(unittest.TestCase):
    """历史坑：data-l10n 块切换时 innerHTML 整体替换，内部 .rv 会丢 .in 类
    导致 opacity:0 不可见。测试守住「不许嵌套」。"""

    def test_no_rv_inside_l10n(self):
        p = parse_stack()
        self.assertEqual(p.rv_in_l10n, [],
                         f".rv 嵌套在 data-l10n 内，切语言会不可见: {p.rv_in_l10n}")

    def test_no_nested_l10n(self):
        p = parse_stack()
        self.assertEqual(p.l10n_nested, [],
                         f"data-l10n 嵌套，外层切换会连带销毁内层: {p.l10n_nested}")

    def test_rv_elements_exist(self):
        self.assertGreater(len(re.findall(r'class="[^"]*\brv\b', SRC)), 20)


class TestInteractiveContracts(unittest.TestCase):
    """脚本 0/3 依赖的 DOM 契约。"""

    def test_chip_filter_values_cover_groups(self):
        btns = set(re.findall(r'data-f="([^"]+)"', SRC))
        groups = set(re.findall(r'<tr[^>]*\bdata-g="([^"]+)"', SRC))
        self.assertIn("all", btns)
        self.assertEqual(groups - btns, set(), "芯片行 data-g 没有对应筛选按钮")

    def test_chip_rows_have_group(self):
        rows = re.findall(r'<tr[^>]*>', SRC)
        tbody_rows = [r for r in rows if "data-g" in r]
        self.assertGreaterEqual(len(tbody_rows), 11)

    def test_video_filter_values_cover_cards(self):
        """筛选按钮引用的词必须真实存在；data-k 允许有元标签（如 cn=中文来源）
        不设按钮 —— 显式列入 META 白名单，新增无按钮词会被拦下。"""
        META_TOKENS = {"cn"}
        btns = set(re.findall(r'data-vf="([^"]+)"', SRC))
        tokens = set()
        for m in re.finditer(r'class="vid[^"]*"[^>]*data-k="([^"]+)"', SRC):
            tokens.update(m.group(1).split())
        self.assertIn("all", btns)
        self.assertTrue(btns - {"all"} <= tokens, "筛选按钮引用了不存在的词")
        orphan = tokens - btns - META_TOKENS
        self.assertEqual(orphan, set(), f"视频卡 data-k 词没有对应筛选按钮: {orphan}")
        self.assertGreaterEqual(len(re.findall(r'class="vid[^"]*"', SRC)), 10)

    def test_res_filter_values_cover_items(self):
        btns = set(re.findall(r'data-rf="([^"]+)"', SRC))
        tokens = set()
        items = re.findall(r'class="res[^"]*"[^>]*data-k="([^"]+)"', SRC)
        for m in items:
            tokens.update(m.split())
        self.assertIn("all", btns)
        self.assertEqual(tokens - btns, set(), "资源 data-k 词没有对应筛选按钮")
        self.assertEqual(len(items), 26, "资源库数量应为 26")

    def test_res_items_have_k(self):
        res_blocks = re.findall(r'<(div|a)[^>]*class="res[" ][^>]*>', SRC)
        self.assertTrue(res_blocks)

    def test_buy_groups_match_buttons(self):
        bf = set(re.findall(r'data-bf="([^"]+)"', SRC))
        bg = set(re.findall(r'class="buy-g[^"]*"[^>]*data-g="([^"]+)"', SRC))
        self.assertIn("all", bf)
        self.assertEqual(bf, bg | {"all"}, f"采购分组与筛选按钮不一致: bf={bf} bg={bg}")

    def test_wizard_groups_and_options(self):
        keys = re.findall(r'wz-opts[^>]*data-key="([^"]+)"', SRC)
        self.assertEqual(keys, ["purpose", "bt", "scale"])
        vals = re.findall(r'class="wz-opt[^"]*"[^>]*data-v="([^"]+)"', SRC)
        self.assertEqual(set(vals[:8]),
                         {"learn", "cheap", "display", "bigdisp",
                          "vision", "audio", "matter", "battery"})
        self.assertEqual(set(vals[8:]), {"any", "need", "no", "proto", "mass"})

    def test_wizard_db_covers_purpose_options(self):
        block = re.search(r"var DB = \{(.*?)\n  \};", SRC, re.S)
        assert block, "决策器 DB 未找到"
        db_keys = set(re.findall(r"^\s{4}(\w+): \{", block.group(1), re.M))
        self.assertEqual(db_keys, {"learn", "cheap", "display", "bigdisp",
                                   "vision", "audio", "matter", "battery"})

    def test_required_ids(self):
        for i in ("chipTable", "vidList", "resList", "resSearch",
                  "wzOut", "langSw"):
            self.assertIn(f'id="{i}"', SRC)

    def test_copy_buttons_have_codebox(self):
        self.assertEqual(len(re.findall(r'class="[^"]*\bcp\b[^"]*"', SRC)),
                         len(re.findall(r'class="[^"]*codebox', SRC)),
                         ".cp 与 .codebox 数量应一一对应")
        self.assertGreaterEqual(SRC.count("codebox"), 6)


class TestNeedleContent(unittest.TestCase):
    """Needle 2 第三路线：事实边界、置信度路由、i18n、资源与术语。"""

    def _a10(self):
        m = re.search(r'<div data-l10n="A10">(.*?)\n    </div>', SRC, re.S)
        self.assertIsNotNone(m, "缺少 data-l10n=A10 块")
        return m.group(1)

    def test_a10_block_present(self):
        blk = self._a10()
        self.assertIn("Needle 2", blk)
        for token in ("45M", "14MB", "28MB"):
            self.assertIn(token, blk)

    def test_three_routes_compared(self):
        blk = self._a10()
        for token in ("小智 AI", "ESP-Claw", "Needle 2", "断网时"):
            self.assertIn(token, blk)

    def test_confidence_routing_code(self):
        blk = self._a10()
        for token in ("confidence_route.py", "confidence", "suppressed_calls",
                      "escalate_to_cloud", "confirm("):
            self.assertIn(token, blk)

    def test_honest_bounds(self):
        blk = self._a10()
        for token in ("ESP32-P4", "32MB PSRAM", "1.86 tok/s", "40 秒",
                      "legacy", "cactus-compute&lt;4", "Needle 3", "13 个部署目标"):
            self.assertIn(token, blk)

    def test_needle_links_in_a10(self):
        blk = self._a10()
        for u in ("github.com/cactus-compute/cactus/tree/legacy",
                  "cactuscompute.com/blog/needle-2",
                  "cactuscompute.com/blog/needle-supported-devices"):
            self.assertIn(u, blk)

    def test_a10_en_block(self):
        en = get_i18n()["b"]["A10"]
        for token in ("Needle 2", "14 MB", "28 MB", "ESP32-P4",
                      "confidence", "legacy", "It does not chat"):
            self.assertIn(token, en)
        self.assertNotRegex(en, r"[\u4e00-\u9fff]", "英文 A10 块残留中文")

    def test_glossary_entries(self):
        b = get_i18n()["b"]
        for k in ("L71", "L72", "L73"):
            self.assertIn('data-l10n="%s"' % k, SRC, f"术语 {k} 缺中文块")
            self.assertIn("<b>", b[k], f"术语 {k} 缺英文块")
            self.assertNotRegex(b[k], r"[\u4e00-\u9fff]", f"术语 {k} 英文残留中文")

    def test_resources_added(self):
        for u in ("github.com/cactus-compute/cactus/tree/legacy",
                  "cactuscompute.com/blog/needle-2",
                  "cactuscompute.com/blog/needle-supported-devices"):
            self.assertIn(u, SRC)

    def test_hero_count_matches_resources(self):
        n = len(re.findall(r'class="res[^"]*"[^>]*data-k="([^"]+)"', SRC))
        m = re.search(r'<div class="stat"><b>(\d+)</b><span>精选资源入口</span></div>', SRC)
        self.assertIsNotNone(m)
        self.assertEqual(int(m.group(1)), n, "Hero 资源计数与实际条目不一致")


class TestLinks(unittest.TestCase):
    def setUp(self):
        self.links = re.findall(r'href="(https?://[^"]+)"', SRC)

    def test_links_present(self):
        self.assertGreaterEqual(len(self.links), 80)

    def test_all_https(self):
        bad = [u for u in self.links if u.startswith("http://")]
        self.assertEqual(bad, [], f"不安全 http 链接: {bad}")

    def test_no_spaces_or_bare_cjk(self):
        bad = [u for u in self.links if " " in u or re.search(r"[\u4e00-\u9fff]", u)]
        self.assertEqual(bad, [], f"URL 含空格/裸中文（未编码）: {bad[:3]}")

    def test_urls_parseable(self):
        for u in self.links:
            p = urlparse(u)
            self.assertTrue(p.netloc, u)
            self.assertNotIn("..", p.path, u)

    def test_taobao_search_links(self):
        tb = [u for u in self.links if "taobao.com" in u]
        self.assertGreater(len(tb), 30, "淘宝搜索直达链接应保留 30+ 条")
        for u in tb:
            p = urlparse(u)
            self.assertEqual(p.netloc, "s.taobao.com", u)
            self.assertEqual(p.path, "/search", u)
            q = parse_qs(p.query).get("q", [""])[0]
            self.assertTrue(q, f"淘宝链接缺 q 参数: {u}")
            self.assertTrue(re.search(r"[\u4e00-\u9fffA-Za-z0-9]", unquote(q)), u)

    def test_no_youtube(self):
        self.assertEqual([u for u in self.links if "youtube" in u.lower()], [],
                         "YouTube 链接应已移除（IP 不可达决策）")

    def test_github_and_espressif_cores(self):
        hosts = {urlparse(u).netloc for u in self.links}
        for h in ("github.com", "docs.espressif.com"):
            self.assertIn(h, hosts)


class TestHtmlSanity(unittest.TestCase):
    def test_tag_balance(self):
        p = parse_stack()
        self.assertEqual(p.unclosed, [], f"未闭合标签: {set(p.unclosed)}")

    def test_no_leftovers(self):
        for pat in (r"TODO", r"FIXME", r"Lorem ipsum", r"\{\{", r"PLACEHOLDER_"):
            self.assertIsNone(re.search(pat, SRC), f"残留 {pat}")

    def test_no_debug_output(self):
        self.assertNotIn("console.log(", SRC.replace("/*", "").replace("*/", ""),
                         "不应残留 console.log")

    def test_no_inline_event_handlers(self):
        bad = re.findall(r'\son(click|error|load)="', SRC)
        self.assertEqual(bad, [], "不应有内联事件处理器（CSP 友好）")

    def test_viewport_meta(self):
        self.assertTrue(re.search(r'<meta name="viewport" content="[^"]*width=device-width', SRC))


class TestScriptSyntax(unittest.TestCase):
    """node --check 逐块校验 JS 语法（node 缺失则 SKIP）。"""

    def setUp(self):
        self.node = shutil.which("node")

    def test_scripts_compile(self):
        if not self.node:
            self.skipTest("node 不可用")
        blocks = script_blocks()
        self.assertGreaterEqual(len(blocks), 4)
        with tempfile.TemporaryDirectory() as td:
            for i, b in enumerate(blocks):
                p = Path(td) / f"s{i}.js"
                p.write_text(b, encoding="utf-8")
                r = subprocess.run([self.node, "--check", str(p)],
                                   capture_output=True, text=True)
                self.assertEqual(r.returncode, 0,
                                 f"script#{i} 语法错误: {r.stderr[:300]}")

    def test_i18n_is_valid_json(self):
        get_i18n()  # json.loads 抛错即失败


# ================================================================ B. 运行时

def _run_harness():
    """跑一次 headless Chrome harness，返回 (results_dict, console_errors)。缓存。"""
    global _HARNESS_CACHE
    if _HARNESS_CACHE is not None:
        return _HARNESS_CACHE
    exe = chrome_path()
    if not exe:
        _HARNESS_CACHE = (None, None)
        return _HARNESS_CACHE
    with tempfile.TemporaryDirectory(prefix="esp32test_") as td:
        cmd = [exe, "--headless=new", "--disable-gpu",
               "--allow-file-access-from-files",
               "--enable-logging=stderr", "--v=0",
               "--no-first-run", "--no-default-browser-check",
               f"--user-data-dir={td}",
               "--virtual-time-budget=10000", "--dump-dom",
               HARNESS.as_uri()]
        r = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=180, errors="replace")
        out = r.stdout
        m = re.search(r'<div id="PROBE">(.*?)</div>', out, re.S)
        console = [ln for ln in r.stderr.splitlines()
                   if re.search(r"Uncaught|ERROR:CONSOLE", ln)]
        if not m:
            _HARNESS_CACHE = (None, console)
            return _HARNESS_CACHE
        try:
            data = json.loads(html_mod.unescape(m.group(1)))
        except json.JSONDecodeError:
            _HARNESS_CACHE = (None, console)
            return _HARNESS_CACHE
        _HARNESS_CACHE = (data, console)
        return _HARNESS_CACHE


_HARNESS_CACHE = None


def _run_langtest():
    """?langtest 自检：逐语言切换，title 回读 LANGS JSON。缓存。"""
    global _LANG_CACHE
    if _LANG_CACHE is not None:
        return _LANG_CACHE
    exe = chrome_path()
    if not exe:
        _LANG_CACHE = None
        return None
    with tempfile.TemporaryDirectory(prefix="esp32lang_") as td:
        cmd = [exe, "--headless=new", "--disable-gpu",
               f"--user-data-dir={td}", "--virtual-time-budget=6000",
               "--dump-dom", SITE.as_uri() + "?langtest"]
        r = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=120, errors="replace")
        m = re.search(r'data-langtest="([^"]*)"', r.stdout)
        if not m:
            _LANG_CACHE = None
            return None
        _LANG_CACHE = json.loads(html_mod.unescape(m.group(1).split(" ", 1)[1]))
        return _LANG_CACHE


_LANG_CACHE = None


def _run_rv_dump():
    """直接 dump-dom 站点（主 frame）。headless 虚拟时间下 iframe 内的
    IntersectionObserver 不触发、主 frame 会触发，故 .rv 显现测试单独跑。"""
    global _RV_CACHE
    if _RV_CACHE is not None:
        return _RV_CACHE
    exe = chrome_path()
    if not exe:
        _RV_CACHE = None
        return None
    with tempfile.TemporaryDirectory(prefix="esp32rv_") as td:
        cmd = [exe, "--headless=new", "--disable-gpu",
               f"--user-data-dir={td}",
               "--window-size=1280,2600",   # 高视口：首批 .rv 落进初始视口
               "--virtual-time-budget=10000", "--dump-dom", SITE.as_uri()]
        r = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=180, errors="replace")
        out = r.stdout
        rv = re.findall(r'class="[^"]*\brv\b[^"]*"', out)
        data = {
            "rv_total": len(rv),
            "rv_in": len([c for c in rv
                          if re.search(r"(^| )in( |$)", c.strip('"'))]),
            "rv_delayed": len(re.findall(
                r'style="[^"]*transition-delay[^"]*"[^>]*class="[^"]*\brv\b'
                r'|class="[^"]*\brv\b[^"]*"[^>]*style="[^"]*transition-delay', out)),
        }
        _RV_CACHE = data
        return data


_RV_CACHE = None


@unittest.skipUnless(chrome_path(), "本机无 Chrome，跳过运行时测试")
class TestRuntime(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.R, cls.console = _run_harness()

    def _skip_if_no_results(self):
        if self.R is None:
            self.skipTest("harness 未产出 PROBE（Chrome 失败或 JSON 解析失败）")

    def test_harness_completed(self):
        self._skip_if_no_results()
        self.assertGreater(len(self.R.get("checks", {})), 15, "harness 步骤未全部执行")

    def test_no_js_errors(self):
        self._skip_if_no_results()
        self.assertEqual(self.R["js_errors"], [], f"页面 JS 异常: {self.R['js_errors']}")
        self.assertEqual(self.console or [], [],
                         f"Chrome 控制台错误: {(self.console or [])[:3]}")

    def test_lang_restore_from_localstorage(self):
        self._skip_if_no_results()
        c = self.R["checks"]
        self.assertTrue(c.get("storage_readback"), "localStorage 写入/读回失败")
        self.assertTrue(c.get("restore_en"), "预置 esp32-lang=en 后未恢复英文")
        self.assertTrue(c.get("restore_title_en"), "恢复英文后 <title> 不是英文")

    def test_switch_back_to_zh(self):
        self._skip_if_no_results()
        c = self.R["checks"]
        self.assertTrue(c.get("switch_back_zh"))
        self.assertTrue(c.get("title_zh"))

    def test_all_l10n_keys_have_en_blocks_runtime(self):
        self._skip_if_no_results()
        self.assertTrue(self.R["checks"].get("all_l10n_in_b"),
                        f"缺块翻译: {self.R['lists'].get('missing_block_keys')}")

    def test_text_node_coverage(self):
        self._skip_if_no_results()
        self.assertTrue(self.R["checks"].get("text_coverage"),
                        f"未覆盖 CJK 文本节点（英文下仍是中文）: "
                        f"{self.R['lists'].get('uncovered_text')}")
        self.assertGreater(self.R["counts"].get("cjk_text_nodes", 0), 100)

    def test_anchors_resolve_runtime(self):
        self._skip_if_no_results()
        self.assertTrue(self.R["checks"].get("anchors_ok"),
                        f"死锚点: {self.R['lists'].get('dead_anchors')}")

    def test_structure_runtime(self):
        self._skip_if_no_results()
        self.assertEqual(self.R["counts"].get("h1"), 1)
        self.assertEqual(self.R["counts"].get("sections"), 14)

    def test_rv_reveal(self):
        """滚动显现：harness iframe 内 IO 在 headless 虚拟时间下不触发，
        故走主 frame 直接 dump-dom（高视口让首批 .rv 落进初始视口）。"""
        rv = _run_rv_dump()
        if rv is None:
            self.skipTest("本机无 Chrome")
        self.assertEqual(rv["rv_total"], 36)
        self.assertGreater(rv["rv_delayed"], 0,
                           "滚动显现脚本未给 .rv 设置 transitionDelay")
        self.assertGreater(rv["rv_in"], 0,
                           "视口内 .rv 未获得 .in 类（IntersectionObserver 未触发）")

    def test_no_horizontal_overflow(self):
        self._skip_if_no_results()
        self.assertLessEqual(self.R["counts"].get("overflow_390", 9999), 395,
                             "390px 视口横向溢出")
        self.assertLessEqual(self.R["counts"].get("overflow_1280", 9999), 1285,
                             "1280px 视口横向溢出")

    def test_wizard_decisions(self):
        self._skip_if_no_results()
        c = self.R["checks"]
        self.assertTrue(c.get("wz_learn"), "决策器 learn 应推荐 S3-DevKitC")
        self.assertTrue(c.get("wz_mass_trap"), "量产路径缺认证模组提醒")
        self.assertTrue(c.get("wz_battery_need_c6"), "H2+需要蓝牙应改推 C6")
        self.assertTrue(c.get("wz_bigdisp_p4"), "大屏应推 P4 且提示无射频")

    def test_chip_filter(self):
        self._skip_if_no_results()
        c = self.R["counts"]
        self.assertEqual(c.get("chip_rows"), 11)
        self.assertEqual(c.get("chip_all_visible"), 11)
        self.assertLess(c.get("chip_c_visible", 99), 11)
        self.assertTrue(self.R["checks"].get("chip_filter_c"))
        self.assertTrue(self.R["checks"].get("chip_filter_reset"))

    def test_video_filter(self):
        self._skip_if_no_results()
        self.assertEqual(self.R["counts"].get("vid_cards"), 10)
        self.assertTrue(self.R["checks"].get("vid_filter_idf"))
        self.assertTrue(self.R["checks"].get("vid_filter_changed"), "idf 筛选后可见数应减少")
        self.assertTrue(self.R["checks"].get("vid_filter_reset"))

    def test_res_search_and_filter(self):
        self._skip_if_no_results()
        self.assertEqual(self.R["counts"].get("res_items"), 26)
        self.assertTrue(self.R["checks"].get("res_search_hit"))
        self.assertTrue(self.R["checks"].get("res_search_miss"))
        self.assertTrue(self.R["checks"].get("res_filter_tool"))

    def test_buy_filter(self):
        self._skip_if_no_results()
        self.assertTrue(self.R["checks"].get("buy_filter_sensor"))
        self.assertTrue(self.R["checks"].get("buy_filter_reset"))

    def test_copy_button(self):
        self._skip_if_no_results()
        self.assertTrue(self.R["checks"].get("copy_button"),
                        f"复制按钮点击后状态异常: {self.R['lists'].get('copy_btn_text')}")

    def test_en_translation_sample(self):
        self._skip_if_no_results()
        c = self.R["checks"]
        self.assertTrue(c.get("en_doc_lang"))
        self.assertTrue(c.get("en_ai_sub_no_cjk"), "切英文后 #ai 简介仍含中文")

    def test_i18n_dict_sizes_runtime(self):
        self._skip_if_no_results()
        self.assertGreater(self.R["counts"].get("i18n_t", 0), 100)
        self.assertGreater(self.R["counts"].get("i18n_b", 0), 50)


# ================================================================ C. 在线

class TestLive(unittest.TestCase):
    """--live 或 ALIYUN_LIVE=1 时启用。全部只读。"""

    @classmethod
    def setUpClass(cls):
        if not (LIVE := "--live" in sys.argv or os.environ.get("ALIYUN_LIVE") == "1"):
            raise unittest.SkipTest("跳过在线冒烟（加 --live 启用）")
        import requests
        cls.sess = requests.Session()
        cls.sess.trust_env = False  # 绕过本地代理污染
        r = cls.sess.get(LIVE_URL, timeout=60)
        cls.resp = r

    def test_https_200(self):
        self.assertEqual(self.resp.status_code, 200)
        self.assertIn("text/html", self.resp.headers.get("Content-Type", ""))

    def test_bytes_match_local(self):
        self.assertEqual(len(self.resp.content), SITE.stat().st_size,
                         "线上字节数与本地不一致——站点未重新部署？")

    def test_content_markers(self):
        body = self.resp.text
        for marker in ("大模型 Agent", "采购清单", "data-l10n", "langSw"):
            self.assertIn(marker, body)

    def test_live_l10n_count(self):
        self.assertEqual(len(re.findall(r'data-l10n="', self.resp.text)),
                         len(re.findall(r'data-l10n="', SRC)),
                         "线上 data-l10n 数量与本地不一致")


class TestMultiLang(unittest.TestCase):
    """9 语言运行时自检：标题、正文块、语言集合。"""

    def setUp(self):
        self.R = _run_langtest()
        if self.R is None:
            self.skipTest("?langtest 未产出 LANGS 结果")

    def test_nine_language_codes(self):
        self.assertEqual([x[0] for x in self.R],
                         ["zh-CN", "en", "zh-TW", "ja", "ko", "es", "pt", "fr", "ru"])

    def test_titles_translated(self):
        bad = [x[0] for x in self.R
               if x[0] != "zh-CN" and (not x[1] or x[1].startswith("ESP32 全景手册"))]
        self.assertEqual(bad, [], f"未翻译的标题: {bad}")

    def test_blocks_no_cjk_residue(self):
        # 日语正文用汉字属正常，只有纯表音语言要求零 CJK 残留
        bad = [x[0] for x in self.R
               if x[0] not in ("zh-CN", "zh-TW", "ja") and x[2]]
        self.assertEqual(bad, [], f"非中文语言仍有中文正文: {bad}")


if __name__ == "__main__":
    unittest.main(verbosity=2, argv=[sys.argv[0]])
