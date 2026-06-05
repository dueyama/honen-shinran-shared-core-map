# AI Researcher Guide

この文書は、他の研究者が本リポジトリをAIエージェントや大規模言語モデルに読ませ、法然・親鸞比較レポートを説明・点検・再生成・発展させるための案内である。人間向けの概要は `README.md`、公開前チェックは `docs/PUBLICATION.md`、固定公開物のハッシュは `docs/checksums.txt` を参照する。

## Intended Use

AIにこのリポジトリを読ませる場合は、次の目的を想定する。

- 公開論文、図表、HTML/PDF、英語AI支援翻訳版の内容を説明する。
- 法然『選択本願念仏集』と親鸞『教行信証』の共有核とはみ出し領域を、過大評価せずに要約する。
- 意味層、文体語彙層、典拠マーカー層を混同せずに読む。
- 公開版HTML、英語版TeX/PDF、英語ラベル図、Errataページを再生成する。
- raw/processed本文、chunk preview、embedding cache/vector、API keyが公開候補に入っていないか確認する。
- 今後の追試や発展案を、本文提供元の利用条件と公開境界を守って設計する。

このリポジトリは、AIが仏教学的・文献学的結論を自律的に確定するためのものではない。研究者が問い、対象文献、解釈、公開判断を行い、AIは実装、集計、可視化、文書化、検証、査読補助を担当する。

## First Files To Read

AIには、まず次の順番で読ませるとよい。

1. `README.md`
   - プロジェクトの位置づけ、方法上の立場、公開物、再現前提、ライセンス。
2. `docs/paper/honen-shinran-shared-core-paper.tex`
   - 日本語正式版論文。引用・精読・ニュアンス確認ではこれを主本文とする。
3. `docs/paper/honen-shinran-shared-core-paper-en.tex`
   - 英語AI支援翻訳版。英語読者向けの補助本文。
4. `docs/paper/index.html` と `docs/paper/en/index.html`
   - GitHub Pagesで読むHTML論文。
5. `docs/source-provenance.html`
   - 公開用の短い出典・検証サマリ。
6. `docs/source-provenance.md`
   - 詳細な検証記録。raw本文は含めない方針で書かれている。
7. `docs/PUBLICATION.md`
   - 公開対象、公開しないもの、GitHub Pages設定、公開前チェック。
8. `docs/checksums.txt`
   - 固定公開物のSHA-256記録。
9. `scripts/check_publication_safety.py`
   - push前安全検査。
10. `scripts/build_public_pages.py`
   - 公開HTML、Errata、ライセンス、Publication文書の生成。
11. `scripts/build_english_tex_from_ja_tex.py`
   - 日本語TeXを構造上の正本として英語TeXを生成するスクリプト。
12. `scripts/make_english_public_figures.py`
   - 英語ラベル図の生成。

`memory.md` は、Codex支援作業の日時、変更概要、検証内容を記録した制作・検証記録である。制作過程を追跡するには有用だが、最初の内容理解では上記の公開文書と論文TeXを優先する。

## Current Public Artifacts

主要な公開成果物は次の通りである。

- GitHub Pagesトップ: `docs/index.html`
- English GitHub Pagesトップ: `docs/en/index.html`
- 日本語HTML論文: `docs/paper/index.html`
- 日本語PDF論文: `docs/paper/honen-shinran-shared-core-paper.pdf`
- 日本語TeX本文: `docs/paper/honen-shinran-shared-core-paper.tex`
- 英語AI支援翻訳版HTML: `docs/paper/en/index.html`
- 英語AI支援翻訳版PDF: `docs/paper/honen-shinran-shared-core-paper-en.pdf`
- 英語AI支援翻訳版TeX: `docs/paper/honen-shinran-shared-core-paper-en.tex`
- 日本語ラベル図: `docs/figures/*.png`
- 英語ラベル図: `docs/figures/en/*.png`
- 出典・検証サマリ: `docs/source-provenance.html`
- Errata: `docs/errata/index.html`, `docs/errata/en/index.html`, `docs/ERRATA.md`
- ライセンス表示: `docs/license.html`
- 固定公開物チェックサム: `docs/checksums.txt`

