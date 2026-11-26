# -*- coding: utf-8 -*-
"""截一张 #support 的图，方便人工看版式。

做法：复制 index.html，末尾追加一段脚本删掉其它 section 与页头页脚，
再用 Chrome headless 截图。语言用 --lang=xx 覆盖，视口用 --box=宽,高。
截图写到 .workbuddy/shots/（已在 .gitignore 里）。
"""
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "index.html")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not os.path.exists(CHROME):
    CHROME = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")

KILL = """
<script>
(function(){
  var keep = document.getElementById('support');
  Array.prototype.forEach.call(document.querySelectorAll('main > section'), function(el){
    if(el !== keep) el.parentNode.removeChild(el);
  });
  Array.prototype.forEach.call(document.querySelectorAll('body > nav, body > header, body > footer, .topbar, .langBox'), function(el){
    el.parentNode.removeChild(el);
  });
  if(keep) keep.scrollIntoView();
})();
</script>
"""


def main():
    lang = "zh-CN"
    scale = "1"
    box = "1180,1150"
    for a in sys.argv[1:]:
        if a.startswith("--lang="):
            lang = a.split("=", 1)[1]
        if a.startswith("--scale="):
            scale = a.split("=", 1)[1]
        if a.startswith("--box="):
            box = a.split("=", 1)[1]
    src = open(SITE, encoding="utf-8").read()
    if lang != "zh-CN":
        src = src.replace(
            "var saved='zh-CN';\n  try{ saved=localStorage.getItem(KEY)||'zh-CN'; }catch(e){}",
            "var saved='%s';" % lang, 1)
    src = src.replace("</body>", KILL + "</body>", 1)
    tmp = tempfile.mkdtemp(prefix="sup_shot_")
    f = os.path.join(tmp, "shot.html")
    open(f, "w", encoding="utf-8", newline="\n").write(src)
    shotdir = os.path.join(ROOT, ".workbuddy", "shots")
    os.makedirs(shotdir, exist_ok=True)
    out = os.path.join(shotdir, "support_%s_%s.png" % (lang.replace("/", "_"), box.replace(",", "x")))
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=" + scale,
                    "--virtual-time-budget=5000", "--window-size=" + box,
                    "--screenshot=" + out, "file:///" + f.replace("\\", "/")],
                   capture_output=True, timeout=180)
    print(out, os.path.getsize(out) if os.path.exists(out) else "MISSING")


if __name__ == "__main__":
    main()
