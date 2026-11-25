# -*- coding: utf-8 -*-
"""给主站加「支持这个项目」区块，并把页脚改成参考站 esppdeck 的形态。

参考对象：https://espdeck.pixzens.com/support + 全站 footer
    <footer class="site-footer">
      <nav class="site-footer-nav">About Guide Support Terms Privacy</nav>
      <p>© 2026 ESPDeck · Open the page. Get hands-on with ESP32.</p>
    </footer>
结构照搬（极简导航 + 版权行贴底居中），配色/字体沿用本站深色变量；
渠道换成我们真实拥有的：GitHub 仓库 + Discussions。参考站的 Ko-fi / 微信赞赏码
是那位开发者的账号，不能照抄；我们的赞赏通道未开通，文案如实说明。

幂等：重复执行不会重复插入区块或叠加样式。
"""
import io
import re
import sys

SITE = "index.html"

# ---------- 1. CSS ----------

OLD_CSS = """footer{border-top:1px solid var(--line-soft);margin-top:70px;padding:30px 0 40px}
.foot-in{max-width:var(--maxw);margin:0 auto;padding:0 22px;display:flex;gap:20px;flex-wrap:wrap;justify-content:space-between;font-size:12.5px;color:var(--muted)}"""

NEW_CSS = """/* 支持区块：结构参考 espdeck.pixzens.com/support，配色用本站变量 */
.sup-lead{color:var(--text-2);font-size:14.5px;margin:10px 0 26px;max-width:74ch}
.sup-ways{display:grid;grid-template-columns:1fr 1fr;gap:14px}
@media(max-width:820px){.sup-ways{grid-template-columns:1fr}}
.sup-card{background:var(--panel);border:1px solid var(--line);border-radius:var(--r);padding:20px 22px;display:flex;flex-direction:column;align-items:flex-start;gap:9px}
.sup-card h3{margin:0;font-size:15.5px;font-weight:650;color:var(--text)}
.sup-card p{margin:0;font-size:13.2px;line-height:1.65;color:var(--muted)}
.sup-btn{display:inline-flex;align-items:center;gap:6px;margin-top:4px;padding:8px 15px;border-radius:9px;background:var(--red);color:#fff;font-size:13px;font-weight:650;text-decoration:none;border:1px solid transparent;transition:background .18s}
.sup-btn:hover{background:var(--red-dim)}
.sup-btn.ghost{background:transparent;border-color:var(--line);color:var(--text-2)}
.sup-btn.ghost:hover{border-color:var(--red);color:var(--text);background:transparent}
.sup-list{margin:26px 0 0;padding-left:1.15em;color:var(--text-2);font-size:14px;line-height:1.85}
.sup-list li+li{margin-top:7px}
.sup-list b{color:var(--text);font-weight:650}
.sup-note{margin:20px 0 0;font-size:12.6px;color:var(--muted);max-width:74ch}

footer{border-top:1px solid var(--line-soft);margin-top:70px;padding:28px 0 34px}
.foot-in{max-width:var(--maxw);margin:0 auto;padding:0 22px;display:flex;flex-direction:column;align-items:center;gap:11px;text-align:center}
.foot-nav{display:flex;flex-wrap:wrap;justify-content:center;gap:7px 18px}
.foot-nav a{color:var(--text-2);font-size:12.5px;font-weight:600;text-decoration:none}
.foot-nav a:hover{color:var(--red)}
.foot-copy{margin:0;font-family:var(--mono);font-size:11px;line-height:1.7;letter-spacing:.03em;color:var(--muted)}
.foot-legal{margin:0;font-size:11.5px;line-height:1.7;color:var(--muted);opacity:.85;max-width:68ch}"""

# ---------- 2. 支持区块 ----------

