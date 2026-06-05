# Okyou2 Memory

## 2026-06-03 JST

- Summary: Initialized `Okyou2` as a new successor project, not a Git continuation of predecessor `Okyou`.
- Context:
  - Read the completed predecessor repository `Okyou`, including README, AI researcher guide, publication checklist, results, manifests, git remote/log status, and recent memory entries.
  - Initially cloned `Okyou` into `Okyou2`, then corrected course after clarifying that `Okyou2` is a successor but not a continuation.
  - Moved that mistaken clone to a temporary backup outside this repository.
  - Clarified that predecessor `Okyou` is released and closed; it is a read-only reference and must not be changed.
- Files prepared:
  - `README.md`
  - `AGENTS.md`
  - `.gitignore`
  - `docs/okyou1-reading-notes.md`
  - `docs/development-brief.md`
  - `memory.md`
- Verification:
  - Confirmed `Okyou2` is a new Git repository on `main` with no remote configured.
  - Confirmed no local absolute project paths, temporary backup paths, API-key env var names, or OpenAI API key pattern remained in the scaffold documents.
  - Ran `git diff --check`; no whitespace errors.
  - Listed scaffold files and confirmed only README/AGENTS/docs/memory/gitignore placeholders are present.
- Commit: see repository history.

## 2026-06-05 JST: English HTML Paper Expanded to Full Paper Structure

- Summary: Replaced the short English access-version paper page with a
  full-structure English HTML paper so it no longer looks like a different
  document from the Japanese PDF/HTML.
- Output:
  - `docs/paper/en/index.html` now follows the same paper structure as the
    Japanese PDF/TeX/HTML: abstract, 7 numbered sections, 25 subsections, 14
    tables, 5 figures, and 13 bibliography entries.
  - The English page uses the same table/figure numbering pattern and in-page
    anchors for figures, tables, and references.
  - This interim step kept the Japanese PDF as the formal citation base while
    presenting the English HTML as a full-structure access version, not as a
    short summary.
  - This was later superseded by the English TeX/PDF pipeline recorded below.
- Public boundary:
  - No OpenAI API calls.
  - No new source-text fetches.
  - No raw/processed source text, chunk previews, embedding caches, or
    embedding vectors were added.
- Verification:
  - `python3 -m py_compile scripts/build_public_pages.py`
  - `python3 scripts/build_public_pages.py`
  - Checked `docs/paper/en/index.html` for matching generated structure counts
    and zero actual replacement characters.
  - Checked `docs/paper/en/index.html` for leaked raw TeX commands; no matches.
  - Checked generated HTML relative links and page anchors; broken count 0.
  - Browser-rendered English page reported 14 tables, 5 figures, 14 captions,
    13 references, Georgia/Times body styling, 860px body width, no replacement
    characters, and no old short-access-version note.
  - Confirmed local and Tailscale preview HTTP 200 for `/paper/en/`.
  - Predecessor `../Okyou` remained unchanged.
- Commit: see repository history.

## 2026-06-05 JST: English TeX/PDF Built from Japanese TeX Structure

- Summary: Corrected the English publication pipeline so the English PDF and
  English HTML are both derived from English TeX, while the English TeX is
  generated against the Japanese TeX structural source.
- Files:
  - Added `scripts/build_english_tex_from_ja_tex.py`.
  - Added `docs/paper/honen-shinran-shared-core-paper-en.template.tex`.
  - Generated `docs/paper/honen-shinran-shared-core-paper-en.tex`.
  - Generated `docs/paper/honen-shinran-shared-core-paper-en.pdf`.
  - Updated `scripts/build_public_pages.py` so English HTML is generated from
    `docs/paper/honen-shinran-shared-core-paper-en.tex`.
  - Updated README, publication notes, provenance notes, and checksums for the
    English PDF/TeX.
- Pipeline:
  - Japanese TeX remains the structural source.
  - English wording is kept in the English template.
  - The generator checks that the English template matches the Japanese TeX
    section, subsection, table, figure, label, figure filename, and `bibitem`
    sequences before writing the public English TeX. English figure paths may
    point to `docs/figures/en/`.
  - English PDF is generated from the public English TeX with
    `uplatex`/`dvipdfmx`.
  - English HTML is generated from the public English TeX by
    `scripts/build_public_pages.py`.
- Verification:
  - `python3 -m py_compile scripts/build_english_tex_from_ja_tex.py scripts/build_public_pages.py`
  - `python3 scripts/build_english_tex_from_ja_tex.py`
  - `uplatex -interaction=nonstopmode honen-shinran-shared-core-paper-en.tex`
    twice.
  - `dvipdfmx honen-shinran-shared-core-paper-en.dvi`
  - `python3 scripts/build_public_pages.py`
  - Checked Japanese and English HTML counts: both have 7 numbered sections
    plus abstract and references, 25 subsections, 14 tables, 5 figures, and 13
    bibliography entries.
  - Checked generated HTML relative links and page anchors; broken count 0.
  - Checked English HTML for replacement characters and stale HTML-version
    wording; count 0.
  - Browser-verified `local HTTP preview`: English PDF link
    present, 9 h2, 25 h3, 5 figures, 14 tables, 14 captions, 13 references,
    no replacement characters, and no stale HTML-version wording.
  - Confirmed HTTP 200 for local and Tailscale English HTML/PDF preview URLs.
  - English PDF/TeX hashes recorded in `docs/checksums.txt`.
- Commit: see repository history.

## 2026-06-05 JST: Japanese HTML Paper Regenerated from Public TeX

- Summary: Replaced the Japanese paper HTML body with a TeX-derived conversion
  from `docs/paper/honen-shinran-shared-core-paper.tex`, because the previous
  HTML paper page was a web summary and could look like a different document
  from the PDF.
- Output:
  - `docs/paper/index.html` now follows the public TeX/PDF order from abstract
    through references.
  - The generated Japanese HTML contains 7 numbered sections plus abstract and
    references, 25 subsections, 14 tables, 5 figures, and 13 bibliography
    entries.
  - Figure/table/citation references are converted to in-page anchors.
  - The TeX-derived Japanese HTML uses a narrower paper-like body width and
    Mincho-style text rendering so it reads closer to the PDF paper, while
    remaining an HTML access version.
- Public boundary:
  - No OpenAI API calls.
  - No new source-text fetches.
  - No raw/processed source text, chunk previews, embedding caches, or
    embedding vectors were added.
- Verification:
  - `python3 -m py_compile scripts/build_public_pages.py`
  - `python3 scripts/build_public_pages.py`
  - Checked `docs/paper/index.html` for generated structure counts and zero
    actual replacement characters.
  - Checked `docs/paper/index.html` for leaked raw TeX commands; no matches.
  - Checked generated HTML relative links and page anchors; broken count 0.
  - Confirmed local/Tailscale preview HTTP 200 for `/paper/` and local HTTP 200
    for `/paper/honen-shinran-shared-core-paper.pdf`.
  - Browser-rendered page reported the TeX-derived structure, transparent
    abstract block, Mincho-family body, 860px body width, and no replacement
    characters.
  - `git diff --check`
  - Predecessor `../Okyou` remained unchanged.
