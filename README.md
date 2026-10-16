# MX record inventory

Read domains from an Excel workbook, query their DNS MX records, and export mail-exchanger hosts in priority order. Lower MX preference values are tried first; equal values do not identify a unique primary server.

## Setup

Requires Python 3.11 or later and access to your configured DNS resolver.

```bash
git clone https://github.com/Hellfire4959/MX-record-python.git
cd MX-record-python
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Usage

Create an `.xlsx` workbook with a **Domain** column in its first worksheet:

| Domain |
| --- |
| example.org |
| example.net |

```bash
python scripts/mx_lookup.py domains.xlsx output/mx-results.xlsx
```

| Output column | Meaning |
| --- | --- |
| `Domain` | Input domain |
| `MX_Found` | `Yes`, `No`, `Null MX`, `Error`, or `Blank` |
| `MX_Records` | Hostnames ordered by MX preference; `0 .` identifies Null MX |
| `Preferences` | Corresponding preference values |
| `Primary_Host` | First host in the sorted results, or `N/A` |
| `Error` | DNS or domain-encoding error type |

A Null MX record explicitly announces that the domain does not accept email. No MX answer is a different result; this utility does not test SMTP delivery or address-record fallback. DNS failures are kept separate from missing answers. Internationalized domain names are converted to IDNA for lookup; the original input stays in the report. The CLI bounds each lookup to five seconds.

The output directory is created if necessary. An existing output workbook is replaced; input and output must be different files.

## Layout and development

- [scripts/mx_lookup.py](scripts/mx_lookup.py) — CLI and lookup functions; replaces the original extensionless `Python-script`.
- [requirements.txt](requirements.txt) — pandas, openpyxl and dnspython.
- [tests/](tests/) — synthetic DNS responses, errors, Null MX and workbook validation.

```bash
python -m unittest discover -s tests -v
```

Tests use mocked DNS responses. Include a sample response and expected row when changing result handling.
