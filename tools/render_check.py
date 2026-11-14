#!/usr/bin/env python3
"""G3 渲染檢查：用無頭瀏覽器打開簡報，逐頁檢查有沒有溢出、出處連結有沒有壞掉，並截圖。

用法：python3 tools/render_check.py runs/<run-id> [--round N] [--html docs/slides/index.html]
寫出 g3_round<N>.md 與截圖 shots/r<N>-<slide>.png；有錯誤時 exit code = 1。
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
MIN_SLIDES, MAX_SLIDES = 8, 15

MEASURE = """() => {
  const res = [];
  document.querySelectorAll('.q').forEach(q => q.classList.add('open'));  // 測驗答案全部打開，測最擠的情況
  document.querySelectorAll('.slide').forEach((s, k) => {
    window.go(k);
    const body = s.querySelector('.body');
    const sr = s.getBoundingClientRect();
    const out = [];
    if (body.scrollHeight > body.clientHeight + 2) out.push(`內容高度 ${body.scrollHeight}px，超過可用的 ${body.clientHeight}px`);
    s.querySelectorAll('.body *').forEach(el => {
      const r = el.getBoundingClientRect();
      if (r.width && (r.right > sr.right - 40 + 1)) out.push(`<${el.tagName.toLowerCase()}> 超出右邊界 ${Math.round(r.right - (sr.right - 40))}px`);
    });
    s.querySelectorAll('svg').forEach(svg => { const b = svg.getBoundingClientRect();
      svg.querySelectorAll('text').forEach(tx => { const r = tx.getBoundingClientRect();
        if (r.top < b.top - 1 || r.bottom > b.bottom + 1 || r.right > b.right + 1) out.push(`圖上文字「${tx.textContent.trim()}」超出圖框`); }); });
    // 文字互相重疊：圖上的標籤、頁尾頁碼 vs 浮動按鈕
    const boxes = [...s.querySelectorAll('svg text, footer .num, footer a')].map(e => [e, e.getBoundingClientRect()]);
    document.querySelectorAll('#nav button').forEach(b => boxes.push([b, b.getBoundingClientRect()]));
    for (let a = 0; a < boxes.length; a++) for (let b = a + 1; b < boxes.length; b++) {
      const [ea, ra] = boxes[a], [eb, rb] = boxes[b];
      const ox = Math.min(ra.right, rb.right) - Math.max(ra.left, rb.left), oy = Math.min(ra.bottom, rb.bottom) - Math.max(ra.top, rb.top);
      if (ox > 2 && oy > 2) out.push(`文字重疊：「${(ea.textContent||'').trim().slice(0,6)}」和「${(eb.textContent||'').trim().slice(0,6)}」`);
    }
    const links = [...s.querySelectorAll('footer a')].map(a => a.getAttribute('href'));
    res.push({id: s.id, overflow: [...new Set(out)].slice(0, 5), links});
  });
  return res;
}"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--round", type=int, default=1)
    ap.add_argument("--html", default=str(ROOT / "docs" / "slides" / "index.html"))
    args = ap.parse_args()
    run, page_path = Path(args.run), Path(args.html).resolve()
    shots = run / "shots"
    shots.mkdir(exist_ok=True)
    chrome = shutil.which("google-chrome") or shutil.which("chromium")
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=chrome) if chrome else p.chromium.launch()
        pg = browser.new_page(viewport={"width": 1280, "height": 720})
        pg.goto(page_path.as_uri())
        pg.wait_for_timeout(500)
        data = pg.evaluate(MEASURE)
        for k, d in enumerate(data):
            pg.evaluate(f"window.go({k})")
            pg.wait_for_timeout(80)
            pg.screenshot(path=str(shots / f"r{args.round}-{d['id']}.png"))
        browser.close()

    issues = []
    if not (MIN_SLIDES <= len(data) <= MAX_SLIDES):
        issues.append(("deck", f"共 {len(data)} 頁，規定 {MIN_SLIDES}–{MAX_SLIDES} 頁"))
    for d in data:
        for o in d["overflow"]:
            issues.append((d["id"], o if o.startswith("文字重疊") else f"溢出：{o}"))
        for href in d["links"]:
            target = (page_path.parent / href).resolve()
            if not target.exists():
                issues.append((d["id"], f"出處連結壞掉：{href}"))
    # graph v2：模板造成的問題退回節點 5，文字太多退回節點 4
    route = lambda msg: "5 渲染模板" if any(k in msg for k in ("重疊", "圖框", "連結")) else "4 逐頁稿"
    issues = [(a, b, route(b)) for a, b in issues]
    failed = sorted({i[0] for i in issues if i[0] != "deck"})
    lines = [f"# G3 渲染檢查 — 第 {args.round} 輪", "", f"- 頁數：{len(data)}（1280×720）",
             f"- 問題：{len(issues)} 個；有問題的頁：{', '.join(failed) or '無'}", f"- 截圖：shots/r{args.round}-*.png", ""]
    lines += ["| 頁 | 說明 | 退回 |", "|---|---|---|", *[f"| {a} | {b} | {c} |" for a, b, c in issues]] if issues else ["全部通過。"]
    out = "\n".join(lines)
    (run / f"g3_round{args.round}.md").write_text(out + "\n", encoding="utf-8")
    (run / f"g3_round{args.round}.json").write_text(json.dumps({"issues": issues, "failed_slides": failed}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(out)
    sys.exit(1 if issues else 0)


if __name__ == "__main__":
    main()