- Commit: see repository history.

## 2026-06-04 JST: Paper Finalization Pass

- Summary: Moved `docs/paper/okyou2-honen-shinran-paper-v0.tex` closer to a submission-style manuscript by removing work-list and internal-note tone from the paper body.
- Text changes:
  - Replaced draft-like phrases such as `最小構成`, `今回`, `現段階`, and `ズレ` with paper-facing wording such as `基本構成`, `本分析`, `現行の処理`, and `対応しない箇所`.
  - Kept the core caveat that the argument is an embedding-based exploratory inference, not a conclusion verified through historical or citation studies.
  - Removed standalone future-work structure from the paper and folded remaining tasks into the `限界` section as methodological limitations.
- Figure changes:
  - Regenerated the high-priest anchor figure with a Japanese, paper-facing title: `SAT漢文・Unicode-safeチャンク地図：法然・親鸞・祖師文献`.
  - Reused existing caches only; no OpenAI API calls and no new source fetches.
- Verification:
  - `python -m py_compile scripts/analyze_nearest_neighbor_subsampling.py scripts/analyze_high_dim_isolation.py scripts/make_shared_core_bar_figure.py scripts/make_sat_safe_honen_shinran_focus_figure.py scripts/make_sat_safe_high_priest_anchor_map.py scripts/make_honen_three_layer_heatmap.py scripts/make_shinran_three_layer_heatmap.py`
  - `uplatex` twice and `dvipdfmx` once regenerated `docs/paper/okyou2-honen-shinran-paper-v0.pdf`.
  - Rendered the PDF to PNG with PyMuPDF and visually checked title, focus map, high-priest anchor map, shared-core/bar figure, three-layer figures, and conclusion/reference pages.
  - Checked generated JSON/CSV/Markdown outputs for forbidden raw fields (`text`, `body`, `embedding`, `preview`, `chunk_text`, `raw_text`) and `U+FFFD`.
  - `git diff --check` passed, and predecessor `../Okyou` had empty `git status --short`.
- Commit: see repository history.

## 2026-06-04 JST: Prior-Research Positioning Pass

- Summary: Incorporated the external positioning memo
  `okyou2-honen-shinran-prior-research-positioning.md`
  into the paper draft.
- Text changes:
  - Added `先行研究と本稿の位置づけ` to the introduction.
  - Clarified that the paper is not the first comparison of `選択集` and
    `教行信証`.
  - Positioned the contribution as re-placing existing comparison questions
    into whole-text chunk distribution, nearest-neighbor, anchor, vocabulary,
    and source-marker views.
  - Added a short caution that `親鸞側の展開` is not a value judgment that
    Shinran completed an incomplete Honen.
  - Added a positioning table linking prior-research concerns to the paper's
    computational views.
- Added references:
  - Moriwaki 1953, Inaba 1972, Umehara 1974, Asai 2004, Nezu 2024.
- Verification:
  - Bibliographic details were checked against INBUDS, Otani repository,
    Gyoshin journal list, NDL Search, and Books.or.jp where available.
  - `uplatex` twice and `dvipdfmx` once regenerated the PDF.
  - Rendered the PDF to PNG and visually checked pages 1--3 and 15--16.
  - `git diff --check` passed.
  - Predecessor `../Okyou` remained unchanged.
- Commit: see repository history.

## 2026-06-03 JST: Honen/Shinran Semantic Map and High-Priest Anchors

- Summary: Built the first Okyou2 semantic-map line of inquiry around Honen, Shinran, and Pure Land patriarch/source anchors.
- Method:
  - Followed predecessor `Okyou` baseline: `text-embedding-3-large`, `tiktoken` `cl100k_base`, 700-token chunks, 100-token overlap.
  - Used seiten HTML for Honen `選択本願念仏集` and Shinran `教行信証`.
  - Fit PCA on Honen/Shinran chunks only.
  - Projected SAT anchor texts for 龍樹, 天親, 曇鸞, 道綽, 善導, and 源信 into that fixed PCA plane.
- Outputs:
  - `data/outputs/honen_shinran_predecessor_style_embedding_map.png`
  - `data/outputs/honen_shinran_high_priest_anchor_map.png`
  - `docs/source-provenance.md`
  - `docs/working-summary-2026-06-03.md`
- Interpretation note:
  - Honen and Shinran overlap substantially, while Shinran spreads farther in the displayed map.
  - High-priest anchors suggest 善導/道綽 near the shared core, with 曇鸞 and 源信 closer to Shinran-side spread.
  - Treat this as semantic-layer evidence only; source-marker and style layers are still required before historical claims.
- Public boundary:
  - Raw text, processed text, embedding cache, and generated outputs remain local-only under ignored `data/`.
  - Do not publish or commit obtained texts.
- Verification:
  - Confirmed predecessor repo `../Okyou` had no local changes after reference reads.
  - Ran `git diff --check`; no whitespace errors.
- Commit: see repository history.

## 2026-06-03 JST: Shinran-Only Zone Summary

- Summary: Added a first-pass summary of map regions where Shinran chunks are far from Honen and high-priest/source anchor points.
- Method:
  - Used `data/outputs/honen_shinran_high_priest_anchor_map_meta.json`.
  - Selected Shinran chunks with nearest non-Shinran 2D PCA distance >= `0.10`.
  - Read local-only chunk text for keyword flags, but wrote no raw text to outputs.
- Outputs:
  - `scripts/summarize_shinran_isolated_zones.py`
  - `docs/shinran-isolated-zones-2026-06-03.md`
  - `data/outputs/shinran_isolated_zones_meta.json`
- Result:
  - Selected 20 Shinran chunks.
  - Initial zone labels: 行巻・真仏土の上方島, 信巻右下の阿闍世・涅槃経島, 化身土末の護法・鬼神・宇宙秩序島, 化身土末の外教批判島, 化身土本の方便・雑行島.
- Caveat:
  - This is a 2D semantic-layer diagnostic. High-dimensional nearest-neighbor checks and source-marker/style layers are still needed.
- Commit: see repository history.

## 2026-06-03 JST: SAT Kanbun Text Preparation

- Summary: Stopped analysis work and prepared clean SAT kanbun-basis texts before any further embeddings.
- Reason:
  - The earlier seiten run used Japanese reading text, not original kanbun.
  - A trial SAT embedding map was generated before a strict text-quality gate and should not be treated as an accepted result.
- Source texts:
  - SAT T2608 `選擇本願念佛集`.
  - SAT T2646 `顯淨土眞實教行證文類`, range `83:0589a01-0643c29`.
