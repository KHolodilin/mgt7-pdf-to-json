# Technical Specification (TS) — **mgt7-pdf-to-json**
Document version: **1.0**
Status: **Canonical final version**
Document language: **English**
Repository: **mgt7-pdf-to-json**

---

## 1. Introduction

### 1.1. Document purpose
This technical specification defines requirements for the Python project **mgt7-pdf-to-json**, which converts India MCA annual return PDF forms **MGT-7** and **MGT-7A** into structured **JSON**.

The document is intended for:
- developers and project architect;
- QA engineers;
- product owner/customer;
- DevOps/CI owner of the repository.

---

## 2. Project goals

### 2.1. Primary goal
Build a CLI tool and a Python library that accept an input PDF file (forms **MGT-7 / MGT-7A**) and produce a structured JSON output according to the agreed schema.

### 2.2. Secondary goals
- support multiple output JSON formats via **mappers** (remapping);
- enable reproducible debugging via **debug artifacts**;
- provide production-grade logging: **structured logging + file output + INFO/DEBUG levels**;
- ensure testability: **unit coverage ≥ 90%** and integration tests.

---

## 3. Scope and constraints

### 3.1. Supported forms
The project must support:
- **MGT-7** — Annual Return (other than OPCs and Small Companies)
- **MGT-7A** — Abridged Annual Return for OPCs and Small Companies

### 3.2. Supported PDF types
- Primary target: **text-based PDFs** (extractable text).
- Scanned/image-only PDFs are **not required** in MVP, but the system must:
  - fail gracefully with a clear error/warning;
  - log that text extraction failed and OCR is required (in strict mode it must fail).

### 3.3. Runtime environment
- Python: **3.9+**
- OS: Windows / Linux (CLI)
- Execution: local console

---

## 4. Terms and definitions

- **Pipeline** — the orchestrator class for the full PDF → JSON process.
- **Extractor** — component responsible for extracting text/tables from PDF.
- **Normalizer** — component responsible for cleaning/normalizing extracted data.
- **Parser** — component responsible for building a structured representation of the document.
- **Mapper** — component that converts ParsedDocument into a specific output JSON schema.
- **Artifacts** — intermediate debug files (raw/normalized/parsed/output).
- **request_id** — a unique run identifier (UUID4) used to correlate logs, artifacts, and output JSON.

---

## 5. System workflow

### 5.1. Input
- PDF file path on disk.

### 5.2. Output
- JSON output file (CLI) or JSON object (library mode).

### 5.3. Processing pipeline
1) Extract: PDF → RawDocument
2) Normalize: RawDocument → NormalizedDocument
3) Parse: NormalizedDocument → ParsedDocument
4) Map: ParsedDocument → Output JSON (schema)
5) Validate: Output JSON → warnings/errors
6) Write: save JSON to file (CLI)

---

## 6. CLI requirements

### 6.1. Command name
The CLI command must be:

```bash
mgt7pdf2json
```

### 6.2. Usage
Minimal:

```bash
mgt7pdf2json <input.pdf>
```

Extended:

```bash
mgt7pdf2json <input.pdf> -o <output.json> --mapper default --config <config.yml>
```

### 6.3. CLI arguments

| Argument | Type | Required | Description |
|---|---:|:---:|---|
| `input` | str | Yes | Input PDF path |
| `-o, --output` | str | No | Output JSON path. If not set — `input.json` |
| `--outdir` | str | No | Output directory (alternative to `--output`) |
| `--mapper` | str | No | Mapper selection: `default`, `minimal`, `db` (default: `default`) |
| `--config` | str | No | YAML config path |
| `--log-level` | str | No | Overrides `logging.level` |
| `--log-format` | str | No | Overrides `logging.format` (`console`/`json`) |
| `--log-dir` | str | No | Overrides `logging.file` |
| `--debug-artifacts` | flag | No | Enables artifacts saving (`artifacts.enabled=true`) |
| `--strict` | flag | No | Enables strict validation |
| `--fail-on-warnings` | flag | No | If warnings exist — exit with error code |

### 6.4. Configuration precedence
**CLI args > YAML config > defaults**

---

## 7. Configuration (YAML)

### 7.1. Requirements
- Config file path is provided via `--config`.
- If `--config` is not provided:
  - use `./config.yml` if present;
  - otherwise use defaults.

### 7.2. Mandatory config schema

```yaml
# Logging settings
logging:
  level: INFO                      # DEBUG, INFO, WARNING, ERROR, CRITICAL
  format: console                  # "console" (readable) or "json" (structured)
  format_file: json                # Format for file logs (default: "json")
  file: logs                       # Directory for log files
  date_format: "%d-%m-%Y"          # Used as log file name: <DATE>.log

# Artifacts (debug intermediate files)
artifacts:
  enabled: false
  dir: artifacts                   # artifacts directory inside logging.file
  save_raw: true
  save_normalized: true
  save_parsed: true
  save_output: false
  keep_days: 7                     # retention policy in days

# Parsing/mapping
pipeline:
  mapper: default                  # default|minimal|db

validation:
  strict: false
  required_fields:
    - meta.form_type
    - meta.financial_year.from
    - meta.financial_year.to
    - company.cin
    - company.name
```

