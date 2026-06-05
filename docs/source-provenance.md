# Source Provenance

This file records source provenance for Okyou2 experiments. Do not paste raw
source text here.

## 2026-06-03: Predecessor Text Integrity Audit

Purpose:

- Check whether the released predecessor `Okyou` embedding chunks included
  `U+FFFD` replacement characters introduced by token-boundary decoding.
- Treat predecessor `Okyou` as read-only. The audit was recorded only in this
  successor repository.

Audited predecessor paths:

- `/Users/daishin/Documents/Codex/Okyou/experiments/sect_sutra_map`
- `/Users/daishin/Documents/Codex/Okyou/experiments/multilingual_sutra_map`

Method:

- Reproduced the predecessor chunking method: `cl100k_base`, 700 tokens,
  100-token overlap, and `encoder.decode()` on fixed token slices.
- Counted `U+FFFD` in processed body text and reproduced chunk text.
- Checked existing predecessor `outputs/embeddings.json` chunk previews where
  present.

Result:

- `sect_sutra_map`: source bodies had 0 replacement characters; reproduced
  chunks had `U+FFFD` in 256 of 433 chunks, 326 replacement characters total.
- `sect_sutra_map/outputs/embeddings.json`: previews had `U+FFFD` in 147 of
  433 chunks, 173 replacement characters total.
- `multilingual_sutra_map`: source bodies had 0 replacement characters;
  reproduced chunks had `U+FFFD` in 44 of 105 chunks, 58 replacement
  characters total.

Interpretive boundary:

- This is a text-integrity audit, not a full re-evaluation of predecessor
  figures or claims.
- The issue is boundary noise introduced during chunk decoding, not corruption
  of the processed source bodies.
- Okyou2 should not reuse predecessor fixed-token decoded chunks as
  publication-grade evidence; future chunks should preserve source line or
  natural-unit boundaries and fail on `U+FFFD`.

Generated local-only output:

- `data/outputs/predecessor_text_integrity_audit.json`

Public boundary:

- The audit output contains no raw source text, but does include local absolute
  paths. Review before publishing.

## 2026-06-03: Honen/Shinran Simple 2D Map

Purpose:

- Rough first look at a 2D page-level map of Honen's `選択本願念仏集` and
  Shinran's `教行信証`.
- This is a preliminary observation map, not a final three-layer analysis.
- This page-level run was an exploratory baseline. The predecessor-style run
  below is the preferred baseline for comparison with Okyou v1.

Source site:

- 聖教電子化研究会: `https://seiten.icho.gr.jp/`

Downloaded local-only source ranges:

- `https://seiten.icho.gr.jp/html/z1-[920-1005].html`
- `https://seiten.icho.gr.jp/html/[152-430].html`

Pages retained by title filter:

- `選擇本願念佛集`: 64 page chunks.
- `教行信証` / `顕浄土...`: 239 page chunks.

Processing:

- Extracted page-level chunks from downloaded HTML.
- For this first rough map, used Japanese reading text from HTML classes
  `honbun`, `s_sage`, and `l_nobegaki`.
- Excluded `r_kanbun` in this first pass to avoid duplicating Shinran pages
  with both Japanese reading and kanbun text.
- Vectorized with character 2-4 gram TF-IDF.
- Projected to 2D with centered SVD using NumPy.
- Rendered points, centroids, and covariance ellipses as an SVG.

Generated local-only outputs:

- `data/outputs/honen_shinran_simple_2d.svg`
- `data/outputs/honen_shinran_simple_2d.svg.png`
- `data/outputs/honen_shinran_simple_2d_meta.json`

Public boundary:

- Raw downloaded HTML under `data/raw/` is not committed.
- Processed text is not committed.
- Figures and metadata may be considered for publication only after checking
  source terms and removing all raw text.
- The current metadata contains page identifiers, source URLs, coordinates,
  and summary statistics, but no source text.

Limitations:

- Page chunks are a coarse unit; later runs should use chapter, section,
  citation, and authorial-comment chunks.
- This first map is a lexical/character n-gram baseline, not a doctrinally
  validated semantic embedding map.
- `選択本願念仏集` and `教行信証` are represented through the available
  seiten HTML reading text, so source-format effects may remain.

## 2026-06-03: Honen/Shinran Predecessor-Style Embedding Map

Purpose:

- Re-run the Honen/Shinran 2D map using the method choices from Okyou v1 as
  the baseline.
- Show both chunk distributions and work centroids, not only average vectors.

Source site:

- 聖教電子化研究会: `https://seiten.icho.gr.jp/`

Downloaded local-only source ranges:

- `https://seiten.icho.gr.jp/html/z1-[920-1005].html`
- `https://seiten.icho.gr.jp/html/[152-430].html`

Pages retained by title filter:

- `選擇本願念佛集`
- `教行信証` / `顕浄土...`

Processing:

- Extracted Japanese reading text from HTML classes `honbun`, `s_sage`, and
  `l_nobegaki`.
- Excluded `r_kanbun` in this first run so the seiten pages with both Japanese
  reading and kanbun would not duplicate content.
- Tokenized with `tiktoken` `cl100k_base`.
- Chunked at 700 tokens with 100-token overlap, matching the Okyou v1 baseline.
- Embedded with OpenAI `text-embedding-3-large`.
- Projected chunk embeddings to 2D using PCA, implemented as centered NumPy
  SVD because `sklearn` is not installed in the current pyenv environment.
- Rendered chunk points, work centroids, and covariance ellipses.

Generated local-only outputs:

- `data/outputs/honen_shinran_predecessor_style_embedding_map.svg`
- `data/outputs/honen_shinran_predecessor_style_embedding_map.png`
- `data/outputs/honen_shinran_predecessor_style_embedding_map_meta.json`
- `data/cache/honen_shinran_predecessor_style_embeddings_text-embedding-3-large_700_100.json`

Run summary:

- `選択本願念仏集`: 103 chunks.
- `教行信証`: 301 chunks.
- Embedding dimension: 3072.
- PCA explained variance ratio: PC1 `0.063873`, PC2 `0.046549`.
- Centroid distance in the displayed PCA plane: `0.173264`.

Public boundary:

