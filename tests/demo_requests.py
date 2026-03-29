#!/usr/bin/env python3
"""
Demo script — call the running DNS Converter API with example records.

Start the server first:
    poetry run dns-converter          # or: poetry run uvicorn dns_converter.api:app

Then run this script:
    poetry run python tests/demo_requests.py
"""

import httpx
import json

BASE = "http://localhost:8000"


def pp(label: str, resp: httpx.Response):
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    print(f"  Status: {resp.status_code}")
    print(json.dumps(resp.json(), indent=2))


def main():
    with httpx.Client(base_url=BASE) as client:

        # --- Example 1: A record with TTL ---
        resp = client.post("/convert", json={
            "record_type": "arecord",
            "address": "10.44.254.13",
            "fqdn": "trino-coordinator.dmp.ent.swift.com",
            "ttl": 3600,
        })
        pp("A record (with TTL)", resp)

        # --- Example 2: A record with reverse-lookup ---
        resp = client.post("/convert", json={
            "record_type": "arecord",
            "address": "10.15.4.85",
            "fqdn": "trino-coordinator.senpac.dmp.dev.swift.com",
            "create_ptr": True,
            "ttl": 3600,
        })
        pp("A record (with PTR / reverse-lookup)", resp)

        # --- Example 3: CNAME record with TTL ---
        resp = client.post("/convert", json={
            "record_type": "cnamerecord",
            "canonical_name": "applb.c17.be.ocp.ent.swift.com",
            "fqdn": "administrator-1.dmp.ent.swift.com",
            "ttl": 3600,
        })
        pp("CNAME record (with TTL)", resp)

        # --- Example 4: CNAME record without TTL ---
        resp = client.post("/convert", json={
            "record_type": "cnamerecord",
            "canonical_name": "applb.c01.be.ocp.ent.swift.com",
            "fqdn": "airflow.be.dmp.ent.swift.com",
        })
        pp("CNAME record (no TTL)", resp)

    print("\n\n--- Equivalent curl commands ---\n")
    print("""# A record
curl -X POST http://localhost:8000/convert \\
  -H "Content-Type: application/json" \\
  -d '{"record_type":"arecord","address":"10.44.254.13","fqdn":"trino-coordinator.dmp.ent.swift.com","ttl":3600}'

# CNAME record
curl -X POST http://localhost:8000/convert \\
  -H "Content-Type: application/json" \\
  -d '{"record_type":"cnamerecord","canonical_name":"applb.c17.be.ocp.ent.swift.com","fqdn":"administrator-1.dmp.ent.swift.com","ttl":3600}'
""")


if __name__ == "__main__":
    main()
