#!/usr/bin/env python3
"""逐屏/整页截图工具：用本机 Chrome headless，无需 Playwright。
用法: python shot_pages.py <html> [--full] [--mobile]
"""
import subprocess, sys, os, re
from pathlib import Path

CHROME = r"C://Program Files//Google//Chrome//Application//chrome.exe"

def shot(src, out, w=1440, h=900, full=False):
    src = Path(src).resolve()
    out = Path(out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
           "--force-device-scale-factor=1",
           f"--user-data-dir=/tmp/hdshot_{abs(hash(str(out))) % 100000}",
           f"--window-size={w},{h}"]
    if full:
        # 先用 JS 读取页面高度，再用高视口整页截
        cmd.append("--virtual-time-budget=2000")
    cmd += [f"--screenshot={out}", src.as_uri()]
    subprocess.run(cmd, capture_output=True, timeout=120)
    return out.exists() and out.stat().st_size > 1000

if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: sys.exit("usage: shot_pages.py <html> [--full] [--mobile]")
    src = a[0]
    full = "--full" in a
    mobile = "--mobile" in a
    w, h = (390, 844) if mobile else (1440, 900)
    if full: h = 9000
    out = str(Path(src).with_suffix("")) + ("-mobile" if mobile else "-full" if full else "-hero") + ".png"
    print("OK" if shot(src, out, w, h, full) else "FAIL", out, Path(out).stat().st_size if Path(out).exists() else 0)
