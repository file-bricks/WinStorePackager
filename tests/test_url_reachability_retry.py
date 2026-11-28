"""Regressionstests: transiente HTTP-Fehler dürfen den URL-Check nicht rot färben."""

from __future__ import annotations

import io
import json
import urllib.error
from pathlib import Path
from unittest import mock

import pytest

from scripts import check_store_readiness as csr

URL = "https://example.invalid/privacy"


class _Resp:
    def __init__(self, status: int):
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _http_error(code: int) -> urllib.error.HTTPError:
    return urllib.error.HTTPError(URL, code, "err", {}, io.BytesIO())


@pytest.fixture
def project(tmp_path: Path) -> Path:
    (tmp_path / "store_package.json").write_text(json.dumps({"privacy_url": URL}), encoding="utf-8")
    return tmp_path


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    monkeypatch.setattr(csr.time, "sleep", lambda _s: None)


def test_transient_503_is_retried_and_then_passes(project: Path):
    with mock.patch("urllib.request.urlopen", side_effect=[_http_error(503), _Resp(200)]) as m:
        assert csr.check_url_reachability(project) == []
    assert m.call_count == 2


def test_persistent_503_is_tolerated_like_offline(project: Path):
    with mock.patch("urllib.request.urlopen", side_effect=_http_error(503)) as m:
        assert csr.check_url_reachability(project) == []
    assert m.call_count == csr._URL_CHECK_ATTEMPTS


def test_404_is_still_reported_without_retry(project: Path):
    with mock.patch("urllib.request.urlopen", side_effect=_http_error(404)) as m:
        errors = csr.check_url_reachability(project)
    assert m.call_count == 1
    assert len(errors) == 1 and "HTTP 404" in errors[0]
