#!/usr/bin/env python3
"""Wiki 健檢（lint）。

檢查項目（依 AGENTS.md 第 5 節）：
  1. 斷鏈與孤兒頁
  2. 拼音格式不一致（聲調符號 ↔ 聲調名；同一泰文字跨頁一致）
  3. 來源之間的矛盾（「來源差異」要有「採用」，且採用的來源等級不能較低）
  4. 基本結構（frontmatter、參考資料、來源編號存在）

用法：python3 tools/lint_wiki.py [--report 路徑]
有錯誤時 exit code = 1。
"""
import argparse
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
RAW = ROOT / "raw"

LINK_RE = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]")
# 泰文 拼音（聲調名）
EXAMPLE_RE = re.compile(
    r"([฀-๿]+)\s+([A-Za-zÀ-ɏ̀-ͯ'\-]+)（([中低降高升])）"
)
TONE_BY_MARK = {"̀": "低", "̂": "降", "́": "高", "̌": "升"}
TIER_RANK = {"A": 3, "B": 2, "C": 1}
SPECIAL = {"index", "log"}


def split_frontmatter(text):
    if not text.startswith("---"):
        return None, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, text
    try:
        return yaml.safe_load(parts[1]) or {}, parts[2]
    except yaml.YAMLError:
        return None, text


def tone_from_roman(roman):
    """Return the tone implied by diacritics, or None if multi-tone/ambiguous."""
    marks = [c for c in unicodedata.normalize("NFD", roman) if c in TONE_BY_MARK]
    if len(marks) > 1:
        return None
    return TONE_BY_MARK[marks[0]] if marks else "中"


def section(body, heading):
    m = re.search(rf"^## {re.escape(heading)}\s*$(.*?)(?=^## |\Z)", body, re.M | re.S)
    return m.group(1) if m else None


def load_raw_tiers():
    tiers = {}
    for p in sorted(RAW.glob("S*.md")):
        fm, _ = split_frontmatter(p.read_text(encoding="utf-8"))
        sid = (fm or {}).get("id") or p.name.split("-")[0]
        tiers[sid] = (fm or {}).get("tier")
    return tiers


def lint():
    errors, warnings = [], []
    tiers = load_raw_tiers()
    pages = {}
    for p in sorted(WIKI.rglob("*.md")):
        pages[p.stem] = p

    inbound = defaultdict(set)
    word_forms = defaultdict(set)  # thai -> {(roman, tone)}
    word_where = defaultdict(set)

    for slug, path in pages.items():
        rel = path.relative_to(ROOT)
        text = path.read_text(encoding="utf-8")
        fm, body = split_frontmatter(text)

        # --- 4. 基本結構 ---
        if fm is None:
            errors.append(f"[結構] {rel}：沒有 frontmatter")
            fm = {}
        if slug not in SPECIAL:
            for key in ("title", "type", "sources", "updated"):
                if key not in fm:
                    errors.append(f"[結構] {rel}：frontmatter 缺 `{key}`")
            refs = section(body, "參考資料")
            if refs is None:
                errors.append(f"[結構] {rel}：缺「## 參考資料」")
            for sid in fm.get("sources") or []:
                if sid not in tiers:
                    errors.append(f"[結構] {rel}：sources 列了 {sid}，但 raw/ 裡沒有這篇")
                elif refs is not None and sid not in refs:
                    errors.append(f"[結構] {rel}：sources 有 {sid}，但「參考資料」沒列")
            if refs:
                for sid in re.findall(r"\bS\d{2}\b", refs):
                    if sid not in tiers:
                        errors.append(f"[結構] {rel}：參考資料列了 {sid}，但 raw/ 裡沒有這篇")

        # --- 1. 斷鏈 ---
        for target in LINK_RE.findall(body):
            target = target.strip()
            if target not in pages:
                errors.append(f"[斷鏈] {rel}：[[{target}]] 指到不存在的頁面")
            elif slug != "index" and target != slug:
                inbound[target].add(slug)

        # --- 2. 拼音格式 ---
        for thai, roman, tone in EXAMPLE_RE.findall(body):
            implied = tone_from_roman(roman)
            if implied is None:
                warnings.append(f"[拼音] {rel}：{thai} {roman} 有多個聲調符號，略過聲調比對")
            elif implied != tone:
                errors.append(
                    f"[拼音] {rel}：{thai} {roman}（{tone}）— 拼音的聲調符號表示「{implied}」，跟聲調名「{tone}」對不上"
                )
            word_forms[thai].add((roman, tone))
            word_where[thai].add(str(rel))

        # --- 3. 來源矛盾 ---
        diff = section(body, "來源差異")
        if diff is not None:
            adopt = re.search(r"採用：\s*(S\d{2})", diff)
            if not adopt:
                errors.append(f"[矛盾] {rel}：「來源差異」沒有寫「採用：Sxx」")
            else:
                chosen = adopt.group(1)
                others = set(re.findall(r"\bS\d{2}\b", diff)) - {chosen}
                undecided = "尚無定論" in diff
                for o in others:
                    ct, ot = tiers.get(chosen), tiers.get(o)
                    if ct and ot and TIER_RANK[ct] < TIER_RANK[ot]:
                        errors.append(
                            f"[矛盾] {rel}：採用 {chosen}（{ct} 級），但它比 {o}（{ot} 級）等級低"
                        )
                    if ct and ot and ct == ot and not undecided:
                        warnings.append(
                            f"[矛盾] {rel}：{chosen} 和 {o} 同為 {ct} 級，規則要求標示「尚無定論」"
                        )

    # 跨頁拼音一致
    for thai, forms in word_forms.items():
        if len(forms) > 1:
            shown = "、".join(f"{r}（{t}）" for r, t in sorted(forms))
            errors.append(f"[拼音] {thai} 在不同頁有不同寫法：{shown}；出現在 {', '.join(sorted(word_where[thai]))}")

    # 孤兒頁
    for slug, path in pages.items():
        if slug in SPECIAL:
            continue
        if not inbound.get(slug):
            errors.append(f"[孤兒] {path.relative_to(ROOT)}：除了 index.md 之外，沒有任何頁面連到它")

    return pages, word_forms, errors, warnings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", help="把報告寫到這個 markdown 檔")
    args = ap.parse_args()
    pages, words, errors, warnings = lint()
    content = [p for p in pages if p not in SPECIAL]
    lines = [
        "# Wiki lint 報告",
        "",
        f"- 頁面數：{len(content)}（不含 index、log）",
        f"- 例字數（不同泰文字）：{len(words)}",
        f"- 錯誤：{len(errors)}　警告：{len(warnings)}",
        "",
    ]
    if errors:
        lines += ["## 錯誤", *[f"- {e}" for e in errors], ""]
    if warnings:
        lines += ["## 警告", *[f"- {w}" for w in warnings], ""]
    if not errors and not warnings:
        lines.append("全部通過。")
    out = "\n".join(lines)
    print(out)
    if args.report:
        Path(args.report).write_text(out + "\n", encoding="utf-8")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
