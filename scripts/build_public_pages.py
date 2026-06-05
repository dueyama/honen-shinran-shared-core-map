from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


TITLE_JA = "法然・親鸞の共有核とはみ出し領域"
SUBTITLE_JA = "三層探索地図による『選択集』・『教行信証』比較"
TITLE_EN = "Shared Core and Divergence Zones in Honen and Shinran"
SUBTITLE_EN = "A Three-Layer Exploratory Map of the Senchakushu and Kyogyoshinsho"
AUTHOR_JA = "上山大信"
AUTHOR_EN = "Daishin Ueyama"
DATE_JA = "2026年6月5日"
DATE_EN = "June 5, 2026"
PUBLIC_PAPER_PDF = "honen-shinran-shared-core-paper.pdf"
PUBLIC_PAPER_TEX = "honen-shinran-shared-core-paper.tex"


STYLE = r"""
:root {
  color-scheme: light;
  --bg: #f5f7f4;
  --paper: #ffffff;
  --ink: #1f2723;
  --muted: #657069;
  --line: #d8ded6;
  --accent: #2f6f73;
  --accent-2: #7f5d2e;
  --soft: #eef4f1;
  --warn: #9a5b3f;
  font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Yu Gothic", "Noto Sans JP", "Noto Sans", sans-serif;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body { margin: 0; background: var(--bg); color: var(--ink); line-height: 1.78; }
a { color: var(--accent); text-underline-offset: 3px; }
header { background: var(--paper); border-bottom: 1px solid var(--line); }
.page { width: min(1040px, calc(100% - 32px)); margin: 0 auto; }
.hero { padding: 34px 0 28px; display: grid; grid-template-columns: minmax(0, 1fr) minmax(280px, 0.72fr); gap: 28px; align-items: center; }
.paper-header { padding: 34px 0 20px; }
h1 { margin: 0 0 12px; font-size: clamp(28px, 4.8vw, 48px); line-height: 1.18; letter-spacing: 0; }
.subtitle { margin: 0 0 12px; color: var(--muted); font-size: clamp(17px, 2.2vw, 22px); line-height: 1.45; }
.meta { color: var(--muted); font-size: 14px; }
.site-nav { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-top: 18px; }
.nav-link { display: inline-flex; min-height: 36px; align-items: center; justify-content: center; padding: 0 13px; border: 1px solid var(--line); border-radius: 6px; color: var(--ink); background: #fff; font-size: 14px; text-decoration: none; }
.nav-link[aria-current="page"] { border-color: #bccbc8; background: #f4f7f5; color: var(--accent); font-weight: 700; }
.lang-switch { display: inline-flex; min-height: 36px; overflow: hidden; border: 1px solid var(--line); border-radius: 999px; background: #fff; }
.lang-switch a { display: inline-flex; align-items: center; padding: 0 12px; color: var(--muted); text-decoration: none; font-size: 14px; }
.lang-switch a + a { border-left: 1px solid var(--line); }
.lang-switch a[aria-current="true"] { background: var(--accent); color: #fff; font-weight: 700; }
main.paper { background: var(--paper); border: 1px solid var(--line); border-radius: 8px; margin: 22px auto 44px; padding: 34px 44px; }
main.home { padding: 28px 0 44px; }
h2 { margin: 34px 0 12px; font-size: 25px; line-height: 1.35; letter-spacing: 0; }
h3 { margin: 26px 0 10px; font-size: 19px; line-height: 1.4; letter-spacing: 0; }
p { margin: 0 0 1em; }
code { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 0.92em; background: #f3f5f2; padding: 0 3px; border-radius: 3px; }
.abstract, .notice { border-left: 5px solid var(--accent); background: #f4f7f5; padding: 18px; margin: 0 0 24px; }
.notice { border-left-color: var(--warn); }
.toc { border: 1px solid var(--line); background: #fbfcfa; border-radius: 7px; padding: 16px; margin: 22px 0; }
.toc h2 { margin-top: 0; font-size: 18px; }
.toc ol { columns: 2; gap: 28px; margin-bottom: 0; }
.grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
.card { border: 1px solid var(--line); border-radius: 8px; background: var(--paper); padding: 16px; }
.card h2, .card h3 { margin-top: 0; font-size: 18px; }
.card p { color: var(--muted); font-size: 14px; }
.figure-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin: 20px 0; }
figure { margin: 26px 0; }
figure img, .figure-grid img, .hero img { display: block; width: 100%; height: auto; border: 1px solid var(--line); border-radius: 7px; background: #fff; }
.figure-grid img { aspect-ratio: 4 / 3; object-fit: contain; }
figcaption, caption { color: var(--muted); font-size: 13px; line-height: 1.6; }
figcaption { margin-top: 8px; }
.table-wrap { overflow-x: auto; margin: 24px 0; }
table { width: 100%; border-collapse: collapse; font-size: 14px; line-height: 1.55; }
th, td { border: 1px solid var(--line); padding: 7px 8px; vertical-align: top; }
th { background: #f5f7f4; font-weight: 700; }
caption { caption-side: top; text-align: left; margin-bottom: 8px; font-weight: 700; }
.ref-list { font-size: 13px; line-height: 1.6; }
.ref-list li { margin-bottom: 0.75em; }
.pill-list { display: flex; flex-wrap: wrap; gap: 8px; padding: 0; margin: 12px 0 0; list-style: none; }
.pill-list li { border: 1px solid var(--line); border-radius: 999px; padding: 4px 10px; background: #fff; color: var(--muted); font-size: 13px; }
.source-link { font-weight: 650; }
footer { border-top: 1px solid var(--line); background: var(--paper); padding: 18px 0; color: var(--muted); font-size: 12px; }
@media (max-width: 760px) {
  .hero, .grid, .figure-grid { grid-template-columns: 1fr; }
  main.paper { padding: 22px 18px; }
  .toc ol { columns: 1; }
  table { font-size: 13px; }
}
"""


