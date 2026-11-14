#!/usr/bin/env python3
"""G2a 證據卡檢查（graph v2 新增，從 G2 往前移）：每張證據卡的引文必須「一字不差」出現在 Wiki 頁裡。

為什麼：run1 最嚴重的錯（把「活音節、不加符號時」的條件丟掉）是在證據卡用自己的話摘要時發生的。
改成「先原文引用、再決定怎麼講」，條件就不會在摘要時消失。

用法：python3 tools/check_cards.py runs/<run-id> [--round N]
- quote：必須是該頁的原文（忽略 ** 粗體記號與多餘空白）
- context：引用表格的某一列時，必須把表頭也一起附上（同樣要逐字對得上），否則表頭的條件會不見
寫出 g2a_round<N>.md；有錯誤時 exit code = 1。
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lint_wiki import split_frontmatter  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"


def norm(s):
    s = s.replace("**", "")
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--round", type=int, default=1)
    args = ap.parse_args()
    run = Path(args.run)
    cards = json.loads((run / "cards.json").read_text(encoding="utf-8"))["cards"]
    pages = {p.stem: norm(split_frontmatter(p.read_text(encoding="utf-8"))[1]) for p in WIKI.rglob("*.md")}
    issues, ids = [], set()
    for c in cards:
        cid = c["id"]
        if cid in ids:
            issues.append((cid, "編號重複"))
        ids.add(cid)
        page = pages.get(c["page"])
        if page is None:
            issues.append((cid, f"頁面 {c['page']} 不存在"))
            continue
        q = norm(c["quote"])
        if q not in page:
            # 找出從哪個字開始對不上，方便修
            k = 0
            while k < len(q) and q[: k + 1] in page:
                k += 1
            issues.append((cid, f"引文在 [[{c['page']}]] 找不到（前 {k} 個字對得上，之後是「{q[k:k + 12]}…」）"))
        if q.startswith("|") and not c.get("context"):
            issues.append((cid, "引用了表格的一列，但沒有附上表頭（context）"))
        if c.get("context") and norm(c["context"]) not in page:
            issues.append((cid, f"表頭（context）在 [[{c['page']}]] 找不到"))
    lines = [f"# G2a 證據卡檢查 — 第 {args.round} 輪", "", f"- 卡片：{len(cards)} 張", f"- 問題：{len(issues)} 個", ""]
    lines += ["| 卡片 | 說明 |", "|---|---|", *[f"| {a} | {b} |" for a, b in issues]] if issues else ["全部通過。"]
    out = "\n".join(lines)
    (run / f"g2a_round{args.round}.md").write_text(out + "\n", encoding="utf-8")
    print(out)
    sys.exit(1 if issues else 0)


if __name__ == "__main__":
    main()
