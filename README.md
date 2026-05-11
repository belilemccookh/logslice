# logslice

A lightweight log parser and filter utility that extracts structured data from unformatted log files.

---

## Installation

```bash
pip install logslice
```

Or install from source:

```bash
git clone https://github.com/yourname/logslice.git && cd logslice && pip install .
```

---

## Usage

```python
from logslice import LogParser

parser = LogParser("app.log")

# Filter entries by log level and extract structured fields
errors = parser.filter(level="ERROR")
for entry in errors:
    print(entry.timestamp, entry.message)
```

You can also use the CLI:

```bash
logslice --file app.log --level ERROR --output results.json
```

**Example output:**

```json
[
  { "timestamp": "2024-03-15T10:42:01", "level": "ERROR", "message": "Connection timeout" },
  { "timestamp": "2024-03-15T11:05:33", "level": "ERROR", "message": "Disk quota exceeded" }
]
```

---

## Features

- Parses unstructured and semi-structured log formats
- Filter by log level, date range, or keyword
- Exports results to JSON, CSV, or plain text
- Zero external dependencies

---

## License

This project is licensed under the [MIT License](LICENSE).