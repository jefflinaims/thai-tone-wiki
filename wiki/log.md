---
title: 紀錄
type: log
---
# 紀錄（只往後加）

## [2026-11-14] setup | 依確認後的需求摘要建立 AGENTS.md 與資料夾
- 訪談 8 題（第一次一次問 4 題，使用者沒逐題作答，所以全部重問）→ 需求摘要 → 使用者確認 → 建檔
- 見 process/interview.md、process/requirements.md

## [2026-11-14] ingest | S01 Tingsabadh & Abramson (1993) "Thai", JIPA（A 級）
- 新增：concepts/five-tones、concepts/vowel-length、concepts/live-dead-syllables、concepts/tone-in-speech
- 跟舊頁比對：Wiki 原本是空的，沒有矛盾
- 缺口：PDF 擷取文字裡的聲調符號是亂碼，五個例字分別是哪個聲調還無法確認 → 待 S03 補上

## [2026-11-14] ingest | S02 Tumtavitikul (1995) "Tonal Movements in Thai", ICPhS（A 級）
- 新增：concepts/pitch-contours
- 更新：concepts/five-tones（加上平調／曲折調分類、連到 pitch-contours）
- 跟舊頁比對：S01 只列出聲調名稱、沒有描述音高，所以兩篇沒有矛盾；S02 補上「中、低微降，高微升」

## [2026-11-14] ingest | S03 LMU Munich「Language Demos: Thai」（B 級）
- 新增：examples/khaa-five-tones、examples/naa-five-tones、concepts/tone-notation
- 更新：concepts/pitch-contours（加上五度數字、來源差異）、concepts/five-tones（連到例字）
- 補上 S01 的缺口：khaa 五個例字分別是哪個聲調（S03 引用 IPA 圖解）
- 跟舊頁比對 → **發現差異**：SoWL 把中、低、高調叫成 mid falling / low falling / high rising，跟 S02「三個平調」的分類不同。依規則採用 A 級的 S02，SoWL 的數字只當發音形狀的參考，寫進 pitch-contours 的「來源差異」

## [2026-11-14] ingest | S04 Wikipedia「Tone name」Thai 段落（B 級）
- 更新：examples/naa-five-tones（補上泰文字、更精確的意思）、concepts/five-tones（加上泰文聲調名）、concepts/pitch-contours（第二組五度數字＋來源差異）
- 跟舊頁比對 → **發現差異**：S03 和 S04 的五度數字不同（例如高調 45 對 35/55）。兩篇都是 B 級，不能互相推翻，所以改用 A 級的 S02 判斷「方向」；教學只講方向，不把某組數字當標準
- 自我檢查：five-tones 多寫了一句「中低降高升是傳統順序」，但目前沒有任何來源支持這句 → 刪掉，等有來源再補
- lint 第一次：**2 個錯誤**（naa-five-tones 連到還不存在的 tone-rules 頁）→ 先拿掉連結，等 S05 建好 tone-rules 再加回來 → lint 通過

## [2026-11-14] ingest | S05 SEAsite（北伊利諾大學）泰語聲調規則表，Hartmann 1986（B 級）
- 新增：concepts/consonant-classes、concepts/tone-marks、concepts/tone-rules、pitfalls/tone-mark-is-not-tone
- 更新：concepts/live-dead-syllables（加上活／死定義，跟 S01 的結尾音合併）、concepts/five-tones（傳統順序：這次有 S05 當來源了；只有四個符號）、examples/khaa-five-tones（補泰文字＋推理欄）、examples/naa-five-tones（加回 tone-rules 連結）
- 跟舊頁比對：用 S05 的規則表推 khaa 五個字的聲調，跟 S03 的對應**完全一致**，沒有矛盾
- 資料缺口：หน่า、หน้า、หนา 前面多一個 ห 的規則，目前的來源都沒講 → 記在 tone-rules 的「還沒涵蓋」

