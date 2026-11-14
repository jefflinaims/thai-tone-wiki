#!/usr/bin/env python3
"""G2 忠實度檢查（程式部分）：逐頁稿 slides.json 有沒有忠於 Wiki？

用法：python3 tools/check_slides.py runs/<run-id> [--round N]
寫出 g2_round<N>.md 與 g2_round<N>.json；有錯誤時 exit code = 1。
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lint_wiki import EXAMPLE_RE, lint, split_frontmatter, tone_from_roman  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
NUM_RE = re.compile(r"\d+(?:\.\d+)?")
THAI_RE = re.compile(r"[฀-๿]+")
MIN_SLIDES, MAX_SLIDES, MIN_COVERAGE = 8, 15, 0.7


def slide_text(s):
    parts = [s.get("title", ""), s.get("subtitle", ""), s.get("note", "")]
    parts += s.get("bullets", [])
    if s.get("table"):
        parts += s["table"].get("head", [])
        for row in s["table"].get("rows", []):
            parts += row
    for q in s.get("quiz", []):
        parts += [q.get("q", ""), q.get("a", "")]
    for c in s.get("contours", []):
        parts += [c.get("label", ""), c.get("value", "")]
    return "\n".join(str(p) for p in parts if p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--round", type=int, default=1)
    args = ap.parse_args()
    run = Path(args.run)
    deck = json.loads((run / "slides.json").read_text(encoding="utf-8"))
    retrieval = json.loads((run / "retrieval.json").read_text(encoding="utf-8"))

    pages = {p.stem: p for p in WIKI.rglob("*.md")}
    page_text = {k: split_frontmatter(v.read_text(encoding="utf-8"))[1] for k, v in pages.items()}
    _, word_forms, _, _ = lint()  # wiki 裡每個泰文字的標準寫法

    issues = []  # (slide_id, kind, message)
    cited_all = set()
    objectives_done = set()
    slides = deck["slides"]

    if not (MIN_SLIDES <= len(slides) <= MAX_SLIDES):
        issues.append(("deck", "頁數", f"共 {len(slides)} 頁，規定 {MIN_SLIDES}–{MAX_SLIDES} 頁"))

    for s in slides:
        sid = s["id"]
        if s.get("objective"):
            objectives_done.add(s["objective"])
        cites = s.get("cites", [])
        if s.get("layout") == "cover":
            continue
        if not cites:
            issues.append((sid, "出處", "沒有列出引用的 Wiki 頁"))
            continue
        bad = [c for c in cites if c not in pages]
        for c in bad:
            issues.append((sid, "出處", f"引用的頁面 [[{c}]] 不存在"))
        good = [c for c in cites if c in pages]
        cited_all.update(good)
        source = "\n".join(page_text[c] for c in good)
        text = slide_text(s)

        for n in sorted(set(NUM_RE.findall(text)), key=lambda x: float(x)):
            if not re.search(rf"(?<![\d.]){re.escape(n)}(?![\d.])", source):
                issues.append((sid, "數字", f"「{n}」在引用的頁面（{', '.join(good)}）裡找不到"))
        for w in sorted(set(THAI_RE.findall(text))):
            if w not in source:
                issues.append((sid, "泰文", f"「{w}」在引用的頁面（{', '.join(good)}）裡找不到"))
        for thai, roman, tone in EXAMPLE_RE.findall(text):
            implied = tone_from_roman(roman)
            if implied and implied != tone:
                issues.append((sid, "拼音", f"{thai} {roman}（{tone}）：聲調符號表示「{implied}」，跟聲調名不符"))
            forms = word_forms.get(thai)
            if forms and (roman, tone) not in forms:
                std = "、".join(f"{r}（{t}）" for r, t in forms)
                issues.append((sid, "拼音", f"{thai} 寫成 {roman}（{tone}），Wiki 的寫法是 {std}"))

    for obj in retrieval["objectives"]:
        if obj["id"] not in objectives_done:
            issues.append(("deck", "目標", f"學習目標 {obj['id']}「{obj['text']}」沒有任何一頁負責"))

    retrieved = {p for o in retrieval["objectives"] for p in o["pages"]}
    cover = len(retrieved & cited_all) / len(retrieved) if retrieved else 0
    unused = sorted(retrieved - cited_all)
    if cover < MIN_COVERAGE:
        issues.append(("deck", "覆蓋率", f"檢索到的 {len(retrieved)} 頁只引用了 {len(retrieved & cited_all)} 頁（{cover:.0%}），未用：{', '.join(unused)}"))

    failed_slides = sorted({i[0] for i in issues if i[0] != "deck"})
    lines = [
        f"# G2 忠實度檢查（程式）— 第 {args.round} 輪",
        "",
        f"- 頁數：{len(slides)}",
        f"- 覆蓋率：{len(retrieved & cited_all)}/{len(retrieved)}（{cover:.0%}）" + (f"，未用：{', '.join(unused)}" if unused else ""),
        f"- 問題：{len(issues)} 個；要重寫的頁：{', '.join(failed_slides) or '無'}",
        "",
    ]
    if issues:
        lines += ["| 頁 | 類型 | 說明 |", "|---|---|---|", *[f"| {a} | {b} | {c} |" for a, b, c in issues]]
    else:
        lines.append("全部通過。")
    out = "\n".join(lines)
    (run / f"g2_round{args.round}.md").write_text(out + "\n", encoding="utf-8")
    (run / f"g2_round{args.round}.json").write_text(
        json.dumps({"issues": issues, "failed_slides": failed_slides, "coverage": cover}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(out)
    sys.exit(1 if issues else 0)


if __name__ == "__main__":
    main()
