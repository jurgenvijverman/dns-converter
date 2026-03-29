"""FastAPI application exposing the DNS record converter as a REST API."""

from __future__ import annotations

from typing import Annotated, Union

from fastapi import FastAPI, Body

from .models import (
    ARecordRequest,
    CnameRecordRequest,
    DnsRecordResponse,
)
from .converter import convert_arecord, convert_cnamerecord

app = FastAPI(
    title="DNS Record Converter",
    description="Converts Infoblox-style DNS records into the dns-records JSON schema.",
    version="0.1.0",
)


@app.post(
    "/convert",
    response_model=DnsRecordResponse,
    response_model_exclude_none=True,
    summary="Convert a single DNS record",
    description=(
        "Accepts either an A record or a CNAME record and returns "
        "the corresponding JSON conforming to the dns-record.json schema."
    ),
)
async def convert_record(
    record: Annotated[
        Union[ARecordRequest, CnameRecordRequest],
        Body(discriminator="record_type"),
    ],
) -> DnsRecordResponse:
    if isinstance(record, ARecordRequest):
        return convert_arecord(record)
    return convert_cnamerecord(record)


@app.get("/health")
async def health():
    return {"status": "ok"}
