#!/usr/bin/env python3
"""G1 覆蓋率關卡：檢索結果夠不夠做簡報？不夠就停。

用法：python3 tools/check_coverage.py runs/<run-id>
讀 retrieval.json，寫 g1_coverage.md。不通過時 exit code = 2（代表「停止」）。
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
MIN_PAGES = 3


def main():
    run = Path(sys.argv[1])
    data = json.loads((run / "retrieval.json").read_text(encoding="utf-8"))
    pages = {p.stem for p in WIKI.rglob("*.md")} - {"index", "log"}
    problems, rows = [], []
    used = set()
    for obj in data["objectives"]:
        found = [p for p in obj["pages"] if p in pages]
        missing = [p for p in obj["pages"] if p not in pages]
        used.update(found)
        rows.append(f"| {obj['id']} | {obj['text']} | {', '.join(found) or '—'} |")
        if missing:
            problems.append(f"{obj['id']} 列了不存在的頁面：{', '.join(missing)}")
        if not found:
            problems.append(f"{obj['id']}「{obj['text']}」在 Wiki 裡找不到任何頁面 → 需要先 ingest 相關資料")
    if len(used) < MIN_PAGES:
        problems.append(f"相關頁面只有 {len(used)} 頁，少於 {MIN_PAGES} 頁 → 停止")
    ok = not problems
    lines = [
        "# G1 覆蓋率關卡",
        "",
        f"- 主題：{data['topic']}",
        f"- 相關頁面：{len(used)} 頁",
        f"- 結果：{'**通過**' if ok else '**停止**'}",
        "",
        "| 學習目標 | 內容 | 對應的 Wiki 頁 |",
        "|---|---|---|",
        *rows,
        "",
    ]
    if problems:
        lines += ["## 問題", *[f"- {p}" for p in problems]]
    out = "\n".join(lines)
    (run / "g1_coverage.md").write_text(out + "\n", encoding="utf-8")
    print(out)
    sys.exit(0 if ok else 2)


if __name__ == "__main__":
    main()
