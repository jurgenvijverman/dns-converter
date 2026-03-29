#!/usr/bin/env python3
"""
Convert DNS record CSV exports into JSON files conforming to the dns-record.json schema.

Usage:
    python convert_dns.py                          # process all CSVs in inputFiles/
    python convert_dns.py inputFiles/foo.csv       # process a single file
    python convert_dns.py file1.csv file2.csv      # process multiple files
"""

from __future__ import annotations

import csv
import json
import sys
import os
from pathlib import Path

# Directories (relative to wherever the script lives)
SCRIPT_DIR = Path(__file__).resolve().parent
INPUT_DIR = SCRIPT_DIR / "inputFiles"
OUTPUT_DIR = SCRIPT_DIR / "outputFiles"


def parse_ttl(raw: str) -> int | None:
    """Return an integer TTL or None when the field is empty."""
    raw = raw.strip()
    if raw == "":
        return None
    return int(raw)


def parse_bool(raw: str) -> bool:
    """Parse a boolean string (TRUE/FALSE/empty) to a Python bool."""
    return raw.strip().upper() == "TRUE"


def row_to_record(row: list[str], record_type: str) -> dict:
    """
    Convert a single CSV row into a JSON record dict.

    A-record CSV columns (after the type tag):
        address, _new_address, fqdn, _new_fqdn, comment, create_ptr,
        creator, ddns_principal, ddns_protected, disabled, ttl, view

    CNAME-record CSV columns (after the type tag):
        canonical_name, fqdn, _new_fqdn, comment, creator,
        ddns_principal, ddns_protected, disabled, ttl, view, ...
    """
    if record_type == "arecord":
        address = row[1].strip()
        fqdn = row[3].strip()
        create_ptr = parse_bool(row[6]) if len(row) > 6 else False
        ttl = parse_ttl(row[11]) if len(row) > 11 else None

        record: dict = {
            "name": fqdn,
            "type": "A",
            "ip-addresses": [address],
        }
        if ttl is not None:
            record["ttl"] = ttl
        if create_ptr:
            record["enable-reverse-lookup"] = True

    elif record_type == "cnamerecord":
        canonical_name = row[1].strip()
        fqdn = row[2].strip()
        ttl = parse_ttl(row[9]) if len(row) > 9 else None

        record = {
            "name": fqdn,
            "type": "CNAME",
            "resolves-to": canonical_name,
        }
        if ttl is not None:
            record["ttl"] = ttl

    else:
        raise ValueError(f"Unknown record type: {record_type}")

    return record


def convert_csv(csv_path: Path) -> dict:
    """Read a single CSV file and return the full JSON structure."""
    records: list[dict] = []

    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue

            tag = row[0].strip().lower()

            # Skip header rows
            if tag.startswith("header-"):
                continue

            if tag in ("arecord", "cnamerecord"):
                records.append(row_to_record(row, tag))

    return {
        "template": {
            "id": "dns-records",
            "version": 1,
        },
        "records": records,
    }


def main():
    # Determine which files to process
    if len(sys.argv) > 1:
        csv_files = [Path(p) for p in sys.argv[1:]]
    else:
        csv_files = sorted(INPUT_DIR.glob("*.csv"))

    if not csv_files:
        print("No CSV files found to process.")
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for csv_path in csv_files:
        print(f"Processing {csv_path.name} ...")
        result = convert_csv(csv_path)

        out_name = csv_path.stem + ".json"
        out_path = OUTPUT_DIR / out_name

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        print(f"  -> {out_path}  ({len(result['records'])} records)")

    print("Done.")


if __name__ == "__main__":
    main()
