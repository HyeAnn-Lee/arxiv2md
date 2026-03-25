"""Tests for arXiv HTML parsing."""

from __future__ import annotations

from arxiv2md.html_parser import parse_arxiv_html


def test_extracts_metadata_and_sections() -> None:
    html = """
    <html>
      <body>
        <article class="ltx_document">
          <h1 class="ltx_title ltx_title_document">Sample Title</h1>
          <div class="ltx_authors">
            <span class="ltx_text ltx_font_bold">Alice<sup>1</sup></span>
            <span class="ltx_text ltx_font_bold">Bob<sup>2</sup></span>
          </div>
          <div class="ltx_abstract">
            <p>Abstract text.</p>
          </div>
          <section class="ltx_section" id="S1">
            <h2 class="ltx_title ltx_title_section">1 Intro</h2>
            <div class="ltx_para"><p>Intro text.</p></div>
          </section>
        </article>
      </body>
    </html>
    """

    parsed = parse_arxiv_html(html)

    assert parsed.title == "Sample Title"
    assert parsed.authors == ["Alice", "Bob"]
    assert parsed.abstract == "Abstract text."
    assert parsed.sections
    assert parsed.sections[0].title == "1 Intro"
    assert parsed.sections[0].html and "Intro text." in parsed.sections[0].html


def test_theorem_headings_excluded_from_section_tree() -> None:
    """Theorem/Lemma/Definition environment headings (ltx_runninghead) must not
    appear as sections in the section tree – they are not document sections."""
    html = """
    <html><body>
    <article class="ltx_document">
      <h1 class="ltx_title ltx_title_document">Test Paper</h1>
      <section id="S1" class="ltx_section">
        <h2 class="ltx_title ltx_title_section">1 Introduction</h2>
        <div class="ltx_para"><p class="ltx_p">Intro text.</p></div>
        <div class="ltx_theorem ltx_theorem_definition" id="S1.Def1">
          <h6 class="ltx_title ltx_runninghead">Definition 1 (Attention).</h6>
          <div class="ltx_para"><p class="ltx_p">Definition content.</p></div>
        </div>
        <div class="ltx_para"><p class="ltx_p">More intro text.</p></div>
      </section>
      <section id="S2" class="ltx_section">
        <h2 class="ltx_title ltx_title_section">2 Methods</h2>
        <div class="ltx_para"><p class="ltx_p">Methods text.</p></div>
        <div class="ltx_theorem ltx_theorem_theorem" id="S2.Thm1">
          <h6 class="ltx_title ltx_runninghead">Theorem 1.</h6>
          <div class="ltx_para"><p class="ltx_p">Theorem statement.</p></div>
        </div>
        <div class="ltx_theorem ltx_theorem_lemma" id="S2.Lem1">
          <h6 class="ltx_title ltx_runninghead">Lemma 1.</h6>
          <div class="ltx_para"><p class="ltx_p">Lemma statement.</p></div>
        </div>
      </section>
    </article>
    </body></html>
    """

    parsed = parse_arxiv_html(html)
    section_titles = [s.title for s in parsed.sections]

    # Only real section headings should appear
    assert "1 Introduction" in section_titles
    assert "2 Methods" in section_titles

    # Theorem / definition / lemma labels must NOT appear as sections
    all_titles = section_titles + [c.title for s in parsed.sections for c in s.children]
    assert "Definition 1 (Attention)." not in all_titles
    assert "Theorem 1." not in all_titles
    assert "Lemma 1." not in all_titles

    # Sections should have correct structure (no spurious children)
    assert len(parsed.sections) == 2
    assert len(parsed.sections[0].children) == 0
    assert len(parsed.sections[1].children) == 0
