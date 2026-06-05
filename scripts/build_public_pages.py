from __future__ import annotations

import html
import re
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
PUBLIC_PAPER_EN_PDF = "honen-shinran-shared-core-paper-en.pdf"
PUBLIC_PAPER_EN_TEX = "honen-shinran-shared-core-paper-en.tex"


STYLE = r"""
:root {
  color-scheme: light;
  --bg: #f6f7f2;
  --paper: #ffffff;
  --panel: #ffffff;
  --ink: #1f2723;
  --muted: #657069;
  --line: #d8ded6;
  --accent: #2f6f73;
  --accent-2: #7f5d2e;
  --soft: #eef4f1;
  --warm: #9a5b3f;
  --warn: #9a5b3f;
  --gold: #a7832d;
  font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Yu Gothic", "Noto Sans JP", "Noto Sans", sans-serif;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body { margin: 0; background: var(--bg); color: var(--ink); line-height: 1.7; }
a { color: var(--accent); text-underline-offset: 3px; }
header { background: var(--paper); border-bottom: 1px solid var(--line); }
.page, .wrap { width: min(1120px, calc(100% - 40px)); margin: 0 auto; }
.hero { padding: 38px 0 34px; display: grid; grid-template-columns: minmax(0, 1fr) minmax(320px, 0.92fr); gap: 28px; align-items: center; }
.paper-header { padding: 34px 0 20px; }
h1 { margin: 0 0 12px; font-size: clamp(28px, 4.2vw, 48px); line-height: 1.16; letter-spacing: 0; }
.subtitle { margin: 0 0 12px; color: var(--muted); font-size: clamp(17px, 2.2vw, 22px); line-height: 1.45; }
.lead { margin: 0; color: var(--muted); font-size: 16px; }
.meta { color: var(--muted); font-size: 14px; }
.site-nav { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin-top: 22px; }
.nav-primary, .nav-tools { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.nav-tools { margin-left: 0; }
.nav-link { display: inline-flex; min-height: 38px; align-items: center; justify-content: center; padding: 0 14px; border: 1px solid var(--line); border-radius: 6px; color: var(--ink); background: #fff; font-size: 14px; text-decoration: none; }
.nav-link[aria-current="page"] { border-color: #bccbc8; background: #f4f7f5; color: var(--accent); font-weight: 700; }
.pdf-link { color: var(--muted); }
.lang-switch { display: inline-flex; min-height: 38px; overflow: hidden; border: 1px solid var(--line); border-radius: 999px; background: #fff; }
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
.card, .notice, .figure-row { border: 1px solid var(--line); border-radius: 8px; background: var(--panel); }
.card { padding: 16px; }
.card h2, .card h3 { margin-top: 0; font-size: 18px; }
.card p { color: var(--muted); font-size: 14px; }
.figure-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin: 20px 0; }
.figure-row { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0; overflow: hidden; margin-top: 18px; }
.figure-row a { display: block; min-width: 0; border-right: 1px solid var(--line); background: #fff; color: var(--ink); text-decoration: none; }
.figure-row a:last-child { border-right: 0; }
.figure-row img { width: 100%; aspect-ratio: 4 / 3; object-fit: contain; display: block; background: #fbfcfa; border-bottom: 1px solid var(--line); }
.figure-row span { display: block; padding: 10px 12px; color: var(--muted); font-size: 13px; }
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
.latex-paper h2 .secno, .latex-paper h3 .secno { color: var(--muted); margin-right: 0.45em; }
.latex-paper { width: min(860px, calc(100% - 32px)); font-family: "Hiragino Mincho ProN", "Yu Mincho", "Noto Serif JP", serif; font-size: 16px; line-height: 1.9; }
.latex-paper h2 { font-size: 22px; margin-top: 36px; }
.latex-paper h3 { font-size: 17px; margin-top: 24px; }
.latex-paper .abstract { border-left: 0; background: transparent; padding: 0; margin-bottom: 20px; }
.latex-paper .abstract h2 { text-align: center; font-size: 18px; margin-top: 0; }
.latex-paper .keywords { font-weight: 650; }
.latex-paper .display-math { text-align: center; margin: 18px 0; font-family: "Times New Roman", serif; font-size: 1.08em; }
.latex-paper .math-inline { font-family: "Times New Roman", serif; }
.latex-paper .table-wrap table { min-width: 720px; }
.latex-paper figure img { max-height: none; object-fit: contain; border-radius: 0; }
.english-paper { font-family: Georgia, "Times New Roman", "Noto Serif", serif; }
.english-paper .abstract h2 { text-align: left; }
.ref-list { font-size: 13px; line-height: 1.6; }
.ref-list li { margin-bottom: 0.75em; }
.pill-list { display: flex; flex-wrap: wrap; gap: 8px; padding: 0; margin: 12px 0 0; list-style: none; }
.pill-list li { border: 1px solid var(--line); border-radius: 999px; padding: 4px 10px; background: #fff; color: var(--muted); font-size: 13px; }
.source-link { font-weight: 650; }
footer { border-top: 1px solid var(--line); background: var(--paper); padding: 18px 0; color: var(--muted); font-size: 12px; }
@media (max-width: 760px) {
  .hero, .grid, .figure-grid, .figure-row { grid-template-columns: 1fr; }
  .figure-row a { border-right: 0; border-bottom: 1px solid var(--line); }
  .figure-row a:last-child { border-bottom: 0; }
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
        nested = current in {"paper", "errata"}
        top = "../" if nested else "./"
        paper_href = "./" if current == "paper" else ("../paper/" if nested else "paper/")
        pdf_href = PUBLIC_PAPER_PDF if current == "paper" else (f"../paper/{PUBLIC_PAPER_PDF}" if nested else f"paper/{PUBLIC_PAPER_PDF}")
        source_href = "../source-provenance.html" if nested else "source-provenance.html"
        errata_href = "./" if current == "errata" else ("../errata/" if current == "paper" else "errata/")
        license_href = "../license.html" if nested else "license.html"
        ja_href = {
            "paper": "./",
            "errata": "./",
            "source": "source-provenance.html",
            "license": "license.html",
        }.get(current, "./")
        en_top = "en/" if current == "errata" else ("en/" if current == "paper" else "en/")
        return f"""