- Raw downloaded HTML under `data/raw/` is not committed.
- Processed text and embedding cache are not committed.
- The metadata contains source page ranges, source URLs, token spans, SHA-256
  hashes, coordinates, and summary statistics, but no source text.
- Figures and metadata may be considered for publication after source-term
  review and another check that no raw text is present.

Limitations:

- This is still only the semantic layer. Style/lexical and source-marker layers
  need to be overlaid before making interpretive claims.
- The current input is seiten Japanese reading text. A later run should compare
  Japanese reading text against kanbun/SAT-style text if the research question
  requires it.
- PCA PC1+PC2 explains about 11.0% of the embedding variance, so the 2D map is
  a useful visual probe but not the full geometry.

## 2026-06-03: Honen/Shinran Map With High-Priest Text Anchors

Purpose:

- Keep the predecessor-style Honen/Shinran semantic map as the fixed baseline.
- Overlay Pure Land patriarch/source texts into the same 2D semantic plane.
- Use this as a first visual probe for which source-text regions are near the
  Honen/Shinran shared area and which are near Shinran's wider spread.

Source sites:

- 聖教電子化研究会: `https://seiten.icho.gr.jp/`
- SAT 大正新脩大藏經テキストデータベース: `https://21dzk.l.u-tokyo.ac.jp/SAT/`

Baseline sources:

- Same Honen/Shinran seiten sources as the predecessor-style embedding map
  above.

Anchor sources:

- 龍樹 `十住毘婆沙論 易行品`:
  `https://21dzk.l.u-tokyo.ac.jp/SAT/T1521_,26,0038a25:1521_,26,0040a22.html`
- 天親 `無量寿経優波提舎願生偈`:
  `https://21dzk.l.u-tokyo.ac.jp/SAT/T1524.html`
- 曇鸞 `往生論註`: `https://21dzk.l.u-tokyo.ac.jp/SAT/T1819.html`
- 道綽 `安楽集`: `https://21dzk.l.u-tokyo.ac.jp/SAT/T1958.html`
- 善導 `観無量寿仏経疏`: `https://21dzk.l.u-tokyo.ac.jp/SAT/T1753.html`
- 源信 `往生要集`: `https://21dzk.l.u-tokyo.ac.jp/SAT/T2682.html`

Processing:

- Reused the Honen/Shinran 700-token, 100-overlap, `text-embedding-3-large`
  embedding baseline.
- Fit PCA only on Honen/Shinran chunks, not on the anchor texts.
- Fetched SAT HTML locally under `data/raw/sat_anchors/`.
- Extracted SAT line bodies from text-bearing line rows and removed HTML
  controls/markup.
- Tokenized anchor texts with `tiktoken` `cl100k_base`.
- Chunked anchor texts at 700 tokens with 100-token overlap.
- Embedded anchor chunks with OpenAI `text-embedding-3-large`.
- Projected anchor embeddings into the fixed Honen/Shinran PCA plane.

Generated local-only outputs:

- `data/outputs/honen_shinran_high_priest_anchor_map.svg`
- `data/outputs/honen_shinran_high_priest_anchor_map.png`
- `data/outputs/honen_shinran_high_priest_anchor_map_meta.json`
- `data/cache/high_priest_anchor_embeddings_text-embedding-3-large_700_100.json`

Run summary:

- `選択本願念仏集`: 103 baseline chunks.
- `教行信証`: 301 baseline chunks.
- 龍樹 `十住毘婆沙論 易行品`: 6 anchor chunks.
- 天親 `無量寿経優波提舎願生偈`: 9 anchor chunks.
- 曇鸞 `往生論註`: 31 anchor chunks.
- 道綽 `安楽集`: 42 anchor chunks.
- 善導 `観無量寿仏経疏`: 23 anchor chunks.
- 源信 `往生要集`: 73 anchor chunks.
- PCA fit-scope explained variance ratio: PC1 `0.063873`,
  PC2 `0.046549`.

Public boundary:

- Raw SAT and seiten HTML under `data/raw/` is not committed.
- Processed text and embedding cache under `data/cache/` is not committed.
- The metadata contains source URLs, chunk identifiers, token spans, SHA-256
  hashes, coordinates, and summary statistics, but no source text.
- Figures and metadata may be considered for publication only after source-term
  review and another check that no raw text is present.

Limitations:

- The baseline Honen/Shinran texts are seiten Japanese reading text, while the
  current anchors are SAT kanbun/Sino-Japanese source text. The embedding model
  is semantic, but script/style effects may still enter the geometry.
- This is still a semantic-layer map. Style/lexical and source-marker layers
  are needed before claiming historical influence.
- The T1521 range is a first-pass `易行品` range and should be reviewed against
  a bibliographic source before publication-grade use.

## 2026-06-03: Shinran-Only Zone Summary

Purpose:

- Identify regions of the high-priest anchor map where Shinran chunks appear
  without nearby Honen or high-priest/source anchor points.
- Summarize those zones without publishing source text.

Inputs:

- `data/outputs/honen_shinran_high_priest_anchor_map_meta.json`
- Local-only reconstructed Shinran token chunks from the seiten HTML.

Processing:

- For each Shinran chunk in the fixed PCA plane, calculated the Euclidean
  distance to the nearest non-Shinran point.
- Non-Shinran points include Honen chunks and the high-priest/source anchor
  chunks.
- Selected chunks whose nearest non-Shinran distance is at least `0.10`.
  This is roughly the upper 5% tail for Shinran chunks in this map.
- Read local text only to flag a small keyword list and assign zone labels.
- Wrote no raw source text to the report or JSON output.

Generated local-only outputs:

- `docs/shinran-isolated-zones-2026-06-03.md`
- `data/outputs/shinran_isolated_zones_meta.json`

Run summary:

- Selected 20 Shinran chunks.
- Initial zones:
  - 行巻・真仏土の上方島: 名号、本願、無量寿、阿弥陀、不退。
  - 信巻右下の阿闍世・涅槃経島: 五逆、提婆、耆婆、慙愧、地獄。
  - 化身土末の護法・鬼神・宇宙秩序島: 大集、鬼神、星宿。
  - 化身土末の外教批判島: 老子、孔子、史記、周書、論語、道士。
  - 化身土本の方便・雑行島: 方便、雑行、専修、回向。

