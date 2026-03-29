# DNS Converter

A Python tool and REST API that converts Infoblox-style DNS record CSV exports into JSON conforming to a strict `dns-record.json` schema.

## Overview

DNS records managed in Infoblox are typically exported as CSV files containing A records and CNAME records. This project provides two ways to convert them into a standardised JSON format:

1. **Batch CLI script** (`convert_dns.py`) — processes entire CSV files at once and writes JSON output files.
2. **REST API** — a FastAPI service that accepts individual records via `POST /convert` and returns the corresponding JSON on the fly.

Both produce output that validates against the `dns-record.json` JSON Schema included in the repository.

## Project Structure

```
dns-converter/
├── pyproject.toml              Poetry project config
├── dns-record.json             JSON Schema defining the output format
├── convert_dns.py              Standalone batch converter (no server needed)
│
├── dns_converter/              Python package (REST API)
│   ├── models.py               Pydantic request / response models
│   ├── converter.py            Core conversion logic
│   ├── api.py                  FastAPI application
│   └── cli.py                  Entry point — starts uvicorn
│
├── tests/
│   ├── test_api.py             pytest test suite
│   └── demo_requests.py        Runnable demo with httpx + curl examples
│
├── inputFiles/                 Sample Infoblox CSV exports
│   ├── dmp.dev.swift.com.csv
│   └── dmp.ent.swift.com.csv
│
└── outputFiles/                Generated JSON (created by convert_dns.py)
```

## Design

### Input format

The CSV files follow the Infoblox export format. Each file begins with two header rows (prefixed `header-arecord` and `header-cnamerecord`) that describe the column layout, followed by data rows prefixed with `arecord` or `cnamerecord`.

**A record columns:**

| Index | Field            | Used |
|-------|------------------|------|
| 0     | record type tag  | yes  |
| 1     | address (IPv4)   | yes  |
| 3     | fqdn             | yes  |
| 6     | create_ptr       | yes  |
| 11    | ttl              | yes  |

**CNAME record columns:**

| Index | Field            | Used |
|-------|------------------|------|
| 0     | record type tag  | yes  |
| 1     | canonical_name   | yes  |
| 2     | fqdn             | yes  |
| 9     | ttl              | yes  |

### Output format

Every response wraps records in a fixed template envelope:

```json
{
  "template": { "id": "dns-records", "version": 1 },
  "records": [
    {
      "name": "trino-coordinator.dmp.ent.swift.com",
      "type": "A",
      "ip-addresses": ["10.44.254.13"],
      "ttl": 3600
    }
  ]
}
```

Optional fields (`ttl`, `enable-reverse-lookup`, `resolves-to`, `ip-addresses`) are only included when they have a value, keeping the output clean.

### REST API design

The API exposes a single conversion endpoint that uses a **discriminated union** on the `record_type` field. This means both A and CNAME records share the same URL and FastAPI automatically routes to the correct Pydantic model for validation.

| Method | Path       | Description                        |
|--------|------------|------------------------------------|
| POST   | `/convert` | Convert a single DNS record        |
| GET    | `/health`  | Health check                       |
| GET    | `/docs`    | Interactive Swagger UI (auto-generated) |

## Getting Started

### Prerequisites

- Python 3.10+
- [Poetry](https://python-poetry.org/docs/#installation)

### Install dependencies

```bash
cd dns-converter
poetry install
```

### Batch conversion (standalone, no server needed)

The standalone script `convert_dns.py` is a plain Python script with no external dependencies — it only uses the standard library (`csv`, `json`, `pathlib`). You can run it without Poetry or any virtual environment.

Before running, copy your Infoblox CSV exports into the `inputFiles/` folder. The CSV files are not included in the repository — only the empty folder is tracked.

Process all CSV files in `inputFiles/` and write JSON to `outputFiles/`:

```bash
python convert_dns.py
```

Or target specific files:

```bash
python convert_dns.py inputFiles/dmp.ent.swift.com.csv
python convert_dns.py inputFiles/dmp.dev.swift.com.csv inputFiles/dmp.ent.swift.com.csv
```

Each input CSV produces a corresponding JSON file in the `outputFiles/` directory (created automatically). For example `inputFiles/dmp.ent.swift.com.csv` becomes `outputFiles/dmp.ent.swift.com.json`.

### Run the tests

The tests use FastAPI's `ASGITransport` with `httpx.AsyncClient` to call the app directly in-process, so **no running server is needed**:

```bash
poetry run pytest tests/test_api.py -v
```

### Start the REST API

```bash
poetry run dns-converter
```

The server starts on `http://localhost:8000` with hot-reload enabled. Open `http://localhost:8000/docs` for the interactive Swagger UI.

### Example API calls

With the server running, you can use curl or any HTTP client:

**A record:**

```bash
curl -X POST http://localhost:8000/convert \
  -H "Content-Type: application/json" \
  -d '{
    "record_type": "arecord",
    "address": "10.44.254.13",
    "fqdn": "trino-coordinator.dmp.ent.swift.com",
    "ttl": 3600
  }'
```

**CNAME record:**

```bash
curl -X POST http://localhost:8000/convert \
  -H "Content-Type: application/json" \
  -d '{
    "record_type": "cnamerecord",
    "canonical_name": "applb.c17.be.ocp.ent.swift.com",
    "fqdn": "administrator-1.dmp.ent.swift.com",
    "ttl": 3600
  }'
```

### Run the interactive demo

The demo script makes real HTTP requests, so it **requires the server to be running** in another terminal:

```bash
poetry run python tests/demo_requests.py
```

This prints the response for four example records and shows the equivalent curl commands.
