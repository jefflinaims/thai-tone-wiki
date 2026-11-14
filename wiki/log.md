---
title: 紀錄
type: log
---
# 紀錄（只往後加）

## [2026-11-14] setup | 依確認後的需求摘要建立 AGENTS.md 與資料夾
- 訪談 8 題（第一次一次問 4 題，使用者沒逐題作答，所以全部重問）→ 需求摘要 → 使用者確認 → 建檔
- 見 docs/interview.md、docs/requirements.md

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
