"""Compare two sets of log entries and report differences."""

from typing import Any


def _entry_key(entry: dict, fields: list[str] | None = None) -> tuple:
    """Build a hashable key from selected fields of an entry."""
    if fields is None:
        fields = ["timestamp", "level", "message"]
    return tuple(entry.get(f) for f in fields)


def diff_entries(
    left: list[dict],
    right: list[dict],
    fields: list[str] | None = None,
) -> dict[str, list[dict]]:
    """Return entries only in left, only in right, and common to both."""
    left_keys = {_entry_key(e, fields): e for e in left}
    right_keys = {_entry_key(e, fields): e for e in right}

    only_left = [left_keys[k] for k in left_keys if k not in right_keys]
    only_right = [right_keys[k] for k in right_keys if k not in left_keys]
    common = [left_keys[k] for k in left_keys if k in right_keys]

    return {"only_left": only_left, "only_right": only_right, "common": common}


def entries_equal(
    left: list[dict],
    right: list[dict],
    fields: list[str] | None = None,
) -> bool:
    """Return True if both entry lists are equivalent by the given fields."""
    result = diff_entries(left, right, fields)
    return not result["only_left"] and not result["only_right"]


def compare_field_values(
    left: list[dict],
    right: list[dict],
    field: str,
) -> dict[str, Any]:
    """Compare the distribution of a single field across two entry sets."""
    def _count(entries: list[dict]) -> dict:
        counts: dict = {}
        for e in entries:
            val = e.get(field)
            if val is not None:
                counts[val] = counts.get(val, 0) + 1
        return counts

    left_counts = _count(left)
    right_counts = _count(right)
    all_keys = set(left_counts) | set(right_counts)

    delta = {
        k: right_counts.get(k, 0) - left_counts.get(k, 0) for k in all_keys
    }

    return {"left": left_counts, "right": right_counts, "delta": delta}


def added_entries(left: list[dict], right: list[dict], fields: list[str] | None = None) -> list[dict]:
    """Return entries present in right but not in left."""
    return diff_entries(left, right, fields)["only_right"]


def removed_entries(left: list[dict], right: list[dict], fields: list[str] | None = None) -> list[dict]:
    """Return entries present in left but not in right."""
    return diff_entries(left, right, fields)["only_left"]
