"""
Test / demo script for the DNS Converter REST API.

Run with:
    poetry run pytest tests/test_api.py -v

These tests use FastAPI's built-in TestClient (backed by httpx),
so no running server is needed.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from dns_converter.api import app


@pytest.fixture
def transport():
    return ASGITransport(app=app)


@pytest_asyncio.fixture
async def client(transport):
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ---------------------------------------------------------------------------
# A-record examples
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_arecord_basic(client):
    """Convert a basic A record with TTL."""
    payload = {
        "record_type": "arecord",
        "address": "10.44.254.13",
        "fqdn": "trino-coordinator.dmp.ent.swift.com",
        "ttl": 3600,
    }

    resp = await client.post("/convert", json=payload)
    assert resp.status_code == 200

    body = resp.json()
    assert body["template"] == {"id": "dns-records", "version": 1}
    assert len(body["records"]) == 1

    rec = body["records"][0]
    assert rec["name"] == "trino-coordinator.dmp.ent.swift.com"
    assert rec["type"] == "A"
    assert rec["ip-addresses"] == ["10.44.254.13"]
    assert rec["ttl"] == 3600
    # No reverse-lookup requested
    assert "enable-reverse-lookup" not in rec


@pytest.mark.asyncio
async def test_arecord_with_ptr(client):
    """Convert an A record that requests a PTR (reverse-lookup)."""
    payload = {
        "record_type": "arecord",
        "address": "10.15.4.85",
        "fqdn": "trino-coordinator.senpac.dmp.dev.swift.com",
        "create_ptr": True,
        "ttl": 3600,
    }

    resp = await client.post("/convert", json=payload)
    assert resp.status_code == 200

    rec = resp.json()["records"][0]
    assert rec["type"] == "A"
    assert rec["enable-reverse-lookup"] is True


@pytest.mark.asyncio
async def test_arecord_no_ttl(client):
    """A record without a TTL — the field should be absent from the output."""
    payload = {
        "record_type": "arecord",
        "address": "192.168.1.10",
        "fqdn": "example.dmp.dev.swift.com",
    }

    resp = await client.post("/convert", json=payload)
    assert resp.status_code == 200

    rec = resp.json()["records"][0]
    assert "ttl" not in rec


# ---------------------------------------------------------------------------
# CNAME-record examples
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_cnamerecord_basic(client):
    """Convert a basic CNAME record."""
    payload = {
        "record_type": "cnamerecord",
        "canonical_name": "applb.c17.be.ocp.ent.swift.com",
        "fqdn": "administrator-1.dmp.ent.swift.com",
        "ttl": 3600,
    }

    resp = await client.post("/convert", json=payload)
    assert resp.status_code == 200

    body = resp.json()
    assert body["template"] == {"id": "dns-records", "version": 1}

    rec = body["records"][0]
    assert rec["name"] == "administrator-1.dmp.ent.swift.com"
    assert rec["type"] == "CNAME"
    assert rec["resolves-to"] == "applb.c17.be.ocp.ent.swift.com"
    assert rec["ttl"] == 3600
    # CNAME should never have ip-addresses
    assert "ip-addresses" not in rec


@pytest.mark.asyncio
async def test_cnamerecord_no_ttl(client):
    """CNAME without a TTL."""
    payload = {
        "record_type": "cnamerecord",
        "canonical_name": "applb.c01.be.ocp.ent.swift.com",
        "fqdn": "airflow.be.dmp.ent.swift.com",
    }

    resp = await client.post("/convert", json=payload)
    assert resp.status_code == 200

    rec = resp.json()["records"][0]
    assert rec["type"] == "CNAME"
    assert "ttl" not in rec


# ---------------------------------------------------------------------------
# Validation / edge cases
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_invalid_record_type(client):
    """Unknown record_type should be rejected."""
    payload = {
        "record_type": "mxrecord",
        "fqdn": "mail.dmp.dev.swift.com",
    }

    resp = await client.post("/convert", json=payload)
    assert resp.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_health_endpoint(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
