import concurrent.futures as _cf
from typing import List as _L, Optional as _O
import urllib.parse as _up
import time as _t
import os as _o
import json as _j
import asyncio as _async
import aiohttp as _aio
from selectolax.parser import HTMLParser as _HTML
from random import uniform as _uni
import requests as _req
from fastapi import Request as _Req, HTTPException as _HTTP
from .custom_link_decoder import _ec, _gbs, _gdp, _du, _dgn, _edc
from .llm_analysis import  _fls, _sm, _rp, _rc,_rd,_st,_kw,_kw_cat,_ka,_sa,_lsr, _kv
from typing import List as _L, Tuple as _T, Union as _U
from datetime import datetime as _d_t, date as _d, timedelta as _td
import math as _m
from dotenv import load_dotenv as _ld
from aiohttp import ClientSession as _CS
from collections import defaultdict as _DD

_ld()
_CTYPE = _o.getenv('CONFIG')
_SURL = _o.getenv('SCRAPER')

# Mock DB Replacement
class _IM:
    def __init__(self, i: int, n: str, d: _O[str] = None):
        self.i = i
        self.n = n
        self.d = d

_items_db: _L[_IM] = [
    _IM(i=1, n="Item One", d="This is the first item."),
    _IM(i=2, n="Item Two", d="This is the second item."),
    _IM(i=3, n="Item Three", d="This is the third item."),
]

def _rdf():
    with open('./d.json', 'r') as _f:
        return _j.load(_f)

_dm = _rdf()

def _rapa(_ad: dict, _n: int, _nm: str, _dm: str, _fl: str, _co: str, _dc: bool) -> tuple[dict, int]:
    _ar = _ad["full_article"][:70000]
    _ti = _ad['title']

    _cfw = False

    print(f"---------- STARTING ANALYSIS FOR ARTICLE # {_n} : {_ti} ---------------")

    _a1, _sc = _rp(_nm, _ar, _fl)
    if _sc == 429:
        return {}, 429
    elif _sc == 404:
        return {}, 404
    elif _sc == 201:
        _cfw = True
        _a1, _rsc = _rp(_nm, _ti, _fl)
        if _rsc != 200:
            return {}, 404

    _a2 = 'Y'
    if _co and _fl == 'POI' and 'y' in _a1.lower():
        # Step 2: Check relation to company
        _a2, _sc = _rc(_co, _ar, _fl)
        if _sc == 429:
            return {}, 429
        elif _sc == 404:
            return {}, 404
        elif _sc == 201:
            _cfw = True
            _a2 = 'N'
    if "y" in _a1.lower() and "y" in _a2.lower():
        _dr = {}
        for _dms in _dm:
            _resp, _sc = _rd(_dms, _ar, _fl)
            if _sc == 429:
                return {}, 429
            elif _sc == 404:
                return {}, 404
            elif _sc == 201:
                _cfw = True

            _dr[_dms] = True if _resp.lower() == 'y' else False

        # Step 4: Summarize the text
        _smry, _sc = _sm(_ti, _ar, _nm, _fl)
        if _sc == 429:
            return {}, 429
        elif _sc == 404:
            return {}, 404
        elif _sc == 201:
            _cfw = True

        # Step 5: Perform sentiment analysis
        # _snt, _scs = _st(_ar, _nm, _fl)
        _snt, _scs =  _st(_ar, _nm, _fl)

        print(_scs, f"CHECK 5: RESULT - Sentiment for article status code: {_scs}")
        if _scs == 429:
            return {}, 429
        elif _scs == 404:
            return {}, 404
        elif _scs == 201:
            _cfw = True

        # Step 6: Extract keywords
        _kwd, _kwsc = _kw(_smry, _fl)
        if _kwsc == 429:
            return {}, 429
        elif _kwsc == 404:
            return {}, 404
        elif _kwsc == 201:
            _cfw = True

        # Step 7: Categorize keywords
        _kw_catd, _kwl = _kw_cat(_ar, _kwd)

        if _dc:
            _ar = ""

        # Prepare final result
        _aa = {
            'title': _ti,
            'date': _ad['date'],
            'link': _ad['link'],
            'full_article': _ar,
            'summary': _smry,
            'sentiment': _snt,
            'keywords': _kwl,
            'keywords_categorised': _kw_catd,
            'domain': _dr,
            'content_filtered': _cfw
        }
        print(f"---------- FINISHED ANALYSIS FOR ARTICLE # {_n} ---------------")
        return _aa, 200
    else:
        print(f"---------- NON-RELEVANT ARTICLE # {_n} ---------------")
        return {}, 400

