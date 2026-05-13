"""Terminal color highlighting for log entries based on level or pattern."""

import re

ANSI_CODES = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "red": "\033[31m",
    "yellow": "\033[33m",
    "green": "\033[32m",
    "cyan": "\033[36m",
    "magenta": "\033[35m",
    "white": "\033[37m",
}

LEVEL_COLORS = {
    "error": "red",
    "critical": "red",
    "fatal": "red",
    "warning": "yellow",
    "warn": "yellow",
    "info": "green",
    "debug": "cyan",
    "trace": "magenta",
}


def colorize(text: str, color: str, bold: bool = False) -> str:
    """Wrap text in ANSI color codes."""
    code = ANSI_CODES.get(color, "")
    bold_code = ANSI_CODES["bold"] if bold else ""
    reset = ANSI_CODES["reset"]
    return f"{bold_code}{code}{text}{reset}"


def highlight_by_level(text: str, level: str) -> str:
    """Apply color to a line of text based on log level."""
    if not level:
        return text
    color = LEVEL_COLORS.get(level.lower())
    if not color:
        return text
    is_bold = level.lower() in ("error", "critical", "fatal")
    return colorize(text, color, bold=is_bold)


def highlight_pattern(text: str, pattern: str, color: str = "yellow") -> str:
    """Highlight all occurrences of a regex pattern within text."""
    if not pattern:
        return text
    try:
        regex = re.compile(pattern)
    except re.error:
        return text

    def replace_match(m: re.Match) -> str:
        return colorize(m.group(0), color, bold=True)

    return regex.sub(replace_match, text)


def highlight_entry(entry: dict, pattern: str = None, use_level_color: bool = True) -> str:
    """Format and highlight a single log entry dict as a colored string."""
    parts = []
    if entry.get("timestamp"):
        parts.append(colorize(entry["timestamp"], "white"))
    if entry.get("level"):
        level = entry["level"]
        level_color = LEVEL_COLORS.get(level.lower(), "white")
        parts.append(colorize(f"[{level.upper()}]", level_color, bold=True))
    if entry.get("message"):
        parts.append(entry["message"])

    line = "  ".join(parts)

    if use_level_color and entry.get("level"):
        line = highlight_by_level(line, entry["level"])

    if pattern:
        line = highlight_pattern(line, pattern)

    return line
