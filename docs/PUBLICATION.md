# GitHub Pages 公開準備

## 公開入口

- `docs/index.html`: 日本語トップ
- `docs/en/index.html`: English top
- `docs/paper/index.html`: 日本語HTML論文（公開TeXから生成）
- `docs/paper/en/index.html`: English HTML paper generated from English TeX
- `docs/paper/honen-shinran-shared-core-paper.pdf`: 日本語PDF
- `docs/paper/honen-shinran-shared-core-paper.tex`: 日本語TeX
- `docs/paper/honen-shinran-shared-core-paper-en.pdf`: English PDF
- `docs/paper/honen-shinran-shared-core-paper-en.tex`: English TeX generated from the Japanese TeX structure
- `docs/paper/okyou2-honen-shinran-english-terminology.md`: 英語版訳語メモ
- `docs/source-provenance.html`: 公開用出典・検証サマリ
- `docs/errata/index.html`: Errata
- `docs/errata/en/index.html`: English Errata
- `docs/ERRATA.md`: Errata記録のMarkdown原本
- `docs/license.html`: ライセンス表示
- `docs/checksums.txt`: 固定公開物のSHA-256記録
- `AI_RESEARCHER_GUIDE.md`: AIエージェント向け再現・点検・発展ガイド

## GitHub Pages 設定

Repository: `https://github.com/dueyama/honen-shinran-shared-core-map`

1. GitHub repository `dueyama/honen-shinran-shared-core-map` を使う。
2. push 前に `python3 scripts/check_publication_safety.py` を実行する。
3. `git status --ignored=matching --short` で `data/`, `.env`, TeX中間生成物, `tmp/` が `!!` 扱いであることを確認する。
4. `main` を push する。
5. Repository settings -> Pages で `Deploy from a branch` を選ぶ。
6. Branch は `main`、folder は `/docs` を選ぶ。
7. 公開URLで `index.html`, `en/`, `paper/`, `paper/en/`, PDF, 主要図を確認する。

## リリース後の運用

- リリース後の公開版PDF/HTMLは固定版として扱う。
- 誤記、リンク切れ、図表ラベル、数値、補足説明、解釈変更が見つかった場合は、公開済み本文を黙って差し替えず、`docs/ERRATA.md` と `docs/errata/` に記録する。
- 本文更新が必要な場合は、新しい版として明示し、旧版との差分と理由をErrataに残す。
- GitHub Release または tag を切る場合は、そのtagを固定版の参照点とする。

## 公開しないもの

- `.env`
- API key / token
- SAT等から取得した raw/processed 本文
- chunk preview
- embedding cache / embedding vector
- ローカル絶対パスを含む研究用出力

## ライセンス

- 解析コード: MIT License。リポジトリ直下の `LICENSE-CODE` を参照する。
- 論文、図表、公開文書、制作プロセス文書、引用メタデータ、公開用派生データ: Creative Commons Attribution 4.0 International (CC BY 4.0)。リポジトリ直下の `LICENSE-CONTENT` を参照する。
- SATなどから取得した元本文は本リポジトリでは再配布せず、本リポジトリのライセンス対象にも含めない。元本文の利用は各提供元の利用条件に従う。

## 英語版方針

英語版は、前稿と同じく英語読者のアクセス補助として作成するAI支援翻訳版である。公開用日本語TeXを構造上の正本とし、英語TeXは日本語TeXの章節・図表・label・参考文献順に揃えて生成する。英語PDFと英語HTMLは、その英語TeXから生成する。公開後は日本語版・英語版とも固定版として扱い、変更はErrataまたは新しい版で管理する。