SECTION = """  <!-- ============ 13 支持 ============ -->
  <section id="support">
    <div class="sec-head"><span class="sec-num">13</span><h2 data-l10n="SP1">支持这个项目</h2></div>
    <p class="sup-lead" data-l10n="SP2">这本手册没有广告、没有登录墙、也没有课程锁，由一个人整理和维护。如果它帮你省下了几个晚上的试错，下面两件事都算支持。</p>
    <div class="sup-ways">
      <div class="sup-card">
        <h3 data-l10n="SP3">给仓库点个 Star</h3>
        <p data-l10n="SP4">不花钱，但决定下一个搜 ESP32 的人能不能找到这里。点过 Star 之后，每次修订也会出现在你的 GitHub 首页。</p>
        <a class="sup-btn" href="https://github.com/oracis/esp32-handbook" target="_blank" rel="noopener" data-l10n="SP5">去 GitHub</a>
      </div>
      <div class="sup-card">
        <h3 data-l10n="SP6">提问、报错、催更</h3>
        <p data-l10n="SP7">表格里的参数不对、链接失效，或者你的实测结果不一样，直接说。每条反馈都会变成下一次修订。</p>
        <a class="sup-btn ghost" href="https://github.com/oracis/esp32-handbook/discussions" target="_blank" rel="noopener" data-l10n="SP8">去 Discussions</a>
      </div>
    </div>
    <ul class="sup-list">
      <li data-l10n="SP9"><b>更多内容</b> —— 把更多 ESP32 场景做成能点、能跳过的实验。</li>
      <li data-l10n="SP10"><b>站点一直在线</b> —— 域名、托管，以及弱网也能打开的体积。</li>
    </ul>
    <p class="sup-note" data-l10n="SP11">打赏通道还没开，开了会挂在这里。在那之前，一个 Star 或一条具体的问题，比打赏更有用。</p>
  </section>
"""

# ---------- 3. 页脚 ----------

FOOTER = """<footer>
  <div class="foot-in">
    <nav class="foot-nav" aria-label="页脚导航">
      <a href="#top" data-l10n="FT1">回到顶部</a>
      <a href="lab/" data-l10n="FT2">实验区</a>
      <a href="#support" data-l10n="FT3">支持</a>
      <a href="https://github.com/oracis/esp32-handbook/discussions" target="_blank" rel="noopener" data-l10n="FT4">反馈</a>
      <a href="https://github.com/oracis/esp32-handbook" target="_blank" rel="noopener">GitHub</a>
    </nav>
    <p class="foot-note" data-l10n="FT8">板子会换，判据不变：先问「要连什么」，再问「要多快」。</p>
    <p class="foot-copy">© 2026 <span data-l10n="FT5">ESP32 全景手册</span> · oracis · <span data-l10n="FT6">静态单页，无外部依赖</span></p>
    <p class="foot-legal" data-l10n="FT7">非官方个人项目，与 Espressif 无隶属关系；电气参数与型号命名以官方 datasheet 为准。</p>
  </div>
</footer>"""


def main():
    src = io.open(SITE, encoding="utf-8").read()
    orig = src
    report = []

    # CSS
    if NEW_CSS in src:
        report.append("CSS 已是新版，跳过")
    elif OLD_CSS in src:
        src = src.replace(OLD_CSS, NEW_CSS, 1)
        report.append("CSS 已替换")
    else:
        print("!! 找不到旧版 footer CSS，中止（请核对 index.html 是否被改过）")
        return 1

    # 支持区块
    if 'id="support"' in src:
        report.append("支持区块已存在，跳过")
    else:
        anchor = "\n</main>\n"
        if src.count(anchor) != 1:
            print("!! </main> 锚点不唯一: %d" % src.count(anchor))
            return 1
        src = src.replace(anchor, "\n" + SECTION + "</main>\n", 1)
        report.append("支持区块已插入")

    # 页脚
    m = re.search(r"<footer>[\s\S]*?</footer>", src)
    if not m:
        print("!! 找不到 <footer> 块")
        return 1
    if m.group(0) == FOOTER:
        report.append("页脚已是新版，跳过")
    else:
        src = src[:m.start()] + FOOTER + src[m.end():]
        report.append("页脚已替换")

    if src == orig:
        print("无改动")
    else:
        io.open(SITE, "w", encoding="utf-8", newline="\n").write(src)
    for r in report:
        print(" -", r)
    print("行数 %d → %d，字节 %d → %d" % (orig.count("\n"), src.count("\n"),
                                          len(orig.encode()), len(src.encode())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
