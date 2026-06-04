# Chunk Text Policy 2026-06-03

## 目的

embedding の chunk と実際の本文文字列の対応を失わないようにする。ただし、取得本文そのものは公開・commit しない。

## 現在の入力本文

法然『選択本願念仏集』と親鸞『教行信証』の初回 embedding run では、聖教電子化研究会 HTML から次の class を抽出した。

- `honbun`
- `s_sage`
- `l_nobegaki`

親鸞ページに含まれる `r_kanbun` は、重複を避けるため初回 run では除外した。法然『選択集』の seiten `z1-*` ページでは、確認した範囲で `r_kanbun` class は検出されない。

したがって、現在の法然/親鸞比較は「厳密な漢文本文同士」ではなく、seiten の日本語読み本文、つまり漢文訓読調の読み下し本文を対象にした比較である。

## chunk と本文の対応

各 chunk は次の情報で本文と対応づける。

- `chunk_id`
- `author`
- `work`
- `page_start`
- `page_end`
- `source_urls`
- `token_start`
- `token_end`
- `text_sha256`

公開用メタデータには raw text を含めない。`text_sha256` と token/page span で照合できるようにする。

## private index

必要に応じて、次のスクリプトでローカル専用の本文対応表を生成する。

```bash
/Users/daishin/.pyenv/shims/python scripts/export_private_chunk_text_index.py
```

出力:

- `data/outputs/PRIVATE_chunk_text_index_text-embedding-3-large_700_100.jsonl`

このファイルは実際の chunk 本文を含む。`data/` 以下なので commit しない。論文・公開 viewer・GitHub Pages 等には出さない。

## 今後の注意

漢文本文同士の比較が必要な場合は、少なくとも次を別 run として作る。

- 親鸞 seiten `r_kanbun` basis。
- 法然側の漢文相当テキストの取得元確認。
- SAT 等を使う場合は、法然『選択集』が対象DBにどの形であるか、また本文利用条件を確認する。

現在の意味マップは、読み下し本文ベースの semantic map として扱う。
