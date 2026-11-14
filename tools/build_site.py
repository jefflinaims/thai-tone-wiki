#!/usr/bin/env python3
"""把 wiki/、raw/、process/、workflow/、runs/ 的 markdown 轉成 GitHub Pages 用的 HTML（輸出到 docs/，給 GitHub Pages 用）。

- [[slug]] 轉成連結（顯示頁面標題）
- 「泰文 拼音（聲調）」自動加上聲調顏色
- 首頁有按鈕可以篩選 概念／例字／易錯
用法：python3 tools/build_site.py
"""
import html
import re
import shutil
from pathlib import Path

import markdown
import yaml

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs"
WIKI = ROOT / "wiki"
EXAMPLE_RE = re.compile(r"([฀-๿]+)\s+([A-Za-zÀ-ɏ̀-ͯ'\-]+)（([中低降高升])）")
TONE_CLASS = {"中": "t-mid", "低": "t-low", "降": "t-fall", "高": "t-high", "升": "t-rise"}
TYPE_LABEL = {"concept": "概念", "example": "例字", "pitfall": "易錯"}
REPO_URL = "https://github.com/jefflinaims/thai-tone-wiki"

CSS = """
:root{--ink:#1f2a37;--muted:#5b6675;--paper:#fbf8f2;--card:#fff;--line:#e6e0d4;--accent:#0f6b6b;
--t-mid:#5a6b7b;--t-low:#4b4fb8;--t-fall:#c0392b;--t-high:#c27c0e;--t-rise:#2e8b57}
*{box-sizing:border-box}body{margin:0;font-family:"Noto Sans TC","Noto Sans Thai","PingFang TC","Microsoft JhengHei",system-ui,sans-serif;
color:var(--ink);background:var(--paper);line-height:1.75}
a{color:var(--accent)}header.top{background:var(--ink);color:#fff;padding:.7rem 1.4rem;display:flex;gap:1.2rem;align-items:center;flex-wrap:wrap}
header.top a{color:#fff;text-decoration:none;opacity:.9}header.top a:hover{opacity:1;text-decoration:underline}
header.top .brand{font-weight:700;margin-right:auto}
.wrap{display:grid;grid-template-columns:250px 1fr;gap:2rem;max-width:1180px;margin:0 auto;padding:1.5rem}
nav.side{font-size:.92rem;position:sticky;top:1rem;align-self:start;max-height:92vh;overflow:auto}
nav.side h4{margin:1rem 0 .3rem;color:var(--muted);font-size:.8rem;letter-spacing:.08em}
nav.side a{display:block;padding:.15rem .4rem;border-radius:6px;text-decoration:none;color:var(--ink)}
nav.side a.cur{background:#e8f1f0;color:var(--accent);font-weight:600}
main{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:1.6rem 2.2rem;min-width:0}
main h1{margin-top:.2rem;font-size:1.7rem}main h2{border-top:1px solid var(--line);padding-top:1rem;margin-top:1.8rem;font-size:1.2rem}
table{border-collapse:collapse;width:100%;margin:.8rem 0;font-size:.95rem;display:block;overflow-x:auto}
th,td{border:1px solid var(--line);padding:.4rem .6rem;text-align:left;vertical-align:top}th{background:#f4efe5}
code,pre{background:#f4efe5;border-radius:6px;font-size:.88rem}pre{padding:.8rem;overflow:auto}code{padding:.1rem .3rem}
blockquote{margin:1rem 0;padding:.6rem 1rem;background:#fff7e6;border-left:4px solid var(--t-high);border-radius:6px}
.meta{color:var(--muted);font-size:.85rem;margin-bottom:1rem}.chip{display:inline-block;border-radius:999px;padding:0 .6rem;font-size:.78rem;background:#eef3f3;color:var(--accent);margin-right:.3rem}
.ex{white-space:nowrap}.ex .th{font-size:1.15em;font-family:"Noto Sans Thai",sans-serif}.ex .ro{font-style:italic;margin:0 .15rem}
.ex .tn{display:inline-block;color:#fff;border-radius:5px;padding:0 .35rem;font-size:.8em;font-style:normal}
.t-mid{background:var(--t-mid)}.t-low{background:var(--t-low)}.t-fall{background:var(--t-fall)}.t-high{background:var(--t-high)}.t-rise{background:var(--t-rise)}
.filters{display:flex;gap:.5rem;flex-wrap:wrap;margin:1rem 0}.filters button{border:1px solid var(--line);background:#fff;border-radius:999px;padding:.35rem 1rem;cursor:pointer;font:inherit}
.filters button.on{background:var(--accent);color:#fff;border-color:var(--accent)}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:.9rem}
.card{border:1px solid var(--line);border-radius:12px;padding:.9rem 1rem;text-decoration:none;color:var(--ink);background:#fff;transition:.15s}
.card:hover{border-color:var(--accent);transform:translateY(-2px)}.card b{display:block;margin:.2rem 0}.card small{color:var(--muted)}
.hero{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1rem;margin:1.2rem 0}
.hero a{display:block;padding:1.2rem;border-radius:14px;background:var(--ink);color:#fff;text-decoration:none}
.hero a b{font-size:1.2rem;display:block}.hero a.alt{background:var(--accent)}.hero a.alt2{background:#fff;color:var(--ink);border:1px solid var(--line)}
@media(max-width:800px){.wrap{grid-template-columns:1fr}nav.side{position:static;max-height:none}}
"""


