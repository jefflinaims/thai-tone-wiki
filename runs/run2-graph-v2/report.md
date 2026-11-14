# 執行報告：run2（graph v2）

- 日期：2026-11-14
- 主題、讀者：跟 run1 相同（泰語五個聲調怎麼聽、怎麼念？／完全沒學過泰語的同學）
- graph：workflow/SKILL.md v2（依 run1 的結果修改）
- 結果：**這一份就是交出去的簡報**（docs/slides/index.html，9 頁）

## 每個節點發生了什麼

| 節點 | 結果 | 紀錄檔 |
|---|---|---|
| G0 模板測試 | 模板改過（字放大），先用假資料測：通過 | runs/g0-template-test/ |
| 1 檢索 Wiki | 沿用 run1 修正後的結果：5 個目標、14 頁 | retrieval.json |
| G1 覆蓋率 | 通過 | g1_coverage.md |
| 2 證據卡 | 33 張，**全部是逐字引文** | cards.json |
| G2a 證據卡檢查 | 第 1 輪通過（33/33 引文都對得上） | g2a_round1.md |
| 3 大綱 ＋ H | 沿用 run1 經使用者確認的 9 頁大綱 | outline.md |
| 4 逐頁稿 | 9 頁，每頁列出用到的證據卡 | slides.round1.json |
| G2 第 1 輪 | 程式 0 個；AI 審查 1 個（s06 的「第一聲（55）？」看不懂） | g2_round1.md、ai_review_round1.json |
| ↳ 退回節點 4 | 只重寫 s06 | slides.json |
| G2 第 2 輪 | 程式 0 個；AI 審查 1 個（s06 新句子在 Wiki 有依據，但不在證據卡裡） | g2_round2.md、ai_review_round2.json |
| ↳ 退回節點 2 | 補 C34、C35 兩張證據卡 → G2a 通過 | g2a_round2.md |
| ↳ **發現 Wiki 本身的問題** | 補 C35 時發現 mandarin-tone-mapping 寫「不到 3 個半音」，跟 pitch-contours 的「≤ 3」不一致 → 修 Wiki，記進 log | wiki/log.md |
| G2a 第 3 輪 | 抓到 C35 的引文跟修正後的 Wiki 對不上（證明這個檢查有用）→ 更新引文 | g2a_round3.md |
| G2a 第 4 輪、G2 第 3–4 輪 | 通過 | g2a_round4.md、g2_round4.md、ai_review_round3.json |
| 5 渲染 ＋ G3 第 1 輪 | 程式通過；人工看截圖也通過 | g3_round1.md、g3_round1_visual.md |

## 跟 run1 比較

| 項目 | run1（graph v1） | run2（graph v2） |
|---|---|---|
| 證據卡造成的錯 | 1 個（丟掉「活音節」的條件），到 G2 AI 審查才抓到 | 0 個；G2a 在節點 2 就檢查 |
| G2 程式抓到的問題 | 1 個（還是誤判） | 0 個 |
| G2 AI 審查抓到的問題 | 5 個（2 個忠實度＋1 個嚴重忠實度＋2 個教學性） | 2 個（1 個教學性＋1 個出處），沒有忠實度錯誤 |
| G3 跑幾輪 | 3 輪（到上限），程式漏抓 4 個問題 | 1 輪 |
| 渲染問題在哪裡被發現 | 最後的 G3，而且靠人看截圖 | G0 已先測過模板，G3 沒有問題 |
| 額外發現 | — | Wiki 兩頁對「3 個半音」的描述不一致（源頭在 Wiki） |

## 結論
- 把檢查往前移到**證據卡（G2a）**和**模板（G0）**之後，後段的 AI 審查只剩「教學性」和「出處」問題，沒有再出現內容講錯。
- 往前移還有一個意外的好處：證據卡要逐字對 Wiki，所以 Wiki 自己寫得不一致的地方也被翻出來了。
