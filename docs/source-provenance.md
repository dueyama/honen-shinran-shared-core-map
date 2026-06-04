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
- Wrote only line ranges, chunk ids, hashes, coordinates, metrics, keyword
  counts, and short top terms; no raw or chunk text field was written.

Generated local-only outputs:

- `data/outputs/readable_map_analysis_2026-06-04_text-embedding-3-large_700_100.json`
- `data/outputs/honen_protrusion_table_2026-06-04.csv`
- `data/outputs/shinran_volume_affinity_table_2026-06-04.csv`
- `docs/readable-map-analysis-2026-06-04.md`

Run summary:

- Honen nearest non-self counts: 親鸞 `50`, 道綽 `11`, 源信 `4`,
  善導 `3`, 曇鸞 `1`.
- Shinran nearest non-self counts: 法然 `48`, 道綽 `45`, 源信 `36`,
  曇鸞 `23`, 天親 `21`, 善導 `17`, 龍樹 `1`.
- Honen protrusion table keeps 24 chunks, prioritizing doctrinal argument
  candidates over paratext/terminal candidates.
- Shinran table labels 191 chunks by approximate volume and affinity zone.

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
