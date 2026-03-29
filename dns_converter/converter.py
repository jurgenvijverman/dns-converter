"""Core conversion logic — turns request models into output records."""

from __future__ import annotations

from .models import (
    ARecordRequest,
    CnameRecordRequest,
    DnsRecordOut,
    DnsRecordResponse,
)


def convert_arecord(req: ARecordRequest) -> DnsRecordResponse:
    """Convert an A-record request into the JSON schema output."""
    record_data: dict = {
        "name": req.fqdn,
        "type": "A",
        "ip-addresses": [req.address],
    }
    if req.ttl is not None:
        record_data["ttl"] = req.ttl
    if req.create_ptr:
        record_data["enable-reverse-lookup"] = True

    return DnsRecordResponse(records=[DnsRecordOut(**record_data)])


def convert_cnamerecord(req: CnameRecordRequest) -> DnsRecordResponse:
    """Convert a CNAME-record request into the JSON schema output."""
    record_data: dict = {
        "name": req.fqdn,
        "type": "CNAME",
        "resolves-to": req.canonical_name,
    }
    if req.ttl is not None:
        record_data["ttl"] = req.ttl

    return DnsRecordResponse(records=[DnsRecordOut(**record_data)])
