# Kanbun Text Preparation 2026-06-03

## 目的

法然『選択本願念仏集』と親鸞『教行信証』について、embedding や map を作る前に、解析に使ってよい漢文系本文をローカルで準備する。

ここでは API を呼ばない。本文取得、SAT HTML からの行単位抽出、品質検査、ローカル出力だけを行う。

## 対象

- 法然『選択本願念仏集』
  - SAT: `T2608`
  - 原題表記: `選擇本願念佛集`
  - Source: `https://21dzk.l.u-tokyo.ac.jp/SAT/T2608.html`
- 親鸞『教行信証』
  - SAT: `T2646`
  - 原題表記: `顯淨土眞實教行證文類`
  - Source: `https://21dzk.l.u-tokyo.ac.jp/SAT/T2646_,83,0589a01:2646_,83,0643c29.html`

## 出力

ローカル専用。`data/` 以下なので commit / publish しない。

- `data/processed/sat_kanbun/honen_t2608_senchakushu.txt`
- `data/processed/sat_kanbun/honen_t2608_senchakushu.lines.jsonl`
- `data/processed/sat_kanbun/shinran_t2646_kyogyoshinsho.txt`
- `data/processed/sat_kanbun/shinran_t2646_kyogyoshinsho.lines.jsonl`
- `data/processed/sat_kanbun/manifest.json`

`.txt` は本文のみを SAT 行単位で改行したもの。`.lines.jsonl` は `line_ref`, `text`, `text_sha256` を持つ。解析時は `.lines.jsonl` を使えば、chunk と原SAT行の対応を失わない。

## 品質検査

次が本文内に残っていないことを検査した。

- replacement character: `U+FFFD`
- HTML tag
- HTML entity
- image placeholder
- button label
- SAT line ref の本文混入
- control character
- empty text
- no lines parsed

結果:

| SAT | status | lines | compact chars | first line | last line | issues |
| --- | --- | ---: | ---: | --- | --- | ---: |
| T2608 | ok | 1644 | 27246 | `T2608_.83.0001a04` | `T2608_.83.0020b14` | 0 |
| T2646 | ok | 4215 | 76030 | `T2646_.83.0589a04` | `T2646_.83.0643a23` | 0 |

## 注意

この準備済み本文は、以前の seiten 日本語読み本文とは別系統である。今後、法然・親鸞の主分析はこの SAT 漢文系本文を基準に作り直す。

既に生成済みの seiten 読み下しベース地図は、探索・比較用の旧runとして扱う。漢文系の解析結果として引用しない。

また、2026-06-03 に一度作った SAT 漢文系 embedding map は、chunk 生成の試行段階で任意 token 境界を使っていたため、採用しない。今後の embedding は、この文書の品質検査を通った `data/processed/sat_kanbun/*.lines.jsonl` から、Unicode 文字境界で丸めた 700 token 近似 chunk として実行する。行単位 chunk は、必要が出た場合の別実験として扱う。

## 再実行

```bash
python3 scripts/prepare_sat_kanbun_texts.py
```

このコマンドは API を呼ばない。
