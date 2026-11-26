# -*- coding: utf-8 -*-
"""在 #support 里加一块「请我喝咖啡」：Ko-fi 按钮 + 内嵌微信收款码。

设计取舍：
- 二维码以 base64 内嵌，保持 index.html 单文件可离线打开（站点自称「无外部依赖」）；
- 原图字节不改，避免重编码把支付码搞花；
- 白底 + 内边距交给 CSS，深色主题下就是一格白色卡片；
- 幂等：已有 .sup-tip 就只跳过结构替换，重复执行不会叠加。

用法：
    python tools/add_tip_block.py            # 写入
    python tools/add_tip_block.py --dry      # 只检查
"""
import base64
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "index.html")
QR = os.path.expandvars(
    r"%USERPROFILE%\.workbuddy\clipboard-images"
    r"\clipboard-2026-11-26T07-14-13-090Z-4ed0a6b6.png")

OLD_NOTE = (
    '    <p class="sup-note" data-l10n="SP11">'
    '打赏通道还没开，开了会挂在这里。在那之前，一个 Star 或一条具体的问题，比打赏更有用。</p>\n'
)

BLOCK = '''    <div class="sup-tip">
      <div class="sup-tip-main">
        <h3 data-l10n="SP11">请我喝一杯咖啡</h3>
        <p data-l10n="SP12">手册免费、也没有广告。如果它帮你少踩了一个坑，可以请我喝杯咖啡：海外走 Ko-fi，国内扫码都行。</p>
        <a class="sup-btn" href="https://ko-fi.com/robinzhou" target="_blank" rel="noopener" data-l10n="SP13">去 Ko-fi</a>
      </div>
      <figure class="sup-qr">
        <img src="__QR__" width="344" height="341" alt="微信收款二维码">
        <figcaption data-l10n="SP14">微信扫码 · 或长按识别</figcaption>
      </figure>
    </div>
    <p class="sup-note" data-l10n="SP15">打赏完全自愿，不影响内容的取舍。手机端可以长按二维码识别，海外读者用 Ko-fi。</p>
'''

CSS_ANCHOR = ".sup-note{margin:20px 0 0;font-size:12.6px;color:var(--muted);text-wrap:pretty}\n"

CSS_ADD = """/* 打赏：Ko-fi + 微信收款码 */
.sup-tip{display:grid;grid-template-columns:1fr auto;gap:26px;align-items:center;margin-top:14px;padding:20px 24px;border:1px solid var(--line);border-radius:var(--r);background:var(--panel)}
@media(max-width:700px){.sup-tip{grid-template-columns:1fr;gap:18px;justify-items:start}}
.sup-tip-main h3{margin:0 0 7px;font-size:15.5px;font-weight:650;color:var(--text)}
.sup-tip-main p{margin:0 0 13px;font-size:13.2px;line-height:1.65;color:var(--muted);max-width:54ch}
.sup-tip-main .sup-btn{margin-top:0}
.sup-qr{margin:0;display:flex;flex-direction:column;align-items:center;gap:7px;flex:none}
.sup-qr img{display:block;width:158px;height:auto;padding:7px;border-radius:11px;background:#fff;border:1px solid var(--line-soft)}
.sup-qr figcaption{font-family:var(--mono);font-size:11.2px;color:var(--muted);letter-spacing:.01em}
"""


def main():
    dry = "--dry" in sys.argv
    src = io.open(SITE, encoding="utf-8").read()

    has_tip = 'class="sup-tip"' in src
    has_css = ".sup-tip{display:grid" in src
    if has_tip and has_css:
        print("已存在 .sup-tip 与对应 CSS，无需改动。")
        return 0
    if not os.path.exists(QR):
        print("!! 找不到二维码图片：%s" % QR)
        return 1

    if not has_tip:
        assert src.count(OLD_NOTE) == 1, "SP11 备注段没找到或不唯一：%d" % src.count(OLD_NOTE)
    if not has_css:
        assert src.count(CSS_ANCHOR) == 1, "CSS 锚点不唯一"

    raw = open(QR, "rb").read()
    uri = "data:image/png;base64," + base64.b64encode(raw).decode("ascii")
    print("二维码 %d 字节 → base64 %.1f KB" % (len(raw), len(uri) / 1024.0))

    new = src
    if not has_css:
        new = new.replace(CSS_ANCHOR, CSS_ANCHOR + CSS_ADD, 1)
    if not has_tip:
        new = new.replace(OLD_NOTE, BLOCK.replace("__QR__", uri), 1)

    print("index.html %d → %d 字节 (+%.1f KB)"
          % (len(src.encode()), len(new.encode()),
             (len(new.encode()) - len(src.encode())) / 1024.0))
    if dry:
        print("dry run，不写入。")
        return 0
    io.open(SITE, "w", encoding="utf-8", newline="\n").write(new)

    back = io.open(SITE, encoding="utf-8").read()
    ok = ('class="sup-tip"' in back and ".sup-tip{display:grid" in back
          and "https://ko-fi.com/robinzhou" in back and uri[:80] in back)
    print("回读校验：%s" % ("OK" if ok else "FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
