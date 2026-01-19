# Usage Examples

## CLI Examples

### Basic Conversion

```bash
# Convert MGT-7 PDF to JSON
mgt7pdf2json examples/U17120DL2013PTC262515_mgt7.pdf

# Output: U17120DL2013PTC262515_mgt7.json
```

### Specify Output File

```bash
mgt7pdf2json examples/U17120DL2013PTC262515_mgt7.pdf -o results/output.json
```

### Use Different Mapper

```bash
# Minimal mapper - essential fields only
mgt7pdf2json examples/U17120DL2013PTC262515_mgt7.pdf --mapper minimal -o output.json

# Database mapper - flattened structure
mgt7pdf2json examples/U17120DL2013PTC262515_mgt7.pdf --mapper db -o output.json
```

### Enable Debug Mode

```bash
# Enable artifacts and debug logging
mgt7pdf2json examples/U17120DL2013PTC262515_mgt7.pdf --debug-artifacts --log-level DEBUG

# Artifacts saved to: logs/artifacts/<request_id>.*.json
```

### Strict Validation

```bash
# Fail if required fields are missing
mgt7pdf2json examples/U17120DL2013PTC262515_mgt7.pdf --strict
```

### With Configuration File

```bash
# Use custom configuration
mgt7pdf2json examples/U17120DL2013PTC262515_mgt7.pdf --config myconfig.yml
```

## Python Library Examples

### Basic Usage

```python
from mgt7_pdf_to_json import Pipeline, Config

# Create pipeline with default config
config = Config.default()
pipeline = Pipeline(config)

# Process PDF
result = pipeline.process("input.pdf", output_path="output.json")

# Access results
print(f"Form Type: {result['meta']['form_type']}")
print(f"Request ID: {result['meta']['request_id']}")
print(f"Company: {result['data']['company']['name']}")
```

### Custom Configuration

```python
from mgt7_pdf_to_json import Pipeline, Config

# Load configuration from file
config = Config.from_yaml("config.yml")

# Override settings programmatically
config.logging.level = "DEBUG"
config.artifacts.enabled = True
config.pipeline.mapper = "minimal"

pipeline = Pipeline(config)
result = pipeline.process("input.pdf")
```

### Processing Multiple Files

```python
from pathlib import Path
from mgt7_pdf_to_json import Pipeline, Config

config = Config.default()
pipeline = Pipeline(config)

pdf_files = Path("pdfs").glob("*.pdf")

for pdf_file in pdf_files:
    output_file = pdf_file.with_suffix(".json")
    try:
        result = pipeline.process(str(pdf_file), str(output_file))
        print(f"✓ Processed: {pdf_file.name}")
        if result.get("errors"):
            print(f"  Errors: {len(result['errors'])}")
    except Exception as e:
        print(f"✗ Failed: {pdf_file.name} - {e}")
```

### Accessing Parsed Data

```python
from mgt7_pdf_to_json import Pipeline, Config

config = Config.default()
pipeline = Pipeline(config)

result = pipeline.process("input.pdf")

# Access meta information
meta = result["meta"]
print(f"Request ID: {meta['request_id']}")
print(f"Form Type: {meta['form_type']}")
print(f"Financial Year: {meta['financial_year']['from']} to {meta['financial_year']['to']}")

# Access company data
company = result["data"]["company"]
print(f"CIN: {company['cin']}")
print(f"Name: {company['name']}")

# Access financial data
financial = result["data"].get("turnover_and_net_worth", {})
print(f"Turnover: {financial.get('turnover_inr', 0)}")
print(f"Net Worth: {financial.get('net_worth_inr', 0)}")

# Access meetings
meetings = result["data"].get("meetings", {}).get("board_meetings", [])
for meeting in meetings:
    print(f"Meeting on {meeting['date']}: {meeting['directors_attended']}/{meeting['directors_total']} directors")

# Check for warnings/errors
if result["warnings"]:
    print(f"Warnings: {len(result['warnings'])}")
    for warning in result["warnings"]:
        print(f"  - {warning['code']}: {warning['message']}")

if result["errors"]:
    print(f"Errors: {len(result['errors'])}")
    for error in result["errors"]:
        print(f"  - {error['code']}: {error['message']}")
```

## Output Format Examples

### Default Mapper Output

Full output with all parsed fields:

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
    "meetings": {
      "board_meetings": [
        {
          "date": "09/04/2024",
          "directors_total": 4,
          "directors_attended": 4
        }
      ]
    }
  },
  "warnings": [],
  "errors": []
}
```

### Minimal Mapper Output

Essential fields only:

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
  "warnings": [],
  "errors": []
}
```

### Database Mapper Output

Flattened structure for database import:

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
          "meeting_date": "09/04/2024",
          "directors_total": 4,
          "directors_attended": 4
        }
      ]
    }
  },
  "warnings": [],
  "errors": []
}
```

## Error Handling Examples

### Handle Processing Errors

```python
from mgt7_pdf_to_json import Pipeline, Config

config = Config.default()
pipeline = Pipeline(config)

try:
    result = pipeline.process("input.pdf")
    
    if result["errors"]:
        print("Processing completed with errors:")
        for error in result["errors"]:
            print(f"  {error['code']}: {error['message']}")
    
    if result["warnings"]:
        print("Warnings:")
        for warning in result["warnings"]:
            print(f"  {warning['code']}: {warning['message']}")
            
except FileNotFoundError:
    print("Error: PDF file not found")
except ValueError as e:
    if "No extractable text" in str(e):
        print("Error: PDF appears to be scanned. OCR required.")
    else:
        print(f"Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Integration Examples

### Batch Processing with Progress

```python
from pathlib import Path
from tqdm import tqdm
from mgt7_pdf_to_json import Pipeline, Config

config = Config.default()
pipeline = Pipeline(config)

pdf_files = list(Path("pdfs").glob("*.pdf"))
results = []

for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
    output_file = pdf_file.with_suffix(".json")
    try:
        result = pipeline.process(str(pdf_file), str(output_file))
        results.append({
            "file": pdf_file.name,
            "status": "success",
            "request_id": result["meta"]["request_id"],
            "warnings": len(result["warnings"]),
            "errors": len(result["errors"])
        })
    except Exception as e:
        results.append({
            "file": pdf_file.name,
            "status": "error",
            "error": str(e)
        })

# Summary
successful = sum(1 for r in results if r["status"] == "success")
print(f"\nProcessed: {successful}/{len(results)} files successfully")
```