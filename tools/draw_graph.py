#!/usr/bin/env python3
"""畫 graph v2 流程圖（docs/img/graph-v2.svg 與 .png）。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
W, H, BW, BH = 1400, 560, 150, 64
AI, GATE, HUMAN, END = ("#efe7fb", "#7b5cc4"), ("#eceff3", "#5b6675"), ("#fde6d8", "#d9622b"), ("#e3f3e6", "#2e8b57")
R1, R2 = 110, 330
nodes = {
    "G0": (30, R1, "G0 模板測試", GATE, True, True),
    "N1": (220, R1, "1 檢索 Wiki", AI, False, False),
    "G1": (410, R1, "G1 覆蓋率", GATE, False, False),
    "N2": (600, R1, "2 證據卡（逐字引文）", AI, False, False),
    "G2a": (790, R1, "G2a 證據卡（檢查）", GATE, True, False),
    "N3": (980, R1, "3 大綱", AI, False, False),
    "H": (1170, R1, "人工確認", HUMAN, False, False),
    "N4": (220, R2, "4 逐頁稿", AI, False, False),
    "G2": (410, R2, "G2 忠實度（程式＋AI）", GATE, False, False),
    "N5": (600, R2, "5 渲染 HTML", AI, False, False),
    "G3": (790, R2, "G3 渲染檢查", GATE, False, False),
    "N6": (980, R2, "6 交件＋報告", END, False, False),
}
o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Noto Sans TC, Noto Sans CJK TC, PingFang TC, Microsoft JhengHei, sans-serif">',
     '<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7d8aa3"/></marker>'
     '<marker id="b" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#d9622b"/></marker></defs>',
     f'<rect width="{W}" height="{H}" fill="#fbf8f2"/>',
     '<text x="30" y="34" font-size="22" font-weight="700" fill="#1f2a37">graph v2：從 LLM Wiki 產生教學 HTML 簡報</text>']


def fwd(d):
    o.append(f'<path d="{d}" fill="none" stroke="#7d8aa3" stroke-width="3" marker-end="url(#a)"/>')


def back(d, label, lx, ly, new=False):
    o.append(f'<path d="{d}" fill="none" stroke="#d9622b" stroke-width="2.5" stroke-dasharray="7 5" marker-end="url(#b)"/>')
    o.append(f'<text x="{lx}" y="{ly}" font-size="15" fill="#d9622b" text-anchor="middle">{label}{"（v2）" if new else ""}</text>')


# 前進
for a, b in [("N1", "G1"), ("G1", "N2"), ("N2", "G2a"), ("G2a", "N3"), ("N3", "H"), ("N4", "G2"), ("G2", "N5"), ("N5", "G3"), ("G3", "N6")]:
    xa, ya = nodes[a][0] + BW, nodes[a][1] + BH / 2
    fwd(f"M {xa} {ya} L {nodes[b][0] - 2} {ya}")
o.append(f'<path d="M {30 + BW} {R1 + BH / 2} L {218} {R1 + BH / 2}" fill="none" stroke="#7d8aa3" stroke-width="3" stroke-dasharray="4 4" marker-end="url(#a)"/>')
fwd(f"M 1245 {R1 + BH} L 1245 262 L 280 262 L 280 {R2 - 2}")
# 退回
back("M 865 110 L 865 86 L 675 86 L 675 108", "引文對不上", 770, 80, True)
back("M 1245 110 L 1245 62 L 1055 62 L 1055 108", "改大綱", 1150, 78)
back("M 1205 110 L 1205 42 L 295 42 L 295 108", "補檢索", 750, 34)
back("M 485 394 L 485 428 L 300 428 L 300 396", "只重寫那幾頁", 392, 448)
back("M 470 330 L 470 214 L 255 214 L 255 176", "缺資料", 362, 208)
back("M 880 394 L 880 492 L 260 492 L 260 396", "文字太多（溢出）", 570, 512)
back("M 835 394 L 835 446 L 675 446 L 675 396", "模板問題", 755, 466, True)
o.append(f'<text x="485" y="196" font-size="15" fill="#d9622b" text-anchor="middle">不足 → 停止</text>')
o.append(f'<text x="105" y="96" font-size="13" fill="#5b6675" text-anchor="middle">模板改過才跑</text>')
# 方框
for k, (x, y, label, (fill, stroke), new, dashed) in nodes.items():
    dash = ' stroke-dasharray="6 4"' if dashed else ""
    o.append(f'<rect x="{x}" y="{y}" width="{BW}" height="{BH}" rx="12" fill="{fill}" stroke="{stroke}" stroke-width="2.5"{dash}/>')
    lines = [label[: label.find("（")], label[label.find("（"):]] if "（" in label else [label]
    for i, ln in enumerate(lines):
        yy = y + BH / 2 + 6 + (i - (len(lines) - 1) / 2) * 20
        o.append(f'<text x="{x + BW / 2}" y="{yy}" font-size="{17 if i == 0 else 14}" font-weight="{700 if i == 0 else 400}" fill="#1f2a37" text-anchor="middle">{ln}</text>')
    if new:
        o.append(f'<rect x="{x + BW - 44}" y="{y - 11}" width="50" height="22" rx="11" fill="#2e8b57"/><text x="{x + BW - 19}" y="{y + 5}" font-size="13" fill="#fff" text-anchor="middle" font-weight="700">v2 新增</text>')
# 圖例
lx = 1190
for i, (name, (fill, stroke)) in enumerate([("AI 節點", AI), ("檢查關卡（程式）", GATE), ("人工確認", HUMAN)]):
    yy = 300 + i * 34
    o.append(f'<rect x="{lx}" y="{yy}" width="26" height="20" rx="5" fill="{fill}" stroke="{stroke}" stroke-width="2"/><text x="{lx + 36}" y="{yy + 16}" font-size="15" fill="#1f2a37">{name}</text>')
o.append(f'<path d="M {lx} 412 L {lx + 26} 412" stroke="#d9622b" stroke-width="2.5" stroke-dasharray="7 5"/><text x="{lx + 36}" y="417" font-size="15" fill="#1f2a37">退回路線（最多 3 輪）</text>')
o.append('</svg>')
svg = "\n".join(o)
(ROOT / "docs" / "img" / "graph-v2.svg").write_text(svg, encoding="utf-8")
try:
    import shutil
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=shutil.which("google-chrome"))
        pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=1.5)
        pg.set_content(f"<html><body style='margin:0'>{svg}</body></html>")
        pg.screenshot(path=str(ROOT / "docs" / "img" / "graph-v2.png"))
        b.close()
except Exception as e:  # noqa: BLE001
    print("png skipped:", e)
print("graph drawn")
