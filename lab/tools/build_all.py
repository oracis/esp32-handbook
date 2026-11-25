#!/usr/bin/env python3
"""把 3D 模块与工作台解释器打包成 IIFE 并内联进 lab/index.html。
可重复运行：只替换各自 marker 之间的内容。
用法：python tools/build_all.py
"""
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAGE = HERE.parent / "index.html"
ESBUILD = HERE / "node_modules" / ".bin" / (
    "esbuild.cmd" if (HERE / "node_modules/.bin/esbuild.cmd").exists() else "esbuild")

MODULES = [
    ("board3d.js", "_board3d.bundle.js", "<!-- BOARD3D_BUNDLE:START -->", "<!-- BOARD3D_BUNDLE:END -->",
     "window.Board3D"),
    ("workbench.js", "_wb.bundle.js", "<!-- WORKBENCH_BUNDLE:START -->", "<!-- WORKBENCH_BUNDLE:END -->",
     "window.Workbench"),
]


def bundle(src_name, out_name, probe):
    out = HERE / out_name
    cmd = [str(ESBUILD), str(HERE / src_name), "--bundle", "--minify", "--format=iife",
           "--target=es2020", f"--outfile={out}", "--log-level=warning"]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(HERE))
    if r.returncode:
        raise SystemExit(f"esbuild {src_name} failed: {r.stderr[:800]}")
    js = out.read_text(encoding="utf-8")
    if probe not in js:
        raise SystemExit(f"{src_name}: bundle missing {probe}")
    return re.sub(r"</script", r"<\\/script", js, flags=re.I)


def main():
    src = PAGE.read_text(encoding="utf-8")
    for src_name, out_name, start, end, probe in MODULES:
        js = bundle(src_name, out_name, probe)
        block = start + "\n<script>\n" + js + "\n</script>\n" + end
        if start in src and end in src:
            a, b = src.index(start), src.index(end) + len(end)
            src = src[:a] + block + src[b:]
            action = "replaced"
        else:
            marker = "<script>\n"
            i = src.index(marker)
            src = src[:i] + block + "\n" + src[i:]
            action = "inserted"
        print(f"{src_name}: {action}, {len(js.encode())} bytes JS")
    with open(PAGE, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print(f"page {PAGE.stat().st_size} bytes")


if __name__ == "__main__":
    main()