<nav class="site-nav" aria-label="サイト内ナビゲーション">
  <div class="nav-primary">
    <a class="nav-link" href="{top}"{aria_page(current == 'home')}>トップ</a>
    <a class="nav-link" href="{paper_href}"{aria_page(current == 'paper')}>論文</a>
    <a class="nav-link" href="{errata_href}"{aria_page(current == 'errata')}>Errata</a>
    <a class="nav-link" href="{source_href}"{aria_page(current == 'source')}>出典・検証記録</a>
    <a class="nav-link" href="{license_href}"{aria_page(current == 'license')}>ライセンス</a>
  </div>
  <div class="nav-tools">
    <span class="lang-switch" aria-label="言語切替">
      <a href="{ja_href}"{aria_true(True)}>日本語</a>
      <a href="{en_top}">English</a>
    </span>
    <a class="nav-link pdf-link" href="{pdf_href}">PDF JP</a>
  </div>
</nav>"""
    if current == "home":
        top = "./"
        paper_href = "../paper/en/"
        errata_href = "../errata/en/"
        source_href = "../source-provenance.html"
        license_href = "../license.html"
        pdf_en = f"../paper/{PUBLIC_PAPER_EN_PDF}"
        pdf_ja = f"../paper/{PUBLIC_PAPER_PDF}"
        ja = "../"
    elif current == "paper":
        top = "../../en/"
        paper_href = "./"
        errata_href = "../../errata/en/"
        source_href = "../../source-provenance.html"
        license_href = "../../license.html"
        pdf_en = f"../{PUBLIC_PAPER_EN_PDF}"
        pdf_ja = f"../{PUBLIC_PAPER_PDF}"
        ja = "../"
    else:
        top = "../../en/"
        paper_href = "../../paper/en/"
        errata_href = "./"
        source_href = "../../source-provenance.html"
        license_href = "../../license.html"
        pdf_en = f"../../paper/{PUBLIC_PAPER_EN_PDF}"
        pdf_ja = f"../../paper/{PUBLIC_PAPER_PDF}"
        ja = "../"
    return f"""
<nav class="site-nav" aria-label="Site navigation">
  <div class="nav-primary">
    <a class="nav-link" href="{top}"{aria_page(current == 'home')}>Top</a>
    <a class="nav-link" href="{paper_href}"{aria_page(current == 'paper')}>Paper</a>
    <a class="nav-link" href="{errata_href}"{aria_page(current == 'errata')}>Errata</a>
    <a class="nav-link" href="{source_href}">Provenance</a>
    <a class="nav-link" href="{license_href}">License</a>
  </div>
  <div class="nav-tools">
    <span class="lang-switch" aria-label="Language">
      <a href="{ja}">日本語</a>
      <a href="./"{aria_true(True)}>English</a>
    </span>
    <a class="nav-link pdf-link" href="{pdf_ja}">PDF JP</a>
    <a class="nav-link pdf-link" href="{pdf_en}">PDF EN</a>
  </div>
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
      <h2>論文</h2>
      <p>日本語PDFを正式な製本版とし、HTML・PDF・TeXソースを公開します。英語版はAI支援翻訳版として別ページに置きます。</p>
    </article>
    <article class="card">
      <h2>Errata</h2>
      <p>リリース後の訂正・補足は<a href="errata/">Errata</a>として公開し、公開済み本文を黙って差し替えません。</p>
    </article>
    <article class="card">
      <h2>English</h2>
      <p>英語読者向けに、前稿と同じくAI支援翻訳版のHTML・PDFを公開します。</p>
    </article>
    <article class="card">
      <h2>コード</h2>
      <p>GitHub Pages生成、TeX整合、図表生成、検証用スクリプトを公開します。APIキーとキャッシュは含めません。</p>
    </article>
    <article class="card">
      <h2>出典・検証</h2>
      <p><a href="source-provenance.html">出典・検証記録</a>で、本文再配布の境界、生成手順、公開前チェックを確認できます。</p>
    </article>
    <article class="card">
      <h2>公開版の固定</h2>
      <p>公開PDF/TeXのSHA-256を<a href="checksums.txt">checksums.txt</a>に記録し、以後の補足はErrataとして重ねます。</p>
    </article>
  </section>
  <section class="notice">
    <h2>公開境界</h2>
    <p>この公開版は本文そのもの、processed text、chunk preview、embedding cache、embedding vectorを含みません。図表・集計・SAT行範囲・検証メモなど、本文を含まない派生情報のみを公開対象にします。</p>
    <p>コードはMIT License、論文・図表・公開文書・公開用派生データはCC BY 4.0で公開します。元本文は再配布せず、各提供元の利用条件に従います。詳細は<a href="license.html">ライセンス</a>を参照してください。</p>
    <p>リリース後は公開版本文を直接書き換えず、訂正・補足・変更履歴は<a href="errata/">Errata</a>として公開する。</p>
    <p>固定公開物のSHA-256は <a href="checksums.txt">checksums.txt</a> に記録する。</p>
  </section>
  <section class="figure-row" aria-label="主要図">
    <a href="figures/sat-safe-honen-shinran-high-priest-anchor-map.png">
      <img src="figures/sat-safe-honen-shinran-high-priest-anchor-map.png" alt="法然・親鸞・祖師文献アンカー地図">
      <span>祖師文献アンカー地図</span>
    </a>
    <a href="figures/shared-core-protrusion-nearest-bars.png">
      <img src="figures/shared-core-protrusion-nearest-bars.png" alt="共有核とはみ出し領域と最近傍非自己の可視化">
      <span>共有核とはみ出し領域</span>
    </a>
    <a href="figures/shinran-three-layer-sequence-heatmap.png">
      <img src="figures/shinran-three-layer-sequence-heatmap.png" alt="親鸞三層チャンク列">
      <span>親鸞三層チャンク列</span>
    </a>
  </section>