- Outputs:
  - `scripts/prepare_sat_kanbun_texts.py`
  - `data/processed/sat_kanbun/honen_t2608_senchakushu.txt`
  - `data/processed/sat_kanbun/honen_t2608_senchakushu.lines.jsonl`
  - `data/processed/sat_kanbun/shinran_t2646_kyogyoshinsho.txt`
  - `data/processed/sat_kanbun/shinran_t2646_kyogyoshinsho.lines.jsonl`
  - `data/processed/sat_kanbun/manifest.json`
  - `docs/kanbun-text-preparation-2026-06-03.md`
- Quality gate:
  - T2608: 1644 SAT lines, 27246 compact chars, 0 quality issues.
  - T2646: 4215 SAT lines, 76030 compact chars, 0 quality issues.
  - Checked for U+FFFD, HTML tags/entities, image placeholders, button labels, SAT line refs in body text, control characters, empty text, and missing parsed lines.
- Public boundary:
  - Processed text under `data/` contains source text and must not be committed or published.
- Next:
  - Rebuild embeddings only from the prepared `.lines.jsonl` files, using Unicode-safe near-700-token chunks.
- Commit: see repository history.

## 2026-06-03 JST: Predecessor Text Integrity Audit

- Summary: Audited predecessor `Okyou` read-only for token-boundary chunk decode noise.
- Reason:
  - Okyou2 trial SAT chunks showed `U+FFFD` when arbitrary token slices were decoded.
  - The predecessor method used the same fixed-token slice then `encoder.decode()` pattern.
- Outputs:
  - `scripts/audit_predecessor_text_integrity.py`
  - `docs/predecessor-text-integrity-audit-2026-06-03.md`
  - `data/outputs/predecessor_text_integrity_audit.json`
- Findings:
  - Predecessor processed body texts had 0 `U+FFFD` replacement characters.
  - `sect_sutra_map`: 256/433 reproduced chunks had `U+FFFD`, 326 replacement chars total.
  - `sect_sutra_map/outputs/embeddings.json`: 147/433 previews had `U+FFFD`, 173 replacement chars total.
  - `multilingual_sutra_map`: 44/105 reproduced chunks had `U+FFFD`, 58 replacement chars total.
- Interpretation:
  - The predecessor text bodies were not corrupt, but predecessor chunk embeddings included boundary-level decode noise.
  - Treat predecessor results as useful reference, not as a strict text-clean baseline for Okyou2.
- Verification:
  - No edits were made to `../Okyou`.
- Commit: see repository history.

## 2026-06-03 JST: SAT Chunking Strategy Comparison

- Summary: Compared old token-slice decode chunks against Unicode-safe near-700-token chunks on SAT T2608/T2646.
- Method:
  - Old: `cl100k_base` token ids sliced at 700 tokens with 100 overlap, then decoded.
  - New: same token grid, but chunk text boundaries are rounded to Python Unicode string offsets via `tiktoken.decode_with_offsets()`.
  - Embedded both with `text-embedding-3-large`.
- Outputs:
  - `scripts/compare_sat_chunking_strategies.py`
  - `docs/chunking-strategy-comparison-2026-06-03.md`
  - `data/outputs/sat_chunking_strategy_compare_text-embedding-3-large_700_100.json`
  - `data/outputs/sat_chunking_strategy_compare_text-embedding-3-large_700_100.svg`
  - `data/outputs/sat_chunking_strategy_compare_text-embedding-3-large_700_100.svg.png`
  - `data/cache/sat_chunking_strategy_compare_text-embedding-3-large_700_100.json`
- Findings:
  - Old method: 260 chunks, 148 affected chunks, 181 replacement chars.
  - New method: 260 chunks, 0 affected chunks, 0 replacement chars.
  - Same-index old/new cosine mean: 法然 `0.990319`, 親鸞 `0.990932`.
  - Old/new centroid cosine: 法然 `0.999352`, 親鸞 `0.999443`.
- Interpretation:
  - The replacement-character issue is real text-quality debt, but it barely moves the large-scale embedding geometry in this comparison.
  - Use Unicode-safe near-700-token chunks as Okyou2's fixed-length baseline; keep row/natural-unit chunks as separate experiments.
- Commit: see repository history.

## 2026-06-03 JST: SAT Safe High-Priest Anchor Map

- Summary: Rebuilt the Honen/Shinran + high-priest overlay on the accepted SAT kanbun safe-chunk baseline.
- Method:
  - Focus: SAT T2608 法然 `選擇本願念佛集`, SAT T2646 親鸞 `顯淨土眞實教行證文類`.
  - Anchors: 龍樹 T1521 易行品 range, 天親 T1524, 曇鸞 T1819, 道綽 T1958, 善導 T1753, 源信 T2682.
  - Chunking: Unicode-safe near-700-token chunks, overlap 100.
  - Embedding: `text-embedding-3-large`.
  - PCA fit: 法然・親鸞 chunks only; anchor chunks projected into that fixed plane.
- Outputs:
  - `scripts/make_sat_safe_high_priest_anchor_map.py`
  - `docs/sat-safe-high-priest-anchor-map-2026-06-03.md`
  - `data/outputs/sat_safe_honen_shinran_high_priest_anchor_map_text-embedding-3-large_700_100.svg`
  - `data/outputs/sat_safe_honen_shinran_high_priest_anchor_map_text-embedding-3-large_700_100.svg.png`
  - `data/outputs/sat_safe_honen_shinran_high_priest_anchor_map_text-embedding-3-large_700_100.json`
  - `data/cache/sat_safe_high_priest_anchor_embeddings_text-embedding-3-large_700_100.json`
- Results:
  - Chunk counts: 法然 69, 親鸞 191, 龍樹 6, 天親 9, 曇鸞 31, 道綽 42, 善導 23, 源信 73.
  - PCA fit-scope PC1 `0.068562`, PC2 `0.047405`.
  - In 2D centroid distance to 親鸞: 道綽 `0.048035`, 善導 `0.076170`, 源信 `0.080767`, 曇鸞 `0.089145`, 天親 `0.099764`, 龍樹 `0.109235`.
- Interpretation:
  - Semantic-layer first reading: 道綽/善導 are near the shared or Shinran-side core; 曇鸞 and 源信 overlap Shinran-side spread; 天親 is more intermediate; 龍樹 is Shinran-side but separated on PC2.
  - Needs source-marker and style-layer checks before historical claims.
- Commit: see repository history.

## 2026-06-03 JST: Honen Distinctive Zones

- Summary: Analyzed Honen chunks that protrude from Shinran/high-priest neighborhoods on the SAT safe map.
- Outputs:
  - `scripts/analyze_honen_distinctive_zones.py`
  - `docs/honen-distinctive-zones-2026-06-03.md`
  - `data/outputs/honen_distinctive_zones_text-embedding-3-large_700_100.json`
