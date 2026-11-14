#!/usr/bin/env python3
"""節點 5：把 slides.json 渲染成單一檔案的 HTML 簡報（docs/slides/index.html）。

用法：python3 tools/render_slides.py runs/<run-id> [--out docs/slides/index.html]
- 每頁頁尾自動加上「出處」連結（連到 docs/wiki/<slug>.html）
- 「泰文 拼音（聲調）」自動上色；←／→、空白鍵翻頁；網址 #3 直接跳到第 3 頁
"""
import argparse
import html
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
EXAMPLE_RE = re.compile(r"([฀-๿]+)\s+([A-Za-zÀ-ɏ̀-ͯ'\-]+)（([中低降高升])）")
TONE = {"中": ("t-mid", "#5a6b7b"), "低": ("t-low", "#4b4fb8"), "降": ("t-fall", "#c0392b"),
        "高": ("t-high", "#c27c0e"), "升": ("t-rise", "#2e8b57")}


def titles():
    out = {}
    for p in WIKI.rglob("*.md"):
        fm = yaml.safe_load(p.read_text(encoding="utf-8").split("---", 2)[1]) or {}
        out[p.stem] = fm.get("title", p.stem)
    return out


def fmt(text):
    h = html.escape(str(text))
    h = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", h)

    def rep(m):
        th, ro, tn = m.groups()
        return (f'<span class="ex"><span class="th" lang="th">{th}</span><span class="ro">{ro}</span>'
                f'<span class="tn {TONE[tn][0]}">{tn}</span></span>')
    return EXAMPLE_RE.sub(rep, h)


def contour_svg(contours, w=560, h=330):
    pad_l, pad_r, pad_t, pad_b = 46, 70, 16, 34
    gw, gh = w - pad_l - pad_r, h - pad_t - pad_b
    y = lambda lv: pad_t + gh * (5 - lv) / 4
    parts = [f'<svg viewBox="0 0 {w} {h}" class="contours" role="img" aria-label="五個聲調的音高曲線">']
    for lv in range(1, 6):
        parts.append(f'<line x1="{pad_l}" x2="{pad_l + gw}" y1="{y(lv)}" y2="{y(lv)}" class="grid"/>'
                     f'<text x="{pad_l - 12}" y="{y(lv) + 5}" class="axis" text-anchor="end">{lv}</text>')
    parts.append(f'<text x="{pad_l + gw / 2}" y="{h - 6}" class="axis" text-anchor="middle">時間 →</text>')
    for c in contours:
        pts = [int(d) for d in c["value"]]
        n = len(pts)
        coords = [(pad_l + gw * i / (n - 1), y(v)) for i, v in enumerate(pts)]
        d = "M " + " L ".join(f"{x:.1f} {yy:.1f}" for x, yy in coords)
        if n == 3:  # 用平滑曲線畫三點的調
            (x0, y0), (x1, y1), (x2, y2) = coords
            d = f"M {x0:.1f} {y0:.1f} Q {x1:.1f} {y1 + (y1 - (y0 + y2) / 2):.1f} {x2:.1f} {y2:.1f}"
        color = TONE[c["tone"]][1]
        ex, ey = coords[-1]
        parts.append(f'<path d="{d}" stroke="{color}" class="curve"/>'
                     f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="5" fill="{color}"/>'
                     f'<text x="{ex + 10:.1f}" y="{ey + 6:.1f}" fill="{color}" class="clabel">{html.escape(c["label"])}</text>')
    parts.append("</svg>")
    return "".join(parts)


