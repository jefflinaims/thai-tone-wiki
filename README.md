# 泰語聲調入門 LLM Wiki（生成式 AI HW10）

- 網站：https://jefflinaims.github.io/thai-tone-wiki/ （教學簡報、Wiki、流程圖、執行報告）
- 架構依 Karpathy〈LLM Wiki〉：`raw/`（8 篇來源的擷取筆記）→ `wiki/`（AI 維護的 18 頁）→ `AGENTS.md`（規範）
- 產生簡報的 graph：`workflow/SKILL.md`（v2.1）；三次實際執行：`runs/run1-graph-v1/`、`runs/run2-graph-v2/`、`runs/run3-independent-review/`
- 過程：`process/interview.md`（需求訪談）、`process/requirements.md`、`process/reflection.md`

## 常用指令
```bash
python3 tools/lint_wiki.py            # Wiki 健檢
python3 tools/build_index.py          # 重建 wiki/index.md
python3 tools/build_site.py           # 產生 docs/wiki/（GitHub Pages）
python3 tools/template_test.py        # G0 模板測試
python3 tools/check_coverage.py runs/<run>   # G1
python3 tools/check_cards.py runs/<run>      # G2a
python3 tools/check_slides.py runs/<run>     # G2（程式）
python3 tools/render_slides.py runs/<run>    # 節點 5
python3 tools/render_check.py runs/<run>     # G3（需要 playwright）
```
GitHub Pages 設定：Settings → Pages → Branch `main`、資料夾 `/docs`。