---

## 8. Logging

### 8.1. Log levels
- DEBUG
- INFO
- WARNING
- ERROR
- CRITICAL

### 8.2. Structured logging
Must support:
- JSON structured logs
- human-readable console logs
- mandatory file logging

### 8.3. Log file naming
Logs are stored in `logging.file`.

Log file name must be based on date only:

```
<DATE>.log
```

Where `<DATE>` is computed using:

- `datetime.now().strftime(logging.date_format)`

Example:
```
logs/19-01-2026.log
```

### 8.4. request_id (mandatory)
A new `request_id` (UUID4) must be generated for every Pipeline run.

Requirements:
- `request_id` must be included in every log record (structured field).
- `request_id` must correlate:
  - logs,
  - artifacts,
  - output JSON.

### 8.5. Required log fields (minimum)
Each event must include:
- `timestamp`
- `level`
- `event`
- `request_id`
- `pdf_path`
- `step` (extract/normalize/parse/map/validate/write)
- `duration_ms`
- `artifact_path` (if any)
- `exception` (on error)

---

## 9. Artifacts (intermediate debug files)

### 9.1. Definition
Artifacts are intermediate files saved for debugging and parsing quality diagnostics.

### 9.2. Storage location
Artifacts must be stored under the log directory:

```
<logging.file>/<artifacts.dir>/
```

Default:
```
logs/artifacts/
```

### 9.3. Artifact naming
Artifacts must be named using `request_id`:

- `<request_id>.raw.json`
- `<request_id>.normalized.json`
- `<request_id>.parsed.json`
- `<request_id>.output.json` (if enabled)

### 9.4. Retention policy (mandatory)
A retention policy must be implemented:
- `artifacts.keep_days` defines how many days to keep artifacts
- cleanup must remove artifacts older than `keep_days`
- cleanup must be logged (`event=artifacts_cleanup`)

---

## 10. Output JSON format

### 10.1. General requirements
- Valid JSON output
- Type casting:
  - numbers → int/float
  - Yes/No → bool
  - dates → `DD/MM/YYYY` in MVP (ISO allowed in db mapper)

### 10.2. Mandatory meta fields
`meta` must include:
- `request_id`
- `schema_version`
- `form_type`
- `financial_year.from`
- `financial_year.to`
- `source.input_file`

Example:

```json
{
  "meta": {
    "request_id": "6a1d1c35-7f88-4e12-9e9f-8d3d4d1b6f5a",
    "schema_version": "1.0",
    "form_type": "MGT-7",
    "financial_year": {
      "from": "01/04/2024",
      "to": "31/03/2025"
    },
    "source": {
      "input_file": "input.pdf"
    }
  },
  "data": {},
  "warnings": [],
  "errors": []
}
```

---

## 10.3. Output JSON examples (mandatory)

### 10.3.1. Example: `default` (full JSON)

```json
{
  "meta": {
    "request_id": "6a1d1c35-7f88-4e12-9e9f-8d3d4d1b6f5a",
    "schema_version": "1.0",
    "form_type": "MGT-7",
    "financial_year": {
      "from": "01/04/2024",
      "to": "31/03/2025"
    },
    "source": {
      "input_file": "U17120DL2013PTC262515_mgt7.pdf"
    }
  },
  "data": {
    "company": {
      "cin": "U17120DL2013PTC262515",
      "name": "TEGAN TEXOFAB PRIVATE LIMITED"
    },
    "turnover_and_net_worth": {
      "turnover_inr": 891114630,
      "net_worth_inr": 266771238
    },
    "share_capital": {
      "equity": {
        "authorized": { "shares": 0, "amount_inr": 0 },
        "paid_up": { "shares": 0, "amount_inr": 0 }
      }
    },
    "meetings": {
      "board_meetings": [
        { "date": "01/04/2024", "directors_total": 2, "directors_attended": 2 }
      ]
    }
  },
  "warnings": [],
  "errors": []
}
```

### 10.3.2. Example: `minimal` (minimal JSON)

```json
{
  "meta": {
    "request_id": "b1c0b5d2-0a7a-4c62-a5df-25fbb8d3d9c2",
    "schema_version": "1.0",
    "form_type": "MGT-7A",
    "financial_year": {
      "from": "01/04/2024",
      "to": "31/03/2025"
    },
    "source": {
      "input_file": "KA903UC002704392_mgt7a.pdf"
    }
  },
  "data": {
    "company": {
      "cin": "U80904KA2022PTC168903",
      "name": "NEOS KOSMOS TECHNOLOGIES PRIVATE LIMITED"
    },
    "turnover_and_net_worth": {
      "turnover_inr": 99189684.57,
      "net_worth_inr": 28069323.1
    }
  },
  "warnings": [
    {
      "code": "PARTIAL_PARSE",
      "message": "Some optional sections were not parsed",
      "details": { "sections": ["XIV", "XV"] }
    }
  ],
  "errors": []
}
```

