#!/usr/bin/env python3
"""把 three.js 3D 板子模块打包成 IIFE 并内联进单文件 lab/index.html。
可重复运行：只替换 BOARD3D_BUNDLE 标记之间的内容。
用法：python tools/build_3d.py
"""
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAGE = HERE.parent / "index.html"
SRC = HERE / "board3d.js"
OUT = HERE / "_board3d.bundle.js"
START = "<!-- BOARD3D_BUNDLE:START -->"
END = "<!-- BOARD3D_BUNDLE:END -->"


def bundle():
    esbuild = HERE / "node_modules" / ".bin" / ("esbuild.cmd" if (HERE / "node_modules/.bin/esbuild.cmd").exists() else "esbuild")
    cmd = [str(esbuild), str(SRC), "--bundle", "--minify", "--format=iife",
           "--target=es2020", f"--outfile={OUT}", "--log-level=warning"]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(HERE))
    if r.returncode:
        raise SystemExit("esbuild failed: " + r.stderr[:1000])
    return OUT.read_text(encoding="utf-8")


def main():
    js = bundle()
    # 防止内联脚本被 </script> 提前截断
    js = re.sub(r"</script", r"<\\/script", js, flags=re.I)
    block = START + "\n<script>\n" + js + "\n</script>\n" + END

    src = PAGE.read_text(encoding="utf-8")
    if START in src and END in src:
        a = src.index(START)
        b = src.index(END) + len(END)
        src = src[:a] + block + src[b:]
        action = "replaced"
    else:
        marker = "<script>\n"
        i = src.index(marker)
        src = src[:i] + block + "\n" + src[i:]
        action = "inserted"
    with open(PAGE, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print(f"3D bundle {action}: {len(js.encode('utf-8'))} bytes JS; "
          f"page {PAGE.stat().st_size} bytes")


if __name__ == "__main__":
    main()
