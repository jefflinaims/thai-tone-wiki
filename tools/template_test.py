#!/usr/bin/env python3
"""G0 模板測試（graph v2 新增，把渲染檢查往前移）：
改了 tools/render_slides.py 之後，先用 workflow/fixtures/stress.json（最難排版的假資料）渲染並跑 G3 的檢查。
通過了才開始寫逐頁稿；不過就修模板，不准動逐頁稿。

用法：python3 tools/template_test.py
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
run = ROOT / "runs" / "g0-template-test"
run.mkdir(parents=True, exist_ok=True)
shutil.copy(ROOT / "workflow" / "fixtures" / "stress.json", run / "slides.json")
html = ROOT / "docs" / "slides" / "_g0.html"
subprocess.run([sys.executable, str(ROOT / "tools" / "render_slides.py"), str(run), "--out", str(html)], check=True)
r = subprocess.run([sys.executable, str(ROOT / "tools" / "render_check.py"), str(run), "--html", str(html)])
html.unlink()
sys.exit(r.returncode)