- Findings:
  - For all 69 Honen chunks, nearest non-Honen groups were 親鸞 50, 道綽 11, 源信 4, 善導 3, 曇鸞 1.
  - When restricted to high-priest anchors, nearest anchors were 道綽 28, 源信 24, 善導 11, 曇鸞 5, 天親 1.
  - Left/lower Honen protrusions show many markers for 選択, 正雑二行, 諸行との取捨, 三心, 善導/観経, and 往生.
  - The most isolated high-dimensional terminal chunk appears to include end/colophon-like material and should not be overread as doctrinal distinctiveness.
- Interpretation:
  - A better first hypothesis is not "Honen has a different nembutsu meaning" but "Honen compresses the classification and selection of nembutsu against other practices."
- Commit: see repository history.

## 2026-06-04 JST: Honen/Shinran Draft and Three-Layer Sequences

- Summary: Extended the SAT safe Honen/Shinran/high-priest analysis into a TeX paper draft and added minimal three-layer Honen and Shinran sequence views.
- Method:
  - Corpus baseline remained SAT kanbun, Unicode-safe near-700-token chunks, overlap 100, `text-embedding-3-large`.
  - Embedding vectors are 3072-dimensional; 2D figures use PCA fit on Honen/Shinran focus chunks, with anchor texts projected into the same plane.
  - Semantic-layer nearest-neighbor checks use original 3072-dimensional cosine similarities.
  - Three-layer Honen view uses semantic affinity to Shinran/high-priest groups, style/lexical dictionary counts, and explicit source-marker dictionary counts.
  - Three-layer Shinran view uses semantic affinity to Honen/high-priest groups, style/lexical dictionary counts, and explicit source-marker dictionary counts.
- Outputs:
  - `docs/paper/okyou2-honen-shinran-paper-v0.tex`
  - `docs/paper/okyou2-honen-shinran-paper-v0.pdf`
  - `docs/figures/sat-safe-honen-shinran-focus-map.png`
  - `docs/figures/honen-three-layer-sequence-heatmap.png`
  - `docs/figures/shinran-three-layer-sequence-heatmap.png`
  - `docs/pca-direction-interpretation-2026-06-04.md`
  - `docs/honen-three-layer-sequence-2026-06-04.md`
  - `docs/shinran-three-layer-sequence-2026-06-04.md`
  - `scripts/make_sat_safe_honen_shinran_focus_figure.py`
  - `scripts/analyze_pca_direction_interpretation.py`
  - `scripts/make_honen_three_layer_heatmap.py`
  - `scripts/make_shinran_three_layer_heatmap.py`
  - `data/outputs/sat_safe_honen_shinran_focus_map_text-embedding-3-large_700_100.json`
  - `data/outputs/pca_direction_interpretation_2026-06-04_text-embedding-3-large_700_100.json`
  - `data/outputs/pca_direction_representative_chunks_2026-06-04.csv`
  - `data/outputs/honen_three_layer_sequence_2026-06-04_text-embedding-3-large_700_100.json`
  - `data/outputs/honen_three_layer_sequence_2026-06-04.csv`
  - `data/outputs/shinran_three_layer_sequence_2026-06-04_text-embedding-3-large_700_100.json`
  - `data/outputs/shinran_three_layer_sequence_2026-06-04.csv`
- Findings:
  - Focus-only map shows Honen and Shinran overlapping strongly, with Shinran spreading farther into right/down zones.
  - PCA direction labels are post-hoc: PC1+ is mostly Shinran 信巻/化身土巻, PC1- is Honen/shared selection-argument core, PC2+ is 行巻/真仏土巻 with 願・回向/名号/阿弥陀 direction, and PC2- is 信/三心・罪救済・方便/外教 direction.
  - Shinran protrusions concentrate in 信巻 and 化身土巻; Honen protrusions concentrate in selection, 正雑二行, 本願念仏, 三心, 付属・証誠.
  - Three-layer Honen heatmap shows strong semantic proximity to Shinran while style features cluster around selection/本願, 正雑/諸行, 念仏/称名, and 往生/浄土 across argument sections.
  - Three-layer Shinran heatmap shows that semantic affinity, lexical/style groups, and explicit source markers do not move identically; the source-marker layer is still a coarse proxy dominated by citation-introduction markers.
- Public boundary:
  - Figure, docs, TeX, and CSV/JSON outputs intentionally omit raw chunk text and embeddings.
  - Local `data/cache` and processed SAT body texts remain non-public.
- Verification:
  - `python -m py_compile scripts/make_honen_three_layer_heatmap.py scripts/make_shinran_three_layer_heatmap.py`
  - `python scripts/make_honen_three_layer_heatmap.py`
  - `python scripts/make_shinran_three_layer_heatmap.py`
  - Checked generated three-layer JSON/CSV/Markdown for `U+FFFD` and raw fields such as `text`, `body`, `embedding`.
  - `uplatex` was run twice and `dvipdfmx` regenerated the paper draft PDF.
  - Rendered the PDF to PNG via PyMuPDF and visually checked the Honen and Shinran three-layer figure pages.
  - `git diff --check` passed, and predecessor `../Okyou` remained unchanged.
- Commit: see repository history.

## 2026-06-04 JST: Shared-Core Revision and Nearest-Neighbor Bias Check

- Summary: Revised the paper draft around the shared-core/protrusion framing and added a capped nearest-neighbor subsampling check.
- Method:
  - No new OpenAI API calls or source-text fetches.
  - Used existing SAT safe chunks and `text-embedding-3-large` caches.
  - Kept the three-layer terminology from the predecessor paper: 意味層・文体語彙層・典拠マーカー層.
  - Clarified that the current 文体語彙層 implementation is a dictionary-based doctrinal vocabulary proxy, not strict stylometry.
  - Defined protrusion score as `p_i = d_i * (1 - s_i)`, where `d_i` is nearest non-self distance in the 2D PCA plane and `s_i` is nearest non-self cosine in 3072D.
  - Ran 1000 iterations of reference-group capped nearest-neighbor subsampling with `sample_cap = 20`.
- Outputs:
  - `scripts/analyze_nearest_neighbor_subsampling.py`
  - `scripts/analyze_high_dim_isolation.py`
  - `scripts/make_shared_core_bar_figure.py`
  - `docs/nearest-neighbor-subsampling-2026-06-04.md`
  - `docs/high-dim-isolation-2026-06-04.md`
  - `docs/figures/shared-core-protrusion-nearest-bars.png`
  - `data/outputs/nearest_neighbor_subsampling_2026-06-04_text-embedding-3-large_700_100.json`
  - `data/outputs/nearest_neighbor_subsampling_2026-06-04_text-embedding-3-large_700_100.csv`
  - `data/outputs/high_dim_isolation_ranking_2026-06-04.csv`
  - updated `docs/paper/okyou2-honen-shinran-paper-v0.tex`