</main>
<footer><div class="page">Honen-Shinran Shared Core Map / GitHub Pages publication. Source texts remain subject to each provider's terms.</div></footer>
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
      <a href="../figures/en/sat-safe-honen-shinran-focus-map.png"><img src="../figures/en/sat-safe-honen-shinran-focus-map.png" alt="Semantic map of Honen and Shinran"></a>
      <figcaption>The central map for reading the shared core and divergence zones.</figcaption>
    </figure>
  </div>
</header>
<main class="home page">
  <section class="grid">
    <article class="card">
      <h2>Paper</h2>
      <p>The Japanese paper is the authoritative print/book edition. The English page is an AI-assisted translation for access by English-language readers.</p>
    </article>
    <article class="card">
      <h2>Errata</h2>
      <p>Corrections and additions after release are published through <a href="../errata/en/">Errata</a>, rather than silent rewrites of the fixed release.</p>
    </article>
    <article class="card">
      <h2>Terminology</h2>
      <p>Translation terms used by the English HTML paper are recorded separately.</p>
    </article>
    <article class="card">
      <h2>Code</h2>
      <p>Generation, alignment, figure, and validation scripts are published without API keys or local caches.</p>
    </article>
    <article class="card">
      <h2>Provenance</h2>
      <p><a href="../source-provenance.html">Source and validation notes</a> record the publication boundary and verification steps.</p>
    </article>
    <article class="card">
      <h2>Fixed PDFs</h2>
      <p>SHA-256 checksums for public PDF/TeX files are recorded in <a href="../checksums.txt">checksums.txt</a>.</p>
    </article>
  </section>
  <section class="notice">
    <h2>Publication Boundary</h2>
    <p>This public edition does not redistribute source text, processed text, chunk previews, embedding caches, or embedding vectors. It publishes only derived figures, tables, line ranges, and documentation.</p>
    <p>Code is released under the MIT License. The paper, figures, public documentation, and public derived data are released under CC BY 4.0. Source texts are not redistributed and remain subject to each provider's terms. See the <a href="../license.html">license page</a>.</p>
    <p>After release, the public paper is treated as a fixed release. Corrections and additions are published through the <a href="../errata/en/">Errata</a> page rather than silently rewriting the release text.</p>
    <p>SHA-256 checksums for fixed public artifacts are recorded in <a href="../checksums.txt">checksums.txt</a>.</p>
  </section>
  <section class="figure-row" aria-label="Key figures">
    <a href="../figures/en/sat-safe-honen-shinran-high-priest-anchor-map.png">
      <img src="../figures/en/sat-safe-honen-shinran-high-priest-anchor-map.png" alt="Honen, Shinran, and Pure Land patriarchal anchors">
      <span>Patriarchal anchors</span>
    </a>
    <a href="../figures/en/shared-core-protrusion-nearest-bars.png">
      <img src="../figures/en/shared-core-protrusion-nearest-bars.png" alt="Shared core and divergence zones">
      <span>Shared core and divergence</span>
    </a>
    <a href="../figures/en/shinran-three-layer-sequence-heatmap.png">
      <img src="../figures/en/shinran-three-layer-sequence-heatmap.png" alt="Shinran three-layer chunk sequence">
      <span>Shinran three-layer sequence</span>
    </a>
  </section>