def split_fm(text):
    if text.startswith("---"):
        _, fm, body = text.split("---", 2)
        return yaml.safe_load(fm) or {}, body
    return {}, text


def tone_spans(h):
    def rep(m):
        th, ro, tn = m.groups()
        return (f'<span class="ex"><span class="th" lang="th">{th}</span> <span class="ro">{ro}</span>'
                f'<span class="tn {TONE_CLASS[tn]}">{tn}</span></span>')
    return EXAMPLE_RE.sub(rep, h)


def collect():
    pages = {}
    for p in sorted(WIKI.rglob("*.md")):
        fm, body = split_fm(p.read_text(encoding="utf-8"))
        pages[p.stem] = {"path": p, "fm": fm, "body": body, "out": f"{p.stem}.html",
                         "title": fm.get("title", p.stem), "type": fm.get("type", "")}
    extra = {}
    for p in sorted((ROOT / "raw").glob("S*.md")):
        fm, body = split_fm(p.read_text(encoding="utf-8"))
        extra[f"raw/{p.name}"] = {"fm": fm, "body": body, "out": f"raw-{p.stem}.html", "title": f"{fm.get('id')} {fm.get('title')}"}
    for rel, title in [("AGENTS.md", "AGENTS.md（Wiki 規範）"), ("process/interview.md", "需求訪談紀錄"),
                       ("process/requirements.md", "需求摘要"), ("workflow/SKILL.md", "SKILL.md（graph）")]:
        p = ROOT / rel
        if p.exists():
            fm, body = split_fm(p.read_text(encoding="utf-8"))
            extra[rel] = {"fm": fm, "body": body, "out": rel.replace("/", "-").replace(".md", ".html"), "title": title}
    for p in sorted(ROOT.glob("process/*.md")):
        if p.name == "submission.md":
            continue
        rel = f"process/{p.name}"
        if rel not in extra:
            fm, body = split_fm(p.read_text(encoding="utf-8"))
            h1 = re.search(r"^# (.+)$", body, re.M)
            extra[rel] = {"fm": fm, "body": body, "out": rel.replace("/", "-").replace(".md", ".html"),
                          "title": h1.group(1) if h1 else p.stem}
    for p in sorted(ROOT.glob("runs/*/*.md")):
        rel = str(p.relative_to(ROOT))
        h1 = re.search(r"^# (.+)$", p.read_text(encoding="utf-8"), re.M)
        extra[rel] = {"fm": {}, "body": p.read_text(encoding="utf-8"), "out": rel.replace("/", "-").replace(".md", ".html"),
                      "title": f"{p.parent.name} / {h1.group(1) if h1 else p.stem}"}
    return pages, extra


def render_md(body, pages, extra):
    body = re.sub(r"\[\[([^\]|#]+)(?:\|([^\]]+))?\]\]",
                  lambda m: f"[{m.group(2) or pages.get(m.group(1).strip(), {}).get('title', m.group(1))}]({m.group(1).strip()}.html)"
                  if m.group(1).strip() in pages else m.group(0), body)
    h = markdown.markdown(body, extensions=["tables", "fenced_code"])
    h = re.sub(r'(?<!["=>])(https?://[^\s<)]+)', r'<a href="\1">\1</a>', h)
    for rel, info in extra.items():
        h = re.sub(rf'(?<![\w/"=.-]){re.escape(rel)}', f'<a href="{info["out"]}">{rel}</a>', h)
    # 檔案相對連結（例如 [docs/requirements.md](requirements.md)）
    def md_href(m):
        name = Path(m.group(1)).name + ".md"
        for rel, info in extra.items():
            if rel == name or rel.endswith("/" + name):
                return f'href="{info["out"]}"'
        return f'href="{Path(m.group(1)).name}.html"'
    h = re.sub(r'href="([\w\-/.]+)\.md"', md_href, h)
    return tone_spans(h)