Limitations:

- This selection is based on 2D PCA distance, not high-dimensional embedding
  nearest-neighbor distance.
- It is semantic-layer evidence only.
- Zone labels are first-pass interpretive labels and should be revised after
  source-marker and style-layer checks.

## 2026-06-03: SAT Kanbun Text Preparation

Purpose:

- Prepare clean kanbun-basis texts before running further embeddings.
- Keep chunk/text correspondence through SAT line references and SHA-256
  hashes.

Source site:

- SAT 大正新脩大藏經テキストデータベース:
  `https://21dzk.l.u-tokyo.ac.jp/SAT/`

Sources:

- 法然 `選擇本願念佛集`, SAT `T2608`:
  `https://21dzk.l.u-tokyo.ac.jp/SAT/T2608.html`
- 親鸞 `顯淨土眞實教行證文類`, SAT `T2646`:
  `https://21dzk.l.u-tokyo.ac.jp/SAT/T2646_,83,0589a01:2646_,83,0643c29.html`

Processing:

- Parsed SAT HTML rows with line references.
- Removed SAT UI controls and HTML markup.
- Kept body text only in processed `.txt` files.
- Kept `line_ref`, `text`, and `text_sha256` in processed `.lines.jsonl`
  files.
- Did not run embeddings in this preparation step.

Quality checks:

- No replacement character `U+FFFD`.
- No HTML tag.
- No HTML entity.
- No image placeholder.
- No button label.
- No SAT line reference mixed into body text.
- No control character.
- No empty text.
- No missing parsed lines.

Generated local-only outputs:

- `data/processed/sat_kanbun/honen_t2608_senchakushu.txt`
- `data/processed/sat_kanbun/honen_t2608_senchakushu.lines.jsonl`
- `data/processed/sat_kanbun/shinran_t2646_kyogyoshinsho.txt`
- `data/processed/sat_kanbun/shinran_t2646_kyogyoshinsho.lines.jsonl`
- `data/processed/sat_kanbun/manifest.json`

Run summary:

- T2608: 1644 SAT lines, 27246 compact chars, quality issues `0`.
- T2646: 4215 SAT lines, 76030 compact chars, quality issues `0`.

Public boundary:

- These processed text files contain source text and must not be committed or
  published.
- Future embedding runs should use these prepared `.lines.jsonl` files and
  Unicode-safe near-700-token chunks. SAT line refs remain metadata for
  provenance, not the required chunk boundary.

Superseded run note:

- The earlier seiten Japanese-reading embedding map remains an exploratory
  reading-text run.
- The first trial SAT kanbun embedding map generated on 2026-06-03 is not an
  accepted analysis result because it was produced before the explicit text
  preparation/quality gate.

## 2026-06-03: SAT Chunking Strategy Comparison

Purpose:

- Compare the old fixed token-slice decode method against a Unicode-safe
  near-700-token chunk method on the same prepared SAT kanbun-basis texts.
- Check both text quality and embedding geometry.

Sources:

- Same prepared SAT T2608/T2646 `.lines.jsonl` files as the SAT kanbun text
  preparation step above.

Processing:

- Old method: encode the whole body with `cl100k_base`, slice token ids at
  700 tokens with 100-token overlap, then decode each slice.
- New method: keep the same 700-token/100-overlap token grid, but use
  `tiktoken.decode_with_offsets()` to round token positions to Python Unicode
  string offsets before creating chunk text.
- Embedded both old and new chunks with OpenAI `text-embedding-3-large`.
- Projected all old/new chunks together with PCA on L2-normalized embeddings.

Run summary:

- Old method: 260 chunks, 148 chunks with `U+FFFD`, 181 replacement characters.
- New method: 260 chunks, 0 chunks with `U+FFFD`, 0 replacement characters.
- Same-index old/new cosine similarity:
  - 法然『選択本願念仏集』: mean `0.990319`, median `0.997852`.
  - 親鸞『教行信証』: mean `0.990932`, median `0.998012`.
- Old/new centroid cosine:
  - 法然: `0.999352`.
  - 親鸞: `0.999443`.
- 法然/親鸞 centroid cosine distance:
  - Old method: `0.055832`.
  - New method: `0.055406`.

Interpretive boundary:

- The old method is text-quality defective but did not substantially move the
  large-scale embedding geometry in this comparison.
- Okyou2 should use the new Unicode-safe method as the fixed-token baseline.

Generated local-only outputs:

- `data/outputs/sat_chunking_strategy_compare_text-embedding-3-large_700_100.json`
- `data/outputs/sat_chunking_strategy_compare_text-embedding-3-large_700_100.svg`
- `data/outputs/sat_chunking_strategy_compare_text-embedding-3-large_700_100.svg.png`
- `data/cache/sat_chunking_strategy_compare_text-embedding-3-large_700_100.json`

## 2026-06-03: SAT Safe High-Priest Anchor Map

Purpose:

- Rebuild the Honen/Shinran + high-priest overlay using the accepted
  Unicode-safe 700-token / 100-overlap chunk baseline.
- Use SAT kanbun-basis texts for both focus texts and anchors.

Focus sources:

- 法然 `選擇本願念佛集`, SAT `T2608`:
  `https://21dzk.l.u-tokyo.ac.jp/SAT/T2608.html`
- 親鸞 `顯淨土眞實教行證文類`, SAT `T2646`:
  `https://21dzk.l.u-tokyo.ac.jp/SAT/T2646_,83,0589a01:2646_,83,0643c29.html`

Anchor sources:

- 龍樹 `十住毘婆沙論 易行品`:
  `https://21dzk.l.u-tokyo.ac.jp/SAT/T1521_,26,0038a25:1521_,26,0040a22.html`
- 天親 `無量寿経優波提舎願生偈`:
  `https://21dzk.l.u-tokyo.ac.jp/SAT/T1524.html`