### 10.3.3. Example: `db` (DB/ETL-friendly JSON)

```json
{
  "meta": {
    "request_id": "c2f1b3a0-1e34-4e1c-8a8b-9cfa2a7a2b11",
    "schema_version": "1.0",
    "form_type": "MGT-7",
    "source": {
      "input_file": "U17120DL2013PTC262515_mgt7.pdf",
      "generated_at": "2026-01-19T13:20:00Z"
    }
  },
  "data": {
    "company": {
      "cin": "U17120DL2013PTC262515",
      "name": "TEGAN TEXOFAB PRIVATE LIMITED"
    },
    "facts": {
      "turnover_inr": 891114630,
      "net_worth_inr": 266771238
    },
    "tables": {
      "board_meetings": [
        {
          "request_id": "c2f1b3a0-1e34-4e1c-8a8b-9cfa2a7a2b11",
          "meeting_date": "01/04/2024",
          "directors_total": 2,
          "directors_attended": 2
        }
      ]
    }
  },
  "warnings": [],
  "errors": []
}
```

---

## 11. Exit codes and stable errors (mandatory)

### 11.1. Requirements
CLI must exit with predictable exit codes for automation use cases.

### 11.2. Exit codes table

| Code | Name | When used |
|---:|---|---|
| 0 | SUCCESS | Successful processing, JSON saved |
| 1 | PROCESSING_ERROR | Extraction/parsing/mapping/write error |
| 2 | VALIDATION_FAILED | Validation failed in strict mode (`--strict`) |
| 3 | INPUT_NOT_FOUND | Input file not found |
| 4 | UNSUPPORTED_FORMAT | Unsupported document / cannot detect form type |
| 5 | WARNINGS_AS_ERRORS | Warnings exist and `--fail-on-warnings` enabled |
| 6 | CONFIG_ERROR | YAML config read/validation error |

### 11.3. Error structure in JSON
`warnings[]` and `errors[]` must contain objects:

```json
{
  "code": "MISSING_FIELD",
  "message": "company.cin is missing",
  "details": {
    "field": "company.cin"
  }
}
```

---

## 12. Project architecture

### 12.1. Repository structure (mandatory)
(See canonical structure in the Russian version.)

---

## 13. Classes and methods (English, mandatory)
All classes and methods must include English docstrings.

Core components:
- Pipeline
- PdfPlumberExtractor
- DocumentNormalizer
- SectionSplitter
- KeyValueParser
- TableParser
- DocumentParser
- BaseMapper + mappers
- Validator
- LoggerFactory

---

## 14. Testing

### 14.1. Unit tests
- unit test coverage **≥ 90%**
- `pytest` + coverage in CI

### 14.2. Integration tests
- at least 2 integration tests using real PDFs from `examples/`
- validate required fields + `meta.request_id`

### 14.3. CLI smoke test
- run CLI via subprocess
- assert exit code = 0
- assert output JSON file exists

---

## 15. Code quality and tooling

- Ruff + Black
- MyPy (at least for public APIs)
- GitHub Actions CI:
  - lint
  - unit tests + coverage
  - integration tests
  - coverage threshold ≥ 90%

---

## 16. Acceptance criteria

The project is accepted if:
1) CLI works for MGT-7 and MGT-7A PDFs.
2) A new request_id is generated per run.
3) request_id exists in logs, output JSON, and artifact names.
4) Logs are saved into `<DATE>.log` under `logging.file`.
5) Artifacts (if enabled) are saved into `logs/artifacts/`.
6) Artifact retention policy (`keep_days`) is implemented.
7) Exit codes are implemented.
8) Structured warnings/errors are implemented.
9) Unit coverage ≥ 90%.
10) Integration tests and CI pipeline exist.

---

## 17. Implementation plan (short)

### Phase 0 — Environment setup and quality workflow (mandatory)
- install dev dependencies: `pip install -e ".[dev]"`
- format: `ruff format .`
- lint: `ruff check --fix .`
- optional type check: `mypy src/mgt7_pdf_to_json`
- tests:
  - `pytest`
  - `pytest --cov=src/mgt7_pdf_to_json --cov-report=term-missing`
- optional: enable pre-commit hooks

### Phase 1 — Project skeleton and CLI
- create package structure
- implement CLI interface

### Phase 2 — Pipeline + Extract/Normalize/Parse
- implement PdfPlumberExtractor
- implement Normalizer
- implement SectionSplitter
- implement DocumentParser

### Phase 3 — Mappers
- DefaultMapper
- MinimalMapper
- DbMapper

### Phase 4 — Logging + request_id
- LoggerFactory (structured logging)
- file `<DATE>.log`
- request_id binding

### Phase 5 — Artifacts + retention
- save intermediate artifacts
- cleanup by keep_days

### Phase 6 — Validation + Exit codes
- Validator
- stable exit codes
- warnings/errors structure

### Phase 7 — Tests + CI
- unit tests ≥ 90%
- integration tests
- GitHub Actions

---

**End of document**