日本語PDFを正式な製本版とし、英語PDF/HTMLはAI支援翻訳版として扱う。英語版はアクセス補助であり、引用や細かなニュアンス確認では日本語版を主本文とする。

## What Is Not In The Public Repo

次のものは公開・追跡しない。

- `.env`
- API key / token
- SAT、J-SOKEN、84000、聖教電子化研究会などから取得したraw本文
- processed本文
- chunk preview
- embedding cache
- embedding vector
- `data/` 以下のローカル研究用出力
- TeX中間生成物
- ローカル絶対パスを含む研究用出力

AIエージェントは、これらをgitに追加してはならない。本文を再取得・再処理する場合は、各提供元の利用条件を確認し、raw本文やprocessed本文を公開commitに含めない。

## Minimal Public Check Path

公開候補を点検するだけなら、まず次を実行する。

```bash
git status --short
git status --ignored=matching --short
python3 -m py_compile scripts/*.py
python3 scripts/check_publication_safety.py
git diff --check
```

`check_publication_safety.py` は、tracked files と `.gitignore` で除外されていない untracked files を公開候補として検査する。禁止パス、秘密情報らしき文字列、長いfloat vector、checksum不一致、ローカルHTMLリンク切れ、20MB超ファイル、公開docs内のローカル絶対パスを検出した場合は失敗する。

## Rebuilding Public Pages

公開HTML、Errata、ライセンスページ、Publication文書を再生成する場合:

```bash
python3 scripts/build_public_pages.py
python3 scripts/check_publication_safety.py
```

英語版TeXを日本語TeXの構造に合わせて再生成する場合:

```bash
python3 scripts/build_english_tex_from_ja_tex.py
```

英語ラベル図を再生成する場合:

```bash
python3 scripts/make_english_public_figures.py
```

これらは既存の本文なし派生データと公開用TeX/HTMLを扱う作業であり、通常はOpenAI APIを再実行しない。

## Rebuilding PDFs

PDFを再生成する場合は、ローカルに `upLaTeX + dvipdfmx` が必要である。

```bash
cd docs/paper
uplatex -interaction=nonstopmode honen-shinran-shared-core-paper.tex
uplatex -interaction=nonstopmode honen-shinran-shared-core-paper.tex
dvipdfmx honen-shinran-shared-core-paper.dvi

uplatex -interaction=nonstopmode honen-shinran-shared-core-paper-en.tex
uplatex -interaction=nonstopmode honen-shinran-shared-core-paper-en.tex
dvipdfmx honen-shinran-shared-core-paper-en.dvi
```

LaTeX中間ファイルはgit管理しない。PDFを更新した場合は、`docs/checksums.txt`、`README.md`、`docs/source-provenance.md`、`memory.md` のハッシュ・検証記録を更新する。

## Full Re-run With Embeddings

埋め込みを再生成する場合は、OpenAI API key が必要である。`.env` に `OPENAI_API_KEY` を置く場合でも、`.env` は絶対にcommitしない。

現在の公開論文は、SAT漢文系本文、Unicode-safe 700-token chunk、100-token overlap、OpenAI `text-embedding-3-large`、PCA 2D投影、近傍集計、語群カウント、典拠マーカー集計を使っている。再実行時には、次の点を必ず記録する。

- 対象文献と出典URL
- 利用条件と公開境界
- chunking policy
- embedding model
- vector dimension
- chunk数
- PCAなどの投影法
- 出力JSON/CSVにraw text、body、preview、embedding vectorが含まれないこと
- `U+FFFD` の混入有無

API再実行が必要な場合は、既存cacheの利用可否を確認し、再課金・再生成の理由を記録する。

## Interpretation Rules

AIは次の点を守って解釈する。

- この研究は、AIに仏教文献の解釈を任せるものではない。
- 図や数値は結論ではなく、読む場所を探すための地図である。
- 意味埋め込みの近さは、引用、影響、典拠関係を直接証明しない。
- PCA 2D図は探索的投影であり、3072次元空間の全構造を示すものではない。
- 文体語彙層は厳密なstylometryではなく、辞書ベースの教義語群カウントproxyである。
- 典拠マーカー層は経名、祖師名、引用導入句などの明示マーカーであり、引用研究そのものではない。
- 「法然が親鸞に近い」という表現は影響史の向きを誤読させやすい。必要に応じて「法然チャンクの多くは、後代の親鸞文献チャンクと意味的に強く重なる」と表現する。
- 既存の歴史研究・引用研究との照合は、この手法の信頼性と限界を検証する次段階の課題である。
- 英語版はAI支援翻訳であり、日本語版が主本文である。