- Findings:
  - Honen-to-Shinran simple nearest-neighbor ratio is `0.724638`, but capped subsampling mean is `0.339275` with 95% range `0.115942`--`0.550725`.
  - Honen-to-Daochuo capped subsampling mean is `0.272`, and Honen-to-Shandao is `0.182464`.
  - Shinran capped subsampling is more distributed: Daochuo `0.227791`, Honen `0.189869`, Vasubandhu `0.159194`, Tanluan `0.14389`, Genshin `0.140906`.
  - Interpretation: simple nearest-neighbor counts include candidate-count bias; the shared-core/protrusion reading remains useful only as an exploratory indicator and must be read with the capped check.
  - High-dimensional isolation ranking using `1 - nearest_nonself_cosine` keeps the broad protrusion reading: Honen centers on 付属・証誠・選択総結 and 三輩・一向専念, while Shinran centers on 信巻 and 化身土巻.
  - Added a paper figure that turns the shared-core/protrusion summary into a qualitative horizontal flow and the simple nearest-neighbor counts into horizontal bars.
- Verification:
  - `python -m py_compile scripts/analyze_nearest_neighbor_subsampling.py scripts/analyze_high_dim_isolation.py scripts/make_shared_core_bar_figure.py`
  - `python scripts/analyze_nearest_neighbor_subsampling.py`
  - `python scripts/analyze_high_dim_isolation.py`
  - `python scripts/make_shared_core_bar_figure.py`
  - Confirmed generated JSON/CSV/Markdown have no forbidden raw fields (`text`, `body`, `embedding`, `preview`, `chunk_text`, `raw_text`) and no `U+FFFD`.
  - Confirmed analysis chunks loaded by `make_all_chunks()` have `0` U+FFFD chunks.
  - Rebuilt the paper with `uplatex` twice and `dvipdfmx` once.
  - Rendered the PDF to PNG via PyMuPDF and visually checked title page, shared/protrusion summary table, subsampling table, Honen/Shinran three-layer figure pages, and conclusion/references.
  - `git diff --check` passed, and predecessor `../Okyou` remained unchanged.
- Commit: see repository history.

## 2026-06-04 JST: Paper Map Figure Renderer Unification

- Summary: Fixed the paper Figure 1/Figure 2 Honen/Shinran ellipse mismatch by using one shared PNG renderer for both paper-facing maps.
- Cause:
  - The embedding, PCA coordinates, and nearest-neighbor analysis were not changed.
  - The mismatch was a rendering-layer problem: the focus-only figure and the high-priest anchor figure had been produced through different drawing paths.
- Method:
  - Added `scripts/sat_safe_map_renderer.py`.
  - Regenerated `docs/figures/sat-safe-honen-shinran-focus-map.png` and `docs/figures/sat-safe-honen-shinran-high-priest-anchor-map.png` through `render_sat_safe_map_png`.
  - Stopped emitting the older SVG path from `scripts/make_sat_safe_high_priest_anchor_map.py` for the paper figure.
  - Clarified in `docs/paper/okyou2-honen-shinran-paper-v0.tex` that the two paper figures use the same coordinate values, display extent, covariance ellipse calculation, and PNG drawing procedure for 法然 and 親鸞.
- Verification:
  - `python -m py_compile scripts/sat_safe_map_renderer.py scripts/make_sat_safe_honen_shinran_focus_figure.py scripts/make_sat_safe_high_priest_anchor_map.py`
  - `python scripts/make_sat_safe_high_priest_anchor_map.py`
  - `python scripts/make_sat_safe_honen_shinran_focus_figure.py`
  - Compared the generated JSON metadata and confirmed exact matches for 法然 and 親鸞 centroid, ellipse width, ellipse height, ellipse angle, p90 radius, renderer, and display extent between the two figures.
  - Rebuilt the paper with `uplatex` twice and `dvipdfmx` once.
  - Rendered PDF pages 5--7 to PNG via PyMuPDF and visually checked Figure 1 and Figure 2.
  - No OpenAI API calls and no new source-text fetches.
- Commit: see repository history.

## 2026-06-05 JST: Final-Draft Review Polish

- Summary: Incorporated the external final-draft review memo
  `okyou2-honen-shinran-final-draft-review.md`
  into the Honen/Shinran paper draft.
- Text changes:
  - Retitled the paper to
    `法然・親鸞の共有核とはみ出し領域：三層探索地図による『選択集』・『教行信証』比較`.
  - Softened the abstract and discussion caveat so the paper says the results
    are exploratory findings not fully checked against historical and citation
    studies, rather than implying those studies are absent.
  - Removed implementation-facing terms from the paper body, including direct
    code API names and internal labels such as fixed decode calls, line-start
    fields, compact-character wording, and PNG procedure wording.
  - Kept the predecessor three-layer names, while explicitly stating that
    `文体語彙層` is a dictionary-based doctrinal word-group proxy rather than
    strict stylometry.
  - Reframed the capped nearest-neighbor table as `上限20サンプリング`
    sensitivity analysis rather than a full bias correction.
  - Clarified that protrusion scores are ranking indicators, and that the
    protrusion tables show top 10 rows while the prose summarizes top 24 rows.
  - Added citations for the Jodoshu/Jodoshuzensho reference entries, Fujiwara
    2020, OpenAI embeddings, and `tiktoken` where they are used.
- Verification:
  - `uplatex` twice and `dvipdfmx` once regenerated
    `docs/paper/okyou2-honen-shinran-paper-v0.pdf`.
  - Rendered selected PDF pages to PNG with PyMuPDF and visually checked the
    title/abstract, prior-research table, data table, focus/anchor maps,
    shared-core bar figure, subsampling table, protrusion table, conclusion,
    and references.
  - Searched the TeX source for rejected draft/internal phrases; no matches
    remained.
  - No OpenAI API calls and no new source-text fetches.
- Commit: see repository history.

## 2026-06-05 JST: Paper Versioned Filename

- Summary: Renamed the current Honen/Shinran manuscript files from `draft` to
  explicit versioned names.
- Current version:
  - `docs/paper/okyou2-honen-shinran-paper-v0.tex`
  - `docs/paper/okyou2-honen-shinran-paper-v0.pdf`
- Versioning convention:
  - Use `paper-v0`, `paper-v1`, `paper-v2`, ... for subsequent manuscript
    versions.
  - Avoid `draft` in committed paper filenames.
- Verification:
  - Rebuilt the renamed TeX file with `uplatex` twice and `dvipdfmx` once.
  - Searched repository docs/scripts for the old draft filename.
- Commit: see repository history.

## 2026-06-05 JST: Peer-Review Response V1

- Summary: Incorporated the external peer-review memo
  `okyou2-honen-shinran-peer-review-report.md`
  into a new V1 manuscript snapshot.
