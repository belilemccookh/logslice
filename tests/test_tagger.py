"""Tests for logslice.tagger."""

import pytest
from logslice.tagger import (
    tag_entry,
    untag_entry,
    tag_entries,
    tag_by_predicate,
    filter_by_tag,
    get_all_tags,
)


def make_entry(level="INFO", message="msg", tags=None):
    e = {"timestamp": "2024-01-01T00:00:00", "level": level, "message": message}
    if tags is not None:
        e["tags"] = list(tags)
    return e


# tag_entry

def test_tag_entry_returns_dict():
    assert isinstance(tag_entry(make_entry(), "web"), dict)


def test_tag_entry_adds_tag():
    result = tag_entry(make_entry(), "web")
    assert "web" in result["tags"]


def test_tag_entry_does_not_mutate_original():
    entry = make_entry()
    tag_entry(entry, "web")
    assert "tags" not in entry


def test_tag_entry_no_duplicates():
    entry = make_entry(tags=["web"])
    result = tag_entry(entry, "web")
    assert result["tags"].count("web") == 1


def test_tag_entry_multiple_tags():
    result = tag_entry(make_entry(), "a", "b", "c")
    assert set(result["tags"]) == {"a", "b", "c"}


# untag_entry

def test_untag_entry_removes_tag():
    entry = make_entry(tags=["web", "api"])
    result = untag_entry(entry, "web")
    assert "web" not in result["tags"]
    assert "api" in result["tags"]


def test_untag_entry_missing_tag_is_noop():
    entry = make_entry(tags=["api"])
    result = untag_entry(entry, "missing")
    assert result["tags"] == ["api"]


def test_untag_entry_does_not_mutate_original():
    entry = make_entry(tags=["web"])
    untag_entry(entry, "web")
    assert "web" in entry["tags"]


# tag_entries

def test_tag_entries_returns_list():
    assert isinstance(tag_entries([make_entry()], "x"), list)


def test_tag_entries_applies_to_all():
    entries = [make_entry() for _ in range(4)]
    result = tag_entries(entries, "bulk")
    assert all("bulk" in e["tags"] for e in result)


# tag_by_predicate

def test_tag_by_predicate_tags_matching():
    entries = [make_entry(level="ERROR"), make_entry(level="INFO")]
    result = tag_by_predicate(entries, "error", lambda e: e["level"] == "ERROR")
    assert "error" in result[0]["tags"]
    assert "error" not in (result[1].get("tags") or [])


def test_tag_by_predicate_returns_all_entries():
    entries = [make_entry() for _ in range(5)]
    result = tag_by_predicate(entries, "x", lambda e: False)
    assert len(result) == 5


# filter_by_tag

def test_filter_by_tag_returns_matching():
    entries = [
        make_entry(tags=["web"]),
        make_entry(tags=["db"]),
        make_entry(tags=["web", "api"]),
    ]
    result = filter_by_tag(entries, "web")
    assert len(result) == 2


def test_filter_by_tag_no_match_returns_empty():
    entries = [make_entry(tags=["db"]), make_entry()]
    assert filter_by_tag(entries, "missing") == []


# get_all_tags

def test_get_all_tags_returns_sorted_unique():
    entries = [
        make_entry(tags=["b", "a"]),
        make_entry(tags=["c", "a"]),
    ]
    assert get_all_tags(entries) == ["a", "b", "c"]


def test_get_all_tags_empty_entries_returns_empty():
    assert get_all_tags([]) == []