def body_html(s):
    lay = s.get("layout", "bullets")
    if lay == "cover":
        return (f'<div class="cover"><p class="kicker">{fmt(s.get("kicker", ""))}</p><h1>{fmt(s["title"])}</h1>'
                f'<p class="sub">{fmt(s.get("subtitle", ""))}</p>'
                + "".join(f'<p class="meta">{fmt(b)}</p>' for b in s.get("bullets", [])) + "</div>")
    out = []
    if s.get("lead"):
        out.append(f'<p class="lead">{fmt(s["lead"])}</p>')
    if lay == "contours":
        out.append('<div class="split"><div>' + contour_svg(s["contours"]) + "</div><div><ul>"
                   + "".join(f"<li>{fmt(b)}</li>" for b in s.get("bullets", [])) + "</ul></div></div>")
    elif lay == "table":
        t = s["table"]
        out.append("<table><thead><tr>" + "".join(f"<th>{fmt(c)}</th>" for c in t["head"]) + "</tr></thead><tbody>"
                   + "".join("<tr>" + "".join(f"<td>{fmt(c)}</td>" for c in row) + "</tr>" for row in t["rows"])
                   + "</tbody></table>")
        if s.get("bullets"):
            out.append("<ul class='after'>" + "".join(f"<li>{fmt(b)}</li>" for b in s["bullets"]) + "</ul>")
    elif lay == "quiz":
        out.append('<div class="quiz">' + "".join(
            f'<button class="q" onclick="this.classList.toggle(\'open\')"><span class="qq">{fmt(q["q"])}</span>'
            f'<span class="qa">{fmt(q["a"])}</span><span class="hint">點一下看答案</span></button>' for q in s["quiz"]) + "</div>")
    else:
        cls = "big" if lay == "big" else ""
        out.append(f"<ul class='{cls}'>" + "".join(f"<li>{fmt(b)}</li>" for b in s.get("bullets", [])) + "</ul>")
    if s.get("note"):
        out.append(f'<p class="note">{fmt(s["note"])}</p>')
    return "".join(out)


CSS = """
:root{--ink:#1f2a37;--muted:#5b6675;--paper:#fbf8f2;--line:#e6e0d4;--accent:#0f6b6b}
*{box-sizing:border-box}html,body{margin:0;height:100%;background:#20262e;overflow:hidden}
body{font-family:"Noto Sans TC","Noto Sans Thai","PingFang TC","Microsoft JhengHei",system-ui,sans-serif;color:var(--ink)}
#stage{position:absolute;left:50%;top:50%;width:1280px;height:720px;transform-origin:50% 50%}
.slide{position:absolute;inset:0;background:var(--paper);display:none;flex-direction:column;padding:44px 64px 0}
.slide.active{display:flex}
.slide header .kicker{margin:0;color:var(--accent);font-weight:700;letter-spacing:.06em;font-size:20px}
.slide header h2{margin:4px 0 0;font-size:42px;line-height:1.25}
.slide .body{flex:1;min-height:0;padding:20px 0 8px;font-size:27px;line-height:1.6;overflow:hidden}
.slide footer{height:52px;border-top:1px solid var(--line);display:flex;align-items:center;gap:12px;font-size:16px;color:var(--muted)}
.slide footer a{color:var(--accent);text-decoration:none;border:1px solid #cfe2e0;border-radius:999px;padding:1px 10px;background:#fff}
.slide footer .num{margin-left:auto;font-variant-numeric:tabular-nums}
ul{margin:0;padding-left:1.1em}li{margin:.25em 0}li::marker{color:var(--accent)}
ul.big{font-size:32px}ul.after{font-size:23px;margin-top:10px}
.lead{margin:0 0 12px;font-size:27px;color:var(--muted)}
.note{margin:12px 0 0;padding:10px 16px;background:#fff7e6;border-left:5px solid #c27c0e;border-radius:8px;font-size:22px}
table{border-collapse:collapse;width:100%;font-size:24px;background:#fff}
th,td{border:1px solid var(--line);padding:6px 12px;text-align:left}th{background:#efe8da;font-size:21px}
.ex{white-space:nowrap}.ex .th{font-family:"Noto Sans Thai","Loma",sans-serif;font-size:1.08em;margin-right:.3em}
.ex .ro{font-style:italic;margin-right:.2em}
.tn{display:inline-block;color:#fff;border-radius:6px;padding:0 .35em;font-size:.78em;line-height:1.45;vertical-align:.08em}
.t-mid{background:#5a6b7b}.t-low{background:#4b4fb8}.t-fall{background:#c0392b}.t-high{background:#c27c0e}.t-rise{background:#2e8b57}
.split{display:grid;grid-template-columns:560px 1fr;gap:36px;align-items:start}.split ul{font-size:24px}
svg.contours{width:560px;height:330px;background:#fff;border:1px solid var(--line);border-radius:12px}
svg .grid{stroke:#eee6d6;stroke-width:1}svg .axis{font-size:14px;fill:#8a93a0}svg .curve{fill:none;stroke-width:5;stroke-linecap:round}
svg .clabel{font-size:19px;font-weight:700}
.cover{margin:auto 0;padding-bottom:30px}.cover .kicker{color:var(--accent);font-weight:700;font-size:24px;margin:0}
.cover h1{font-size:64px;margin:10px 0 6px;line-height:1.2}.cover .sub{font-size:30px;color:var(--muted);margin:0 0 30px}
.cover .meta{font-size:20px;color:var(--muted);margin:4px 0}
.quiz{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.q{all:unset;cursor:pointer;background:#fff;border:2px solid var(--line);border-radius:14px;padding:14px 18px;font-size:23px;display:flex;flex-direction:column;gap:6px}
.q:hover{border-color:var(--accent)}.q .qa{display:none;color:var(--accent);font-weight:700}.q.open .qa{display:block}.q.open .hint{display:none}
.q .hint{font-size:15px;color:var(--muted)}
#nav{position:fixed;right:16px;bottom:12px;display:flex;gap:8px;z-index:9}
#nav button{background:#ffffffdd;border:0;border-radius:8px;padding:6px 14px;font-size:16px;cursor:pointer}
#bar{position:fixed;left:0;top:0;height:4px;background:#2e8b57;z-index:9;transition:width .2s}
@media print{html,body{overflow:visible;background:#fff}#stage{position:static;transform:none!important}.slide{display:flex;position:relative;page-break-after:always;height:720px}#nav,#bar{display:none}}
"""