- Files:
  - Created `docs/paper/okyou2-honen-shinran-paper-v1.tex`.
  - Regenerated `docs/paper/okyou2-honen-shinran-paper-v1.pdf`.
  - Rebuilt `scripts/analyze_high_dim_isolation.py` so the high-dimensional
    isolation check ranks all eligible Honen/Shinran chunks, not only the
    protrusion table rows.
  - Regenerated `docs/high-dim-isolation-2026-06-04.md` and the local
    text-free CSV output.
- Text changes:
  - Added representative close-reading candidates without quoting raw text:
    Honen chunk 7, Shinran chunk 84, and Shinran chunk 182.
  - Added dictionary summary tables for the `文体語彙層` and
    `典拠マーカー層`.
  - Clarified that `文体語彙層` is a dictionary-based doctrinal word-group
    proxy, and that `典拠マーカー層` is not quote detection.
  - Added caveats for anchor imbalance, the arbitrary but practical upper-20
    subsampling cap, and the exploratory meaning of protrusion rankings.
  - Replaced overstrong wording such as `親鸞独自候補` with
    `親鸞側突出候補`.
  - Added a robustness table comparing protrusion-score top 24 chunks with
    high-dimensional isolation top 24 chunks. Both Honen and Shinran have
    overlap 11/24 and Jaccard `0.297`, so individual ranks are unstable while
    the broad Honen selection-logic and Shinran Shin/Keshindo readings remain.
- Source and API boundary:
  - No OpenAI API calls.
  - No new SAT or other source-text fetches.
  - Existing SAT safe chunks, embedding cache, and text-free analysis outputs
    were reused.
  - No raw/processed text or embedding vectors were added to the manuscript.
- Verification:
  - `python3 -m py_compile scripts/analyze_high_dim_isolation.py`
  - `python3 scripts/analyze_high_dim_isolation.py`
  - `uplatex -interaction=nonstopmode okyou2-honen-shinran-paper-v1.tex`
    and `dvipdfmx okyou2-honen-shinran-paper-v1.dvi`
  - Rendered selected PDF pages to PNG via PyMuPDF and visually checked the
    title/abstract, dictionary tables, shared-core/bar figure, three-layer
    figures, representative examples, robustness table, discussion, and
    references.
  - Searched generated V1 artifacts for `U+FFFD`; no matches.
  - TeX log had no overfull boxes, unresolved references, fatal errors, or
    LaTeX errors. Only harmless underfull warnings remained for wrapped SAT
    line ranges in the representative-example table.
- Commit: see repository history.

## 2026-06-05 JST: Peer-Review Response V2

- Summary: Incorporated the v1 peer-review memo
  `okyou2-honen-shinran-peer-review-report-v1.md`
  into a new V2 manuscript snapshot.
- Files:
  - Created `docs/paper/okyou2-honen-shinran-paper-v2.tex`.
  - Regenerated `docs/paper/okyou2-honen-shinran-paper-v2.pdf`.
- Text changes:
  - Removed the version marker from the displayed paper date.
  - Clarified the first definition of `はみ出し領域` as a relative protrusion
    region.
  - Added an abstract-level caveat that `文体語彙層` is dictionary-based
    lexical/topic density, not strict stylometry.
  - Strengthened the method explanation of `文体語彙層` as a proxy inherited
    from the predecessor naming.
  - Added a short selection rationale for the three representative chunks:
    Honen selection argument, Shinran Shin-volume sin/salvation, and Shinran
    Keshindo external/provisional sorting.
  - Normalized the Table 13 SAT ranges to `T2608, 83...` / `T2646, 83...`
    style.
  - Added a conclusion paragraph that returns the result to prior
    `選択集`/`教行信証` comparison research and frames the output as candidate
    regions rather than replacement conclusions.
- Source and API boundary:
  - No OpenAI API calls.
  - No new source-text fetches.
  - No raw/processed text or embedding vectors were added.
- Verification:
  - `uplatex -interaction=nonstopmode okyou2-honen-shinran-paper-v2.tex`
    was run twice.
  - `dvipdfmx okyou2-honen-shinran-paper-v2.dvi` regenerated the PDF.
  - Rendered selected V2 PDF pages to PNG via PyMuPDF and visually checked the
    title/abstract, method caveat, three-layer figure caption, representative
    examples, robustness table, limits/conclusion, and references.
  - Searched the V2 TeX log for overfull boxes, unresolved references, fatal
    errors, and LaTeX errors; no matches.
  - Searched the V2 TeX for stale v1/date markers, old SAT table notation,
    `親鸞独自候補`, and `U+FFFD`; no matches.
- Commit: see repository history.

## 2026-06-05 JST: Final Public Check V3

- Summary: Incorporated the final public-check memo
  provided review memo
  into a new V3 manuscript snapshot.
- Files:
  - Created `docs/paper/okyou2-honen-shinran-paper-v3.tex`.
  - Regenerated `docs/paper/okyou2-honen-shinran-paper-v3.pdf`.
  - Added `docs/paper/okyou2-honen-shinran-english-terminology.md` to fix
    English-version terminology before translation.
- Text changes:
  - Changed Table 12 column `zone` to `内容ゾーン`.
  - Normalized Table 11 and Table 12 SAT line references to
    `T2608, 83...` / `T2646, 83...` style.
  - Added `（2026年6月5日閲覧）` to URL-based bibliography entries.
  - Fixed core English terms for the forthcoming English version, including
    `shared core`, `divergence zones`, `relative protrusion zones`,
    `lexical-thematic layer`, and `source-marker layer`.
- Source and API boundary:
  - No OpenAI API calls.
  - No new source-text fetches.
  - No raw/processed text, chunk previews, or embedding vectors were added.
- Verification:
  - `uplatex -interaction=nonstopmode okyou2-honen-shinran-paper-v3.tex`
    was run twice.
  - `dvipdfmx okyou2-honen-shinran-paper-v3.dvi` regenerated the PDF.
  - Rendered selected V3 PDF pages to PNG via PyMuPDF and visually checked
    Table 11, Table 12, and references.
  - Searched the V3 TeX and terminology memo for stale `zone`, old SAT table
    notation, `U+FFFD`, and `親鸞独自候補`; no matches.
  - Searched the V3 TeX log for overfull boxes, unresolved references, fatal
    errors, and LaTeX errors; no matches.
- Commit: see repository history.

## 2026-06-05 JST: GitHub Pages Publication Prep

- Summary: Prepared the Okyou2 paper for GitHub Pages publication in the same
  general shape as the predecessor public paper, while keeping Okyou2 as a
  separate successor repository.
- Files:
  - Added `scripts/build_public_pages.py`.
  - Generated `docs/.nojekyll`.
  - Generated `docs/index.html` and `docs/en/index.html`.
  - Generated `docs/paper/index.html` and `docs/paper/en/index.html`.
  - Generated `docs/source-provenance.html`.
  - Generated `docs/PUBLICATION.md`.
  - Generated `docs/errata/`, `docs/errata/en/`, redirect `docs/errata.html`,
    and `docs/ERRATA.md`.
  - Updated `README.md` with the Pages entry points and release policy.