## [2026-11-14] ingest | S06 ThaiPod101〈Your Ultimate Guide to Learning Thai Tones〉（C 級）
- 新增：examples/khaao-set、examples/everyday-pairs、pitfalls/rising-is-not-lowest、pitfalls/romanization-needs-tone
- 更新：concepts/five-tones（加例字、練習方法）、concepts/pitch-contours（連到新易錯頁）
- 跟舊頁比對 → **發現矛盾**：S06 說「升調是五個裡最低的」，跟 S02（A 級）「升調是明顯上升的曲折調」衝突。依規則採用 S02，S03、S04 的五度數字也支持 S02 → 寫成易錯頁 rising-is-not-lowest
- 拼音統一：S06 把不送氣 k 寫成 g（glai、glâi），依 AGENTS.md 3.2 改成 klai、klâi
- 用 S05 規則表驗證 S06 的 10 個例字：可以推的都對得上；หมา 的「ห 前綴」規則仍缺來源
- S06 原文有內部不一致（同一個字兩種意思）→ 該組例字不收；另一組含不適合課堂的字義，也不收

## [2026-11-14] ingest | S07 UCLA Phonetics「The tones of Standard Chinese」（B 級）
- 新增：pitfalls/mandarin-tone-mapping（泰語聲調能不能套國語四聲）
- 更新：concepts/five-tones、concepts/pitch-contours（連到新易錯頁）
- 跟舊頁比對：沒有矛盾。S07 也指出國語實測值跟傳統數字有差，支持 pitch-contours「只講方向、不背數字」的決定

## [2026-11-14] lint | 7 篇 ingest 完成後的全面健檢
- 17 頁、31 個不同的泰文例字；斷鏈 0、孤兒頁 0、拼音不一致 0、來源矛盾規則違反 0
- 腳本抓不到、由 AI 提出的資料缺口：ห 前綴（หน่า、หนา、หมา）的聲調規則目前沒有來源 → 建議下一篇 ingest 找「ห นำ」的規則說明

## [2026-11-14] lint | 做網站時發現 lint 本身的漏洞
- build_site.py 讀 raw/S04、S05、S07 的 frontmatter 時當掉：title 的引號寫法不是合法 YAML
- 追查後發現 **lint 也讀不到這三篇的 tier，卻沒有報錯**，所以之前「採用的來源等級不能較低」這條檢查，碰到 S04/S05/S07 時其實是跳過的
- 修正：lint 遇到 raw frontmatter 讀不出來或沒有 tier 時，改成報錯（重跑後確實抓到 3 個錯）→ 修好三篇的 title 引號（只改 metadata 格式，沒改內容）→ lint 通過
- 另外：單獨出現的泰文聲調符號（例如「ข＋่」）在網頁上顯示成方框，統一在前面加上虛線圓圈 ◌（「ข＋◌่」），共 30 處
- 資料夾調整：docs/ 改放 GitHub Pages 網站，訪談與需求摘要移到 process/

## [2026-11-14] fix | 跑 graph（run2）時發現 Wiki 自己前後不一致
- pitfalls/mandarin-tone-mapping 寫「上揚的幅度**不到** 3 個半音」，但 concepts/pitch-contours（依 S02）寫的是「**≤** 3 半音」
- run1 的 AI 審查曾把簡報上的「不到 3 個半音」抓出來，當時只改了簡報，沒有回頭查 Wiki；這次在 run2 補證據卡時才發現源頭在 Wiki
- 修正：改成「在 3 個半音以內」。lint 只比對泰文拼音，抓不到這種文字上的矛盾，之後 ingest 時要人工比對程度詞

## [2026-11-17] ingest | S08 Wikipedia「Thai script」ho nam 段落（B 級）
- 目的：補上 11/14 lint 提出的資料缺口（ห 前綴的聲調規則）
- 新增：concepts/ho-nam
- 更新：concepts/tone-rules（「還沒涵蓋」改成「特殊寫法」）、examples/everyday-pairs、examples/naa-five-tones（拿掉「待補」）
- 跟舊頁比對：把 S08 的規則套進 S05 的規則表，หนา、หน่า、หน้า、หมา 四個字推出的聲調，跟 S04、S06 記載的**完全一致**，沒有矛盾
- 注意：run2 的證據卡 C15 引用的是 everyday-pairs 修改前的文字（「規則待補」）。run2 是歷史紀錄，不回頭改；簡報本身沒有用到那一欄