</main>
<footer><div class="page">Honen-Shinran Shared Core Map / GitHub Pages publication.</div></footer>
"""
    return html_shell("en", TITLE_EN, body)


def table(headers: list[str], rows: list[list[str]], caption: str | None = None, ident: str | None = None) -> str:
    cap = f"<caption>{caption}</caption>" if caption else ""
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = "\n".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    div_id = f' id="{ident}"' if ident else ""
    return f'<div class="table-wrap"{div_id}><table>{cap}<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def tex_plain(text: str) -> str:
    replacements = {
        r"\%": "%",
        r"\_": "_",
        r"\&": "&",
        r"\#": "#",
        r"\$": "$",
        r"\{": "{",
        r"\}": "}",
        "~": " ",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text


def math_html(text: str) -> str:
    value = tex_plain(text.strip())
    value = re.sub(r"\\texttt\{([^{}]*)\}", r"\1", value)
    value = value.replace(r"\%", "%")
    value = html.escape(value)
    value = re.sub(r"([A-Za-z])_\{([^}]+)\}", r"\1<sub>\2</sub>", value)
    value = re.sub(r"([A-Za-z])_([A-Za-z0-9]+)", r"\1<sub>\2</sub>", value)
    value = value.replace(r"\times", "×")
    return value


def protect_html(parts: list[str], value: str) -> str:
    token = f"@@HTML{len(parts)}@@"
    parts.append(value)
    return token


def latex_inline(text: str, label_map: dict[str, tuple[str, int]], cite_map: dict[str, int]) -> str:
    text = tex_plain(text.strip())
    protected: list[str] = []

    def code_repl(match: re.Match[str]) -> str:
        return protect_html(protected, f"<code>{html.escape(tex_plain(match.group(1)))}</code>")

    def strong_repl(match: re.Match[str]) -> str:
        return protect_html(protected, f"<strong>{latex_inline(match.group(1), label_map, cite_map)}</strong>")

    def url_repl(match: re.Match[str]) -> str:
        url = tex_plain(match.group(1))
        safe_url = html.escape(url, quote=True)
        return protect_html(protected, f'<a href="{safe_url}">{html.escape(url)}</a>')

    def href_repl(match: re.Match[str]) -> str:
        url = tex_plain(match.group(1))
        label = latex_inline(match.group(2), label_map, cite_map)
        safe_url = html.escape(url, quote=True)
        return protect_html(protected, f'<a href="{safe_url}">{label}</a>')

    def emph_repl(match: re.Match[str]) -> str:
        return protect_html(protected, f"<em>{latex_inline(match.group(1), label_map, cite_map)}</em>")

    def ref_repl(match: re.Match[str]) -> str:
        key = match.group(1)
        kind, number = label_map.get(key, ("ref", 0))
        if number:
            return protect_html(protected, f'<a href="#{html.escape(key, quote=True)}">{number}</a>')
        return "?"

    def cite_repl(match: re.Match[str]) -> str:
        links = []
        for key in [item.strip() for item in match.group(1).split(",")]:
            number = cite_map.get(key)
            if number:
                links.append(f'<a href="#ref-{html.escape(key, quote=True)}">{number}</a>')
            else:
                links.append("?")
        return protect_html(protected, "[" + ", ".join(links) + "]")

    def math_repl(match: re.Match[str]) -> str:
        return protect_html(protected, f'<span class="math-inline">{math_html(match.group(1))}</span>')

    text = re.sub(r"\\texttt\{([^{}]*)\}", code_repl, text)
    text = re.sub(r"\\href\{([^{}]*)\}\{([^{}]*)\}", href_repl, text)
    text = re.sub(r"\\emph\{([^{}]*)\}", emph_repl, text)
    text = re.sub(r"\\textbf\{([^{}]*)\}", strong_repl, text)
    text = re.sub(r"\\url\{([^{}]*)\}", url_repl, text)
    text = re.sub(r"\\cite\{([^{}]*)\}", cite_repl, text)
    text = re.sub(r"\\ref\{([^{}]*)\}", ref_repl, text)
    text = re.sub(r"\\\((.*?)\\\)", math_repl, text)
    text = text.replace(r"\noindent", "")
    text = text.replace(r"\quad", " ")
    text = text.replace("{", "").replace("}", "")
    escaped = html.escape(text)
    for idx, value in enumerate(protected):
        escaped = escaped.replace(f"@@HTML{idx}@@", value)
    return escaped


def extract_braced(line: str, command: str) -> str | None:
    prefix = "\\" + command + "{"
    start = line.find(prefix)
    if start == -1:
        return None
    pos = start + len(prefix)
    depth = 1
    out: list[str] = []
    while pos < len(line):
        char = line[pos]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return "".join(out)
        out.append(char)
        pos += 1
    return None


def build_latex_maps(tex: str) -> tuple[dict[str, tuple[str, int]], dict[str, int]]:
    label_map: dict[str, tuple[str, int]] = {}
    fig_no = 0
    table_no = 0
    block_re = re.compile(r"\\begin\{(figure|table)\}.*?\\end\{\1\}", re.S)
    for match in block_re.finditer(tex):
        block = match.group(0)
        label_match = re.search(r"\\label\{([^}]+)\}", block)
        if not label_match:
            continue
        label = label_match.group(1)
        if match.group(1) == "figure":
            fig_no += 1
            label_map[label] = ("fig", fig_no)
        else:
            table_no += 1
            label_map[label] = ("tab", table_no)
    cite_map = {
        key: idx + 1
        for idx, key in enumerate(re.findall(r"\\bibitem\{([^}]+)\}", tex))
    }
    return label_map, cite_map


def read_environment(lines: list[str], start: int, env: str) -> tuple[list[str], int]:
    collected: list[str] = []
    i = start + 1
    end_marker = f"\\end{{{env}}}"
    while i < len(lines):
        if lines[i].strip().startswith(end_marker):
            return collected, i + 1
        collected.append(lines[i])
        i += 1
    return collected, i


def paragraph_html(lines: list[str], label_map: dict[str, tuple[str, int]], cite_map: dict[str, int]) -> str:
    text = " ".join(line.strip() for line in lines).strip()
    if not text:
        return ""
    if text.startswith(r"\noindent\textbf{キーワード：}") or text.startswith(r"\noindent \textbf{Keywords:}"):
        text = text.replace(r"\noindent", "", 1)
        return f'<p class="keywords">{latex_inline(text, label_map, cite_map)}</p>'
    return f"<p>{latex_inline(text, label_map, cite_map)}</p>"


def convert_enumerate(block: list[str], label_map: dict[str, tuple[str, int]], cite_map: dict[str, int]) -> str:
    text = "\n".join(block)
    items = [item.strip() for item in re.split(r"\\item", text) if item.strip()]
    lis = "\n".join(f"<li>{latex_inline(item, label_map, cite_map)}</li>" for item in items)
    return f"<ol>\n{lis}\n</ol>"


def split_table_row(line: str) -> list[str]:
    line = line.strip()
    line = re.sub(r"\\\\\s*$", "", line)
    return [cell.strip() for cell in line.split("&")]


def convert_table(
    block: list[str],
    label_map: dict[str, tuple[str, int]],
    cite_map: dict[str, int],
    table_label: str = "表",
) -> str:
    source = "\n".join(block)
    caption = extract_braced(source, "caption") or ""
    label_match = re.search(r"\\label\{([^}]+)\}", source)
    label = label_match.group(1) if label_match else ""
    number = label_map.get(label, ("tab", 0))[1]
    tabular_start = source.find(r"\begin{tabular}")
    tabular_end = source.find(r"\end{tabular}")
    if tabular_start == -1 or tabular_end == -1:
        return ""
    content_start = source.find("\n", tabular_start)
    if content_start == -1 or content_start >= tabular_end:
        return ""
    tabular_content = source[content_start:tabular_end]
    rows: list[tuple[str, list[str]]] = []
    section = "head"
    for raw in tabular_content.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith(r"\toprule") or line.startswith(r"\bottomrule"):
            continue
        if line.startswith(r"\midrule"):
            section = "body"
            continue
        if "&" not in line:
            continue
        rows.append((section, split_table_row(line)))
    head_rows = [cells for part, cells in rows if part == "head"]
    body_rows = [cells for part, cells in rows if part == "body"]
    thead = ""
    if head_rows:
        thead_cells = "".join(f"<th>{latex_inline(cell, label_map, cite_map)}</th>" for cell in head_rows[0])
        thead = f"<thead><tr>{thead_cells}</tr></thead>"
    body = "\n".join(
        "<tr>" + "".join(f"<td>{latex_inline(cell, label_map, cite_map)}</td>" for cell in row) + "</tr>"
        for row in body_rows
    )
    cap = f"<caption>{table_label} {number}. {latex_inline(caption, label_map, cite_map)}</caption>" if caption else ""
    table_id = f' id="{html.escape(label, quote=True)}"' if label else ""
    return f'<div class="table-wrap"{table_id}><table>{cap}{thead}<tbody>{body}</tbody></table></div>'


def convert_figure(
    block: list[str],
    label_map: dict[str, tuple[str, int]],
    cite_map: dict[str, int],
    figure_label: str = "図",
    image_prefix: str = "",
) -> str:
    source = "\n".join(block)
    image_match = re.search(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", source)
    caption = extract_braced(source, "caption") or ""
    label_match = re.search(r"\\label\{([^}]+)\}", source)
    label = label_match.group(1) if label_match else ""
    number = label_map.get(label, ("fig", 0))[1]
    if not image_match:
        return ""
    src = image_prefix + tex_plain(image_match.group(1))
    caption_html = latex_inline(caption, label_map, cite_map)
    alt_text = re.sub(
        r"\\ref\{([^}]+)\}",
        lambda match: str(label_map.get(match.group(1), ("", 0))[1] or ""),
        tex_plain(caption),
    )
    alt_text = re.sub(r"\\cite\{([^}]+)\}", "", alt_text)
    alt_text = re.sub(r"\\[A-Za-z]+\{([^{}]*)\}", r"\1", alt_text)
    alt_text = alt_text.replace("{", "").replace("}", "").strip()
    figure_id = f' id="{html.escape(label, quote=True)}"' if label else ""
    safe_src = html.escape(src, quote=True)
    return (
        f"<figure{figure_id}>"
        f'<a href="{safe_src}"><img src="{safe_src}" alt="{html.escape(alt_text, quote=True)}"></a>'
        f"<figcaption>{figure_label} {number}. {caption_html}</figcaption>"
        "</figure>"
    )


def convert_bibliography(
    block: list[str],
    label_map: dict[str, tuple[str, int]],
    cite_map: dict[str, int],
    title: str = "参考文献",
) -> str:
    source = "\n".join(block)
    pieces = re.split(r"\\bibitem\{([^}]+)\}", source)
    items = []
    for idx in range(1, len(pieces), 2):
        key = pieces[idx]
        content = pieces[idx + 1].strip()
        number = cite_map.get(key, len(items) + 1)
        body = latex_inline(" ".join(content.splitlines()), label_map, cite_map)
        items.append(f'<li id="ref-{html.escape(key, quote=True)}" value="{number}">{body}</li>')
    return f'<section id="references" class="references"><h2>{title}</h2><ol class="ref-list">\n' + "\n".join(items) + "\n</ol></section>"


def convert_latex_body(
    tex: str,
    abstract_title: str = "要旨",
    figure_label: str = "図",
    table_label: str = "表",
    references_title: str = "参考文献",
    image_prefix: str = "",
) -> str:
    label_map, cite_map = build_latex_maps(tex)
    body = tex.split(r"\begin{document}", 1)[1].split(r"\end{document}", 1)[0]
    body = body.replace(r"\maketitle", "")
    lines = body.splitlines()
    out: list[str] = []
    paragraph: list[str] = []
    sec_no = 0
    sub_no = 0
    unnumbered_no = 0

    def flush() -> None:
        nonlocal paragraph
        html_block = paragraph_html(paragraph, label_map, cite_map)
        if html_block:
            out.append(html_block)
        paragraph = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            flush()
            i += 1
            continue
        if line.startswith(r"\begin{abstract}"):
            flush()
            block, i = read_environment(lines, i, "abstract")
            paras = []
            current: list[str] = []
            for raw in block:
                if raw.strip():
                    current.append(raw)
                elif current:
                    paras.append(paragraph_html(current, label_map, cite_map))
                    current = []
            if current:
                paras.append(paragraph_html(current, label_map, cite_map))
            out.append(f'<section class="abstract" id="abstract"><h2>{abstract_title}</h2>' + "\n".join(paras) + "</section>")
            continue
        if line.startswith(r"\section{"):
            flush()
            sec_no += 1
            sub_no = 0
            title = extract_braced(line, "section") or ""
            out.append(f'<h2 id="section-{sec_no}"><span class="secno">{sec_no}</span>{latex_inline(title, label_map, cite_map)}</h2>')
            i += 1
            continue
        if line.startswith(r"\section*{"):
            flush()
            unnumbered_no += 1
            title = extract_braced(line, "section*") or ""
            plain_title = tex_plain(title).strip().lower()
            ident = "license" if plain_title in {"license", "ライセンス"} else f"unnumbered-section-{unnumbered_no}"
            out.append(f'<h2 id="{html.escape(ident, quote=True)}">{latex_inline(title, label_map, cite_map)}</h2>')
            i += 1
            continue
        if line.startswith(r"\subsection{"):
            flush()
            sub_no += 1
            title = extract_braced(line, "subsection") or ""
            out.append(f'<h3 id="section-{sec_no}-{sub_no}"><span class="secno">{sec_no}.{sub_no}</span>{latex_inline(title, label_map, cite_map)}</h3>')
            i += 1
            continue
        if line.startswith(r"\subsection*{"):
            flush()
            title = extract_braced(line, "subsection*") or ""
            out.append(f"<h3>{latex_inline(title, label_map, cite_map)}</h3>")
            i += 1
            continue
        if line.startswith(r"\begin{enumerate}"):
            flush()
            block, i = read_environment(lines, i, "enumerate")
            out.append(convert_enumerate(block, label_map, cite_map))
            continue
        if line.startswith(r"\begin{table}"):
            flush()
            block, i = read_environment(lines, i, "table")
            out.append(convert_table(block, label_map, cite_map, table_label=table_label))
            continue
        if line.startswith(r"\begin{figure}"):
            flush()
            block, i = read_environment(lines, i, "figure")
            out.append(convert_figure(block, label_map, cite_map, figure_label=figure_label, image_prefix=image_prefix))
            continue
        if line.startswith(r"\begin{thebibliography}"):
            flush()
            block, i = read_environment(lines, i, "thebibliography")
            out.append(convert_bibliography(block, label_map, cite_map, title=references_title))
            continue
        if line.startswith(r"\["):
            flush()
            if line.endswith(r"\]") and len(line) > 4:
                equation = line[2:-2].strip()
                out.append(f'<div class="display-math">{math_html(equation)}</div>')
                i += 1
                continue
            equation_lines: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith(r"\]"):
                equation_lines.append(lines[i].strip())
                i += 1
            i += 1
            out.append(f'<div class="display-math">{math_html(" ".join(equation_lines))}</div>')
            continue
        if line.startswith(r"\centering") or line.startswith(r"\small") or line.startswith(r"\footnotesize"):
            i += 1
            continue
        paragraph.append(line)
        i += 1
    flush()
    return "\n".join(out)


def move_translation_note_after_abstract(article_body: str) -> str:
    note_match = re.search(r"\n?(<p><strong>Translation note\.</strong>.*?</p>)\n?", article_body, re.S)
    if not note_match:
        return article_body
    note = note_match.group(1)
    without_note = article_body[: note_match.start()] + article_body[note_match.end() :]
    abstract_match = re.search(r'(<section class="abstract" id="abstract">.*?</section>)', without_note, re.S)
    if not abstract_match:
        return without_note.strip() + "\n" + note
    return (
        without_note[: abstract_match.end()]
        + "\n"
        + note
        + without_note[abstract_match.end() :]
    )


def paper_ja_from_tex() -> str:
    tex = (DOCS / "paper" / PUBLIC_PAPER_TEX).read_text(encoding="utf-8")
    article_body = convert_latex_body(tex)
    body = f"""