- Publication shape:
  - Japanese PDF/TeX v3 remains the citation and close-reading base.
  - Japanese HTML is a linked web reading version with figures, tables,
    references, source/provenance links, and publication boundary notes.
  - English PDF/TeX/HTML are now prepared through the Japanese-TeX-aligned
    English TeX pipeline recorded below.
- Release policy:
  - Once released, public PDF/HTML are treated as fixed release artifacts.
  - Later corrections, additions, link fixes, figure-label fixes, and
    interpretive changes should be recorded as errata, not silently rewritten
    into the released text.
  - If the paper body must be updated, create a clearly versioned release and
    keep the old-version difference and reason in the errata record.
- Source and API boundary:
  - No OpenAI API calls.
  - No new source-text fetches.
  - No raw/processed text, chunk previews, embedding caches, or embedding
    vectors were added to the public HTML.
- Verification:
  - `python3 -m py_compile scripts/build_public_pages.py`
  - `python3 scripts/build_public_pages.py`
  - Checked generated HTML relative links and page anchors.
  - Checked generated public files for API keys, local absolute paths, old SAT
    URL tokens, and forbidden raw-data indicators. Matches were only negative
    publication-boundary statements.
  - Served `docs/` locally at `local HTTP preview` and confirmed HTTP 200
    for `/`, `/en/`, `/paper/`, `/paper/en/`, `/source-provenance.html`, and
    `/paper/okyou2-honen-shinran-paper-v3.pdf`.
  - After adding the release errata policy, also confirmed HTTP 200 for
    `/errata/`, `/errata/en/`, and `/ERRATA.md`.
  - Playwright screenshot verification was attempted, but the local Node
    environment did not have the `playwright` package installed.
  - Predecessor `../Okyou` remained unchanged.
- Commit: see repository history.

## 2026-06-05 JST: Public Filename and Checksum Final Check

- Summary: Matched Okyou2's public-release integrity pattern to the predecessor
  Okyou publication.
- Predecessor pattern checked:
  - Read-only predecessor `Okyou` uses `docs/checksums.txt` to record SHA-256
    hashes for fixed public artifacts.
  - The predecessor README and Pages top pages link to `checksums.txt` and
    describe later corrections as separate supplements or errata.
- Public filename changes:
  - Renamed the public Japanese paper files from versioned working names to
    stable publication names:
    - `docs/paper/honen-shinran-shared-core-paper.pdf`
    - `docs/paper/honen-shinran-shared-core-paper.tex`
  - Historical v0/v1/v2 manuscript snapshots remain versioned.
  - Updated public HTML and publication docs to link to the stable publication
    filename, not the v3 working filename.
- SHA-256 checksums:
  - Added `docs/checksums.txt`.
  - Recorded `c177fc6c02a5eabbc112999d2fd495ec921dbbb705abaa50dfe2287c87d22098`
    for `docs/paper/honen-shinran-shared-core-paper.pdf`.
  - Recorded `21e5d4af9b0f44912ef8d0d639841f672ba2f36076ac5ded0ebec236db2c7d81`
    for `docs/paper/honen-shinran-shared-core-paper.tex`.
- Verification:
  - Built the public TeX filename with `uplatex` twice.
  - Regenerated the public PDF filename with `dvipdfmx`.
  - Ran `shasum -a 256` on the public PDF and TeX.
  - Rendered selected public PDF pages to PNG with PyMuPDF and visually
    checked title/abstract, method, shared-core/bar figure,
    representative-section, and references pages.
  - Searched the public TeX log for overfull boxes, unresolved references,
    fatal errors, and LaTeX errors; no matches. Only existing underfull
    warnings for wrapped SAT line ranges remained.
  - Regenerated GitHub Pages HTML from `scripts/build_public_pages.py`.
  - Checked generated HTML relative links and page anchors.
  - Checked public files for API keys, local absolute paths, old SAT URL
    tokens, `U+FFFD`, and stale public links to the v3 PDF name.
  - Predecessor `../Okyou` remained unchanged.
- Commit: see repository history.

## 2026-06-05 JST: License, English Translation Note, Errata, and Page Style Alignment

- Summary: Aligned the public Okyou2 Pages surface more closely with the
  predecessor Okyou publication while keeping the Japanese paper as the
  authoritative edition and the English materials as AI-assisted translations.
- License:
  - Added `LICENSE`, `LICENSE-CODE`, and `LICENSE-CONTENT`.
  - Code is MIT License.
  - Paper, figures, public documentation, process reports, citation metadata,
    and public derived data are CC BY 4.0.
  - SAT/J-SOKEN/84000/source texts, processed text, chunk previews, embedding
    caches, and embedding vectors are not redistributed and are outside the
    repo license grant.
- English/Japanese edition status:
  - Added the predecessor-style English `Translation note` to the English TeX,
    English PDF, English paper HTML, and English top page.
  - Removed the Japanese paper edition-status note; README alone records that
    the Japanese PDF is the authoritative Japanese print/book edition and the
    English PDF/HTML are AI-assisted translations.
  - Removed stale HTML-version wording from the English TeX template
    and regenerated English TeX/PDF/HTML.
- Errata/Page:
  - Public correction terminology is `Errata`.
  - Main public pages are `docs/errata/index.html`, `docs/errata/en/index.html`,
    and `docs/ERRATA.md`; `docs/errata.html` is only a redirect.
  - Pages top layout now follows the predecessor more closely: pale background,
    white header, six-card grid, figure row, compact nav, and `Errata` labels.
- Verification:
  - `python3 -m py_compile scripts/build_public_pages.py`
  - `python3 -m py_compile scripts/build_english_tex_from_ja_tex.py`
  - `python3 scripts/build_english_tex_from_ja_tex.py`
  - `uplatex -interaction=nonstopmode honen-shinran-shared-core-paper-en.tex`
    twice, then `dvipdfmx honen-shinran-shared-core-paper-en.dvi`.
  - `python3 scripts/build_public_pages.py`
  - HTML link checker over `docs/**/*.html`: broken count 0.
  - Browser check at `local HTTP preview`: six cards, three figure-row
    items, predecessor-like background, `Errata` links, no Japanese katakana
    errata label.
  - Browser check at `local HTTP preview`: 10 h2, 25 h3, 5
    figures, 14 tables, 13 references, English PDF link, translation note, no
    stale HTML-version wording.
  - Confirmed translation-note placement against the predecessor pattern:
    English TeX/PDF place it immediately after `\maketitle` and before
    `abstract`; English HTML places it after the abstract and before keywords.
  - PyMuPDF text extraction: Japanese PDF has no translation note or Japanese
    edition-status note; English PDF has the translation note and no
    stale HTML-version wording.
  - TeX log scan found no fatal errors, LaTeX errors, overfull boxes,
    unresolved references, or rerun warnings.
  - `git diff --check`
  - Predecessor `../Okyou` remained unchanged.