- 曇鸞 `往生論註`: `https://21dzk.l.u-tokyo.ac.jp/SAT/T1819.html`
- 道綽 `安楽集`: `https://21dzk.l.u-tokyo.ac.jp/SAT/T1958.html`
- 善導 `観無量寿仏経疏`: `https://21dzk.l.u-tokyo.ac.jp/SAT/T1753.html`
- 源信 `往生要集`: `https://21dzk.l.u-tokyo.ac.jp/SAT/T2682.html`

Processing:

- Used prepared `.lines.jsonl` for focus texts.
- Parsed SAT line bodies for anchor texts from local cached HTML.
- Created Unicode-safe near-700-token chunks with 100-token overlap.
- Embedded with OpenAI `text-embedding-3-large`.
- Embedding dimension: `3072`.
- Fit PCA only on focus chunks, then projected anchor chunks into the fixed
  focus PCA plane.

Run summary:

- Focus chunks: 法然 `69`, 親鸞 `191`.
- Anchor chunks: 龍樹 `6`, 天親 `9`, 曇鸞 `31`, 道綽 `42`, 善導 `23`,
  源信 `73`.
- PCA fit-scope explained variance ratio: PC1 `0.068562`, PC2 `0.047405`.
- In the displayed PCA plane, centroid distances to 親鸞 are:
  道綽 `0.048035`, 善導 `0.076170`, 源信 `0.080767`, 曇鸞 `0.089145`,
  天親 `0.099764`, 龍樹 `0.109235`.

Interpretive boundary:

- This is still semantic-layer evidence. Do not treat it as proof of
  historical influence without source-marker and style-layer checks.
- The 2D PCA plane explains about 11.6% of the focus embedding variance.
- The displayed 2D plane is therefore an exploratory projection of the 3072D
  embedding space; high-dimensional nearest-neighbor counts use the original
  3072D vectors.
- PCA is not the only possible 2D projection. It is used here as the baseline
  because it is linear, stable, and allows anchor chunks to be projected into
  the same fitted plane. UMAP, t-SNE, MDS, or other projections remain future
  robustness checks.

Generated local-only outputs:

- `data/outputs/sat_safe_honen_shinran_high_priest_anchor_map_text-embedding-3-large_700_100.svg`
- `data/outputs/sat_safe_honen_shinran_high_priest_anchor_map_text-embedding-3-large_700_100.svg.png`
- `data/outputs/sat_safe_honen_shinran_high_priest_anchor_map_text-embedding-3-large_700_100.json`
- `data/cache/sat_safe_high_priest_anchor_embeddings_text-embedding-3-large_700_100.json`

## 2026-06-03: SAT Safe Anchor Affinity

Purpose:

- Check the high-dimensional nearest-neighbor relation behind the 2D SAT safe
  map.
- Avoid over-reading PCA geometry alone.

Sources:

- Same SAT focus and anchor sources as the SAT safe high-priest anchor map.

Processing:

- Loaded SAT safe chunk embeddings from the local cache.
- Calculated cosine similarities in the original embedding space.
- Counted nearest non-self groups and nearest high-priest anchors.
- Wrote only counts, ranks, line ranges, and identifiers; no source text.

Run summary:

- Shinran nearest anchor counts: 源信 `58`, 道綽 `58`, 曇鸞 `27`,
  善導 `24`, 天親 `22`, 龍樹 `2`.
- Shinran nearest non-self counts when Honen is included: 法然 `48`,
  道綽 `45`, 源信 `36`, 曇鸞 `23`, 天親 `21`, 善導 `17`, 龍樹 `1`.
- Honen nearest non-self counts: 親鸞 `50`, 道綽 `11`, 源信 `4`,
  善導 `3`, 曇鸞 `1`.
- Honen nearest anchor counts: 道綽 `28`, 源信 `24`, 善導 `11`,
  曇鸞 `5`, 天親 `1`.

Generated local-only output:

- `data/outputs/sat_safe_anchor_affinity_text-embedding-3-large_700_100.json`

Interpretive boundary:

- This supports the observation that Honen and Shinran overlap strongly in
  embedding space, while Shinran also spreads toward several high-priest
  anchor regions.
- It does not by itself prove historical influence. Historical relation,
  citation markers, and text-form effects must be handled separately.

## 2026-06-03: Honen Distinctive Zones

Purpose:

- Inspect Honen chunks that protrude from the Honen/Shinran/high-priest map.
- Test whether the protrusion looks like a different interpretation of
  nembutsu or a difference in book structure and argument form.

Sources:

- Same SAT safe T2608/T2646 focus sources and high-priest anchor sources as the
  SAT safe map.

Processing:

- Selected Honen chunks far from non-Honen points in the displayed PCA plane.
- Also selected Honen chunks with the weakest high-dimensional nearest
  non-Honen cosine.
- Counted keyword groups and top terms from local source text.
- Wrote only line ranges, keyword counts, term counts, and identifiers; no
  source text.

Run summary:

- The protruding Honen regions emphasize `選択`, `正雑二行`,
  `諸行との取捨`, `一向専念`, `三心/真実心`, `善導/観経`,
  `付属/証誠`, and `往生`.
- The current interpretation is that the protrusion reflects the argument of
  selecting nembutsu from among other practices more than a simple doctrinal
  difference in the meaning of nembutsu.
- Some of the most isolated Honen chunks may include terminal or colophon-like
  material and should be filtered out before doctrinal interpretation.

Generated local-only outputs:

- `docs/honen-distinctive-zones-2026-06-03.md`
- `data/outputs/honen_distinctive_zones_text-embedding-3-large_700_100.json`

Interpretive boundary:

- This is a first-pass semantic/style reading. It should be checked by chapter
  structure and source-marker extraction before publication.

## 2026-06-03: Honen Corpus Context

Purpose:

- Record why there is probably no single Honen work that is directly equivalent
  to Shinran's `教行信証`.
- Identify future Honen-side corpus candidates.

Reference sources checked:

- 浄土宗公式『選択集』解説:
  `https://jodo.or.jp/newspaper/special/6226/`
- 新纂浄土宗大辞典「選択本願念仏集」:
  `https://jodoshuzensho.jp/daijiten/index.php/%E9%81%B8%E6%8A%9E%E6%9C%AC%E9%A1%98%E5%BF%B5%E4%BB%8F%E9%9B%86`
