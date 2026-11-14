#!/usr/bin/env python3
"""依各頁 frontmatter 重建 wiki/index.md（每頁一行：連結＋一句摘要＋來源數）。"""
import re
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
GROUPS = [("concepts", "概念頁"), ("examples", "例字頁"), ("pitfalls", "易錯頁")]


def summary(body):
    after_h1 = body.split("\n# ", 1)[-1].split("\n", 1)[-1]
    for para in after_h1.strip().split("\n\n"):
        para = para.strip()
        if para and not para.startswith(("#", "|", "-", ">", "```")):
            return re.sub(r"\s+", " ", para)
    return ""


def main():
    raw_count = len(list((ROOT / "raw").glob("S*.md")))
    lines = [
        "---", "title: 目錄", "type: index", f"updated: {date.today()}", "---",
        "# 泰語聲調入門 Wiki：目錄", "",
        f"已 ingest {raw_count} 篇來源（見 raw/）。回答問題前先讀這一頁。", "",
    ]
    for folder, label in GROUPS:
        pages = sorted((WIKI / folder).glob("*.md"))
        if not pages:
            continue
        lines += [f"## {label}（{folder}/）", ""]
        for p in pages:
            text = p.read_text(encoding="utf-8")
            _, fm, body = text.split("---", 2)
            meta = yaml.safe_load(fm)
            srcs = meta.get("sources") or []
            lines.append(f"- [[{p.stem}]] **{meta['title']}**：{summary(body)}（來源 {len(srcs)}：{', '.join(srcs)}）")
        lines.append("")
    (WIKI / "index.md").write_text("\n".join(lines), encoding="utf-8")
    print("index.md rebuilt")


if __name__ == "__main__":
    main()
