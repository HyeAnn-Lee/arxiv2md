"""Tests for fetch-layer HTML payload validation."""

from __future__ import annotations

import pytest
import httpx

from arxiv2md import fetch as fetch_module
from arxiv2md.fetch import _ensure_valid_html_payload, _fetch_with_retries, _looks_like_failed_ar5iv_conversion


def _patch_fetch_client(monkeypatch: pytest.MonkeyPatch, html: str) -> None:
    class FakeAsyncClient:
        def __init__(self, **_: object) -> None:
            pass

        async def __aenter__(self) -> FakeAsyncClient:
            return self

        async def __aexit__(self, exc_type: object, exc: object, tb: object) -> bool:
            return False

        async def get(self, url: str) -> httpx.Response:
            request = httpx.Request("GET", url)
            return httpx.Response(
                200,
                headers={"content-type": "text/html; charset=utf-8"},
                text=html,
                request=request,
            )

    monkeypatch.setattr(fetch_module, "ARXIV2MD_FETCH_MAX_RETRIES", 0)
    monkeypatch.setattr(fetch_module.httpx, "AsyncClient", FakeAsyncClient)


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


@pytest.mark.asyncio
async def test_fetch_with_retries_rejects_failed_ar5iv_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    html = """
    <html>
      <head><title>No content available</title></head>
      <body><span class="ltx_ERROR">Conversion to HTML had a Fatal error.</span></body>
    </html>
    """

    _patch_fetch_client(monkeypatch, html)

    with pytest.raises(RuntimeError, match="ar5iv conversion failed"):
        await _fetch_with_retries("https://ar5iv.labs.arxiv.org/html/2504.08066")


@pytest.mark.asyncio
async def test_fetch_with_retries_returns_normal_ar5iv_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    html = """
    <html>
      <head><title>Normal Paper Title</title></head>
      <body><article class="ltx_document"><p>Text.</p></article></body>
    </html>
    """

    _patch_fetch_client(monkeypatch, html)

    result = await _fetch_with_retries("https://ar5iv.labs.arxiv.org/html/2501.11120")
    assert result == html