- 新纂浄土宗大辞典「黒谷上人語灯録」:
  `https://jodoshuzensho.jp/daijiten/index.php/%E9%BB%92%E8%B0%B7%E4%B8%8A%E4%BA%BA%E8%AA%9E%E7%81%AF%E9%8C%B2`
- 新纂浄土宗大辞典「無量寿経釈」:
  `https://jodoshuzensho.jp/daijiten/index.php/%E7%84%A1%E9%87%8F%E5%AF%BF%E7%B5%8C%E9%87%88`

Working conclusion:

- `選択本願念仏集` remains the closest single Honen work, but it is a focused
  argument for selecting nembutsu, not a large `教行信証`-style doctrinal
  architecture.
- `黒谷上人語灯録` is a later collection of Honen's writings, sayings, and
  letters, so it should be treated as a Honen corpus, not as one authored
  system-book.
- `三部経釈` and related sutra-commentary materials are useful candidates, but
  the textual transmission and machine-readable availability need checking
  before use.

## 2026-06-04: Readable Map Analysis Tables

Purpose:

- Turn the SAT safe Honen/Shinran/high-priest map into reader-facing analysis
  tables without exposing raw chunk text.
- Provide a first minimal three-layer analysis: semantic affinity, style
  vocabulary groups, and source-marker groups.

Inputs:

- `data/cache/sat_chunking_strategy_compare_text-embedding-3-large_700_100.json`
- `data/cache/sat_safe_high_priest_anchor_embeddings_text-embedding-3-large_700_100.json`
- `data/outputs/sat_safe_honen_shinran_high_priest_anchor_map_text-embedding-3-large_700_100.json`
- local-only prepared SAT text/chunks under `data/processed/` and cached anchor
  HTML under `data/raw/`

Processing:

- Reconstructed Unicode-safe chunks using the accepted 700-token / 100-overlap
  policy.
- Used cached `text-embedding-3-large` vectors; no OpenAI API request was made.
- Calculated high-dimensional nearest non-self and nearest anchor affinities.
- Assigned approximate Shinran volume labels from SAT line ranges.
- Assigned coarse Honen section labels from SAT line ranges.
- Counted dictionary-based style vocabulary groups and source-marker groups.
- Calculated a Shinran protrusion score with the same shape as the Honen table:
  nearest non-Shinran 2D distance multiplied by one minus nearest non-self
  cosine.
- Added coarse Shinran protrusion-zone labels for 信巻, 真仏土巻, and 化身土巻
  based on local-only text feature counts and marker hits.
- Wrote only line ranges, chunk ids, hashes, coordinates, metrics, keyword
  counts, and short top terms; no raw or chunk text field was written.

Generated local-only outputs:

- `data/outputs/readable_map_analysis_2026-06-04_text-embedding-3-large_700_100.json`
- `data/outputs/honen_protrusion_table_2026-06-04.csv`
- `data/outputs/shinran_volume_affinity_table_2026-06-04.csv`
- `data/outputs/shinran_protrusion_table_2026-06-04.csv`
- `data/outputs/sat_safe_honen_shinran_focus_map_text-embedding-3-large_700_100.json`
- `data/outputs/pca_direction_interpretation_2026-06-04_text-embedding-3-large_700_100.json`
- `data/outputs/pca_direction_representative_chunks_2026-06-04.csv`
- `data/outputs/nearest_neighbor_subsampling_2026-06-04_text-embedding-3-large_700_100.json`
- `data/outputs/nearest_neighbor_subsampling_2026-06-04_text-embedding-3-large_700_100.csv`
- `data/outputs/high_dim_isolation_ranking_2026-06-04.csv`
- `data/outputs/honen_three_layer_sequence_2026-06-04_text-embedding-3-large_700_100.json`
- `data/outputs/honen_three_layer_sequence_2026-06-04.csv`
- `data/outputs/shinran_three_layer_sequence_2026-06-04_text-embedding-3-large_700_100.json`
- `data/outputs/shinran_three_layer_sequence_2026-06-04.csv`
- `docs/readable-map-analysis-2026-06-04.md`
- `docs/pca-direction-interpretation-2026-06-04.md`
- `docs/nearest-neighbor-subsampling-2026-06-04.md`
- `docs/high-dim-isolation-2026-06-04.md`
- `docs/honen-three-layer-sequence-2026-06-04.md`
- `docs/shinran-three-layer-sequence-2026-06-04.md`
- `docs/figures/shared-core-protrusion-nearest-bars.png`
- `docs/figures/sat-safe-honen-shinran-focus-map.png`
- `docs/figures/honen-three-layer-sequence-heatmap.png`
- `docs/figures/shinran-three-layer-sequence-heatmap.png`

Run summary:

- Honen nearest non-self counts: 親鸞 `50`, 道綽 `11`, 源信 `4`,
  善導 `3`, 曇鸞 `1`.
- Shinran nearest non-self counts: 法然 `48`, 道綽 `45`, 源信 `36`,
  曇鸞 `23`, 天親 `21`, 善導 `17`, 龍樹 `1`.
- Honen protrusion table keeps 24 chunks, prioritizing doctrinal argument
  candidates over paratext/terminal candidates.
- Shinran table labels 191 chunks by approximate volume and affinity zone.
- Shinran protrusion table keeps 24 chunks. Its top-volume counts are 信巻
  `13`, 化身土巻 `8`, 真仏土巻 `2`, 証巻 `1`.
- Shinran protrusion zones are led by 信巻の信/三心・罪救済 `13`, 化身土巻の
  護法・鬼神・宇宙秩序 `4`, 真仏土巻の名号・本願・真実 `2`, 化身土巻の
  外教批判 `1`, and 化身土巻の方便・真仮整理 `1`.
- The paper figure order now starts with a focus-only Honen/Shinran map and
  then shows the high-priest anchor overlay separately. Both figures use the
  same PCA coordinate basis; the focus-only figure fits the visible extent to
  Honen/Shinran chunks for readability.
- PCA direction interpretation was added as a post-hoc edge-chunk summary. In
  the current focus map, PC1+ is Shinran 信巻/化身土巻 with 罪救済 and
  廃立/取捨 markers; PC1- is relatively Honen/shared 選択論証; PC2+ is
  阿弥陀・光明・名号・願回向; PC2- is 信/三心・罪救済・方便/外教.
