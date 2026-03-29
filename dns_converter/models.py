"""Pydantic models matching the dns-record.json schema."""

from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Literal


class ARecordRequest(BaseModel):
    """Raw CSV fields for an A record."""

    record_type: Literal["arecord"] = "arecord"
    address: str = Field(..., description="IPv4 address")
    fqdn: str = Field(..., description="Fully qualified domain name")
    create_ptr: bool = Field(False, description="Create reverse-lookup PTR record")
    ttl: int | None = Field(None, ge=300, description="Time to live in seconds")

    model_config = {"json_schema_extra": {"examples": [
        {
            "record_type": "arecord",
            "address": "10.44.254.13",
            "fqdn": "trino-coordinator.dmp.ent.swift.com",
            "create_ptr": False,
            "ttl": 3600,
        }
    ]}}


class CnameRecordRequest(BaseModel):
    """Raw CSV fields for a CNAME record."""

    record_type: Literal["cnamerecord"] = "cnamerecord"
    canonical_name: str = Field(..., description="Target hostname the CNAME resolves to")
    fqdn: str = Field(..., description="Fully qualified domain name (alias)")
    ttl: int | None = Field(None, ge=300, description="Time to live in seconds")

    model_config = {"json_schema_extra": {"examples": [
        {
            "record_type": "cnamerecord",
            "canonical_name": "applb.c17.be.ocp.ent.swift.com",
            "fqdn": "administrator-1.dmp.ent.swift.com",
            "ttl": 3600,
        }
    ]}}


# --- Response models ---

class DnsTemplate(BaseModel):
    id: str = "dns-records"
    version: int = 1


class DnsRecordOut(BaseModel):
    """A single DNS record in the output schema."""

    name: str
    type: Literal["A", "CNAME"]
    ip_addresses: list[str] | None = Field(None, alias="ip-addresses")
    ttl: int | None = None
    enable_reverse_lookup: bool | None = Field(None, alias="enable-reverse-lookup")
    resolves_to: str | None = Field(None, alias="resolves-to")

    model_config = {"populate_by_name": True, "by_alias": True}


class DnsRecordResponse(BaseModel):
    """Full response wrapping a single converted record."""

    template: DnsTemplate = DnsTemplate()
    records: list[DnsRecordOut]