<header>
  <div class="page paper-header">
    <h1>{TITLE_JA}</h1>
    <p class="subtitle">{SUBTITLE_JA}</p>
    <p class="meta">{AUTHOR_JA} / {DATE_JA}</p>
{nav('ja', 'paper')}
  </div>
</header>
<main class="paper page latex-paper">
  {article_body}
</main>
<footer><div class="page">HTML版は公開TeX原稿から生成したWeb版です。ページ固定の確認にはPDF版を使用してください。</div></footer>
"""
    return html_shell("ja", f"{TITLE_JA}: {SUBTITLE_JA}", body)


def paper_en_from_tex() -> str:
    tex = (DOCS / "paper" / PUBLIC_PAPER_EN_TEX).read_text(encoding="utf-8")
    article_body = convert_latex_body(
        tex,
        abstract_title="Abstract",
        figure_label="Figure",
        table_label="Table",
        references_title="References",
        image_prefix="../",
    )
    article_body = move_translation_note_after_abstract(article_body)
    body = f"""
<header>
  <div class="page paper-header">
    <h1>{TITLE_EN}</h1>
    <p class="subtitle">{SUBTITLE_EN}</p>
    <p class="meta">{AUTHOR_EN} / {DATE_EN}</p>
{nav('en', 'paper')}
  </div>