- Nearest-neighbor subsampling was added to check reference-group chunk count
  bias. Each non-target author group was capped at `min(20, group_size)` chunks
  over 1000 iterations. Honen-to-Shinran simple nearest-neighbor ratio drops
  from `0.724638` to a sampled mean `0.339275`, so the simple count clearly
  includes candidate-count effects. The broad reading remains that Honen is
  strongest toward Shinran/Daochuo, while Shinran is distributed across
  Daochuo/Honen/Vasubandhu/Tanluan after the cap.
- A high-dimensional isolation ranking was added as a PCA-independent companion
  to protrusion score. It uses `1 - nearest_nonself_cosine` from existing
  text-free protrusion CSVs. The top-20 summary still centers Honen on
  付属・証誠・選択総結 and 三輩・一向専念, and Shinran on 信巻 and 化身土巻,
  so the broad protrusion reading does not depend only on 2D map distance.
- A shared-core/protrusion and nearest-neighbor bar figure was added for the
  paper. The top panel is a qualitative schematic of the shared-core/protrusion
  summary table; the bottom panels visualize simple nearest non-self chunk
  counts for Honen and Shinran. It contains no raw text or embeddings.
- A Honen three-layer chunk-sequence heatmap was added. The semantic layer uses
  3072D max cosine from each Honen chunk to Shinran/high-priest author groups;
  the style and source-marker layers use the same dictionaries as the Shinran
  heatmap. The first read is that Honen keeps strong semantic proximity to
  Shinran while the style layer concentrates around 選択/本願, 正雑/諸行,
  念仏/称名, and 往生/浄土 across the argument sections.
- A Shinran three-layer chunk-sequence heatmap was added. The semantic layer
  uses 3072D max cosine from each Shinran chunk to Honen/high-priest author
  groups; the style layer uses dictionary count groups; the source-marker layer
  uses explicit sutra/commentary/patriarch/citation-introduction markers.
  Source-marker rows are dominated by 引用導入, showing that this minimal marker
  layer identifies citation density more readily than precise source structure.

Quality checks:

- Output JSON has no fields named `text`, `body`, or `embedding`.
- Generated JSON/CSV/Markdown contain `0` replacement characters.
- The analysis-table chunk rows report `replacement_chars = 0`.

Interpretive boundary:

- Volume and section labels are line-start approximations. Some chunks overlap
  boundaries because the fixed baseline uses 100-token overlap.
- Keyword groups are a minimal dictionary-based proxy; they do not yet
  distinguish quoted source stance from Shinran/Honen authorial stance.
- Short top terms are feature labels, not source text passages. Treat the
  generated data as local-only until publication review.

## 2026-06-04 Paper Finalization Pass

Scope:

- Revised `docs/paper/okyou2-honen-shinran-paper-v0.tex` toward a paper-facing
  manuscript tone.
- Regenerated `docs/paper/okyou2-honen-shinran-paper-v0.pdf`.
- Regenerated `docs/figures/sat-safe-honen-shinran-high-priest-anchor-map.png`
  from the existing anchor-map metadata using the shared PNG renderer.

Source and API boundary:

- No OpenAI API calls.
- No new SAT, J-SOKEN, or other source text fetches.
- Existing local SAT-derived chunks, caches, and metadata were reused.
- Raw/processed text and embedding caches remain local-only under `data/`.

Paper-facing cleanup:

- Replaced internal or draft-like wording in the paper body with paper-facing
  terms, while preserving the exploratory-method caveat.
- Kept the three-layer names from the predecessor paper:
  意味層, 文体語彙層, 典拠マーカー層.
- Changed the high-priest anchor figure title to
  `SAT漢文・Unicode-safeチャンク地図：法然・親鸞・祖師文献`.
- Unified the paper-facing figure renderer for the focus-only map and the
  high-priest anchor map in `scripts/sat_safe_map_renderer.py`.
- The paper-facing focus ellipses for 法然 and 親鸞 now use the same coordinate
  values, display extent, covariance ellipse calculation, and PNG drawing path
  in both figures. The older SVG renderer is not used for paper figures.

Verification:

- `python -m py_compile` passed for the changed/new analysis and figure scripts.
- Recomputed figure metadata and confirmed that 法然 and 親鸞 centroid,
  ellipse width, ellipse height, ellipse angle, p90 radius, renderer, and
  display extent match exactly between the focus-only and anchor-map paper
  figures.
- `uplatex` was run twice and `dvipdfmx` once.
- The rebuilt PDF was rendered to PNG with PyMuPDF and visually checked.
- Generated JSON/CSV/Markdown outputs were checked for forbidden raw fields
  (`text`, `body`, `embedding`, `preview`, `chunk_text`, `raw_text`) and
  `U+FFFD`; no matches were found.
- `git diff --check` passed.
- Predecessor `/Users/daishin/Documents/Codex/Okyou` remained unchanged.

## 2026-06-04 Prior-Research Positioning Memo

External input:

- `/Users/daishin/Downloads/okyou2-honen-shinran-prior-research-positioning.md`

Purpose:

- Add a paper-facing prior-research positioning section for the comparison of
  Honen's `選択集` and Shinran's `教行信証`.
- Clarify that the novelty is not the comparison itself, but the whole-text
  chunk distribution and three-layer visualization of existing comparison
  questions.

Bibliographic checks used:

- INBUDS entries for 森脇一掬「選択集と教行信証に関する一考察」
  and 梅原隆章「選択集と教行信証」.
- Otani University repository entry for 稲葉秀賢「『教行信証』と『選択集』」.
- 行信教校 `行信学報` journal list for 浅井成海「『選択集』と
  『教行信証』――基本的問題の継承と展開――」.
- NDL Search and Books.or.jp for 根津茂『日本仏教を変えた親鸞の独自性』.

Paper updates:

- Added `1.2 先行研究と本稿の位置づけ`.
- Added `表1: 先行研究の関心と本稿の分析観点`.
- Added references for Moriwaki 1953, Inaba 1972, Umehara 1974, Asai 2004,
  and Nezu 2024.

