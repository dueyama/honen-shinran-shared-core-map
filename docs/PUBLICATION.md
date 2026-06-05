# GitHub Pages 公開準備

## 公開入口

- `docs/index.html`: 日本語トップ
- `docs/en/index.html`: English top
- `docs/paper/index.html`: 日本語HTML論文
- `docs/paper/en/index.html`: English HTML access version
- `docs/paper/okyou2-honen-shinran-paper-v3.pdf`: 日本語PDF
- `docs/paper/okyou2-honen-shinran-paper-v3.tex`: 日本語TeX
- `docs/paper/okyou2-honen-shinran-english-terminology.md`: 英語版訳語メモ
- `docs/source-provenance.html`: 公開用出典・検証サマリ
- `docs/errata.html`: リリース後エラッタ
- `docs/ERRATA.md`: エラッタ記録のMarkdown原本

## GitHub Pages 設定

1. GitHub に repository を作成する。
2. `main` を push する。
3. Repository settings -> Pages で `Deploy from a branch` を選ぶ。
4. Branch は `main`、folder は `/docs` を選ぶ。
5. 公開URLで `index.html`, `en/`, `paper/`, `paper/en/`, PDF, 主要図を確認する。

## リリース後の運用

- リリース後の公開版PDF/HTMLは固定版として扱う。
- 誤記、リンク切れ、図表ラベル、数値、補足説明、解釈変更が見つかった場合は、公開済み本文を黙って差し替えず、`docs/ERRATA.md` と `docs/errata.html` に記録する。
- 本文更新が必要な場合は、新しい版として明示し、旧版との差分と理由をエラッタに残す。
- GitHub Release または tag を切る場合は、そのtagを固定版の参照点とする。

## 公開しないもの

- `.env`
- API key / token
- SAT等から取得した raw/processed 本文
- chunk preview
- embedding cache / embedding vector
- ローカル絶対パスを含む研究用出力

## 英語版方針

日本語v3 PDFを引用・精読用の正本とし、英語HTMLは access version として提供する。英語版PDF/TeXは次の公開準備段階で作成できる。