async def _eapc(_nw, _nm, _dm, _aac, _fl, _co, _dc, _bsaa, _rq):
    # print("_eapc", _nw, _nm, _dm, _aac, _fl, _co, _dc, _bsaa, _rq)
    if isinstance(_dm, str):
        _dm = [_dm]

    _fn = []
    _ct = 0

    with _cf.ThreadPoolExecutor(max_workers=_bsaa) as _exe:
        _fta = {}

        for _n, _ad in enumerate(_nw):
            _ft = _exe.submit(_rapa, _ad, _n, _nm, _dm, _fl, _co, _dc)
            _fta[_ft] = _ad  # Map future to the article

        for _ft in _cf.as_completed(_fta):
            _ar = _fta[_ft]
            try:
                _aa, _asc = _ft.result()

                if await _rq.is_disconnected():
                    print("Client disconnected, cancelling news extraction.")
                    raise _HTTP(status_code=499, detail="Client Closed Request")

                if _asc == 429:
                    print("Received 429: Too Many Requests, Halt Process and Return News Analysed So Far...")
                    return _fn, 429

                if _asc == 404:
                    print("Received 404: Uncategorised Error, Skipping")
                    continue
                if _asc == 400:
                    print("Received 400: Unrelated Article, Skipping")
                    continue

                if _asc == 200 or _asc == 201:
                    _fn.append(_aa)
                    _ct += 1

                if _ct >= _aac:
                    break

            except Exception as _e:
                print(f"Error processing article {_ar['title']}: {_e}")

    return _fn, 200

async def _eac(_nw: _L, _rq: _Req) -> _L:
    print("Starting Article Extraction - Calling API Here")

    _url = f"{_SURL}/scrapeArticles"
    _pl = _j.dumps(_nw)
    _hdrs = {
        'Content-Type': 'application/json'
    }

    _res = _req.request("POST", _url, headers=_hdrs, data=_pl)
    _asr = _res.json()

    _nw = []
    for _r in _asr:
        if await _rq.is_disconnected():
            raise _HTTP(status_code=499, detail="Client Closed Request")
        if _r["success"]:
            if len(_r['scraped']['content']) > 50:
                _fr = _r["original"]
                _fr.update(
                    {"scraped_title": _r['scraped']['title'],
                     "full_article": _r['scraped']['content'],
                     "scraping_timestamp": _r['scraped']['timestamp'],
                     "scraping_contentlength": _r['scraped']['contentLength'],
                     "scraping_success": _r["success"]
                     })
                _nw.append(_fr)

    return _nw

def _sar(_ar):
    print(f"Starting Article Extraction - Calling API for article {_ar.get('title')}")

    _url = f"{_SURL}/scrapeSingleArticle"
    _pl = _j.dumps(_ar)
    _hdrs = {'Content-Type': 'application/json'}

    _res = _req.post(_url, headers=_hdrs, data=_pl)

    _rslt = _res.json()
    if _rslt["success"]:
        if len(_rslt['scraped']['content']) > 50:
            _fr = _rslt["original"]
            _fr.update(
                {"scraped_title": _rslt['scraped']['title'],
                 "full_article": _rslt['scraped']['content'],
                 "scraping_timestamp": _rslt['scraped']['timestamp'],
                 "scraping_contentlength": _rslt['scraped']['contentLength'],
                 "scraping_success": _rslt["success"]
                 })
            return _fr
    else:
        return None


def _pb(_btch):
    print("_btch", _btch)
    with _cf.ThreadPoolExecutor() as _exec:
        return list(_exec.map(_sar, _btch))

async def _eac_c(_nws: _L, _req: _Req, _bs: int) -> _L:
    _ar_res = []
    _bsz = _bs
    print("_nws", _nws)
    # Split news-batches of length "_bsz"
    for _i in range(0, len(_nws), _bsz):
        _btch = _nws[_i:_i + _bsz]
        print(f"Processing batch {_i // _bsz + 1} of {_m.ceil(len(_nws) / _bsz)}")
        print("_btch", _btch)
        _btch_res = _pb(_btch)  # Process the current batch concurrently
        _ar_res.extend(_btch_res)  # Add results

    _ar_res = [_ar for _ar in _ar_res if _ar]
    print("_ar_res", _ar_res)
    return _ar_res