JS = """
const S=[...document.querySelectorAll('.slide')];let i=0;
function fit(){const k=Math.min(innerWidth/1280,innerHeight/720);document.getElementById('stage').style.transform=`translate(-50%,-50%) scale(${k})`;}
function go(n){i=Math.max(0,Math.min(S.length-1,n));S.forEach((s,k)=>s.classList.toggle('active',k===i));
document.getElementById('bar').style.width=((i+1)/S.length*100)+'%';history.replaceState(null,'','#'+(i+1));}
addEventListener('keydown',e=>{if(['ArrowRight','PageDown',' '].includes(e.key)){e.preventDefault();go(i+1)}
if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();go(i-1)}if(e.key==='Home')go(0);if(e.key==='End')go(S.length-1)});
addEventListener('resize',fit);fit();go((parseInt(location.hash.slice(1))||1)-1);window.go=go;
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--out", default=str(ROOT / "docs" / "slides" / "index.html"))
    args = ap.parse_args()
    deck = json.loads((Path(args.run) / "slides.json").read_text(encoding="utf-8"))
    names = titles()
    slides = deck["slides"]
    blocks = []
    for n, s in enumerate(slides, 1):
        cites = "".join(f'<a href="../wiki/{c}.html" target="_blank">{html.escape(names.get(c, c))}</a>' for c in s.get("cites", []))
        foot = f'<footer>{"出處（Wiki）：" + cites if cites else "資料來源：泰語聲調入門 LLM Wiki"}<span class="num">{n} / {len(slides)}</span></footer>'
        head = "" if s.get("layout") == "cover" else (
            f'<header><p class="kicker">{fmt(s.get("kicker", ""))}</p><h2>{fmt(s["title"])}</h2></header>')
        blocks.append(f'<section class="slide" id="{s["id"]}" data-objective="{s.get("objective", "")}">{head}'
                      f'<div class="body">{body_html(s)}</div>{foot}</section>')
    doc = f"""<!DOCTYPE html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(deck["title"])}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700&family=Noto+Sans+Thai:wght@400;700&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body><div id="bar"></div><div id="stage">{"".join(blocks)}</div>
<div id="nav"><button onclick="go(i-1)" aria-label="上一頁">←</button><button onclick="go(i+1)" aria-label="下一頁">→</button></div>
<script>{JS}</script></body></html>"""
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    print(f"rendered {len(slides)} slides → {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
