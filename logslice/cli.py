"""Command-line interface for logslice."""

import argparse
import json
import sys
from typing import List, Optional

from logslice.aggregator import summarize
from logslice.filter import filter_by_level, filter_by_pattern
from logslice.formatter import format_entries
from logslice.parser import parse_lines


def build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser."""
    p = argparse.ArgumentParser(
        prog="logslice",
        description="Parse, filter, and format log files.",
    )
    p.add_argument("file", nargs="?", help="Log file to process (default: stdin)")
    p.add_argument("-l", "--level", help="Filter by log level (e.g. ERROR, WARN)")
    p.add_argument("-p", "--pattern", help="Filter by regex pattern in message field")
    p.add_argument(
        "-f",
        "--format",
        choices=["text", "json", "csv"],
        default="text",
        help="Output format (default: text)",
    )
    p.add_argument(
        "--summarize",
        action="store_true",
        help="Print a summary report instead of log entries",
    )
    p.add_argument(
        "--group-by",
        default="level",
        dest="group_by",
        help="Field to group by when summarizing (default: level)",
    )
    return p


def run(argv: Optional[List[str]] = None) -> int:
    """Entry point for the CLI.

    Args:
        argv: Argument list (defaults to sys.argv).

    Returns:
        Exit code (0 for success, non-zero for error).
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.file:
            with open(args.file, "r", encoding="utf-8") as fh:
                raw_lines = fh.readlines()
        else:
            raw_lines = sys.stdin.readlines()
    except OSError as exc:
        print(f"logslice: error reading file: {exc}", file=sys.stderr)
        return 1

    entries = list(parse_lines(raw_lines))

    if args.level:
        entries = filter_by_level(entries, args.level)
    if args.pattern:
        entries = filter_by_pattern(entries, args.pattern)

    if args.summarize:
        report = summarize(entries, group_field=args.group_by)
        print(json.dumps(report, indent=2))
    else:
        for line in format_entries(entries, fmt=args.format):
            print(line)

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(run())