async def _nle(_nm: str, _cmp: str, _sd: _d, _ed: _d, _cntry: str, _req: _Req):
    _dur = []
    if _ed.year != _sd.year:
        _start_tpl = (_sd.strftime("%Y-%m-%d"), _d_t(_sd.year, 12, 31).strftime("%Y-%m-%d"))
        _dur.append(_start_tpl)
        _cur_yr = _sd.year + 1
        while _cur_yr < _ed.year:
            _cur_tpl = (_d_t(_cur_yr, 1, 1).strftime("%Y-%m-%d"), _d_t(_cur_yr, 12, 31).strftime("%Y-%m-%d"))
            _dur.append(_cur_tpl)
            _cur_yr += 1

        _ed_tpl = (_d_t(_ed.year, 1, 1).strftime("%Y-%m-%d"), _ed.strftime("%Y-%m-%d"))
        _dur.append(_ed_tpl)
    else:
        _dur.append((_sd.strftime("%Y-%m-%d"), _ed.strftime("%Y-%m-%d")))

    _base_url = 'https://news.google.com/search?q='
    _nws = []
    print(_dur)

    async with _CS() as _ses:
        for _n in _dur:
            if await _req.is_disconnected():
                print("Client disconnected, cancelling news extraction.")
                raise _HTTP(status_code=499, detail="Client Closed Request")
            _dur_srch = f'after:{_n[0]} before:{_n[1]}' if len(_dur) > 1 else f'after:{_sd} before:{_ed}'
            _cntry_url = f'&gl={_cntry}&&hl=en-{_cntry}&ceid={_cntry}:en'
            _hco_url = _base_url + _up.quote(f'{_nm} {_cmp} {_dur_srch}') + _cntry_url
            print(f"Fetching URL: {_hco_url}")

            _html = await _fetch(_ses, _hco_url)
            if _html is None:
                print(f"No content retrieved for year {_n}")
                continue

            _tree = _HTML(_html)
            _arts = _tree.css('.D9SJMe .IFHyqb.DeXSAc')

            if not _arts:
                print(f'No news found for year: {_n}')
                continue

            for _art in _arts:
                try:
                    if await _req.is_disconnected():
                        print("Client disconnected, cancelling news extraction.")
                        raise _HTTP(status_code=499, detail="Client Closed Request")
                    _dt_el = _art.css_first('.hvbAAd')
                    _dt = _dt_el.attributes.get('datetime')[:10] if _dt_el else None

                    _ttl_el = _art.css_first('.JtKRv')
                    _ttl = _ttl_el.text() if _ttl_el else None

                    _lnk = _ttl_el.attributes.get('href') if _ttl_el else None
                    if _lnk:
                        _lnk = _up.urljoin('https://news.google.com', _lnk)

                    if _lnk:
                        _nws.append({'title': _ttl, 'date': _dt, 'link': _lnk})
                    else:
                        print(f"Invalid link found for article: {_ttl}")
                except Exception as _e:
                    print(f"Error parsing article for year {_n}: {_e}")

            print(f"{len(_nws)} articles found for year {_n}")

    return _nws


async def _fetch(_ses: _CS, _url: str, _prxy=None, _rtr=3):
    _hdrs = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    try:
        async with _ses.get(_url, headers=_hdrs, proxy=_prxy) as _resp:
            if _resp.status == 200:
                await _async.sleep(8)  
                return await _resp.text()
            elif _resp.status == 429:
                print(f"Received 429 for {_url}, retrying after delay...")
                await _async.sleep(_uni(5, 10)) 
                if _rtr > 0:
                    return await _fetch(_ses, _url, _prxy, _rtr - 1)
                else:
                    return None
            else:
                print(f"Failed to fetch {_url} with status code {_resp.status}")
                return None
    except Exception as _e:
        print(f"Error fetching {_url}: {_e}")
        return None


