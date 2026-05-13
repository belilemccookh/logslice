"""Runner module — high-level entry point for processing log files via Pipeline."""

from typing import Any, Dict, List, Optional

from logslice.pipeline import Pipeline
from logslice.writer import write_entries, write_to_stdout


def load_lines_from_file(path: str) -> List[str]:
    """Read lines from a log file, stripping trailing newlines."""
    with open(path, "r", encoding="utf-8") as fh:
        return [line.rstrip("\n") for line in fh.readlines()]


def run_pipeline(
    source: str,
    level: Optional[str] = None,
    pattern: Optional[str] = None,
    time_start: Optional[str] = None,
    time_end: Optional[str] = None,
    field_filter: Optional[Dict[str, str]] = None,
    output_fmt: str = "text",
    output_path: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Load a log file, apply filters, and write output.

    Returns the list of processed entries.
    """
    lines = load_lines_from_file(source)
    pipeline = Pipeline.from_lines(lines)

    if level:
        pipeline = pipeline.filter_level(level)

    if pattern:
        pipeline = pipeline.filter_pattern(pattern)

    if time_start or time_end:
        pipeline = pipeline.filter_time(start=time_start, end=time_end)

    if field_filter:
        for field, value in field_filter.items():
            pipeline = pipeline.filter_field(field, value)

    entries = pipeline.entries()

    if output_path:
        write_entries(entries, output_path, fmt=output_fmt)
    else:
        content = pipeline.export(fmt=output_fmt)
        write_to_stdout(content)

    return entries