</header>
<main class="paper page latex-paper english-paper">
  {article_body}
</main>
<footer><div class="page">English HTML is generated from the English TeX, which is structurally aligned to the Japanese TeX. For citation and nuance, use the Japanese edition as the primary text.</div></footer>
"""
    return html_shell("en", f"{TITLE_EN}: {SUBTITLE_EN}", body)



def source_provenance_html() -> str:
    body = f"""
<header><div class="page paper-header"><h1>出典・検証記録</h1><p class="subtitle">Honen-Shinran Shared Core Map publication provenance</p>{nav('ja', 'source')}</div></header>
<main class="paper page">
  <section class="notice"><h2>公開境界</h2><p>このページは公開用の短い出典・検証サマリです。詳細な制作・検証記録はリポジトリ内の <code>memory.md</code> と <code>docs/source-provenance.md</code> を参照してください。</p></section>
  <h2>本文・派生データ</h2>
  <ul>
    <li>raw/processed本文、chunk preview、embedding cache、embedding vectorは公開HTMLに含めない。</li>
    <li>図表、SAT行範囲、集計値、検証メモ、公開可能な派生情報のみを掲載する。</li>
    <li>本文提供元の利用条件は各提供元に従う。</li>
  </ul>
  <h2>ライセンス</h2>
  <ul>
    <li>解析コード: MIT License。リポジトリ直下の <code>LICENSE-CODE</code> を参照。</li>
    <li>論文、図表、公開文書、制作プロセス文書、引用メタデータ、公開用派生データ: Creative Commons Attribution 4.0 International (CC BY 4.0)。リポジトリ直下の <code>LICENSE-CONTENT</code> を参照。</li>
    <li>SATなどから取得した元本文は本リポジトリでは再配布せず、本リポジトリのライセンス対象にも含めない。元本文の利用は各提供元の利用条件に従う。</li>
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
    <li>日本語HTML論文は、PDFと同じ公開TeX原稿 <code>docs/paper/{PUBLIC_PAPER_TEX}</code> から生成する。</li>
    <li>英語TeXは、日本語TeXの構造を正本として <code>scripts/build_english_tex_from_ja_tex.py</code> で生成する。</li>
    <li>英語PDFと英語HTML論文は、同じ公開英語TeX原稿 <code>docs/paper/{PUBLIC_PAPER_EN_TEX}</code> から生成する。</li>
    <li>PDFはPyMuPDFでPNGレンダリングして目視確認。</li>
    <li>先行 <code>Okyou</code> repository は読み取り専用で参照し、変更しない。</li>
  </ul>
  <h2>リリース後の訂正</h2>
  <p>公開リリース後は、本文・PDF・主要HTMLをその時点の固定版として扱う。誤記、補足、解釈の変更、図表差し替えが必要な場合は、公開版を黙って置き換えず、<a href="errata/">Errata</a>に記録する。</p>
  <h2>固定公開物</h2>
  <p>公開用PDFとTeXのSHA-256は <a href="checksums.txt">checksums.txt</a> に記録する。tag/release作成時には、このハッシュとrelease tag上のファイルが一致することを確認する。</p>
