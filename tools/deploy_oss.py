# -*- coding: utf-8 -*-
"""把两个站点推到阿里云 OSS（香港），并在推之前留线上旧版备份。

    python tools/deploy_oss.py            # 双站
    python tools/deploy_oss.py --main     # 只主站
    python tools/deploy_oss.py --lab      # 只实验室

凭据取环境变量 ALIBABA_CLOUD_ACCESS_KEY_ID / ALIBABA_CLOUD_ACCESS_KEY_SECRET。
上传前清空 http(s)_proxy —— 本机代理会让 oss2 的 SSL 握手偶发超时。
"""
import datetime
import hashlib
import os
import sys

import oss2

REGION = "cn-hongkong"
ENDPOINT = "https://oss-cn-hongkong.aliyuncs.com"
BACKUP = ".workbuddy/backups/oss"
# 两个桶的对象键都是根目录的 index.html；本地文件路径与键不同，单独给出
TARGETS = {
    "main": ("esp32-handbook-hk", "index.html", "index.html"),
    "lab": ("esp32-lab-hk", "index.html", "lab/index.html"),
}
HEADERS = {
    "Content-Type": "text/html; charset=utf-8",
    "Cache-Control": "public, max-age=300",
}


def md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def main():
    only = [a.lstrip("-") for a in sys.argv[1:] if a.startswith("--")]
    names = [n for n in TARGETS if not only or n in only]
    if not names:
        print("没有匹配的目标，可选：--main / --lab")
        return 1

    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY",
              "all_proxy", "ALL_PROXY"):
        os.environ.pop(k, None)

    auth = oss2.Auth(os.environ["ALIBABA_CLOUD_ACCESS_KEY_ID"],
                     os.environ["ALIBABA_CLOUD_ACCESS_KEY_SECRET"])
    os.makedirs(BACKUP, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    bad = 0

    for name in names:
        bucket_name, key, local = TARGETS[name]
        if not os.path.exists(local):
            print("!! 本地文件不存在:", local)
            bad += 1
            continue
        b = oss2.Bucket(auth, ENDPOINT, bucket_name)

        # 1) 备份线上旧版
        try:
            old = b.get_object(key).read()
            bak = os.path.join(BACKUP, "%s.%s.%s" % (bucket_name, stamp, os.path.basename(key)))
            open(bak, "wb").write(old)
            print(" - 线上旧版已备份 %.0f KB → %s" % (len(old) / 1024, bak))
        except oss2.exceptions.NoSuchKey:
            print(" - 线上无旧版（首次部署）")

        # 2) 上传
        local_md5 = md5(local)
        b.put_object_from_file(key, local, headers=HEADERS)

        # 3) 回读校验
        back = b.get_object(key).read()
        remote_md5 = hashlib.md5(back).hexdigest()
        size = os.path.getsize(local)
        ok = remote_md5 == local_md5
        print("%s %-16s %s  %8.0f KB  md5 %s" % ("OK " if ok else "BAD",
                                                 bucket_name, key, size / 1024, remote_md5[:12]))
        if not ok:
            bad += 1
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
