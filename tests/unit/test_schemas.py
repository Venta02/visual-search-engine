"""Unit tests for Pydantic schemas."""

import pytest
from pydantic import ValidationError

from src.models import SearchResult, TextSearchRequest


def test_text_search_request_accepts_valid_input():
    req = TextSearchRequest(query="cat", limit=5)
    assert req.query == "cat"
    assert req.limit == 5
    assert req.score_threshold is None


def test_text_search_request_rejects_empty_query():
    with pytest.raises(ValidationError):
        TextSearchRequest(query="", limit=5)


def test_text_search_request_caps_limit():
    with pytest.raises(ValidationError):
        TextSearchRequest(query="cat", limit=1000)


def test_search_result_score_must_be_in_range():
    with pytest.raises(ValidationError):
        SearchResult(id=1, score=1.5)
    with pytest.raises(ValidationError):
        SearchResult(id=1, score=-0.1)