</main>
<footer><div class="page">Honen-Shinran Shared Core Map provenance summary.</div></footer>
"""
    return html_shell("ja", "Honen-Shinran Shared Core Map 出典・検証記録", body)


def errata_html() -> str:
    body = f"""
<header><div class="page paper-header"><h1>Errata</h1><p class="subtitle">Honen-Shinran Shared Core Map release errata</p>{nav('ja', 'errata')}</div></header>
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
        <tr><td>未登録</td><td>公開版</td><td>-</td><td>現時点でリリース後の記録はない。</td><td>-</td></tr>
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
    return html_shell("ja", "Honen-Shinran Shared Core Map Errata", body)


def errata_en_html() -> str:
    body = f"""
<header><div class="page paper-header"><h1>Errata</h1><p class="subtitle">Honen-Shinran Shared Core Map release errata</p>{nav('en', 'errata')}</div></header>
<main class="paper page">
  <section class="notice">
    <h2>Policy</h2>
    <p>After release, the public PDF and HTML are treated as fixed editions. Corrections, broken links, figure-label fixes, supplementary notes, and interpretive changes are recorded here and in <code>docs/ERRATA.md</code> rather than silently rewriting the released paper.</p>
  </section>
  <h2>Record</h2>
  <div class="table-wrap">
    <table>
      <thead><tr><th>Date</th><th>Target</th><th>Type</th><th>Note</th><th>Status</th></tr></thead>
      <tbody>
        <tr><td>Not registered</td><td>Public release</td><td>-</td><td>No post-release errata have been registered yet.</td><td>-</td></tr>
      </tbody>
    </table>
  </div>
  <h2>Types</h2>
  <ul>
    <li><strong>Correction:</strong> Typographical errors, numerical errors, link failures, or figure/table label fixes.</li>
    <li><strong>Supplement:</strong> Additional explanation that does not change the main conclusion.</li>
    <li><strong>Revision candidate:</strong> A methodological or interpretive change to be handled in a later version.</li>
  </ul>
</main>
<footer><div class="page">Released paper changes are tracked as errata.</div></footer>
"""
    return html_shell("en", "Honen-Shinran Shared Core Map Errata", body)