- Current public SHA-256:
  - `886dd089af33a17f4a983795d6d1d38730f309fc5c1ebc49e36a1dbc6b7c1b34`
    for `docs/paper/honen-shinran-shared-core-paper.pdf`
  - `ed5880e1d25a8c4c87bca53203cbed3000bb856484e062078acd06a69ceb1e6a`
    for `docs/paper/honen-shinran-shared-core-paper.tex`
  - `28291b93d8496096d67cce85f1dea2b3c53db4b314c93ea50ccdc1ee8d8831a8`
    for `docs/paper/honen-shinran-shared-core-paper-en.pdf`
  - `02ecbc972ab00ad7daf8b7e1aab7ff3bfbfd227b15f736c2607dab5757044c9f`
    for `docs/paper/honen-shinran-shared-core-paper-en.tex`
- Commit: see repository history.

## 2026-06-05 JST: English Figure Localization

- Summary: Matched the predecessor pattern by giving the English public paper
  its own English-labeled figure assets instead of reusing Japanese PNGs.
- Figure output:
  - Added `docs/figures/en/sat-safe-honen-shinran-focus-map.png`.
  - Added `docs/figures/en/sat-safe-honen-shinran-high-priest-anchor-map.png`.
  - Added `docs/figures/en/shared-core-protrusion-nearest-bars.png`.
  - Added `docs/figures/en/honen-three-layer-sequence-heatmap.png`.
  - Added `docs/figures/en/shinran-three-layer-sequence-heatmap.png`.
- Code:
  - Added `scripts/make_english_public_figures.py`.
  - Updated `scripts/sat_safe_map_renderer.py` with optional English labels,
    legend text, and notes while preserving the existing coordinate and
    covariance-ellipse logic.
  - Updated `scripts/build_english_tex_from_ja_tex.py` so Japanese and English
    figure filename sequences must match, while English paths may point to
    `docs/figures/en/`.
  - Updated `scripts/build_public_pages.py` and the English TeX template so
    English HTML/PDF use the English figure directory.
- Public boundary:
  - No OpenAI API calls were made.
  - No new source-text fetches were made.
  - No raw/processed text, chunk previews, embedding caches, or embedding
    vectors were added.
  - English figure rendering reads existing text-free CSV/JSON analysis
    outputs only.
- Verification:
  - `python3 -m py_compile scripts/sat_safe_map_renderer.py scripts/make_english_public_figures.py scripts/build_english_tex_from_ja_tex.py scripts/build_public_pages.py`
  - `python3 scripts/make_english_public_figures.py`
  - Visually checked all five English PNGs.
  - `python3 scripts/build_english_tex_from_ja_tex.py`
  - `uplatex -interaction=nonstopmode honen-shinran-shared-core-paper-en.tex`
    twice, then `dvipdfmx honen-shinran-shared-core-paper-en.dvi`.
  - `python3 scripts/build_public_pages.py`
  - Confirmed English TeX/HTML figure references all point to `figures/en/`.
  - Rendered English PDF pages 7-13 with PyMuPDF and visually confirmed
    Figures 1-5 are English-labeled.
  - Browser check at `local HTTP preview`: 4 images, all from
    `../figures/en/`, all non-zero natural sizes.
  - Browser check at `local HTTP preview`: 5 images, all from
    `../../figures/en/`, all non-zero natural sizes.
  - Predecessor `../Okyou` remained unchanged.
- Current English public SHA-256:
  - `28291b93d8496096d67cce85f1dea2b3c53db4b314c93ea50ccdc1ee8d8831a8`
    for `docs/paper/honen-shinran-shared-core-paper-en.pdf`
  - `02ecbc972ab00ad7daf8b7e1aab7ff3bfbfd227b15f736c2607dab5757044c9f`
    for `docs/paper/honen-shinran-shared-core-paper-en.tex`
- Commit: see repository history.

## 2026-06-05 JST: Publication Safety and Push Preparation

- Summary: Added and ran a repeatable push-preparation safety check to ensure
  GitHub publication candidates do not include private text, embedding caches,
  vectors, secrets, TeX intermediates, or local absolute paths.
- Code/docs:
  - Added `scripts/check_publication_safety.py`.
  - Updated `README.md` and generated `docs/PUBLICATION.md` with the pre-push
    command `python3 scripts/check_publication_safety.py`.
  - Updated generation code so regenerated publication notes keep the safety
    step.
  - Removed local absolute path markers from public candidate text files.
  - Updated predecessor-audit and heatmap scripts to avoid hard-coded local
    absolute paths in generated/public files.
- Safety findings:
  - `data/` contains local private raw/processed/cache/output material, but it
    is ignored and not a Git publication candidate.
  - `git ls-files data ...` returned no tracked private data or TeX
    intermediate files.
  - Untracked non-ignored files are intended public additions: licenses,
    English public figures, English PDF/TeX, errata pages, license page, and
    publication scripts.
  - Remote configuration must be confirmed before push.
- Verification:
  - `python3 -m py_compile scripts/check_publication_safety.py scripts/audit_predecessor_text_integrity.py scripts/make_honen_three_layer_heatmap.py scripts/make_shinran_three_layer_heatmap.py scripts/build_public_pages.py scripts/sat_safe_map_renderer.py scripts/make_english_public_figures.py scripts/build_english_tex_from_ja_tex.py`
  - `python3 scripts/build_public_pages.py`
  - `python3 scripts/check_publication_safety.py`
  - `rg` over Git candidates found no local absolute path markers.
  - `git diff --check`
  - Browser check at `local HTTP preview` covered top, English top,
    Japanese paper, English paper, provenance, errata, English errata, and
    license pages; no broken images or local absolute path markers, and English
    pages used `figures/en/`.
  - PyMuPDF-rendered Japanese and English PDF page 1 plus a figure page; the
    English translation note is before abstract and the English figure page is
    English-labeled.
  - Predecessor sibling repo `../Okyou` remained unchanged.
- Commit: see repository history.

## 2026-06-05 JST: GitHub Repository Naming

- Summary: Aligned public repository references with the created GitHub repo
  `dueyama/honen-shinran-shared-core-map`.
- Changes:
  - Set local `origin` to
    `https://github.com/dueyama/honen-shinran-shared-core-map.git`.
  - Updated README public repository and planned Pages URL.
  - Updated `docs/checksums.txt` public URLs to
    `https://dueyama.github.io/honen-shinran-shared-core-map/`.
  - Updated `scripts/build_public_pages.py` so generated public pages use
    `Honen-Shinran Shared Core Map` instead of public-facing `Okyou2` labels.
  - Regenerated public HTML and `docs/PUBLICATION.md`.
- Verification:
  - `git remote -v`
  - `python3 scripts/build_public_pages.py`
  - `python3 -m py_compile scripts/build_public_pages.py scripts/check_publication_safety.py`
- Commit: see repository history.
