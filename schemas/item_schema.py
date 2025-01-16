from pydantic import BaseModel as _BM, Field as _Fld, HttpUrl as _Url, constr as _StrCon, conlist as _LstCon
from typing import List as _L, Optional as _Opt
from datetime import date as _Dt
from enum import Enum as _Enum

class _Sentiment(str, _Enum):
    neg = "negative"
    neutral = "neutral"
    positive = "positive"

class _Flag(str, _Enum):
    poi = "POI"
    entity = "Entity"

class _RequestType(str, _Enum):
    single = "single"
    bulk = "bulk"

class _NewsItem(_BM):
    title: str
    date: _Opt[_Dt]
    link: _Url

    def __getitem__(self, item):
        return getattr(self, item)

class _ArticleExtractionRequest(_BM):
    news: _L[_NewsItem]
    name: str
    domain: str

class _LinkExtractionRequest(_BM):
    name: str = _Fld(..., description="Mandatory name field.")
    flag: _Flag = _Fld(..., description='"POI" or "Entity" - Mandatory')
    company: _Opt[str] = _Fld(None, description="Optional company name.")
    domain: _Opt[_LstCon(str, max_length=3)] = _Fld(None, description="Optional list of strings, maximum 3.")
    start_date: _Dt = _Fld(..., description="Mandatory start date in YYYY-MM-DD format.")
    end_date: _Dt = _Fld(..., description="Mandatory end date in YYYY-MM-DD format.")
    country: _StrCon(strip_whitespace=True) = _Fld(..., description="Mandatory country field.")
    request_type: _RequestType = _Fld(..., description='"single" or "bulk" - Mandatory')

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Sample Entity",
                "flag": "POI",
                "company": "Sample Company",
                "domain": ["Tech", "Finance", "Health"],
                "start_date": "2024-10-07",
                "end_date": "2024-11-19",
                "country": "USA",
                "request_type": "single"
            }
        }

class _BulkExtractionRequest(_BM):
    bulk_request: _L[_LinkExtractionRequest]
