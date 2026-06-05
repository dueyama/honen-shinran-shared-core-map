# 法然・親鸞論文 英語版用語メモ

作成日: 2026-06-05

このメモは、公開用TeX `honen-shinran-shared-core-paper.tex` を英語版へ展開する際の訳語を固定するための公開可能な補助メモである。本文、processed text、chunk preview、embedding vector は含めない。

## 推奨タイトル

第一候補:

```text
Shared Core and Divergence Zones in Honen and Shinran:
A Three-Layer Exploratory Map of the Senchakushu and Kyogyoshinsho
```

方法寄りの候補:

```text
Mapping the Shared Core and Divergence Zones of Honen and Shinran:
A Three-Layer Analysis of the Senchakushu and Kyogyoshinsho
```

## 中心用語

| 日本語 | 英語版の推奨訳 | 備考 |
|---|---|---|
| 共有核 | shared core | タイトル・要旨で使用する。 |
| はみ出し領域 | divergence zones | タイトル・結果・考察ではこの訳を優先する。 |
| 相対的突出領域 | relative protrusion zones | 方法節・スコア説明で使用する。 |
| 三層探索地図 | three-layer exploratory map | タイトル・方法節向き。 |
| 意味層 | semantic layer | 埋め込み近傍とPCA図を含む。 |
| 文体語彙層 | lexical-thematic layer | strict stylometry と誤読されないようにする。 |
| 典拠マーカー層 | source-marker layer | citation detection ではないことを明記する。 |
| 最近傍非自己 | nearest neighbor outside the same author group | "non-self neighbor" は避ける。 |
| 祖師文献アンカー | Pure Land patriarchal text anchors | 初出で Pure Land を付ける。 |
| 選択論証 | argument for the selection of nembutsu | selection logic より説明的。 |
| 本願・信・証の典拠的体系 | source-based doctrinal architecture of vow, shinjin, and realization | 初出で説明を添える。 |

## 英語要旨の方針

英語版の要旨は、日本語要旨の逐語訳ではなく 250--300 words 程度に圧縮する。構成は次の順にする。

1. Honen and Shinran share a large semantic core.
2. The central question is not whether they overlap, but where each text diverges from that shared core.
3. The paper uses three layers: semantic similarity, lexical-thematic markers, and explicit source markers.
4. Honen's divergence zones concentrate around the argument for selecting nembutsu from among other practices.
5. Shinran's divergence zones concentrate around the Shin and Keshindo fascicles, expanding toward a source-based doctrinal architecture.
6. The result is exploratory and does not replace doctrinal, historical, or citation-based scholarship.

## 表記方針

- 人名は本文では `Honen`, `Shinran` とし、必要に応じて初出で長音記号つきの `Hōnen` を併記する。
- 書名はローマ字を基本にし、初出で日本語名を添える。
- `Senchakushu` は `Senchakushu (Senchaku Hongan Nembutsu Shu)` と説明する。
- `Kyogyoshinsho` は `Kyogyoshinsho (Ken Jodo Shinjitsu Kyogyosho Monrui)` と説明する。
- `lexical-thematic layer` は辞書ベースの語群カウントであり、strict stylometry ではないと繰り返す。
- `source-marker layer` は citation detection ではなく、explicit markers for locating candidates と説明する。