Verification:

- `uplatex` was run twice and `dvipdfmx` once.
- The rebuilt PDF was rendered to PNG with PyMuPDF and visually checked on
  the title/abstract, new prior-research section, new table, and references.
- `git diff --check` passed.
- Predecessor `/Users/daishin/Documents/Codex/Okyou` remained unchanged.

## 2026-06-05 Final-Draft Review Polish

External input:

- `/Users/daishin/Downloads/okyou2-honen-shinran-final-draft-review.md`

Scope:

- Revised `docs/paper/okyou2-honen-shinran-paper-v0.tex`.
- Regenerated `docs/paper/okyou2-honen-shinran-paper-v0.pdf`.

Source and API boundary:

- No OpenAI API calls.
- No new SAT, J-SOKEN, Jodoshuzensho, or other source text fetches.
- Existing text-free analysis outputs, figure assets, and bibliography notes
  were reused.
- Raw/processed text and embedding caches remain local-only under ignored
  `data/` paths and were not added to the paper.

Paper updates:

- Changed the paper title and PDF metadata to use `三層探索地図`.
- Defined `はみ出し領域` as an exploratory working concept for relative
  protrusion from the shared core.
- Replaced code-facing method names in the prose with paper-facing descriptions
  of token-boundary-safe chunking and SAT line references.
- Kept `意味層`, `文体語彙層`, and `典拠マーカー層`, while clarifying that
  the current `文体語彙層` implementation is a dictionary-based proxy.
- Expanded Table 2 with SAT identifiers/ranges and whether each source is full
  text or excerpt in this analysis.
- Reworded Table 7 as an upper-20 subsampling sensitivity analysis, not a full
  bias correction.
- Clarified that Tables 9 and 10 print the top 10 protrusion rows while the
  prose summarizes the top 24 rows.
- Added or used citations for Jodoshu/Jodoshuzensho reference entries,
  Fujiwara 2020, OpenAI embeddings documentation, and `tiktoken`.

Verification:

- `uplatex` was run twice and `dvipdfmx` once.
- The rebuilt PDF was rendered to PNG with PyMuPDF and visually checked on
  selected pages covering the title, prior-research section, data table, map
  figures, shared-core/bar figure, subsampling table, protrusion table,
  conclusion, and references.
- The TeX source was searched for rejected internal/draft terms including code
  API names, English internal labels, old correction wording, and overstrong
  caveat phrasing; no matches remained.

## 2026-06-05 Paper Versioned Filename

Scope:

- Renamed the current manuscript files from the old `draft` filename to a
  versioned paper filename:
  - `docs/paper/okyou2-honen-shinran-paper-v0.tex`
  - `docs/paper/okyou2-honen-shinran-paper-v0.pdf`

Versioning convention:

- The current manuscript is `v0`.
- Future manuscript snapshots should use `paper-v1`, `paper-v2`, and so on.
- Avoid `draft` in paper filenames intended for repository tracking.

Verification:

- Rebuilt `okyou2-honen-shinran-paper-v0.tex` with `uplatex` twice and
  `dvipdfmx` once.
- Searched repository docs/scripts for the old manuscript filename.

## 2026-06-05 Peer-Review Response V1

External input:

- `/Users/daishin/Downloads/okyou2-honen-shinran-peer-review-report.md`

Scope:

- Created the next manuscript snapshot:
  - `docs/paper/okyou2-honen-shinran-paper-v1.tex`
  - `docs/paper/okyou2-honen-shinran-paper-v1.pdf`
- Updated `scripts/analyze_high_dim_isolation.py`.
- Regenerated `docs/high-dim-isolation-2026-06-04.md`.
- Regenerated the local text-free high-dimensional isolation CSV under
  `data/outputs/`.

Source and API boundary:

- No OpenAI API calls were made for this revision.
- No new SAT, J-SOKEN, Jodoshuzensho, or other source text fetches were made.
- Existing SAT safe chunk metadata, existing embedding cache, existing figure
  assets, and existing text-free analysis outputs were reused.
- The manuscript and committed docs do not include raw SAT text, processed
  source text, chunk previews, or embedding vectors.

Peer-review responses incorporated:

- Added three representative case-study candidates without reproducing raw
  source text. Each row uses SAT line range, chunk number, nearest-neighbor
  relation, and word-group labels only.
- Added supplementary-style dictionary tables for the `文体語彙層` and
  `典拠マーカー層`.
- Clarified that the current `文体語彙層` is a dictionary-based doctrinal
  vocabulary proxy, not strict stylometry.
- Clarified that the `典拠マーカー層` is a marker count for locating
  inspection targets, not citation detection.
- Expanded caveats for anchor representativeness, especially small or excerpted
  anchor groups.
- Added a note that the upper-20 subsampling cap is a practical sensitivity
  setting, not a theoretically privileged threshold.
- Replaced overstrong independence wording with `親鸞側突出候補`.
- Added a high-dimensional isolation robustness check using `1 - s_i` over all
  eligible Honen/Shinran chunks.

High-dimensional isolation check:

- Honen protrusion top 24 vs high-dimensional isolation top 24:
  overlap 11 chunks, Jaccard `0.297`.
- Shinran protrusion top 24 vs high-dimensional isolation top 24:
  overlap 11 chunks, Jaccard `0.297`.
- Interpretation: individual chunk rankings are exploratory and method
  dependent, but the broad Honen selection-logic and Shinran Shin/Keshindo
  concentration remains visible without the 2D PCA distance term.

Verification:

- `/Users/daishin/.pyenv/shims/python -m py_compile scripts/analyze_high_dim_isolation.py`
- `/Users/daishin/.pyenv/shims/python scripts/analyze_high_dim_isolation.py`
- `uplatex -interaction=nonstopmode okyou2-honen-shinran-paper-v1.tex`
- `dvipdfmx okyou2-honen-shinran-paper-v1.dvi`
- Rendered selected V1 PDF pages to PNG with PyMuPDF and visually checked the
  title/abstract, dictionary tables, shared-core/bar figure, three-layer
  figures, representative examples, robustness table, discussion, and
  references.
- Searched V1 TeX, high-dimensional isolation markdown, and CSV output for
  `U+FFFD`; no matches.