def side_nav(pages, cur):
    out = ['<nav class="side"><a href="index.html"' + (' class="cur"' if cur == "index" else "") + '>目錄（全部頁面）</a>']
    for t, label in TYPE_LABEL.items():
        out.append(f"<h4>{label}</h4>")
        for slug, p in pages.items():
            if p["type"] == t:
                c = ' class="cur"' if slug == cur else ""
                out.append(f'<a href="{p["out"]}"{c}>{html.escape(p["title"])}</a>')
    out.append('<h4>過程紀錄</h4><a href="process-interview.html">需求訪談</a><a href="AGENTS.html">AGENTS.md</a>'
               '<a href="workflow-SKILL.html">graph（SKILL.md）</a><a href="log.html">ingest 紀錄</a></nav>')
    return "\n".join(out)


def page_html(title, nav, content, depth=""):
    return f"""<!DOCTYPE html><html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}｜泰語聲調入門 Wiki</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700&family=Noto+Sans+Thai:wght@400;700&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>
<header class="top"><span class="brand">泰語聲調入門 LLM Wiki</span><a href="{depth}index.html">Wiki 目錄</a><a href="{depth}../slides/index.html">教學簡報</a><a href="{depth}../index.html">作業首頁</a><a href="{REPO_URL}">GitHub</a></header>
<div class="wrap">{nav}<main>{content}</main></div></body></html>"""


def build_index(pages):
    cards = []
    for slug, p in pages.items():
        if p["type"] not in TYPE_LABEL:
            continue
        srcs = p["fm"].get("sources") or []
        first = re.sub(r"\*\*|\[\[|\]\]", "", next((x.strip() for x in p["body"].split("\n# ", 1)[-1].split("\n", 1)[-1].strip().split("\n\n") if x.strip() and not x.strip().startswith(("#", "|", "-", ">"))), ""))
        cards.append(f'<a class="card" data-type="{p["type"]}" href="{p["out"]}"><span class="chip">{TYPE_LABEL[p["type"]]}</span>'
                     f'<b>{html.escape(p["title"])}</b><small>{html.escape(first[:70])}{"…" if len(first) > 70 else ""}</small><br>'
                     f'<small>來源：{", ".join(srcs)}</small></a>')
    raw_count = len(list((ROOT / "raw").glob("S*.md")))
    return f"""<h1>泰語聲調入門 Wiki</h1>
<p class="meta">{len(cards)} 個頁面，整理自 {raw_count} 篇公開來源（2 篇學術論文、4 篇大學教材／百科、1 篇教學網站）。由 AI 依 <a href="AGENTS.html">AGENTS.md</a> 維護。</p>
<div class="filters"><button class="on" data-f="all">全部</button><button data-f="concept">概念</button><button data-f="example">例字</button><button data-f="pitfall">易錯</button></div>
<div class="cards">{"".join(cards)}</div>
<h2>來源（raw/）</h2><ul>{"".join(f'<li><a href="raw-{p.stem}.html">{p.stem}</a></li>' for p in sorted((ROOT / "raw").glob("S*.md")))}</ul>
<script>document.querySelectorAll('.filters button').forEach(b=>b.onclick=()=>{{document.querySelectorAll('.filters button').forEach(x=>x.classList.toggle('on',x===b));
document.querySelectorAll('.card').forEach(c=>c.style.display=(b.dataset.f==='all'||c.dataset.type===b.dataset.f)?'':'none')}})</script>"""


def main():
    if (OUT / "wiki").exists():
        shutil.rmtree(OUT / "wiki")
    (OUT / "wiki").mkdir(parents=True)
    pages, extra = collect()
    wiki_out = OUT / "wiki"
    for slug, p in pages.items():
        if slug == "index":
            content = build_index(pages)
        else:
            meta = ""
            if p["type"] in TYPE_LABEL:
                meta = (f'<div class="meta"><span class="chip">{TYPE_LABEL[p["type"]]}</span>來源：{", ".join(p["fm"].get("sources") or [])}'
                        f'　更新：{p["fm"].get("updated", "")}　<a href="{REPO_URL}/blob/main/{p["path"].relative_to(ROOT)}">原始 markdown</a></div>')
            content = meta + render_md(p["body"], pages, extra)
        (wiki_out / p["out"]).write_text(page_html(p["title"], side_nav(pages, slug), content), encoding="utf-8")
    for rel, info in extra.items():
        content = render_md(info["body"], pages, extra)
        if info["fm"] and rel.startswith("raw/"):
            fm = info["fm"]
            content = (f'<div class="meta"><span class="chip">{fm.get("tier")} 級</span>{html.escape(str(fm.get("type", "")))}　'
                       f'<a href="{fm.get("url")}">原文</a></div>') + content
        (wiki_out / info["out"]).write_text(page_html(info["title"], side_nav(pages, None), content), encoding="utf-8")
    print(f"site/wiki: {len(pages)} wiki pages + {len(extra)} other pages")


if __name__ == "__main__":
    main()
