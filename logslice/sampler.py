"""Sampling utilities for logslice — reduce large log streams to representative subsets."""

import random
from typing import List, Dict, Any, Optional


def sample_entries(
    entries: List[Dict[str, Any]],
    n: int,
    seed: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Return up to *n* randomly sampled entries from *entries*.

    The original order of selected entries is preserved.

    Args:
        entries: List of parsed log entry dicts.
        n: Maximum number of entries to return.
        seed: Optional random seed for reproducibility.

    Returns:
        A list of sampled entries (len <= n).
    """
    if n <= 0:
        return []
    if n >= len(entries):
        return list(entries)
    rng = random.Random(seed)
    indices = sorted(rng.sample(range(len(entries)), n))
    return [entries[i] for i in indices]


def sample_every_nth(
    entries: List[Dict[str, Any]],
    n: int,
) -> List[Dict[str, Any]]:
    """Return every *n*-th entry from *entries* (systematic sampling).

    Args:
        entries: List of parsed log entry dicts.
        n: Step size; must be >= 1.

    Returns:
        Every n-th entry starting from index 0.

    Raises:
        ValueError: If *n* is less than 1.
    """
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    return entries[::n]


def sample_head(
    entries: List[Dict[str, Any]],
    n: int,
) -> List[Dict[str, Any]]:
    """Return the first *n* entries."""
    if n <= 0:
        return []
    return entries[:n]


def sample_tail(
    entries: List[Dict[str, Any]],
    n: int,
) -> List[Dict[str, Any]]:
    """Return the last *n* entries."""
    if n <= 0:
        return []
    return entries[-n:]
