from fastapi import APIRouter as _Rtr, HTTPException as _HTTPE, Request as _Req
from typing import List as _L, Dict as _D
from models.item_model import _gd, _nle_c
from schemas.item_schema import _LinkExtractionRequest as _LER, _BulkExtractionRequest as _BER
import asyncio as _asyncio
import uuid as _uuid

_rtr = _Rtr()

@_rtr.post(
    "/items/link_extraction",
    response_model=None,
    summary="Extract Links Based on Input Data"
)
async def _gle(link_request: _LER, req: _Req):
    items = await _gd(
        _nm=link_request.name,
        _sdt=link_request.start_date,
        _edt=link_request.end_date,
        _dmn=link_request.domain,
        _flg=link_request.flag,
        _cmp=link_request.company,
        _cntry=link_request.country,
        _req=req,
        _r_type=link_request.request_type
    )
    if not items:
        raise _HTTPE(status_code=404, detail="Items not found")
    return items

@_rtr.post(
    "/items/bulk_extraction",
    response_model=None,
    summary="Bulk Link Extraction Service"
)
async def _bulk_extraction(bulk_request: _BER, req: _Req):
    extracted_items: _D[str, list] = {}

    async def _process_item(item):
        _key = (
            f"{item.name}_[{item.flag}]_[{item.company}]_"
            f"[{','.join(item.domain)}]_{item.start_date}_{item.end_date}_{item.country}"
        )
        unique_key = str(_uuid.uuid5(_uuid.NAMESPACE_DNS, _key))
        if _key in extracted_items:
            return
        data = await _gd(
            _nm=item.name,
            _sdt=item.start_date,
            _edt=item.end_date,
            _dmn=item.domain,
            _flg=item.flag,
            _cmp=item.company,
            _cntry=item.country,
            _req=req,
            _r_type=item.request_type
        )
        extracted_items[_key] = data if data else "No items found"

    await _asyncio.gather(*(_process_item(item) for item in bulk_request.bulk_request))
    if all(val == "No items found" for val in extracted_items.values()):
        raise _HTTPE(status_code=404, detail="No items found for any request")
    return extracted_items

@_rtr.post(
    "/items/news_link",
    response_model=None,
    summary="Extract News Links Based on Input User"
)
async def _news_link(link_request: _LER, req: _Req):
    """
    Handle POST requests for news link extraction by passing request data to the controller.
    """
    items = await _nle_c(
        _nm=link_request.name,
        _cmp=link_request.company,
        _sdt=link_request.start_date,
        _edt=link_request.end_date,
        _cntry=link_request.country,
        _req=req
    )
    if not items:
        raise _HTTPE(status_code=404, detail="Items not found")
    return items