async def _pd(_ses, _n, _nm, _cmp, _cntry, _b_url):
    try:
        _dur_srch = f'after:{_n[0]} before:{_n[1]}'
        _cntry_url = f'&gl={_cntry}&hl=en-{_cntry}&ceid={_cntry}:en'
        _hco_url = _b_url + _up.quote(f'{_nm} {_cmp} {_dur_srch}') + _cntry_url
        print(f"Fetching URL: {_hco_url}")

        _html = await _fetch(_ses, _hco_url)
        if _html is None:
            print(f"No content retrieved for duration {_n}")
            return []

        _nws = []
        _tree = _HTML(_html)
        _arts = _tree.css('.D9SJMe .IFHyqb.DeXSAc')

        if not _arts:
            print(f'No news found for year: {_n}')

        async def _pa(_art):
            try:
                _dt_el = _art.css_first('.hvbAAd')
                _dt = _dt_el.attributes.get('datetime')[:10] if _dt_el else None

                _ttl_el = _art.css_first('.JtKRv')
                _ttl = _ttl_el.text() if _ttl_el else None

                _lnk = _ttl_el.attributes.get('href') if _ttl_el else None
                if _lnk:
                    _lnk = _up.urljoin('https://news.google.com', _lnk)

                if _lnk:
                    return {'title': _ttl, 'date': _dt, 'link': _lnk}
                else:
                    print(f"Invalid link found for article: {_ttl}")
                    return None
            except Exception as _e:
                print(f"Error parsing article for year {_n}: {_e}")
                return None

        _tsks = [_pa(_art) for _art in _arts]
        _res = await _async.gather(*_tsks, return_exceptions=True)

        _nws = [_r for _r in _res if _r is not None]

        print(f"{len(_nws)} articles found for duration {_n}")
        return _nws

    except Exception as _e:
        print(f"Error processing duration {_n}: {_e}")
        return []


async def _nle_c(_nm: str, _cmp: str, _sdt: _d, _edt: _d, _cntry: str, _req: _Req):
    _dur = []
    if _edt.year != _sdt.year:
        _st_tpl = (_sdt.strftime("%Y-%m-%d"), _d_t(_sdt.year, 12, 31).strftime("%Y-%m-%d"))
        _dur.append(_st_tpl)
        _cur_yr = _sdt.year + 1
        while _cur_yr < _edt.year:
            _cur_yr_tpl = (_d_t(_cur_yr, 1, 1).strftime("%Y-%m-%d"),
                           _d_t(_cur_yr, 12, 31).strftime("%Y-%m-%d"))
            _dur.append(_cur_yr_tpl)
            _cur_yr += 1

        _edt_tpl = (_d_t(_edt.year, 1, 1).strftime("%Y-%m-%d"), _edt.strftime("%Y-%m-%d"))
        _dur.append(_edt_tpl)
    else:
        _dur.append((_sdt.strftime("%Y-%m-%d"), _edt.strftime("%Y-%m-%d")))

    _b_url = 'https://news.google.com/search?q='
    _nws = []
    print(_dur)

    async with _CS() as _ses:
        _tsks = [
            _pd(_ses, _n, _nm, _cmp, _cntry, _b_url)
            for _n in _dur
        ]

        for _tsk in _async.as_completed(_tsks):
            if await _req.is_disconnected():
                print("Client disconnected, cancelling news extraction.")
                raise _HTTP(status_code=499, detail="Client Closed Request")

            try:
                _res = await _tsk
                _nws.extend(_res)
            except Exception as _e:
                print(f"Error processing a task: {_e}")

    return _nws

