"""Reporter module: generates summary reports from log entries."""

from typing import Any, Dict, List, Optional

from logslice.counter import (
    count_entries,
    count_by_level,
    count_errors,
    count_warnings,
    frequency_table,
)


def build_report(
    entries: List[Dict[str, Any]],
    top_n: int = 5,
    extra_fields: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Build a summary report dict from a list of log entries.

    Args:
        entries: Parsed log entries.
        top_n: How many top values to include in frequency tables.
        extra_fields: Additional fields to include frequency tables for.

    Returns:
        A dict containing report statistics.
    """
    report: Dict[str, Any] = {
        "total": count_entries(entries),
        "errors": count_errors(entries),
        "warnings": count_warnings(entries),
        "by_level": count_by_level(entries),
        "top_messages": frequency_table(entries, "message", top_n=top_n),
    }

    if extra_fields:
        report["extra"] = {
            field: frequency_table(entries, field, top_n=top_n)
            for field in extra_fields
        }

    return report


def format_report(report: Dict[str, Any]) -> str:
    """Format a report dict as a human-readable string.

    Args:
        report: Report dict as returned by build_report.

    Returns:
        A formatted multi-line string.
    """
    lines = [
        "=== Log Report ===",
        f"Total entries : {report.get('total', 0)}",
        f"Errors        : {report.get('errors', 0)}",
        f"Warnings      : {report.get('warnings', 0)}",
        "",
        "Entries by level:",
    ]

    for level, count in sorted(report.get("by_level", {}).items()):
        lines.append(f"  {level:<12} {count}")

    top_msgs = report.get("top_messages", [])
    if top_msgs:
        lines.append("")
        lines.append("Top messages:")
        for item in top_msgs:
            lines.append(f"  ({item['count']:>4}x) {item['value']}")

    extra = report.get("extra", {})
    for field, table in extra.items():
        lines.append("")
        lines.append(f"Top '{field}' values:")
        for item in table:
            lines.append(f"  ({item['count']:>4}x) {item['value']}")

    return "\n".join(lines)