def html_shell(lang: str, title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>{STYLE}</style>
</head>
<body>
{body}
</body>
</html>
"""


def aria_page(active: bool) -> str:
    return ' aria-current="page"' if active else ""


def aria_true(active: bool) -> str:
    return ' aria-current="true"' if active else ""


def nav(lang: str, current: str) -> str:
    if lang == "ja":
        top = "../" if current == "paper" else "./"
        paper_href = "./" if current == "paper" else "paper/"
        pdf_href = PUBLIC_PAPER_PDF if current == "paper" else f"paper/{PUBLIC_PAPER_PDF}"
        source_href = "../source-provenance.html" if current == "paper" else "source-provenance.html"
        errata_href = "../errata.html" if current == "paper" else "errata.html"
        ja_href = {
            "paper": "./",
            "source": "source-provenance.html",
            "errata": "errata.html",
        }.get(current, "./")
        en_top = "en/"
        return f"""
<nav class="site-nav" aria-label="サイト内ナビゲーション">
  <a class="nav-link" href="{top}"{aria_page(current == 'home')}>トップ</a>
  <a class="nav-link" href="{paper_href}"{aria_page(current == 'paper')}>論文HTML</a>
  <a class="nav-link" href="{pdf_href}">PDF</a>
  <a class="nav-link" href="{source_href}"{aria_page(current == 'source')}>出典・検証記録</a>
  <a class="nav-link" href="{errata_href}"{aria_page(current == 'errata')}>エラッタ</a>
  <span class="lang-switch" aria-label="言語切替">
    <a href="{ja_href}"{aria_true(True)}>日本語</a>
    <a href="{en_top}">English</a>
  </span>
</nav>"""
    top = "../" if current == "home" else "../../en/"
    ja = "../" if current == "paper" else "../"
    return f"""
<nav class="site-nav" aria-label="Site navigation">
  <a class="nav-link" href="{top}"{aria_page(current == 'home')}>Top</a>
  <a class="nav-link" href="{'../paper/en/' if current == 'home' else './'}"{aria_page(current == 'paper')}>Paper HTML</a>
  <a class="nav-link" href="{'../paper/' + PUBLIC_PAPER_PDF if current == 'home' else '../' + PUBLIC_PAPER_PDF}">PDF JP</a>
  <a class="nav-link" href="{'../paper/okyou2-honen-shinran-english-terminology.md' if current == 'home' else '../okyou2-honen-shinran-english-terminology.md'}">Terminology</a>
  <a class="nav-link" href="{'../errata.html' if current == 'home' else '../../errata.html'}">Errata</a>
  <span class="lang-switch" aria-label="Language">
    <a href="{ja}">日本語</a>
    <a href="{'./' if current == 'home' else './'}"{aria_true(True)}>English</a>
  </span>
</nav>"""


def home_ja() -> str:
    body = f"""
<header>
  <div class="page hero">
    <div>
      <h1>{TITLE_JA}</h1>
      <p class="subtitle">{SUBTITLE_JA}</p>
      <p class="meta">{AUTHOR_JA} / {DATE_JA}</p>
{nav('ja', 'home')}
    </div>
    <figure>
      <a href="figures/sat-safe-honen-shinran-focus-map.png"><img src="figures/sat-safe-honen-shinran-focus-map.png" alt="法然・親鸞の意味地図"></a>
      <figcaption>法然・親鸞の共有核とはみ出し領域を読むための中心図。</figcaption>
    </figure>
  </div>
</header>
<main class="home page">
  <section class="grid">
    <article class="card">
      <h2>論文HTML</h2>
      <p>図表・参考資料・用語メモへ直接移動できるWeb版です。</p>
      <p><a href="paper/">日本語HTMLを読む</a></p>
    </article>
    <article class="card">
      <h2>PDF</h2>
      <p>ページ固定の引用・印刷用PDFです。</p>
      <p><a href="paper/{PUBLIC_PAPER_PDF}">PDFを開く</a></p>
    </article>
    <article class="card">
      <h2>English</h2>
      <p>英語読者向けHTML版と訳語メモです。</p>
      <p><a href="paper/en/">English HTML</a></p>
    </article>
  </section>
  <section class="notice">
    <h2>公開境界</h2>
    <p>この公開版は本文そのもの、processed text、chunk preview、embedding cache、embedding vectorを含みません。図表・集計・SAT行範囲・検証メモなど、本文を含まない派生情報のみを公開対象にします。</p>
    <p>リリース後は公開版本文を直接書き換えず、訂正・補足・変更履歴は<a href="errata.html">エラッタ</a>として公開する。</p>
    <p>固定公開物のSHA-256は <a href="checksums.txt">checksums.txt</a> に記録する。</p>
  </section>
  <section>
    <h2>主要図</h2>
    <div class="figure-grid">
      <a href="figures/sat-safe-honen-shinran-high-priest-anchor-map.png"><img src="figures/sat-safe-honen-shinran-high-priest-anchor-map.png" alt="法然・親鸞・祖師文献アンカー地図"></a>
      <a href="figures/shared-core-protrusion-nearest-bars.png"><img src="figures/shared-core-protrusion-nearest-bars.png" alt="共有核とはみ出し領域と最近傍非自己の可視化"></a>
      <a href="figures/shinran-three-layer-sequence-heatmap.png"><img src="figures/shinran-three-layer-sequence-heatmap.png" alt="親鸞三層チャンク列"></a>
    </div>
  </section>
</main>
<footer><div class="page">Okyou2 / GitHub Pages publication draft. Source texts remain subject to each provider's terms.</div></footer>
"""
    return html_shell("ja", TITLE_JA, body)


def home_en() -> str:
    body = f"""
<header>
  <div class="page hero">
    <div>
      <h1>{TITLE_EN}</h1>
      <p class="subtitle">{SUBTITLE_EN}</p>
      <p class="meta">{AUTHOR_EN} / {DATE_EN}</p>
{nav('en', 'home')}
    </div>
    <figure>
      <a href="../figures/sat-safe-honen-shinran-focus-map.png"><img src="../figures/sat-safe-honen-shinran-focus-map.png" alt="Semantic map of Honen and Shinran"></a>
      <figcaption>The central map for reading the shared core and divergence zones.</figcaption>
    </figure>
  </div>
</header>
<main class="home page">
  <section class="grid">
    <article class="card">
      <h2>Paper HTML</h2>
      <p>A web version with direct links to figures, tables, references, and source notes.</p>
      <p><a href="../paper/en/">Read the English HTML</a></p>
    </article>
    <article class="card">
      <h2>Japanese PDF</h2>
      <p>The Japanese version is the authoritative version for citation.</p>
      <p><a href="../paper/{PUBLIC_PAPER_PDF}">Open PDF</a></p>
    </article>
    <article class="card">
      <h2>Terminology</h2>
      <p>Translation terms are fixed before the full English release workflow.</p>
      <p><a href="../paper/okyou2-honen-shinran-english-terminology.md">Terminology memo</a></p>
    </article>
  </section>
  <section class="notice">
    <h2>Publication Boundary</h2>
    <p>This public draft does not redistribute source text, processed text, chunk previews, embedding caches, or embedding vectors. It publishes only derived figures, tables, line ranges, and documentation.</p>
    <p>After release, the public paper is treated as a fixed release. Corrections and additions are published through the <a href="../errata.html">errata</a> page rather than silently rewriting the release text.</p>
    <p>SHA-256 checksums for fixed public artifacts are recorded in <a href="../checksums.txt">checksums.txt</a>.</p>
  </section>
</main>
<footer><div class="page">Okyou2 / GitHub Pages publication draft.</div></footer>
"""
    return html_shell("en", TITLE_EN, body)


def table(headers: list[str], rows: list[list[str]], caption: str | None = None) -> str:
    cap = f"<caption>{caption}</caption>" if caption else ""
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = "\n".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    return f'<div class="table-wrap"><table>{cap}<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def paper_ja() -> str:
    rows_corpus = [
        ["中心", "法然", "選擇本願念佛集", "T2608", "全体", "69"],
        ["中心", "親鸞", "顯淨土眞實教行證文類", "T2646", "全体", "191"],
        ["アンカー", "龍樹", "十住毘婆沙論 易行品", "T1521, 0038a25--0040a22", "抜粋", "6"],
        ["アンカー", "天親", "無量寿経優波提舎願生偈", "T1524", "全体", "9"],
        ["アンカー", "曇鸞", "往生論註", "T1819", "全体", "31"],
        ["アンカー", "道綽", "安楽集", "T1958", "全体", "42"],
        ["アンカー", "善導", "観無量寿仏経疏", "T1753", "全体", "23"],
        ["アンカー", "源信", "往生要集", "T2682", "全体", "73"],
    ]
    rows_summary = [
        ["共有核", "法然・親鸞チャンクが相互に近接し、道綽・善導などのアンカーも重なる", "念仏・称名、往生・浄土、信・三心", "専修念仏・浄土教的共通問題圏"],
        ["法然はみ出し", "非法然点から相対的に離れ、選択論証部に集中", "正雑二行、三輩・一向専念、本願念仏、付属・証誠", "念仏を諸行から選び出す論証"],
        ["親鸞はみ出し", "非親鸞点から相対的に離れ、信巻・化身土巻に集中", "信巻、化身土巻、罪・救済、方便・化身土、廃立・取捨", "本願・信・証・真仏土/化身土の典拠的体系"],
    ]
    rows_nearest = [
        ["法然", "親鸞", "50", "72.5%"],
        ["法然", "道綽", "11", "15.9%"],
        ["法然", "源信", "4", "5.8%"],
        ["親鸞", "法然", "48", "25.1%"],
        ["親鸞", "道綽", "45", "23.6%"],
        ["親鸞", "源信", "36", "18.8%"],
        ["親鸞", "曇鸞", "23", "12.0%"],
        ["親鸞", "天親", "21", "11.0%"],
    ]
    rows_cases = [
        ["法然", "chunk 7, 正雑二行", "T2608, 83.0003a04--0003b04", "最近傍は親鸞、近傍祖師は善導、語群は正雑・諸行", "正行・雑行の分類を通じて、念仏を諸行から選び出す論証として読める。"],
        ["親鸞", "chunk 84, 信巻", "T2646, 83.0614a08--0614b05", "最近傍は源信、語群は罪・救済", "信巻の罪・救済問題が、源信方向の主題圏と接しながら現れる。"],
        ["親鸞", "chunk 182, 化身土巻", "T2646, 83.0640b28--0640c27", "最近傍は道綽、語群は廃立・取捨", "化身土巻の外教批判・真仮整理が、道綽方向の問題圏と接しつつ現れる。"],
    ]
    refs = references("ja")
    body = f"""
<header>
  <div class="page paper-header">
    <h1>{TITLE_JA}</h1>
    <p class="subtitle">{SUBTITLE_JA}</p>
    <p class="meta">{AUTHOR_JA} / {DATE_JA}</p>
{nav('ja', 'paper')}
  </div>
</header>
<main class="paper page">
  <section class="abstract" id="abstract">
    <h2>要旨</h2>
    <p>本稿は、法然『選擇本願念佛集』と親鸞『顯淨土眞實教行證文類』が、意味空間上でどのように重なり、また共有核から相対的に離れて現れる「はみ出し領域」（相対的突出領域）がどの方向に現れるかを、意味層・文体語彙層・典拠マーカー層の三層から検討する探索的研究である。文体語彙層は厳密な文体計量ではなく、辞書ベースの語彙・主題濃淡として扱う。</p>
    <p>結果として、法然チャンク69件の最近傍非自己は親鸞50件、道綽11件、源信4件、善導3件、曇鸞1件であり、法然チャンクの多くは親鸞文献チャンクと意味空間上で強く重なる。一方、親鸞チャンク191件の最近傍非自己は法然48件、道綽45件、源信36件、曇鸞23件、天親21件、善導17件、龍樹1件に分かれた。</p>
    <p>共有核からのはみ出し領域を比較すると、法然側では正雑二行、諸行との取捨、本願、付属・証誠など、念仏を諸行から選び出す論証が現れた。これに対し親鸞側では、信巻の信・三心・罪救済、化身土巻の護法・鬼神・宇宙秩序、外教批判、方便・真仮整理が目立った。</p>
  </section>
  <p><strong>キーワード:</strong> 法然、親鸞、選択本願念仏集、教行信証、共有核、はみ出し領域、意味埋め込み、三層分析、SAT、典拠マーカー</p>
  <section class="toc">
    <h2>目次</h2>
    <ol>
      <li><a href="#intro">はじめに</a></li>
      <li><a href="#data">データ</a></li>
      <li><a href="#method">方法</a></li>
      <li><a href="#results">結果</a></li>
      <li><a href="#discussion">考察</a></li>
      <li><a href="#limitations">限界</a></li>
      <li><a href="#conclusion">結論</a></li>
      <li><a href="#references">参考文献</a></li>
    </ol>
  </section>
  <section id="intro">
    <h2>1 はじめに</h2>
    <p>本稿は、拙稿「意味・文体・典拠マーカーの三層地図による仏教文献探索」を受け、対象を浄土教文献に狭めて再検討する探索的研究である。前稿では、意味的に近いこと、文体的に近いこと、典拠・引用経路として近いことは同一ではない、という点を中心命題とした。</p>
    <p>本稿では、法然の代表的著作として『選擇本願念佛集』を、親鸞の代表的著作として『顯淨土眞實教行證文類』を中心対象に据える。両者は浄土教の中心問題を共有するため、意味空間上でも大きく重なることが予想される。したがって、本稿で重要なのは「重なるかどうか」ではなく、重なった上で、どの方向に差異が出るかである。</p>
    <p>ここでいう「はみ出し領域」とは、共有核から相対的に離れて現れる本文領域、すなわち相対的突出領域を指す探索的な作業概念である。</p>
  </section>
  <section id="data">
    <h2>2 データ</h2>
    <p>分析本文はいずれもSAT大正新脩大藏經テキストデータベースから取得した漢文本文を用いた。比較アンカーとして、浄土教祖師文献から龍樹、天親、曇鸞、道綽、善導、源信のテキストを加えた。</p>
    {table(["分類", "著者", "文献", "SAT ID・範囲", "扱い", "チャンク数"], rows_corpus, "表1. 対象文献とチャンク数")}
    <p>本文取得では、SAT HTMLから本文行を抽出し、UI部品、HTMLタグ、画像プレースホルダ、SAT行番号の本文混入を除去した。公開版にはraw本文、processed text、chunk preview、embedding vectorを含めない。</p>
  </section>
  <section id="method">
    <h2>3 方法</h2>
    <p>本文は <code>tiktoken</code> の <code>cl100k_base</code> でトークン化し、700トークン、100トークン重なりでチャンク化した。チャンク本文はUnicode文字境界に合わせて作成し、各チャンクにSAT行範囲、チャンク番号、SHA-256 hashを付した。</p>
    <p>埋め込みにはOpenAI <code>text-embedding-3-large</code> を用いた。本稿で分析した各チャンクベクトルは3072次元である。法然・親鸞チャンクでPCAを適合し、祖師文献アンカーは同じPCA面へ投影した。PCA 2軸合計の寄与率は約11.6%であり、2次元図は探索用の投影である。</p>
    <ol>
      <li>意味層: 3072次元コサイン類似度、2次元PCA上の距離、最近傍非自己、最近傍アンカー。</li>
      <li>文体語彙層: 辞書ベースの語群カウント。厳密な文体計量ではなく、語彙・主題の局所的濃淡を示す代替指標である。</li>
      <li>典拠マーカー層: 経名、論釈名、祖師名、引用導入句の辞書カウント。引用検出そのものではない。</li>
    </ol>
    <p>はみ出し候補は、2次元PCA上の最近傍非自己距離 <span class="math-inline">d<sub>i</sub></span> と、3072次元空間での最近傍非自己コサイン類似度 <span class="math-inline">s<sub>i</sub></span> から、<span class="math-inline">p<sub>i</sub> = d<sub>i</sub>(1 - s<sub>i</sub>)</span> として抽出した。</p>
  </section>
  <section id="results">
    <h2>4 結果</h2>
    <figure id="fig-focus"><a href="../figures/sat-safe-honen-shinran-focus-map.png"><img src="../figures/sat-safe-honen-shinran-focus-map.png" alt="法然・親鸞の意味地図"></a><figcaption>図1. SAT漢文・Unicode-safeチャンクによる法然・親鸞の意味地図。</figcaption></figure>
    <figure id="fig-anchor"><a href="../figures/sat-safe-honen-shinran-high-priest-anchor-map.png"><img src="../figures/sat-safe-honen-shinran-high-priest-anchor-map.png" alt="法然・親鸞・祖師文献アンカー地図"></a><figcaption>図2. 法然・親鸞・祖師文献アンカー地図。</figcaption></figure>
    {table(["領域", "計算上のサイン", "主な語群・巻/章", "解釈"], rows_summary, "表2. 共有核とはみ出し領域の要約")}
    {table(["対象", "最近傍グループ", "チャンク数", "比率"], rows_nearest, "表3. 最近傍非自己の主要結果")}
    <figure id="fig-bars"><a href="../figures/shared-core-protrusion-nearest-bars.png"><img src="../figures/shared-core-protrusion-nearest-bars.png" alt="共有核とはみ出し領域と最近傍非自己の可視化"></a><figcaption>図3. 共有核とはみ出し領域と最近傍非自己の可視化。上段は定性的要約、下段は最近傍非自己数を示す。</figcaption></figure>
    <figure id="fig-honen-seq"><a href="../figures/honen-three-layer-sequence-heatmap.png"><img src="../figures/honen-three-layer-sequence-heatmap.png" alt="法然三層チャンク列"></a><figcaption>図4. 法然『選択集』三層チャンク列。文体語彙層は語群カウントの代替指標であり、典拠マーカー層は引用検出そのものではない。</figcaption></figure>
    <figure id="fig-shinran-seq"><a href="../figures/shinran-three-layer-sequence-heatmap.png"><img src="../figures/shinran-three-layer-sequence-heatmap.png" alt="親鸞三層チャンク列"></a><figcaption>図5. 親鸞『教行信証』三層チャンク列。</figcaption></figure>
    <p>法然側のはみ出し上位24件は、付属・証誠・選択総結10件、三輩・一向専念4件、本願念仏4件、三心・信心3件、正雑二行3件であった。親鸞側では、信巻13件、化身土巻8件を中心に広がる。</p>
    {table(["対象", "箇所", "SAT行範囲", "近傍・語群", "読解上の確認点"], rows_cases, "表4. 代表箇所の確認")}
  </section>
  <section id="discussion">
    <h2>5 考察</h2>
    <p>以下の考察は、埋め込み空間上の配置、高次元コサイン類似度、2次元PCA上のはみ出し、辞書ベースの語群、典拠マーカーから得た探索的所見である。本稿の結果は、既存研究を置き換える結論ではなく、既存研究と照合すべき精査候補を抽出する探索地図である。</p>
    <h3>法然は「念仏を選ぶ論理」を構成する</h3>
    <p>法然『選択集』の特徴は、念仏を諸行から選び出す論証にある。本分析で抽出したはみ出し領域でも、正雑二行、諸行との取捨、本願、三輩・一向専念、付属・証誠が強く現れた。</p>
    <h3>親鸞は「本願・信・証の典拠的体系」へ展開する</h3>
    <p>親鸞『教行信証』は、法然に近い領域を持ちながら、道綽、源信、曇鸞、天親、善導へ広がった。とくに信巻や化身土巻では、法然近接と親鸞側突出候補、祖師近接が混在する。</p>
    <h3>三層分析の意義</h3>
    <p>意味層だけでは解釈が混ざる。意味層、文体語彙層、典拠マーカー層を分けることで、意味的近接をただちに影響関係や教義的一致として読んでしまう危険を抑えることができる。</p>
  </section>
  <section id="limitations">
    <h2>6 限界</h2>
    <ol>
      <li>2次元PCAは全分散の約11.6%のみを示すため、図上の距離は高次元空間の近傍関係と必ずしも一致しない。</li>
      <li>チャンクは700トークン・100トークン重なりであり、巻・章・引用単位などの自然境界とは一致しない。</li>
      <li>語群カウントは辞書ベースの限定的な実装であり、否定、引用者、文脈、語義の違いを見ていない。</li>
      <li>典拠マーカー層は引用検出そのものではない。</li>
      <li>古写経本、異本、写本系資料はまだ直接分析に組み込んでいない。</li>
    </ol>
  </section>
  <section id="conclusion">
    <h2>7 結論</h2>
    <p>法然と親鸞は意味空間上で強く重なる。しかし、本稿で重要なのは、重なるかどうかではなく、共有核から何がどの方向へはみ出すかである。</p>
    <p>法然側のはみ出し領域は、念仏理解の単純な差というより、念仏を諸行から選び出す論証、すなわち正雑二行、取捨、選択、本願、付属・証誠のまとまりとして現れる。親鸞側のはみ出し領域は、信巻の罪と救済、化身土巻の方便・真仮整理、護法・鬼神・宇宙秩序、外教批判として現れ、法然側とは異なる広がり方を示した。</p>
    <p>これは既存研究を置き換える結論ではなく、歴史研究・引用研究との比較によって検証すべき精査候補である。</p>
  </section>
  <section id="references" class="references">
    <h2>参考文献</h2>
    {refs}
  </section>
</main>
<footer><div class="page">HTML版はWeb閲覧用の整理版です。引用時はPDF版と照合してください。</div></footer>
"""
    return html_shell("ja", f"{TITLE_JA}: {SUBTITLE_JA}", body)


def references(lang: str) -> str:
    if lang == "ja":
        items = [
            '上山大信「意味・文体・典拠マーカーの三層地図による仏教文献探索：宗派別参照群・阿弥陀経二訳・親鸞文献の予備的分析」2026. <a href="https://dueyama.github.io/buddhist-text-embedding-map/paper/">前論文HTML</a>（2026年6月5日閲覧）',
            'SAT大正新脩大藏經テキストデータベース. <a href="https://21dzk.l.u-tokyo.ac.jp/SAT/">https://21dzk.l.u-tokyo.ac.jp/SAT/</a>（2026年6月5日閲覧）',
            '森脇一掬「選択集と教行信証に関する一考察」『龍谷論叢』1, 48--72, 1953. INBUDS ID: IB00020630A. <a href="https://tripitaka.l.u-tokyo.ac.jp/INBUDS/">INBUDS</a>（2026年6月5日閲覧）',
            '稲葉秀賢「『教行信証』と『選択集』」『親鸞教学』21, 33--50, 1972. <a href="https://otani.repo.nii.ac.jp/records/10720">大谷大学リポジトリ</a>（2026年6月5日閲覧）',
            '梅原隆章「選択集と教行信証」『日本文化と浄土教論攷：井川定慶博士喜寿記念』362--371, 1974. INBUDS ID: IB00046839A. <a href="https://tripitaka.l.u-tokyo.ac.jp/INBUDS/">INBUDS</a>（2026年6月5日閲覧）',
            '浅井成海「『選択集』と『教行信証』――基本的問題の継承と展開――」『行信学報』18, 2004. <a href="https://www.gyousin.com/institute/journal/">行信教校</a>（2026年6月5日閲覧）',
            '根津茂『日本仏教を変えた親鸞の独自性：『教行信証』と『選択集』の比較から見えてきた、念仏の真価』法藏館, 2024. <a href="https://ndlsearch.ndl.go.jp/books/R100000001-I2711B17026510">NDL Search</a>（2026年6月5日閲覧）',
            '新纂浄土宗大辞典「選択本願念仏集」. <a href="https://jodoshuzensho.jp/daijiten/index.php/%E9%81%B8%E6%8A%9E%E6%9C%AC%E9%A1%98%E5%BF%B5%E4%BB%8F%E9%9B%86">jodoshuzensho.jp</a>（2026年6月5日閲覧）',
            '新纂浄土宗大辞典「黒谷上人語灯録」. <a href="https://jodoshuzensho.jp/daijiten/index.php/%E9%BB%92%E8%B0%B7%E4%B8%8A%E4%BA%BA%E8%AA%9E%E7%81%AF%E9%8C%B2">jodoshuzensho.jp</a>（2026年6月5日閲覧）',
            '浄土宗公式サイト「法然上人のご生涯と浄土宗の教え 選択集」. <a href="https://jodo.or.jp/newspaper/special/6226/">jodo.or.jp</a>（2026年6月5日閲覧）',
            '藤原智「『教行信証』における引用文について：古写経本による再検討」『近現代『教行信証』研究検証プロジェクト研究紀要』3, 63--107, 2020. <a href="https://www.jstage.jst.go.jp/article/kyogyoshinsho/3/0/3_63/_article/-char/ja/">J-STAGE</a>（2026年6月5日閲覧）',
            'OpenAI, Embeddings documentation. <a href="https://platform.openai.com/docs/guides/embeddings">platform.openai.com</a>（2026年6月5日閲覧）',
            'OpenAI, <code>tiktoken</code>. <a href="https://github.com/openai/tiktoken">GitHub</a>（2026年6月5日閲覧）',
        ]
    else:
        items = [
            'Daishin Ueyama, "Exploratory Mapping of Buddhist Texts with a Three-Layer Map of Meaning, Style, and Source Markers," 2026. <a href="https://dueyama.github.io/buddhist-text-embedding-map/paper/">Previous paper</a>. Accessed June 5, 2026.',
            'SAT Taisho Shinshu Daizokyo Text Database. <a href="https://21dzk.l.u-tokyo.ac.jp/SAT/">https://21dzk.l.u-tokyo.ac.jp/SAT/</a>. Accessed June 5, 2026.',
            'Moriwaki Ikku, "Senchakushu to Kyogyoshinsho ni kansuru ichi kosatsu," Ryukoku Ronsou 1, 48--72, 1953. INBUDS ID: IB00020630A.',
            'Inaba Shuken, "\'Kyogyoshinsho\' to \'Senchakushu\'," Shinran Kyogaku 21, 33--50, 1972.',
            'Umehara Ryusho, "Senchakushu to Kyogyoshinsho," 1974. INBUDS ID: IB00046839A.',
            'Asai Narumi, "\'Senchakushu\' to \'Kyogyoshinsho\'," Gyoshin Gakuho 18, 2004.',
            'Nezu Shigeru, Nihon Bukkyo o kaeta Shinran no dokujisei, Hozokan, 2024.',
            'Jodoshuzensho Dictionary, "Senchaku Hongan Nembutsu Shu." Accessed June 5, 2026.',
            'Jodoshu official site, "Senchakushu." Accessed June 5, 2026.',
            'Fujiwara Satoshi, "A Reexamination of Quotations in Kyogyoshinsho Based on Old Manuscript Sutras," 2020.',
            'OpenAI, Embeddings documentation. Accessed June 5, 2026.',
            'OpenAI, <code>tiktoken</code>. Accessed June 5, 2026.',
        ]
    return "<ol class=\"ref-list\">" + "\n".join(f"<li>{item}</li>" for item in items) + "</ol>"


def paper_en() -> str:
    rows_corpus = [
        ["Core", "Honen", "Senchakushu", "T2608", "Complete", "69"],
        ["Core", "Shinran", "Kyogyoshinsho", "T2646", "Complete", "191"],
        ["Anchor", "Nagarjuna", "Chapter on Easy Practice", "T1521, 0038a25--0040a22", "Excerpt", "6"],
        ["Anchor", "Vasubandhu", "Treatise on the Pure Land", "T1524", "Complete", "9"],
        ["Anchor", "Tanluan", "Commentary on the Treatise on Birth", "T1819", "Complete", "31"],
        ["Anchor", "Daochuo", "Anleji", "T1958", "Complete", "42"],
        ["Anchor", "Shandao", "Commentary on the Contemplation Sutra", "T1753", "Complete", "23"],
        ["Anchor", "Genshin", "Ojoyoshu", "T2682", "Complete", "73"],
    ]
    rows_summary = [
        ["Shared core", "Honen and Shinran chunks are mutually close; Daochuo and Shandao anchors also overlap.", "nembutsu/name, birth/Pure Land, shinjin/three minds", "A shared Pure Land problem field."],
        ["Honen divergence", "Honen chunks move away from non-Honen points and concentrate in selection-argument sections.", "right/miscellaneous practices, three grades, original vow, entrustment/verification", "Argument for selecting nembutsu from among other practices."],
        ["Shinran divergence", "Shinran chunks move away from non-Shinran points and concentrate in the Shin and Keshindo fascicles.", "Shin fascicle, Keshindo fascicle, sin/salvation, provisional/true sorting", "A source-based doctrinal architecture of vow, shinjin, realization, true land, and transformed land."],
    ]
    rows_cases = [
        ["Honen", "chunk 7, right/miscellaneous practices", "T2608, 83.0003a04--0003b04", "nearest: Shinran; nearest patriarch: Shandao; word group: right/miscellaneous practices", "A candidate for reading Honen's argument as the selection of nembutsu from other practices."],
        ["Shinran", "chunk 84, Shin fascicle", "T2646, 83.0614a08--0614b05", "nearest: Genshin; word group: sin/salvation", "A candidate showing that the Shin fascicle's sin/salvation problem touches a Genshin-like thematic field."],
        ["Shinran", "chunk 182, Keshindo fascicle", "T2646, 83.0640b28--0640c27", "nearest: Daochuo; word group: rejection/selection", "A candidate for external criticism and true/provisional sorting in the Keshindo fascicle."],
    ]
    body = f"""
<header>
  <div class="page paper-header">
    <h1>{TITLE_EN}</h1>
    <p class="subtitle">{SUBTITLE_EN}</p>
    <p class="meta">{AUTHOR_EN} / {DATE_EN}</p>
{nav('en', 'paper')}
  </div>
</header>
<main class="paper page">
  <section class="notice">
    <h2>Translation Note</h2>
    <p>This English HTML version is prepared as an access version for English-language readers. The Japanese v3 PDF remains the authoritative version for citation and close interpretation. The figures are currently shared with the Japanese version; English figure assets can be regenerated in a later publication pass.</p>
  </section>
  <section class="abstract" id="abstract">
    <h2>Abstract</h2>
    <p>This study examines how Honen's <em>Senchakushu</em> and Shinran's <em>Kyogyoshinsho</em> overlap in semantic space, and where each text diverges from their shared core. It uses a three-layer exploratory map consisting of a semantic layer, a lexical-thematic layer, and a source-marker layer. The lexical-thematic layer is not strict stylometry; it is a dictionary-based measure of local lexical and thematic density.</p>
    <p>Among 69 Honen chunks, the nearest neighbor outside the same author group is Shinran in 50 cases, Daochuo in 11, Genshin in 4, Shandao in 3, and Tanluan in 1. Among 191 Shinran chunks, the nearest outside group is distributed across Honen, Daochuo, Genshin, Tanluan, Vasubandhu, Shandao, and Nagarjuna. Honen's divergence zones concentrate around the argument for selecting nembutsu from among other practices. Shinran's divergence zones concentrate in the Shin and Keshindo fascicles, extending toward a source-based doctrinal architecture of vow, shinjin, realization, true land, transformed land, sin/salvation, and true/provisional sorting.</p>
    <p>The result is exploratory. It does not replace doctrinal, historical, or citation-based scholarship, but identifies candidate regions that should be compared with existing research.</p>
  </section>
  <p><strong>Keywords:</strong> Honen, Shinran, Senchakushu, Kyogyoshinsho, shared core, divergence zones, semantic embeddings, three-layer analysis, SAT, source-marker layer</p>
  <section class="toc">
    <h2>Contents</h2>
    <ol>
      <li><a href="#intro">Introduction</a></li>
      <li><a href="#data">Data</a></li>
      <li><a href="#method">Method</a></li>
      <li><a href="#results">Results</a></li>
      <li><a href="#discussion">Discussion</a></li>
      <li><a href="#limitations">Limitations</a></li>
      <li><a href="#conclusion">Conclusion</a></li>
      <li><a href="#references">References</a></li>
    </ol>
  </section>
  <section id="intro">
    <h2>1 Introduction</h2>
    <p>This paper narrows the framework of the preceding three-layer Buddhist text map to Pure Land materials, especially the relation between Honen and Shinran. The central issue is not whether the two authors overlap. Since both treat central Pure Land questions, substantial overlap is expected. The important question is where each text diverges after that overlap appears.</p>
    <p>Here, "divergence zones" refers to textual regions that move relatively away from the shared core. In the method section these are also called relative protrusion zones.</p>
  </section>
  <section id="data">
    <h2>2 Data</h2>
    <p>The main targets are Honen's <em>Senchakushu</em> and Shinran's <em>Kyogyoshinsho</em>. Pure Land patriarchal text anchors include Nagarjuna, Vasubandhu, Tanluan, Daochuo, Shandao, and Genshin. The public version does not include source text, processed text, chunk previews, or embedding vectors.</p>
    {table(["Type", "Author", "Work", "SAT ID/range", "Coverage", "Chunks"], rows_corpus, "Table 1. Texts and chunk counts")}
  </section>
  <section id="method">
    <h2>3 Method</h2>
    <p>The text was tokenized with <code>cl100k_base</code>, chunked into 700-token windows with 100-token overlap, and reconstructed at Unicode character boundaries. Embeddings were generated with OpenAI <code>text-embedding-3-large</code>; each vector has 3072 dimensions. PCA is used only as an exploratory two-dimensional projection.</p>
    <p>The three layers are: semantic similarity in the 3072-dimensional embedding space, lexical-thematic word-group counts, and explicit source-marker counts. The source-marker layer is not citation detection; it is a way of locating candidate regions for closer reading.</p>
    <p>The protrusion score is defined as <span class="math-inline">p<sub>i</sub> = d<sub>i</sub>(1 - s<sub>i</sub>)</span>, where <span class="math-inline">d<sub>i</sub></span> is the nearest non-self distance in the 2D PCA plane and <span class="math-inline">s<sub>i</sub></span> is the nearest non-self cosine similarity in the original 3072-dimensional space.</p>
  </section>
  <section id="results">
    <h2>4 Results</h2>
    <figure><a href="../../figures/sat-safe-honen-shinran-focus-map.png"><img src="../../figures/sat-safe-honen-shinran-focus-map.png" alt="Semantic map of Honen and Shinran"></a><figcaption>Figure 1. Semantic map of Honen and Shinran using SAT Chinese text and Unicode-safe chunks.</figcaption></figure>
    <figure><a href="../../figures/sat-safe-honen-shinran-high-priest-anchor-map.png"><img src="../../figures/sat-safe-honen-shinran-high-priest-anchor-map.png" alt="Honen, Shinran, and Pure Land patriarchal text anchors"></a><figcaption>Figure 2. Honen, Shinran, and Pure Land patriarchal text anchors.</figcaption></figure>
    {table(["Region", "Computational sign", "Main groups/volumes", "Interpretation"], rows_summary, "Table 2. Shared core and divergence zones")}
    <figure><a href="../../figures/shared-core-protrusion-nearest-bars.png"><img src="../../figures/shared-core-protrusion-nearest-bars.png" alt="Shared core, divergence zones, and nearest-neighbor counts"></a><figcaption>Figure 3. Shared core, divergence zones, and nearest-neighbor counts.</figcaption></figure>
    <figure><a href="../../figures/honen-three-layer-sequence-heatmap.png"><img src="../../figures/honen-three-layer-sequence-heatmap.png" alt="Three-layer chunk sequence for Honen"></a><figcaption>Figure 4. Three-layer chunk sequence for Honen's <em>Senchakushu</em>. The lexical-thematic layer is a word-group count proxy, and the source-marker layer is not citation detection.</figcaption></figure>
    <figure><a href="../../figures/shinran-three-layer-sequence-heatmap.png"><img src="../../figures/shinran-three-layer-sequence-heatmap.png" alt="Three-layer chunk sequence for Shinran"></a><figcaption>Figure 5. Three-layer chunk sequence for Shinran's <em>Kyogyoshinsho</em>.</figcaption></figure>
    {table(["Target", "Location", "SAT line range", "Neighbor/word group", "Reading point"], rows_cases, "Table 3. Representative candidate passages")}
  </section>
  <section id="discussion">
    <h2>5 Discussion</h2>
    <p>Honen's distinctive region appears less as a difference in the meaning of nembutsu itself than as a dense argument for why nembutsu should be selected from among other practices. Shinran's distribution, by contrast, expands from the shared Pure Land core toward the Shin and Keshindo fascicles and toward several Pure Land patriarchal anchors.</p>
    <p>The three-layer design matters because semantic proximity mixes quotation, shared topic, vocabulary, and authorial exposition. Separating semantic similarity, lexical-thematic density, and explicit source markers reduces the risk of reading embedding proximity as direct influence or doctrinal identity.</p>
  </section>
  <section id="limitations">
    <h2>6 Limitations</h2>
    <ol>
      <li>The two PCA axes explain only about 11.6 percent of the variance.</li>
      <li>Fixed-length chunks do not match fascicle, chapter, paragraph, or quotation boundaries.</li>
      <li>The lexical-thematic layer is dictionary-based and not strict stylometry.</li>
      <li>The source-marker layer does not distinguish quotation from authorial exposition.</li>
      <li>Manuscript variants and old manuscript sutra research are not yet integrated.</li>
    </ol>
  </section>
  <section id="conclusion">
    <h2>7 Conclusion</h2>
    <p>Honen and Shinran strongly overlap in semantic space. The central result is that their difference appears not primarily as a difference in the meaning of nembutsu itself, but as a difference in how the same Pure Land problem field is developed. Honen's divergence zones move toward the argument for selecting nembutsu; Shinran's divergence zones move toward a source-based doctrinal architecture centered on the Shin and Keshindo fascicles.</p>
    <p>This is not a replacement for existing doctrinal, historical, or citation-based scholarship. It is a map of candidate regions to be returned to those bodies of research.</p>
  </section>
  <section id="references" class="references">
    <h2>References</h2>
    {references('en')}
  </section>
</main>
<footer><div class="page">English access version. For citation, check the Japanese v3 PDF.</div></footer>
"""
    return html_shell("en", f"{TITLE_EN}: {SUBTITLE_EN}", body)


def source_provenance_html() -> str:
    body = f"""
<header><div class="page paper-header"><h1>出典・検証記録</h1><p class="subtitle">Okyou2 publication provenance</p>{nav('ja', 'source')}</div></header>
<main class="paper page">
  <section class="notice"><h2>公開境界</h2><p>このページは公開用の短い出典・検証サマリです。詳細な作業台帳はリポジトリ内の <code>memory.md</code> と <code>docs/source-provenance.md</code> を参照してください。</p></section>
  <h2>本文・派生データ</h2>
  <ul>
    <li>raw/processed本文、chunk preview、embedding cache、embedding vectorは公開HTMLに含めない。</li>
    <li>図表、SAT行範囲、集計値、検証メモ、公開可能な派生情報のみを掲載する。</li>
    <li>本文提供元の利用条件は各提供元に従う。</li>
  </ul>
  <h2>主要入力</h2>
  <ul>
    <li>SAT大正新脩大藏經テキストデータベース。</li>
    <li>既存のUnicode-safe SAT漢文チャンクと既存embedding cache。</li>
    <li>OpenAI <code>text-embedding-3-large</code> による3072次元埋め込み。</li>
  </ul>
  <h2>公開前検証</h2>
  <ul>
    <li>TeX PDFは <code>uplatex</code> と <code>dvipdfmx</code> で生成。</li>
    <li>PDFはPyMuPDFでPNGレンダリングして目視確認。</li>
    <li>先行 <code>Okyou</code> repository は読み取り専用で参照し、変更しない。</li>
  </ul>
  <h2>リリース後の訂正</h2>
  <p>公開リリース後は、本文・PDF・主要HTMLをその時点の固定版として扱う。誤記、補足、解釈の変更、図表差し替えが必要な場合は、公開版を黙って置き換えず、<a href="errata.html">エラッタ</a>に記録する。</p>
  <h2>固定公開物</h2>
  <p>公開用PDFとTeXのSHA-256は <a href="checksums.txt">checksums.txt</a> に記録する。tag/release作成時には、このハッシュとrelease tag上のファイルが一致することを確認する。</p>
</main>
<footer><div class="page">Okyou2 provenance summary.</div></footer>
"""
    return html_shell("ja", "Okyou2 出典・検証記録", body)


def errata_html() -> str:
    body = f"""
<header><div class="page paper-header"><h1>エラッタ</h1><p class="subtitle">Okyou2 release errata</p>{nav('ja', 'errata')}</div></header>
<main class="paper page">
  <section class="notice">
    <h2>運用方針</h2>
    <p>リリース後の公開版は固定版として扱う。誤記、リンク切れ、図表の修正、補足説明、解釈の変更が必要になった場合は、公開済み本文を黙って差し替えず、このページと <code>docs/ERRATA.md</code> に記録する。</p>
  </section>
  <h2>記録形式</h2>
  <div class="table-wrap">
    <table>
      <thead><tr><th>日付</th><th>対象</th><th>種別</th><th>内容</th><th>対応</th></tr></thead>
      <tbody>
        <tr><td>未登録</td><td>v3公開版</td><td>-</td><td>現時点でリリース後エラッタはない。</td><td>-</td></tr>
      </tbody>
    </table>
  </div>
  <h2>種別</h2>
  <ul>
    <li><strong>訂正:</strong> 誤記、数値、リンク、図表ラベルなどの明確な誤り。</li>
    <li><strong>補足:</strong> 本文の結論を変えない説明追加。</li>
    <li><strong>改訂候補:</strong> 解釈や方法上の変更が必要だが、固定版本文には直接反映しないもの。</li>
  </ul>
</main>
<footer><div class="page">Released paper changes are tracked as errata.</div></footer>
"""
    return html_shell("ja", "Okyou2 エラッタ", body)


def errata_md() -> str:
    return """# Errata

このファイルは、公開リリース後の訂正・補足・変更候補を記録する。

## 運用方針

- リリース後の公開版PDF/HTMLは固定版として扱う。
- 誤記、数値、リンク、図表ラベル、説明不足、解釈変更が見つかった場合は、公開済み本文を黙って差し替えず、このファイルと `docs/errata.html` に記録する。
- 本文を更新する必要がある場合は、新しい版として明示し、旧版との差分と理由をエラッタに残す。

## 記録形式

| 日付 | 対象 | 種別 | 内容 | 対応 |
| --- | --- | --- | --- | --- |
| 未登録 | v3公開版 | - | 現時点でリリース後エラッタはない。 | - |

## 種別

- 訂正: 誤記、数値、リンク、図表ラベルなどの明確な誤り。
- 補足: 本文の結論を変えない説明追加。
- 改訂候補: 解釈や方法上の変更が必要だが、固定版本文には直接反映しないもの。
"""


def publication_md() -> str:
    return """# GitHub Pages 公開準備

## 公開入口

- `docs/index.html`: 日本語トップ
- `docs/en/index.html`: English top
- `docs/paper/index.html`: 日本語HTML論文
- `docs/paper/en/index.html`: English HTML access version
- `docs/paper/honen-shinran-shared-core-paper.pdf`: 日本語PDF
- `docs/paper/honen-shinran-shared-core-paper.tex`: 日本語TeX
- `docs/paper/okyou2-honen-shinran-english-terminology.md`: 英語版訳語メモ
- `docs/source-provenance.html`: 公開用出典・検証サマリ
- `docs/errata.html`: リリース後エラッタ
- `docs/ERRATA.md`: エラッタ記録のMarkdown原本
- `docs/checksums.txt`: 固定公開物のSHA-256記録

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

公開用日本語PDFを引用・精読用の正本とし、英語HTMLは access version として提供する。英語版PDF/TeXは次の公開準備段階で作成できる。
"""


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"Wrote {path.relative_to(ROOT)}")


def main() -> None:
    write(DOCS / ".nojekyll", "")
    write(DOCS / "index.html", home_ja())
    write(DOCS / "en" / "index.html", home_en())
    write(DOCS / "paper" / "index.html", paper_ja())
    write(DOCS / "paper" / "en" / "index.html", paper_en())
    write(DOCS / "source-provenance.html", source_provenance_html())
    write(DOCS / "errata.html", errata_html())
    write(DOCS / "ERRATA.md", errata_md())
    write(DOCS / "PUBLICATION.md", publication_md())


if __name__ == "__main__":
    main()
