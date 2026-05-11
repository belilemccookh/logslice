"""Core log line parser for logslice.

Parses unformatted log lines into structured dictionaries using
configurable regex patterns for common log formats.
"""

import re
from typing import Optional

# Common log format patterns
PATTERNS = {
    "common": re.compile(
        r'(?P<timestamp>\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)'
        r'\s+(?P<level>DEBUG|INFO|WARNING|WARN|ERROR|CRITICAL|FATAL)'
        r'\s+(?P<message>.+)',
        re.IGNORECASE,
    ),
    "bracketed": re.compile(
        r'\[(?P<timestamp>[^\]]+)\]'
        r'\s+\[?(?P<level>DEBUG|INFO|WARNING|WARN|ERROR|CRITICAL|FATAL)\]?'
        r'\s+(?P<message>.+)',
        re.IGNORECASE,
    ),
    "syslog": re.compile(
        r'(?P<timestamp>\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})'
        r'\s+(?P<host>\S+)'
        r'\s+(?P<process>\S+):'
        r'\s+(?P<message>.+)',
    ),
}


def parse_line(line: str, pattern_name: str = "common") -> Optional[dict]:
    """Parse a single log line into a structured dictionary.

    Args:
        line: Raw log line string.
        pattern_name: Name of the pattern to use (default: 'common').

    Returns:
        A dict with parsed fields, or None if the line does not match.
    """
    line = line.rstrip("\n\r")
    pattern = PATTERNS.get(pattern_name)
    if pattern is None:
        raise ValueError(f"Unknown pattern: '{pattern_name}'. Available: {list(PATTERNS)}")

    match = pattern.match(line)
    if not match:
        return None

    result = match.groupdict()
    # Normalise level to uppercase
    if "level" in result and result["level"]:
        result["level"] = result["level"].upper()
        if result["level"] == "WARN":
            result["level"] = "WARNING"
        elif result["level"] == "FATAL":
            result["level"] = "CRITICAL"
    return result


def parse_lines(lines, pattern_name: str = "common") -> list[dict]:
    """Parse an iterable of log lines, skipping non-matching lines.

    Args:
        lines: Iterable of raw log line strings.
        pattern_name: Name of the pattern to use.

    Returns:
        List of parsed log entry dicts.
    """
    results = []
    for line in lines:
        entry = parse_line(line, pattern_name=pattern_name)
        if entry is not None:
            results.append(entry)
    return results