## Publication And Errata Rules

公開後のPDF/HTMLは固定版として扱う。誤記、リンク切れ、図表ラベル、数値、補足説明、解釈変更が見つかった場合は、公開済み本文を黙って差し替えず、`docs/ERRATA.md` と `docs/errata/` に記録する。

固定公開物のSHA-256は `docs/checksums.txt` に記録されている。公開tagまたはGitHub Releaseを作る場合は、tag上のPDF/TeXがこのハッシュと一致することを確認する。

## Good Extension Ideas

このrepoから自然に発展できる方向は次の通りである。

- 法然側corpusの拡張。
  - 『黒谷上人語灯録』系資料、『三部経釈』などを、本文品質と利用条件を確認した上で追加する。
- 親鸞側の精密化。
  - 『教行信証』巻別、引用文/地文分離、三部経引用との照合を行う。
- 高僧アンカーの拡張。
  - 龍樹、天親、曇鸞、道綽、善導、源信に加え、関連注釈・異本・引用研究と比較する。
- 方法検証。
  - chunk size sensitivity、自然単位chunk、別embedding model、PCA以外のUMAP/t-SNE/MDSなどを比較する。
- 三層分析の強化。
  - 意味層、文体語彙層、典拠マーカー層をより明確に分離し、各層の一致/不一致を表にする。
- 公開viewerの強化。
  - 巻別表示、層別表示、filter、近傍表、共有核/はみ出し領域の切替を追加する。
- 既存研究との照合。
  - 藤原智「『教行信証』における引用文について：古写経本による再検討」など、引用研究の成果と探索結果を比較する。

## Suggested Initial Prompt For AI

研究者が別のAIにこのrepoを渡す場合、次のようなプロンプトから始めるとよい。

```text
このリポジトリは、法然『選択本願念仏集』と親鸞『教行信証』を、
意味埋め込み、文体語彙、典拠マーカーの三層で比較する公開リポジトリです。

まず README.md と AI_RESEARCHER_GUIDE.md を読み、その後
docs/paper/honen-shinran-shared-core-paper.tex、
docs/paper/honen-shinran-shared-core-paper-en.tex、
docs/PUBLICATION.md、docs/checksums.txt、docs/source-provenance.html を読んでください。

目的は、既存成果を過大評価せずに説明し、公開境界を守りながら、
再現可能性・安全性・今後の発展案を整理することです。

守ること:
- .env、API key、raw/processed本文、chunk preview、embedding cache/vector、data/ をcommitしない。
- 意味埋め込みの近さを引用・影響・典拠関係の証明として扱わない。
- 日本語版PDF/TeXを主本文として扱い、英語版はAI支援翻訳版として扱う。
- 公開前に python3 scripts/check_publication_safety.py を実行する。
- 公開後の訂正はErrataとして扱う。

まず、現在の公開物、再現コマンド、公開しないもの、未検証点、発展案を短く要約してください。
```

## Suggested Review Prompt

論文や結果をAIに査読させる場合は、次の観点を指定するとよい。

```text
この論文を、デジタル人文学・仏教学・NLPの探索的研究として査読してください。
新規性を過大評価していないか、意味埋め込みと典拠研究を混同していないか、
法然と親鸞の関係を影響史として断定しすぎていないか、
図表から読めることと読めないことが区別されているか、
本文再配布制限と出典クレジットが十分かを確認してください。

改善提案は、公開前に必要な修正、公開後Errataで足りる修正、
次版以降の追試・追加図・追加対照実験に分けてください。
```

## License Summary

コードは MIT License、論文・図表・公開文書・制作プロセス・引用メタデータ・公開用派生データは CC BY 4.0 である。SAT、J-SOKEN、84000、聖教電子化研究会などから取得した元本文は、本リポジトリでは再配布せず、本リポジトリのライセンス対象外である。
