"""Write exported log data to files or stdout."""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

from logslice.exporter import export_entries


def write_to_file(
    entries: List[Dict[str, Any]],
    path: str,
    fmt: Optional[str] = None,
    **kwargs: Any,
) -> int:
    """Export entries and write them to a file.

    The format is inferred from the file extension when *fmt* is not given:
    - ``.json`` → json
    - ``.csv``  → csv
    - everything else → text

    Args:
        entries: Parsed log entry dicts.
        path: Destination file path.
        fmt: Explicit format override ('text', 'json', 'csv').
        **kwargs: Extra arguments forwarded to :func:`export_entries`.

    Returns:
        Number of bytes written.
    """
    if fmt is None:
        suffix = Path(path).suffix.lower()
        fmt = {"json": "json", ".json": "json", ".csv": "csv"}.get(suffix, "text")

    content = export_entries(entries, fmt=fmt, **kwargs)
    encoded = content.encode("utf-8")
    Path(path).write_bytes(encoded)
    return len(encoded)


def write_to_stdout(
    entries: List[Dict[str, Any]],
    fmt: str = "text",
    **kwargs: Any,
) -> None:
    """Export entries and print them to stdout.

    Args:
        entries: Parsed log entry dicts.
        fmt: Output format ('text', 'json', 'csv').
        **kwargs: Extra arguments forwarded to :func:`export_entries`.
    """
    content = export_entries(entries, fmt=fmt, **kwargs)
    sys.stdout.write(content)
    if content and not content.endswith("\n"):
        sys.stdout.write("\n")


def write_entries(
    entries: List[Dict[str, Any]],
    destination: Optional[str] = None,
    fmt: str = "text",
    **kwargs: Any,
) -> None:
    """Unified entry point: write to a file when *destination* is given,
    otherwise write to stdout.

    Args:
        entries: Parsed log entry dicts.
        destination: Optional file path. ``None`` means stdout.
        fmt: Output format ('text', 'json', 'csv').
        **kwargs: Extra arguments forwarded to :func:`export_entries`.
    """
    if destination:
        write_to_file(entries, destination, fmt=fmt, **kwargs)
    else:
        write_to_stdout(entries, fmt=fmt, **kwargs)
