# Okyou2 Development Brief

## 位置づけ

`Okyou2` は、先行 `Okyou` の完了後に始める別個の後継プロジェクトである。先行 repo はリリース済みで閉じているため、参考資料として読むだけにし、変更しない。先行 repo のコードや公開成果をそのまま伸ばすのではなく、「仏教文献をどう比較すると研究上意味があるか」を再設計する。

## 初期仮説

先行 `Okyou` では、意味埋め込みは同内容・近縁内容の検出に有効だった。一方で、訳者の癖、文体、典拠、引用、宗派的用法を同じ距離空間だけで読むと解釈が混ざる。`Okyou2` では、比較軸をレイヤー化する。

## 分析レイヤー案

1. Semantic layer
   - OpenAI embedding などで主題・意味の近さを見る。
2. Style layer
   - character n-gram、訳語、助字、句法、文長などで文体差を見る。
3. Source-marker layer
   - 固有句、典拠句、引用マーカー、経名・仏菩薩名などを辞書またはルールで拾う。
4. Structure layer
   - 巻、品、段落、偈、引用単位など、固定長ではない区切りで比較する。
5. Multilingual layer
   - 漢訳、英訳、チベット語、サンスクリット、パーリなどの対応関係を work 単位で評価する。

## 最初のマイルストーン

### M0: 準備

- 新規 repo として初期化する。
- 先行 repo 読解メモを残す。
- 先行 repo を読み取り専用の参照元として固定する。
- raw 本文、cache、outputs を ignore する。

### M1: 問いの選定

候補:

- 阿弥陀経二訳を、意味・文体・典拠マーカーに分けて再評価する。
- 法華経を抜粋ではなく安定した全文単位で扱えるか確認する。
- 禅系は経典ではなく語録・祖師文献を入れるとどう見えるか試す。
- 多言語同一 work ペアを複数作り、cross-language margin を測る。

### M2: manifest 設計

先行 repo の manifest を参考にしつつ、次の項目を最初から持つ。

- `work_id`
- `text_id`
- `language`
- `script`
- `source_kind`
- `source_url`
- `source_license_note`
- `public_policy`
- `analysis_layers`
- `chunking_policy`

### M3: API 不要 baseline

embedding の前に、character n-gram、文字数、文長、固有句頻度などの再現しやすい baseline を作る。

### M4: embedding run

対象と公開境界が固まってから embedding を生成する。cache は commit しない。

### M5: 表示

単一の 2D map ではなく、レイヤー切替、近傍表、heatmap、根拠特徴の表示を優先する。

## 初期ディレクトリ方針

- `docs/`: 研究メモ、方針、結果、公開用文書。
- `experiments/`: 実験コード。raw/processed 本文と outputs は ignore。
- `scripts/`: repo 運用や検証用スクリプト。
- `memory.md`: 作業台帳。

## 成功条件

最初の実装段階では、少なくとも次を満たす。

- 先行 `Okyou` と別 repo として説明できる。
- どの本文が公開可能で、どれがローカル研究 cache か区別できる。
- semantic と style の結果を混同しない。
- 結果ごとに未検証点を明記する。
