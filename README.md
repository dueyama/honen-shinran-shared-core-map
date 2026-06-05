# 法然・親鸞の共有核とはみ出し領域

三層探索地図による『選択集』・『教行信証』比較の論文・図表・再現用コードをまとめた公開準備リポジトリです。意味埋め込み、語群カウント、典拠マーカーを重ね、法然『選択本願念仏集』と親鸞『教行信証』が共有する念仏圏と、そこからのはみ出し領域を探索的に可視化します。

This repository contains the paper, figures, publication pages, and reproducibility scripts for an exploratory three-layer comparison of Honen's *Senchaku Hongan Nembutsu Shu* and Shinran's *Ken Jodo Shinjitsu Kyo Gyo Sho Monrui* (*Kyogyoshinsho*). It uses semantic embeddings, lexical-thematic counts, and source-marker features to examine their shared core and divergence zones.

## Project Position / プロジェクトの位置づけ

This work is a follow-up to the previous public project, [意味埋め込みによる仏教文献の探索地図](https://dueyama.github.io/buddhist-text-embedding-map/). The previous project is treated as a completed and released publication, not as a working branch of this repository. This repository narrows the question to Honen and Shinran and develops the three-layer reading of semantic, lexical-thematic, and source-marker evidence.

本研究は、先行公開プロジェクト [意味埋め込みによる仏教文献の探索地図](https://dueyama.github.io/buddhist-text-embedding-map/) の後続研究です。ただし、先行プロジェクトを継続編集するものではなく、別個の公開物として、法然と親鸞の比較に対象を絞っています。先行研究で得られた公開方式、本文非再配布方針、埋め込み地図の限界認識を引き継ぎながら、意味層・文体語彙層・典拠マーカー層を分けて読むことを試みます。

The research questions, corpus choices, interpretation, and publication direction were guided by Daishin Ueyama. Code, figures, paper drafts, English translation, and publication pages were developed through iterative work with Codex and review-style exchanges with ChatGPT Pro. The repository is therefore also a process record for producing a humanities data-analysis paper with AI assistance.

研究上の問い、対象文献の選定、解釈、公開方針は上山大信の判断にもとづきます。コード、図表、論文草稿、英語版、公開ページは Codex との反復作業と ChatGPT Pro による査読形式の検討を通じて整えました。その意味で、本リポジトリは、AI支援による人文系データ解析論文制作の過程記録でもあります。

## Methodological Note / 方法上の立場

このプロジェクトは、AI に仏教文献の解釈を任せることを目的としたものではありません。むしろ、本文をチャンク化し、意味埋め込みによる近傍構造を作り、そこに語彙・典拠マーカー・文献単位の情報を重ねることで、人間が読み直すべき箇所を探すための探索地図を作る試みです。

人文学的な解釈には、問いの立て方、対象文献の選び方、先行研究の系譜、研究者ごとの重みづけが必ず入ります。本プロジェクトが期待しているのは、それらを消すことではなく、解釈が分岐する前に、本文側にどのような意味的地形があるのかを、できるだけ再現可能な形で見てみることです。

もちろん、現在の埋め込みモデルにはモデルごとの癖があります。チャンク化、前処理、対象文献、投影法によっても結果は変わります。したがって、本プロジェクトの図や数値は、教義史的結論、影響関係、引用関係を直接証明するものではありません。

ただし、複数のモデルや条件をまたいで安定して現れる近傍構造があるなら、それは単なる可視化上の偶然ではなく、本文読解に戻るための有用な制約条件になるかもしれません。その意味で、埋め込みによる文献比較は、解釈を一意に決める技術ではなく、複数の研究者が同じ地図を前に議論するための共通座標系になりうると考えています。

このリポジトリの図や数値は、結論ではありません。読む場所を探すための地図です。

---

This project does not aim to delegate the interpretation of Buddhist texts to AI. Rather, it divides texts into chunks, represents them in an embedding space, and overlays lexical, source-marker, and bibliographic information in order to build exploratory maps for human readers.

Humanistic interpretation inevitably depends on research questions, corpus selection, scholarly traditions, and the reader's own weighting of passages. The aim of this project is not to remove such interpretation, but to observe, in a reproducible way, some of the semantic terrain of the texts before interpretations begin to diverge.

Of course, current embedding models have their own biases. Results may also change depending on chunking, preprocessing, corpus selection, and projection methods. The figures and statistics in this project therefore do not directly prove doctrinal conclusions, historical influence, or citation relationships.

Still, if certain neighborhood structures remain stable across multiple models and conditions, they may be more than accidental visual patterns. They may serve as useful constraints for returning to close reading. In this sense, embedding-based comparison is not a technology for deciding interpretation once and for all, but may become a shared coordinate system for discussion among human readers.

The figures and numbers in this repository are not conclusions. They are maps for finding where to read next.

## Public Artifacts

- GitHub Pages entry point: `docs/index.html`
- English GitHub Pages entry point: `docs/en/index.html`
- Japanese HTML paper: `docs/paper/index.html`
- Japanese paper PDF: `docs/paper/honen-shinran-shared-core-paper.pdf`
- Japanese paper TeX: `docs/paper/honen-shinran-shared-core-paper.tex`
- English AI-assisted translation HTML: `docs/paper/en/index.html`
- English AI-assisted translation PDF: `docs/paper/honen-shinran-shared-core-paper-en.pdf`
- English AI-assisted translation TeX: `docs/paper/honen-shinran-shared-core-paper-en.tex`
- English figure variants: `docs/figures/en/*.png`
- Source provenance and verification notes: `docs/source-provenance.html`
- Errata pages: `docs/errata/index.html`, `docs/errata/en/index.html`
- License page: `docs/license.html`
- Publication checksum record: `docs/checksums.txt`
- AI researcher guide: `AI_RESEARCHER_GUIDE.md`

The Japanese paper PDF is the authoritative print/book edition. The English paper is provided as an AI-assisted translation for access by English-language readers; when citing or checking nuance, use the Japanese edition as the primary text.

日本語論文PDFを正式な製本版とし、英語版PDF/HTMLは英語読者のためのAI支援翻訳版として公開します。引用や細かなニュアンス確認では、日本語版を主たる本文として扱ってください。

## Publication Integrity / 公開版の固定

The public PDF and TeX files use stable filenames without version numbers. They are fixed at release tag `v1.0.0`, and their SHA-256 checksums are recorded in `docs/checksums.txt`:

```text
886dd089af33a17f4a983795d6d1d38730f309fc5c1ebc49e36a1dbc6b7c1b34  docs/paper/honen-shinran-shared-core-paper.pdf
ed5880e1d25a8c4c87bca53203cbed3000bb856484e062078acd06a69ceb1e6a  docs/paper/honen-shinran-shared-core-paper.tex
28291b93d8496096d67cce85f1dea2b3c53db4b314c93ea50ccdc1ee8d8831a8  docs/paper/honen-shinran-shared-core-paper-en.pdf
02ecbc972ab00ad7daf8b7e1aab7ff3bfbfd227b15f736c2607dab5757044c9f  docs/paper/honen-shinran-shared-core-paper-en.tex
```

The checksums above match the PDF/TeX files stored at git tag `v1.0.0`. After public release, later corrections should be published as supplements or Errata rather than silent rewrites of the fixed public artifacts. If a revised edition is necessary, it should be released as a new explicit version with a reason and difference record.

公開PDF/TeXは、安定したファイル名のまま git tag `v1.0.0` で固定します。上記のSHA-256ハッシュは、`v1.0.0` に含まれるPDF/TeXと一致します。公開後の訂正は、固定公開物を黙って差し替えるのではなく、追補または Errata として公開します。本文更新が必要な場合は、新しい版として明示し、旧版との差分と理由を残します。

This repository also treats the publication method itself as an experiment: a humanities data-analysis paper is published through GitHub Pages and GitHub Releases, while git history, release tags, checksums, and process notes make the public artifact and later supplements traceable.

本リポジトリでは、この公開方法そのものも試行対象としています。人文系データ解析論文を GitHub Pages と GitHub Releases で公開し、git履歴、release tag、checksum、制作記録によって、公開版と後続の追補を追跡できる形にします。

## Repository Layout

- `docs/`: GitHub Pages site, paper HTML/PDF/TeX, figures, errata, provenance, and license pages
- `docs/figures/`: Japanese public figures
- `docs/figures/en/`: English-labeled public figures for the English translation
- `docs/paper/`: Japanese and English paper artifacts
- `scripts/`: analysis, figure generation, TeX/HTML generation, and publication safety checks
- `experiments/`: placeholder for experiment code organization
- `AI_RESEARCHER_GUIDE.md`: guide for AI-assisted review, reproduction, and extension
- `memory.md`: project ledger for the Codex-assisted workflow
- `AGENTS.md`: working rules for AI agents in this repository

## Reproducibility

The public paper was generated from local SAT-derived text preparation, Unicode-safe 700-token chunking with 100-token overlap, OpenAI `text-embedding-3-large`, PCA projection for 2D visualization, and text-free derived analysis outputs.

Private raw/processed source texts, chunk previews, and embedding caches are intentionally not included. Rebuilding the full analysis requires local source acquisition under each provider's terms of use and an OpenAI API key.

Publication-page and safety checks can be run with:

```bash
python3 scripts/build_public_pages.py
python3 scripts/check_publication_safety.py
```

The safety check examines tracked files plus untracked files not excluded by `.gitignore`. It fails on forbidden publication paths, secret-like tokens, long vector-like arrays, checksum mismatches, broken local HTML links, oversized files, and local absolute path markers in public docs.

## Publication Policy

This repository is prepared for public GitHub/GitHub Pages use, but it does not redistribute raw source texts from SAT, J-SOKEN, 84000, or other providers. Public artifacts omit raw text, processed text, chunk previews, embedding caches, embedding vectors, and local source paths.

Before the first public push, run:

```bash
python3 scripts/check_publication_safety.py
git status --ignored=matching --short
```

Confirm that `data/`, `.env`, TeX intermediate files, `tmp/`, and Python caches are ignored and that the safety check passes.

See `docs/PUBLICATION.md` for the publication checklist.

## GitHub Pages

Public repository: `https://github.com/dueyama/honen-shinran-shared-core-map`

Planned public site: `https://dueyama.github.io/honen-shinran-shared-core-map/`

Use GitHub Pages with:

- Source: `main` branch
- Folder: `/docs`

After publication, confirm that the landing page, Japanese/English paper pages, PDF links, figures, provenance page, errata pages, and license page load correctly.

## License

This repository uses a split license.

- Code is licensed under the MIT License. See `LICENSE-CODE`.
- The paper, figures, documentation, process records, citation metadata, and public derived data are licensed under Creative Commons Attribution 4.0 International (CC BY 4.0). See `LICENSE-CONTENT`.
- Source texts retrieved from SAT, J-SOKEN, 84000, or other providers are not redistributed here and are not covered by this repository's licenses.

本リポジトリは分割ライセンスを採用しています。

- コードは MIT License です。`LICENSE-CODE` を参照してください。
- 論文、図表、公開文書、制作プロセス、引用メタデータ、公開用派生データは Creative Commons Attribution 4.0 International (CC BY 4.0) です。`LICENSE-CONTENT` を参照してください。
- SAT、J-SOKEN、84000 などから取得した元本文は本リポジトリでは再配布しておらず、本リポジトリのライセンス対象外です。
