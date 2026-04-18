"""Tests for fetch-layer HTML payload validation."""

from __future__ import annotations

import pytest

from arxiv2md.fetch import _ensure_valid_html_payload, _looks_like_failed_ar5iv_conversion


def test_detects_ar5iv_fatal_conversion_page() -> None:
    html = """
    <html>
      <head><title>No content available</title></head>
      <body>
        <span class="ltx_ERROR">Conversion to HTML had a Fatal error and exited abruptly.</span>
        <a class="ar5iv-severity-fatal">Conversion report</a>
      </body>
    </html>
    """

    assert _looks_like_failed_ar5iv_conversion(html) is True


def test_accepts_normal_ar5iv_html_payload() -> None:
    html = """
    <html>
      <head><title>Normal Paper Title</title></head>
      <body>
        <article class="ltx_document">
          <section><h2>Introduction</h2><p>Text.</p></section>
        </article>
      </body>
    </html>
    """

    _ensure_valid_html_payload("https://ar5iv.labs.arxiv.org/html/2501.11120", html)


def test_rejects_failed_ar5iv_html_payload() -> None:
    html = """
    <html>
      <head><title>No content available</title></head>
      <body><span class="ltx_ERROR">Conversion to HTML had a Fatal error.</span></body>
    </html>
    """

    with pytest.raises(RuntimeError, match="ar5iv conversion failed"):
        _ensure_valid_html_payload("https://ar5iv.labs.arxiv.org/html/2504.08066", html)


def test_non_ar5iv_urls_skip_payload_failure_check() -> None:
    html = """
    <html>
      <head><title>No content available</title></head>
      <body><span class="ltx_ERROR">Conversion to HTML had a Fatal error.</span></body>
    </html>
    """

    _ensure_valid_html_payload("https://arxiv.org/html/2504.08066", html)