async def _gd(_nm: str, _sdt: _d, _edt: _d, _dmn: str, _flg: str, _cmp: str, _cntry: str, _req: _Req, _r_type: str) -> _j:
    _dcfg = False
    if _CTYPE.lower() == "demo":
        _dcfg = True
        if _r_type == "single":
            _a_cap = 20
            _aa_cap = 20
            _bs_as = 20
            _bs_aa = 20
        else:
            _a_cap = 7
            _aa_cap = 7
            _bs_as = 7
            _bs_aa = 7
    else:
        _a_cap = 5
        _aa_cap = 5
        _bs_as = 1
        _bs_aa = 1
    if _cntry.lower() == "zz":
        _cntry = "US"
    _d_chk = _nm.lower().replace(" ", "")
    if _d_chk in _dm:
        _t.sleep(5)
        if await _req.is_disconnected():
            print("Client disconnected, cancelling news extraction.")
            raise _HTTP(status_code=499, detail="Client Closed Request")
        return {
            "status": 200,
            "message": "successful",
            "data": _dm[_d_chk]["data"],
            "keywords-data-agg": _dm[_d_chk]["keywords-data-agg"],
        }

    _start_ls = _d_t.now()
    print(f"Begin News Screening Analysis for: {_nm} from {_sdt} to {_edt}")

    if await _req.is_disconnected():
        print("Client disconnected, cancelling news extraction.")
        raise _HTTP(status_code=499, detail="Client Closed Request")

    if _dcfg:
        _nws = await _nle_c(_nm, _cmp, _sdt, _edt, _cntry, _req)
    else:
        _nws = await _nle(_nm, _cmp, _sdt, _edt, _cntry, _req)

    _cnt = 0
    while not _nws and _cnt < 5:
        _cnt += 1
        print(f"Retrying... attempt {_cnt}")
        _nws = await _nle(_nm, _cmp, _sdt, _edt, _cntry, _req)

    if not _nws:
        return {"status": 404, "message": "no news found", "data": []}

    if await _req.is_disconnected():
        print("Client disconnected, cancelling news extraction.")
        raise _HTTP(status_code=499, detail="Client Closed Request")

    _start_sort = _d_t.now()
    _nws = _lsr(_nws, 3, _df=_dcfg)
    _nws = _nws[:_a_cap]

    _start_dec = _d_t.now()
    _nws = _edc(_nws)

    if await _req.is_disconnected():
        print("Client disconnected, cancelling news extraction.")
        raise _HTTP(status_code=499, detail="Client Closed Request")

    _start_art_ext = _d_t.now()

    if _dcfg:
        _nws = await _eac_c(_nws, _req, _bs_as)
    else:
        _nws = await _eac(_nws, _req)

    _no_of_ext = len(_nws)

    if await _req.is_disconnected():
        print("Client disconnected, cancelling news extraction.")
        raise _HTTP(status_code=499, detail="Client Closed Request")

    _start_anal = _d_t.now()
    _nws, _sc = await _eapc(_nws, _nm, _dmn, _aa_cap, _flg, _cmp, _dcfg, _bs_aa, _req)

    if await _req.is_disconnected():
        print("Client disconnected, cancelling news extraction.")
        raise _HTTP(status_code=499, detail="Client Closed Request")

    _start_kw_agg = _d_t.now()
    _kw_data_agg = await _ka(_nws, _nm, _cmp)

    if await _req.is_disconnected():
        print("Client disconnected, cancelling news extraction.")
        raise _HTTP(status_code=499, detail="Client Closed Request")

    try:
        _senti_data_agg = await _sa(_nws)
    except:
        try:
            _cts = _DD(lambda: _DD(int))
            for _e in _nws:
                _dt_key = _e["date"]
                _snt = _e["sentiment"]
                _cts[_dt_key][_snt] += 1

            _agg_snt_cts = []
            for _dt_key, _snts in _cts.items():
                _res = dict()
                _res["month"] = _dt_key
                _res["negative"] = 0
                _res["positive"] = 0
                _res["neutral"] = 0
                for _snt, _cnt in _snts.items():
                    _res[_snt] = _cnt

                _agg_snt_cts.append(_res)

            _snt_data_agg = _agg_snt_cts
            _snt_data_agg = sorted(_snt_data_agg, key=lambda _x: _d_t.strptime(_x.get('month'), '%Y-%m-%d'), reverse=False)

        except:
            _senti_data_agg = []

    _stopped = _d_t.now()

    if _sc == 429:
        print('--------- API LIMIT HIT --------', _sc)

    _al_meta = {
        "analysis_limit_hit": _sc == 429,
        "total_extracted_articles": _no_of_ext,
        "final_relevant_articles": len(_nws),
    }

    print("link extraction time", _start_dec - _start_ls)
    print("decoding time", _start_art_ext - _start_dec)
    print("article extraction", _start_anal - _start_art_ext)
    print("analysis", _start_kw_agg - _start_anal)
    print("aggregation process", _stopped - _start_kw_agg)
    print("Total Time ---- ", _stopped - _start_ls)

    if not len(_nws) and _sc == 429:
        return {
            "status": 200,
            "message": "successful",
            "data": [],
            "keywords-data-agg": [],
            "sentiment-data-agg": [],
            "analysis-metadata": _al_meta,
        }
    elif not len(_nws):
        return {"status": 404, "message": "no news found", "data": []}
    else:
        return {
            "status": 200,
            "message": "successful",
            "data": _nws,
            "keywords-data-agg": _kw_data_agg,
            "sentiment-data-agg": _senti_data_agg,
            "analysis-metadata": _al_meta,
        }