- The V1 TeX log had no overfull boxes, unresolved references, fatal errors, or
  LaTeX errors. Remaining underfull warnings are from wrapped SAT line ranges
  in the representative-example table.

## 2026-06-05 Peer-Review Response V2

External input:

- `/Users/daishin/Downloads/okyou2-honen-shinran-peer-review-report-v1.md`

Scope:

- Created the next manuscript snapshot:
  - `docs/paper/okyou2-honen-shinran-paper-v2.tex`
  - `docs/paper/okyou2-honen-shinran-paper-v2.pdf`

Source and API boundary:

- No OpenAI API calls were made for this revision.
- No new SAT, J-SOKEN, Jodoshuzensho, or other source text fetches were made.
- Existing paper text, existing analysis outputs, and existing figure assets
  were reused.
- The manuscript does not include raw SAT text, processed source text, chunk
  previews, or embedding vectors.

Peer-review responses incorporated:

- Removed the displayed manuscript version marker from the date.
- Clarified the first definition of `はみ出し領域` as a relative protrusion
  region.
- Reconfirmed that `文体語彙層` is dictionary-based lexical/topic density and
  not strict stylometry.
- Added a selection rationale for the three representative chunks.
- Normalized Table 13 SAT range notation to `T2608, 83...` and `T2646, 83...`
  style.
- Added a concluding paragraph returning the result to prior
  `選択集`/`教行信証` comparison research.

Verification:

- `uplatex -interaction=nonstopmode okyou2-honen-shinran-paper-v2.tex` was run
  twice.
- `dvipdfmx okyou2-honen-shinran-paper-v2.dvi` regenerated the PDF.
- Rendered selected V2 PDF pages to PNG with PyMuPDF and visually checked the
  title/abstract, method caveat, three-layer figure caption, representative
  examples, robustness table, limits/conclusion, and references.
- Searched the V2 TeX log for overfull boxes, unresolved references, fatal
  errors, and LaTeX errors; no matches.
- Searched the V2 TeX for stale v1/date markers, old SAT table notation,
  `親鸞独自候補`, and `U+FFFD`; no matches.

## 2026-06-05 Final Public Check V3

External input:

- `/tmp/codex-remote-attachments/019e8ca1-3204-7170-9150-32a368a08ba1/678697D5-730F-4B48-B178-D35286DA47DA/1-okyou2-honen-shinran-final-public-check.md`

Scope:

- Created a publication-polish manuscript snapshot:
  - `docs/paper/okyou2-honen-shinran-paper-v3.tex`
  - `docs/paper/okyou2-honen-shinran-paper-v3.pdf`
- Added English-version terminology notes:
  - `docs/paper/okyou2-honen-shinran-english-terminology.md`

Source and API boundary:

- No OpenAI API calls were made for this revision.
- No new SAT, J-SOKEN, Jodoshuzensho, or other source text fetches were made.
- Existing paper text, existing analysis outputs, and existing figure assets
  were reused.
- The new manuscript and terminology memo do not include raw SAT text,
  processed source text, chunk previews, or embedding vectors.

Public-version responses incorporated:

- Changed Table 12 column `zone` to `内容ゾーン`.
- Normalized Table 11 and Table 12 SAT line references to
  `T2608, 83...` / `T2646, 83...` style.
- Added `（2026年6月5日閲覧）` to URL-based bibliography entries.
- Fixed English-version terminology before translation:
  `shared core`, `divergence zones`, `relative protrusion zones`,
  `lexical-thematic layer`, `source-marker layer`, and related terms.

Verification:

- `uplatex -interaction=nonstopmode okyou2-honen-shinran-paper-v3.tex` was run
  twice.
- `dvipdfmx okyou2-honen-shinran-paper-v3.dvi` regenerated the PDF.
- Rendered selected V3 PDF pages to PNG with PyMuPDF and visually checked
  Table 11, Table 12, and references.
- Searched the V3 TeX and terminology memo for stale `zone`, old SAT table
  notation, `U+FFFD`, and `親鸞独自候補`; no matches.
- Searched the V3 TeX log for overfull boxes, unresolved references, fatal
  errors, and LaTeX errors; no matches.

## 2026-06-05 GitHub Pages Publication Prep

Scope:

- Added a static GitHub Pages publication surface under `docs/`.
- Added Japanese and English top pages.
- Added Japanese paper HTML and English access-version paper HTML.
- Added public source/provenance HTML.
- Added release errata tracking:
  - `docs/errata.html`
  - `docs/ERRATA.md`

Release policy:

- Once released, public PDF/HTML are fixed release artifacts.
- Later corrections, additions, link fixes, figure-label fixes, and
  interpretive changes should be recorded as errata, not silently rewritten
  into the released text.
- If the paper body must be updated, create a clearly versioned release and
  record the old-version difference and reason in the errata record.

Source and API boundary:

- No OpenAI API calls were made.
- No new SAT, J-SOKEN, Jodoshuzensho, or other source text fetches were made.
- Existing paper text, existing analysis outputs, and existing figure assets
  were reused.
- The generated public HTML does not include raw source text, processed source
  text, chunk previews, embedding caches, or embedding vectors.

Verification:

- `/Users/daishin/.pyenv/shims/python -m py_compile scripts/build_public_pages.py`
- `/Users/daishin/.pyenv/shims/python scripts/build_public_pages.py`
- Checked generated HTML relative links and page anchors.
- Checked generated public files for API keys, local absolute paths, old SAT
  URL tokens, and forbidden raw-data indicators. Matches were only negative
  publication-boundary statements.
- Served `docs/` locally at `http://127.0.0.1:8765/` and confirmed HTTP 200
  for `/`, `/en/`, `/paper/`, `/paper/en/`, `/source-provenance.html`, and
  `/paper/okyou2-honen-shinran-paper-v3.pdf`.
- After adding the release errata policy, also confirmed HTTP 200 for
  `/errata.html` and `/ERRATA.md`.
- Playwright screenshot verification was attempted, but the local Node
  environment did not have the `playwright` package installed.
- Predecessor `/Users/daishin/Documents/Codex/Okyou` remained unchanged.
