# 先行 Okyou 読解メモ

確認日: 2026-06-03 JST

対象: 先行 `Okyou` repository

## 読んだ主なファイル

- `README.md`
- `AI_RESEARCHER_GUIDE.md`
- `docs/results.md`
- `docs/PUBLICATION.md`
- `experiments/sect_sutra_map/manifest.json`
- `experiments/multilingual_sutra_map/manifest.json`
- `experiments/shinran_amida_sources/manifest.json`
- `memory.md` の最新部分

## 先行プロジェクトの完了状態

先行 `Okyou` は、仏教文献の意味埋め込みによる探索地図を公開成果物としてまとめたプロジェクトである。日本語論文を主本文とし、英語AI支援翻訳、図表、公開ビューア、制作プロセス文書、GitHub Pages 導線まで整備済みだった。

中心パイプラインは `experiments/sect_sutra_map/` にあり、宗派別参照群、阿弥陀経二訳、親鸞文献、多言語パイロットを扱っていた。公開版 `docs/viewer/viewer_data.json` は本文プレビューやローカルパスを除いた派生データで、raw/processed 本文や embedding cache は公開対象外にされていた。

## 得られていた成果

- 宗派別参照群マップ v0。
- 阿弥陀経二訳の semantic embedding と character TF-IDF 比較。
- 訳者重心の初期検討。
- 解深密経の漢訳と 84000 英訳による多言語比較パイロット。
- 親鸞文献と阿弥陀経二訳の参照指標分析。
- 日本語・英語の論文HTML/PDF、図、公開ビューア、制作プロセス文書。

## 強い設計

- 公開物と非公開本文/cache の境界が明確。
- manifest に対象文献、出典、layer、訳者、宗派を集約している。
- 結果と未検証点を `docs/results.md` に残している。
- `memory.md` に変更、検証、commit hash を残す運用がある。
- AI向け再現・発展ガイドがあり、別のエージェントに読ませやすい。

## 限界として残っていた点

- 法華経など一部の大部経典は抜粋または SAT 表示範囲ベースで、全文比較ではない可能性があった。
- 禅、天台、真言、日蓮などの祖師文献・注釈・語録は十分に投入されていなかった。
- semantic embedding が意味の近さを拾う一方、文体・訳語・句法の癖は別レイヤーとして未分離だった。
- 多言語比較は有望な単発パイロットで、同一 work の異言語ペア集合としての評価は未実装だった。
- PCA 2D map は探索表示であり、引用・影響・宗派分類の証明にはならない。

## Okyou2 への取り込み方

`Okyou2` は先行 repo の履歴や公開成果物を続けない。取り込むのは、次の設計原則である。

- raw/processed 本文を公開 commit に入れない。
- manifest で出典、利用条件、分析 layer を明記する。
- 意味、文体、典拠マーカー、多言語対応を混ぜずに比較する。
- 日本語の研究判断を主にし、英語は必要に応じて補助版として扱う。
- 変更ごとに検証内容と未検証点を短く記録する。
