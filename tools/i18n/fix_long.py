#!/usr/bin/env python3
"""补翻超长 HTML 块：按行拆开逐行翻译，再合并写回缓存与字典。"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build


def main():
    cache = build.load_cache()
    _, _, items = build.collect()
    for lang in build.LANGS:
        bucket = cache.setdefault(lang, {})
        todo = [t for _, _, t in items if t not in bucket]
        if not todo:
            continue
        print(lang, "todo", len(todo), flush=True)
        for text in todo:
            lines = text.split("\n")
            results = [None] * len(lines)
            with ThreadPoolExecutor(max_workers=6) as ex:
                futs = {ex.submit(build.translate_one, ln, lang): i
                        for i, ln in enumerate(lines) if ln.strip()}
                for f in as_completed(futs):
                    i = futs[f]
                    try: results[i] = f.result()
                    except Exception as e:
                        print("   line fail", i, str(e)[:70], flush=True)
                        results[i] = lines[i]
            for i, ln in enumerate(lines):
                if results[i] is None:
                    results[i] = ln
            bucket[text] = "\n".join(results)
        build.save_cache(cache)
        print(lang, "done", flush=True)
    build.write_dicts(cache, build.grab_json(build.SITE_HTML),
                      build.grab_json(build.LAB_HTML))
    print("dicts rewritten", flush=True)


if __name__ == "__main__":
    main()
