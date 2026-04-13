"""Tests for HTML availability/failure detection in fetch logic."""

from __future__ import annotations

from arxiv2md.fetch import _is_ar5iv_fatal_page, _is_arxiv_no_html_page


def test_detects_arxiv_no_html_page() -> None:
    html = """
    <html><body>
      <h1>No HTML for '2504.08066'</h1>
      <p>HTML is not available for the source.</p>
    </body></html>
    """
    assert _is_arxiv_no_html_page(html) is True


def test_detects_ar5iv_fatal_page() -> None:
    html = """
    <html><head><title>No content available</title></head>
    <body>
      <span class="ltx_ERROR">
        Conversion to HTML had a Fatal error and exited abruptly.
      </span>
    </body></html>
    """
    assert _is_ar5iv_fatal_page(html) is True


def test_does_not_flag_normal_html() -> None:
    html = """
    <html><head><title>Paper Title</title></head>
    <body><article class="ltx_document"><h2>Intro</h2></article></body></html>
    """
    assert _is_arxiv_no_html_page(html) is False
    assert _is_ar5iv_fatal_page(html) is False
