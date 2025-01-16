import json as _j
import time as _t
from urllib.parse import quote as _q, urlparse as _u
import requests as _r
from selectolax.parser import HTMLParser as _hp
from requests.packages.urllib3.exceptions import InsecureRequestWarning as _iw

_r.packages.urllib3.disable_warnings(_iw)

import concurrent.futures as _cf

_s = _r.Session()
_s.verify = False


class Serializer:
    def __init__(self):
        self._data = {}

    def set(self, key, value):
        self._data[key] = _j.dumps(value)

    def get(self, key):
        if key in self._data:
            return _j.loads(self._data[key])
        return None


def _gbs(_su):
    _srl = Serializer()
    try:
        _p = _u(_su).path.split("/")
        if "news.google.com" in _su and len(_p) > 1 and _p[-2] in ["articles", "read"]:
            _srl.set("_st", True)
            _srl.set("_b64", _p[-1])
        else:
            _srl.set("_st", False)
            _srl.set("_msg", "Invalid format.")
    except Exception as _e:
        _srl.set("_st", False)
        _srl.set("_msg", f"Error: {str(_e)}")
    return _srl


def _gdp(_b64):
    _srl = Serializer()
    try:
        _url = f"https://news.google.com/articles/{_b64}"
        _res = _r.get(_url, verify=False)
        _res.raise_for_status()
        _p = _hp(_res.text).css_first("c-wiz > div[jscontroller]")
        if not _p:
            _srl.set("_st", False)
            _srl.set("_msg", "Attributes missing.")
        else:
            _srl.set("_st", True)
            _srl.set("_sig", _p.attributes.get("data-n-a-sg"))
            _srl.set("_ts", _p.attributes.get("data-n-a-ts"))
            _srl.set("_b64", _b64)
    except _r.exceptions.RequestException:
        try:
            _url = f"https://news.google.com/rss/articles/{_b64}"
            _res = _r.get(_url, verify=False)
            _res.raise_for_status()
            _p = _hp(_res.text).css_first("c-wiz > div[jscontroller]")
            if not _p:
                _srl.set("_st", False)
                _srl.set("_msg", "Fallback failed.")
            else:
                _srl.set("_st", True)
                _srl.set("_sig", _p.attributes.get("data-n-a-sg"))
                _srl.set("_ts", _p.attributes.get("data-n-a-ts"))
                _srl.set("_b64", _b64)
        except _r.exceptions.RequestException as _err:
            _srl.set("_st", False)
            _srl.set("_msg", f"Request error: {str(_err)}")
    except Exception as _e:
        _srl.set("_st", False)
        _srl.set("_msg", f"Error: {str(_e)}")
    return _srl


def _du(_sig, _ts, _b64):
    _srl = Serializer()
    try:
        _url = "https://news.google.com/_/DotsSplashUi/data/batchexecute"
        _pl = [
            "Fbv4je",
            f'["garturlreq",[["X","X",["X","X"],null,null,1,1,"US:en",null,1,null,null,null,null,null,0,1],"X","X",1,[1,1,1],1,1,null,0,0,null,0],"{_b64}",{_ts},"{_sig}"]',
        ]
        _hdr = {"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8", "User-Agent": "Mozilla/5.0"}
        _res = _r.post(_url, headers=_hdr, data=f"f.req={_q(_j.dumps([[_pl]]))}", verify=False)
        _res.raise_for_status()
        _pd = _j.loads(_res.text.split("\n\n")[1])[:-2]
        _decoded = _j.loads(_pd[0][2])[1]
        _srl.set("status", True)
        _srl.set("decoded_url", _decoded)
    except _r.exceptions.RequestException as _e:
        _srl.set("_st", False)
        _srl.set("_msg", f"Request error: {str(_e)}")
    except (_j.JSONDecodeError, IndexError, TypeError) as _e:
        _srl.set("_st", False)
        _srl.set("_msg", f"Parse error: {str(_e)}")
    except Exception as _e:
        _srl.set("_st", False)
        _srl.set("_msg", f"Error: {str(_e)}")
    return _srl


def _dgn(_sq, _iv=None):
    _srl = Serializer()
    try:
        _b64_r = _gbs(_sq.get("link"))
        if not _b64_r.get("_st"):
            return _b64_r
        _dp_r = _gdp(_b64_r.get("_b64"))
        if not _dp_r.get("_st"):
            return _dp_r
        _d_r = _du(_dp_r.get("_sig"), _dp_r.get("_ts"), _dp_r.get("_b64"))
        if _iv:
            _t.sleep(_iv)
        print("_d_r", vars(_d_r))
        _sq["decoding"] = vars(_d_r).get('_data')
        _sq["decoding"]["decoded_url"] = _sq["decoding"]["decoded_url"].strip('"')
        # _sq["decoding"] = _u(_sq["decoding"]["decoded_url"])
        print("_sq______",type(_sq["decoding"]), type(_u(_sq["decoding"]["decoded_url"])), _u(_sq["decoding"]["decoded_url"].strip('"')) )
        return _sq
    except Exception as _e:
        _srl.set("_st", False)
        _srl.set("_msg", f"Error: {str(_e)}")
        return _srl

def _edc(_sq):
    """
    Concurrently performs decoding of URLs from provided queries.
    """
    import concurrent.futures as _cf

    with _cf.ThreadPoolExecutor() as _ex:
        _ft = {_ex.submit(_dgn, _arg): _arg for _arg in _sq}

        _rs = []
        for _ftd in _cf.as_completed(_ft):
            print("_ftd.result()",_ftd.result())
            _rs.append(_ftd.result())
    print("execute_decoding_concurrently_rs", _rs)
    return _rs

def _ec(_src):
    with _cf.ThreadPoolExecutor() as _ex:
        _futs = {_ex.submit(_dgn, _s): _s for _s in _src}
        _res = [_f.result() for _f in _cf.as_completed(_futs)]
    return _res
