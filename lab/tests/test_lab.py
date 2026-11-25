#!/usr/bin/env python3
"""lab 虚拟实验室自动化自测。
用法:
  python tests/test_lab.py            # 离线全量（页面内嵌 e2e/audit 钩子驱动）
  python tests/test_lab.py --live URL # 额外跑线上冒烟
钩子说明：页面在 ?audit / ?play / ?e2e=<mode> 下把结果写进 <title>，
本脚本用本机 Chrome headless dump-dom 读回断言；正式访问零影响。
"""
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"
LOCAL = (ROOT / "index.html").resolve().as_uri()
LIVE = None

CASES = {
    "audit":    dict(budget=3000, w=1440, h=900, expect=lambda R: (
        R["sw"] == R["iw"], R["parts"] == 12, R["over"] == [],
        R["board"][0] > 600, R["serialH"] > 100, R["codeH"] > 100)),
    "audit-m":  dict(budget=3000, w=500, h=844, expect=lambda R: (
        R["sw"] == R["iw"], R["over"] == [],
        R["sh"] > R["ih"], R["parts"] == 12)),
    "play":     dict(budget=8000, w=1440, h=900, expect=lambda R: (
        R["lines"] >= 4, R["led"] is True, R["running"] is True)),
    "e2e=l1":  dict(budget=4000, w=1440, h=900, expect=lambda R: (
        R["fn"] == "lesson_1.ino", R["tabs"] == 3, R["lines1s"] >= 2,
        R["noise"] is True, "err" not in R)),
    "e2e=l2":  dict(budget=8000, w=1440, h=900, expect=lambda R: (
        R["ledAt"] is True, R["lines"] >= 2, R["running"] is True, "err" not in R)),
    "e2e=l3":  dict(budget=8000, w=1440, h=900, expect=lambda R: (
        R["fn"] == "lesson_3.ino", R["inputShown"] is True,
        R["echoFound"] is True, R["txFound"] is True, R["lines"] >= 4, "err" not in R)),
    "e2e=pop":  dict(budget=4000, w=1440, h=900, expect=lambda R: (
        R["popShow"] is True, R["popT"] == "USB 转串口芯片",
        R["popLen"] > 20, R["popHidden"] is True, "err" not in R)),
    "e2e=tabs": dict(budget=4000, w=1440, h=900, expect=lambda R: (
        R["wire"] is True, R["pins"] == 3, R["points"] == 4, "err" not in R)),
    "e2e=zoom": dict(budget=4000, w=1440, h=900, expect=lambda R: (
        R["zoom"] != "100%", "scale(" in R["tf"], R["reset"] == "100%", "err" not in R)),
}

_cache = {}


def run_case(q, budget, w, h, base=None):
    base = base or LOCAL
    key = (q, w, base)
    if key in _cache:
        return _cache[key]
    uri = base + ("&" if "?" in base else "?") + q
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
           "--force-device-scale-factor=1", f"--window-size={w},{h}",
           f"--virtual-time-budget={budget}", "--dump-dom", uri]
    p = subprocess.run(cmd, capture_output=True, timeout=180)
    dom = p.stdout.decode("utf-8", "ignore")
    m = re.search(r"<title>(.*?)</title>", dom)
    title = m.group(1) if m else ""
    if not (title.startswith("AUDIT ") or title.startswith("PLAY ") or title.startswith("E2E ")):
        raise AssertionError(
            f"用例 {q} 未返回自检结果（title={title[:60] or '空'}，"
            f"data-err={bool(re.search(r'<body[^>]*data-err', dom))}）")
    R = json.loads(title.split(" ", 1)[1])
    _cache[key] = R
    return R


class TestLab(unittest.TestCase):
    """离线：页面内嵌钩子驱动的全场景自测"""


def _mk(name, cfg):
    def fn(self):
        R = run_case(name, cfg["budget"], cfg["w"], cfg["h"])
        for ok in cfg["expect"](R):
            self.assertTrue(ok, f"{name} 失败: {json.dumps(R, ensure_ascii=False)}")
    fn.__name__ = "test_" + name.replace("=", "_")
    setattr(TestLab, fn.__name__, fn)


for _name, _cfg in CASES.items():
    _mk(_name, _cfg)


class TestLive(unittest.TestCase):
    """--live URL 时才跑：线上审计 + 第 1 课播放 + 第 3 课串口回显"""

    def _live(self):
        if not LIVE:
            self.skipTest("需要 --live URL")
        return LIVE

    def test_live_audit(self):
        R = run_case("audit", 4000, 1440, 900, self._live())
        self.assertEqual(R["parts"], 12)
        self.assertEqual(R["over"], [])
        self.assertGreater(R["board"][0], 600)

    def test_live_play(self):
        R = run_case("play", 8000, 1440, 900, self._live())
        self.assertTrue(R["led"] is True, R)
        self.assertGreaterEqual(R["lines"], 4)

    def test_live_echo(self):
        R = run_case("e2e=l3", 8000, 1440, 900, self._live())
        self.assertTrue(R["echoFound"], R)


if __name__ == "__main__":
    argv = [sys.argv[0], "-v"]
    if "--live" in sys.argv:
        i = sys.argv.index("--live")
        LIVE = sys.argv[i + 1]
    unittest.main(argv=argv)
