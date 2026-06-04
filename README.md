# Okyou2

`Okyou2` は、完了済みの先行プロジェクト `Okyou` を参照点にした、別個の後継研究プロジェクトです。

先行 `Okyou` は、仏教文献の意味埋め込み分析、論文HTML/PDF、公開ビューア、GitHub Pages 公開までを終えたリリース済み成果物として扱います。このリポジトリはその Git 履歴や公開成果物をそのまま伸ばす継続作業場ではありません。先行 `Okyou` は参考資料として読むだけで、変更しません。ここでは、先行成果から得た設計・限界・公開安全策を踏まえて、新しい問い、データ構造、分析レイヤー、表示方法を作ります。

## 現在の状態

- 新規 Git リポジトリとして初期化済み。
- 先行 `Okyou` の tracked ファイルは引き継いでいません。
- 先行 `Okyou` は読み取り専用の参照元として扱います。
- `.env`、raw/processed 本文、embedding cache、生成 outputs は持ち込んでいません。
- まずは調査メモと発展ブリーフだけを置いた準備段階です。

## 最初に読むファイル

- `docs/okyou1-reading-notes.md`: 先行 `Okyou` を読んだ要約。
- `docs/development-brief.md`: `Okyou2` としての初期方針。
- `docs/working-summary-2026-06-03.md`: 法然・親鸞・高僧文献マップまでの作業まとめ。
- `docs/shinran-isolated-zones-2026-06-03.md`: 親鸞だけが入り込む意味マップ領域の初回要約。
- `docs/kanbun-text-preparation-2026-06-03.md`: SAT 漢文系本文の準備と品質検査。
- `docs/predecessor-text-integrity-audit-2026-06-03.md`: 先行 `Okyou` のチャンク文字列品質監査。
- `docs/chunking-strategy-comparison-2026-06-03.md`: 旧 token decode chunk と Unicode-safe 700 token chunk の比較。
- `docs/sat-safe-high-priest-anchor-map-2026-06-03.md`: SAT 漢文系 safe chunk 版の法然・親鸞・高僧文献 map。
- `docs/honen-distinctive-zones-2026-06-03.md`: 法然側のはみ出し領域の初回内容ラベル。
- `AGENTS.md`: Codex/AI エージェント向けの作業ルール。
- `memory.md`: この repo の作業台帳。

## 初期テーマ

`Okyou2` の自然な出発点は、先行 `Okyou` で見えた課題を別プロジェクトとして整理し直すことです。

1. 意味埋め込み、文体特徴、典拠マーカーを別レイヤーとして扱う。
2. 固定長チャンクだけでなく、巻・品・段落・引用単位の自然チャンクを検討する。
3. 多言語・異訳比較を、単発パイロットではなくペア集合として評価する。
4. 研究者が比較軸を切り替えられるビューアまたはレポートを作る。

## 安全方針

本文提供元の利用条件を確認するまで、SAT、J-SOKEN、84000 などから取得した raw/processed 本文は commit しません。公開するのは、再現用コード、manifest、要約統計、本文を含まない派生データ、図表、文書に限定します。