def errata_redirect_html() -> str:
    return """<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="refresh" content="0; url=errata/">
  <title>Honen-Shinran Shared Core Map Errata</title>
</head>
<body>
  <p><a href="errata/">Errata</a></p>
</body>
</html>
"""


def errata_md() -> str:
    return """# Errata

このファイルは、公開リリース後の訂正・補足・変更候補を記録する。

## 運用方針

- リリース後の公開版PDF/HTMLは固定版として扱う。
- 誤記、数値、リンク、図表ラベル、説明不足、解釈変更が見つかった場合は、公開済み本文を黙って差し替えず、このファイルと `docs/errata/` に記録する。
- 本文を更新する必要がある場合は、新しい版として明示し、旧版との差分と理由をErrataに残す。

## 記録形式

| 日付 | 対象 | 種別 | 内容 | 対応 |
| --- | --- | --- | --- | --- |
| 未登録 | 公開版 | - | 現時点でリリース後の記録はない。 | - |

## 種別

- 訂正: 誤記、数値、リンク、図表ラベルなどの明確な誤り。
- 補足: 本文の結論を変えない説明追加。
- 改訂候補: 解釈や方法上の変更が必要だが、固定版本文には直接反映しないもの。
"""


def license_html() -> str:
    body = f"""
<header><div class="page paper-header"><h1>ライセンス</h1><p class="subtitle">Honen-Shinran Shared Core Map license notice</p>{nav('ja', 'license')}</div></header>
<main class="paper page">
  <section class="notice">
    <h2>分割ライセンス</h2>
    <p>このリポジトリは、先行 <code>Okyou</code> と同じ方針で、コード、非コード研究成果、元本文を分けて扱います。</p>
  </section>
  <h2>Code</h2>
  <p>解析コードと公開ページ生成スクリプトは MIT License で公開します。詳細はリポジトリ直下の <code>LICENSE-CODE</code> を参照してください。</p>
  <h2>Research Outputs</h2>
  <p>論文、図表、公開文書、制作プロセス文書、引用メタデータ、公開用派生データは Creative Commons Attribution 4.0 International (CC BY 4.0) で公開します。</p>
  <p><a href="https://creativecommons.org/licenses/by/4.0/">https://creativecommons.org/licenses/by/4.0/</a></p>
  <h2>Source Texts</h2>
  <p>SAT、J-SOKEN、84000、その他の本文提供元から取得した raw/processed 本文、chunk preview、embedding cache、embedding vector は、この公開リポジトリでは再配布しません。これらの元本文は本リポジトリのライセンス対象外であり、各提供元の利用条件に従います。</p>
  <h2>English Notice</h2>
  <p>This repository uses a split license. Code is licensed under the MIT License. Non-code research outputs, including the paper, figures, documentation, process reports, citation metadata, and public derived data, are licensed under Creative Commons Attribution 4.0 International (CC BY 4.0). Source texts retrieved from SAT, J-SOKEN, 84000, or other text providers are not redistributed in this repository and are not covered by this repository's licenses.</p>
</main>
<footer><div class="page">License notice for Honen-Shinran Shared Core Map public materials.</div></footer>
"""
    return html_shell("ja", "Honen-Shinran Shared Core Map ライセンス", body)


def publication_md() -> str:
    return """# GitHub Pages 公開準備

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
"""


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"Wrote {path.relative_to(ROOT)}")


def main() -> None:
    write(DOCS / ".nojekyll", "")
    write(DOCS / "index.html", home_ja())
    write(DOCS / "en" / "index.html", home_en())
    write(DOCS / "paper" / "index.html", paper_ja_from_tex())
    write(DOCS / "paper" / "en" / "index.html", paper_en_from_tex())
    write(DOCS / "source-provenance.html", source_provenance_html())
    write(DOCS / "errata.html", errata_redirect_html())
    write(DOCS / "errata" / "index.html", errata_html())
    write(DOCS / "errata" / "en" / "index.html", errata_en_html())
    write(DOCS / "ERRATA.md", errata_md())
    write(DOCS / "license.html", license_html())
    write(DOCS / "PUBLICATION.md", publication_md())


if __name__ == "__main__":
    main()
