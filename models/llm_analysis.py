import re as _r
import os as _o
import openai as _oa
import pandas as pd
from openai import AzureOpenAI as _ai
from dotenv import load_dotenv as _ld
import ast as _as
import spacy as _sp
from collections import Counter as _ct, defaultdict as _dfd
from datetime import datetime as _dt
import calendar as _cl

_nlp = _sp.load("en_core_web_sm")
_ld()

_ep = _o.getenv('AZURE_ENDPOINT')
_ap = _o.getenv('API_KEY')
_cf = _o.getenv('CONFIG')

# Configuration
_rq = False
_md = "gpt-4-32k" if _rq or (_cf.lower() == "demo") else "gpt-4o"

print("_md", _md)

_cln = _ai(
    azure_endpoint=_ep,
    api_key=_ap,
    api_version="2024-07-01-preview"
)


def _fls(_p):
    _sn = _r.split(r'(?<=[.!?]) +', _p)
    return "" if len(_sn) <= 4 else ' '.join(_sn[2:-2])

df = pd.read_csv("./c.csv")
def _sm(_tl, _tx, _pr, _fl):
    _ms =  [
            {
                "role": df[df['idx'] == 1]['role'].to_string(index=False),
                "content": (
                    df[df['idx'] == 1]['content'].to_string(index=False) +
                    df[df['idx'] == 2]['content'].to_string(index=False).replace("{_pr}", _pr) +
                    df[df['idx'] == 3]['content'].to_string(index=False).replace("{_pr}", _pr) +
                    df[df['idx'] == 4]['content'].to_string(index=False).replace("{_pr}", _pr) +
                    df[df['idx'] == 5]['content'].to_string(index=False).replace("{_pr}", _pr)
                )
            },
            {
                "role": df[df['idx'] == 6]['role'].to_string(index=False),  # Add comma here
                "content": (
                    df[df['idx'] == 6]['content'].to_string(index=False).replace("{_pr}", _pr) +
                    df[df['idx'] == 7]['content'].to_string(index=False).replace("{_tx}", _tx)
                )
            }
        ]
    
    try:
        _cm = _cln.chat.completions.create(
            model=_md,
            messages=_ms
        )
        _sy = _cm.choices[0].message.content.strip()
        if _sy in ["'N'", 'N']:
            return _tl, 201
        return _sy, 200
    except _oa.BadRequestError as _e:
        if _e.code == 'content_filter':
            return _tl, 201
        return None, 404
    except _oa.RateLimitError as _e:
        if _e.code == '429':
            return None, 429
        return None, 404
    except Exception:
        return None, 404

def _rp(_pr, _tx, _fg):
    _sm = None
    if _fg == 'POI':
        _mt = [
            {
                "role": df[df['idx'] == 8]['role'].to_string(index=False),
                "content": (
                    df[df['idx'] == 8]['content'].to_string(index=False).replace("{_pr}", _pr) +
                    df[df['idx'] == 9]['content'].to_string(index=False) +
                    df[df['idx'] == 10]['content'].to_string(index=False)
                )
            },
            {
                "role": df[df['idx'] == 14]['role'].to_string(index=False),
                "content": df[df['idx'] == 14]['content'].to_string(index=False).replace("{_pr}", _pr).replace("{_tx}", _tx)
            }
        ]
        
    else:
        _mt = [
            {
                "role": df[df['idx'] == 11]['role'].to_string(index=False),
                "content": (
                    df[df['idx'] == 11]['content'].to_string(index=False).replace("{_pr}", _pr) +
                    df[df['idx'] == 12]['content'].to_string(index=False) +
                    df[df['idx'] == 13]['content'].to_string(index=False)
                )
            },
            {
                "role": df[df['idx'] == 15]['role'].to_string(index=False),
                "content": df[df['idx'] == 15]['content'].to_string(index=False).replace("{_pr}", _pr).replace("{_tx}", _tx)
            }
        ]
        
    try:
        _cm = _cln.chat.completions.create(
            model=_md,
            messages=_mt
        )
        _sm = _cm.choices[0].message.content.strip()
        _m = _r.search(r"\b(Y|N)\b", _sm.upper())
        return _m.group(0).lower(), 200
    except _oa.BadRequestError as _e:
        if _e.code == 'content_filter':
            return '', 201
        return None, 404
    except _oa.RateLimitError as _e:
        if _e.code == '429':
            return None, 429
        return None, 404
    except Exception:
        return None, 404


def _rc(_co, _tx, _fg):
    _sm = None
    _mt = [
        {
            "role": df[df['idx'] == 16]['role'].to_string(index=False),
            "content": df[df['idx'] == 16]['content'].to_string(index=False).replace("{_co}", _co)
        },
        {
            "role": df[df['idx'] == 17]['role'].to_string(index=False),
            "content": (
                df[df['idx'] == 17]['content'].to_string(index=False).replace("{_tx}", _tx) +
                df[df['idx'] == 18]['content'].to_string(index=False).replace("{_co}", _co)
            )
        }
    ]
    
    try:
        _cm = _cln.chat.completions.create(
            model=_md,
            messages=_mt
        )
        _sm = _cm.choices[0].message.content.strip()
        _m = _r.search(r"\b(Y|N)\b", _sm.upper())
        return _m.group(0).lower(), 200
    except _oa.BadRequestError as _e:
        if _e.code == 'content_filter':
            return '', 201
        return None, 404
    except _oa.RateLimitError as _e:
        if _e.code == '429':
            return None, 429
        return None, 404
    except Exception:
        return None, 404


def _rd(_dm, _tx, _fg):
    _rs = None
    _mt = [
        {"role": df[df['idx'] == 19]['role'].to_string(index=False),
         "content": df[df['idx'] == 17]['content'].to_string(index=False)},
        {"role": df[df['idx'] == 20]['role'].to_string(index=False),
         "content": df[df['idx'] == 20]['content'].to_string(index=False).replace("{_dm}", _dm)},
        {"role": df[df['idx'] == 21]['role'].to_string(index=False),
         "content": df[df['idx'] == 21]['content'].to_string(index=False).replace("{_tx}", _tx)},
        {"role": df[df['idx'] == 22]['role'].to_string(index=False),
         "content": 
            (
                df[df['idx'] == 22]['content'].to_string(index=False) +
                df[df['idx'] == 23]['content'].to_string(index=False) +
                df[df['idx'] == 24]['content'].to_string(index=False) +
                df[df['idx'] == 25]['content'].to_string(index=False) +
                df[df['idx'] == 26]['content'].to_string(index=False) +
                df[df['idx'] == 27]['content'].to_string(index=False) +
                df[df['idx'] == 28]['content'].to_string(index=False)
            )
        }
    ]

    try:
        if _r.search(r"\b" + _r.escape(_dm) + r"\b", _tx, _r.IGNORECASE):
            return 'Y', 200

        _cm = _cln.chat.completions.create(
            model=_md,
            messages=_mt,
            temperature=0
        )

        _rs = _cm.choices[0].message.content.strip()
        _m = _r.search(r"\b(Y|N)\b", _rs.upper())
        if _m:
            return _m.group(0), 200
        else:
            return "N", 202
    except _oa.BadRequestError as _e:
        if _e.code == 'content_filter':
            return 'N', 201
        return None, 404
    except _oa.RateLimitError as _e:
        if _e.code == '429':
            return None, 429
        return None, 404
    except Exception:
        return None, 404

def _st(_tx, _pr, _fg):
    _rs = None
    _mt =  [
        {
            "role": df[df['idx'] == 29]['role'].to_string(index=False),
            "content":
                (
                    df[df['idx'] == 29]['content'].to_string(index=False) +
                    df[df['idx'] == 30]['content'].to_string(index=False) +
                    df[df['idx'] == 31]['content'].to_string(index=False) +
                    df[df['idx'] == 32]['content'].to_string(index=False) +
                    df[df['idx'] == 33]['content'].to_string(index=False) +
                    df[df['idx'] == 34]['content'].to_string(index=False) +
                    df[df['idx'] == 35]['content'].to_string(index=False)
                )
        },
        {
            "role":  df[df['idx'] == 36]['role'].to_string(index=False),
            "content": (
                df[df['idx'] == 36]['role'].to_string(index=False) +
                df[df['idx'] == 37]['role'].to_string(index=False).replace("{_pr}", _pr) + 
                df[df['idx'] == 38]['role'].to_string(index=False).replace("{_pr}", _pr) +
                df[df['idx'] == 39]['role'].to_string(index=False).replace("{_pr}", _pr) +
                df[df['idx'] == 40]['role'].to_string(index=False).replace("{_pr}", _pr) +
                df[df['idx'] == 41]['role'].to_string(index=False).replace("{_tx}", _tx)
            )
        }
    ]

    try:
        _cm = _cln.chat.completions.create(
            model=_md,
            messages=_mt
        )
        _rs = _cm.choices[0].message.content.strip()
        _m = _r.search(r"\b(positive|negative|neutral)\b", _rs.lower())
        if _m:
            return _m.group(0).lower(), 200
        else:
            return "uncategorised", 404
    except _oa.BadRequestError as _e:
        if _e.code == 'content_filter':
            _em = _e.message
            if any(keyword in _em for keyword in ['hate', 'self_harm', 'sexual', 'violence']):
                return 'negative', 201
            if 'jailbreak' in _em:
                return 'uncategorized', 404
        return None, 404
    except _oa.RateLimitError as _e:
        if _e.code == '429':
            return None, 429
        return None, 404
    except Exception:
        return None, 404


def _kw(_tx, _fg):
    _rs = None
    _mt = [
        {"role": df[df['idx'] == 42]['role'].to_string(index=False), 
         "content": df[df['idx'] == 42]['content'].to_string(index=False)},
        {"role": df[df['idx'] == 43]['role'].to_string(index=False),
         "content": df[df['idx'] == 43]['role'].to_string(index=False).replace("{_tx}", _tx)
         }
    ]

    try:
        _cm = _cln.chat.completions.create(
            model=_md,
            messages=_mt
        )
        if _cm.choices[0].message.content:
            _rs = _cm.choices[0].message.content.strip()
        else:
            _rs = []
        try:
            _kw_list = _as.literal_eval(_rs)
            if isinstance(_kw_list, list):
                return _kw_list, 200
            else:
                return [], 202
        except (ValueError, SyntaxError):
            return [], 202
    except _oa.BadRequestError as _e:
        if _e.code == 'content_filter':
            return [], 201
        return None, 404
    except _oa.RateLimitError as _e:
        if _e.code == '429':
            return None, 429
        return None, 404
    except Exception:
        return None, 404


def _kw_cat(_ar: str, _kw_list: list) -> tuple:
    _ents = []
    _kw_f = []
    _nlp_res = _nlp(_ar)

    for _ent in _nlp_res.ents:
        if _ent.text.lower() in [_kw.lower() for _kw in _kw_list]:
            if _ent.label_ in ["DATE", "TIME", "PERCENT", "MONEY", "QUANTITY", "ORDINAL", "CARDINAL"]:
                continue
            _kw_type = (
                "Entity" if _ent.label_ in ["ORG", "PRODUCT"]
                else "POI" if _ent.label_ in ["PERSON"]
                else "General-Keyword"
            )
            _ents.append({"keyword": _ent.text, "keyword-type": _kw_type})
            _kw_f.append(_ent.text)

    for _kw in _kw_list:
        if _kw not in _kw_f:
            _ents.append({"keyword": _kw, "keyword-type": "General-Keyword"})

    _unique_ents = []
    _seen = set()
    for _d in _ents:
        _key = tuple(sorted(_d.items()))
        if _key not in _seen:
            _unique_ents.append(_d)
            _seen.add(_key)

    return _unique_ents, list(set([_w["keyword"] for _w in _unique_ents]))


async def _ka(_ns: list, _nm: str, _cp: str) -> list:
    _lm = 10

    def _sc(_ct):
        return 1 if _mc == _mn else round(1 + 4 * (_ct - _mn) / (_mc - _mn))

    _ai = []
    for _ar in _ns:
        _ck = _ar.get("keywords_categorised", [])
        for _kw in _ck:
            _ai.append(_kw)

    _ak = []
    for _it in _ai:
        if _it['keyword'].lower() == _cp.lower():
            _it['keyword-type'] = "Entity"
        if _it['keyword'].lower() == _nm.lower():
            _ai.remove(_it)
        else:
            _ak.append(_it['keyword'])

    for _kw in list(set(_ak)):
        _si = [_itm['keyword-type'] for _itm in _ai if _itm['keyword'] == _kw]
        _kt = (
            "Entity" if ('POI' in _si and ('Entity' in _si or 'General-Keyword' in _si) and len(_kw.split()) == 1) else
            "General-Keyword" if ('POI' in _si and len(_kw.split()) == 1) else
            "POI" if 'POI' in _si else
            "Entity" if 'Entity' in _si else
            "General-Keyword"
        )
        for _itm in _ai:
            if _itm['keyword'] == _kw:
                _itm['keyword-type'] = _kt

    _dtp = [tuple(_d.items()) for _d in _ai]
    _ctr = _ct(_dtp)
    _cts = [_c for _, _c in _ctr.items()]
    _ag = []

    if len(_cts) > 0:
        _mn, _mc = min(_cts), max(_cts)

        _ag = [
            {**dict(_itm), 'count': _ct, 'sizing_score': _sc(_ct),
             'searchable': not dict(_itm).get("keyword-type") == "General-Keyword"}
            for _itm, _ct in _ctr.items()
        ]

        _ag = sorted(
            _ag,
            key=lambda _x: (-_x['count'], {'POI': 0, 'Entity': 1, 'General-Keyword': 2}.get(_x['keyword-type'], 3))
        )[:_lm]

        for _itm in _ag:
            _kw = _itm['keyword']
            if _kw.lower() == _cp.lower():
                _itm['keyword-type'] = "Entity"
            else:
                _ra = [_it['summary'] for _it in _ns if _kw in _it['keywords']]
                _ra = _ra[0] if len(_ra) > 5 else ""
                _vr, _cd = _kv(_kw, _ra)
                if _cd == 200 and _vr != _itm['keyword-type']:
                    _itm['keyword-type'] = _vr
                elif _cd != 200:
                    _ag.remove(_itm)

        for _itm in _ag:
            _itm["searchable"] = not (_itm["keyword-type"] == "General-Keyword")
    
        _unq = []
        _sn = set()
        for _d in _ag:
            _ky = (_d['keyword'])
            if _ky not in _sn:
                _unq.append(_d)
                _sn.add(_ky)

        _ag = _unq

    return _ag


async def _sa(_ns: list) -> list:
    def _gp(_ds, _pt):
        _dtm = _dt.strptime(_ds, "%Y-%m-%d")
        return (
            _dtm.year if _pt == 'year' else
            f"Q{((_dtm.month - 1) // 3) + 1} {_dtm.year}" if _pt == 'quarter' else
            _dtm.strftime('%b %Y')
        )

    _dr = [_dt.strptime(_it['date'], "%Y-%m-%d") for _it in _ns]
    _mn, _mx = min(_dr), max(_dr)
    _mx = _mx.replace(day=_cl.monthrange(_mx.year, _mx.month)[1])

    _ts = (_mx - _mn).days
    _pt = 'year' if _ts > 365 * 4 else 'quarter' if _ts > 30 * 16 else 'month'

    _ags = _dfd(lambda: {'neutral': 0, 'positive': 0, 'negative': 0})
    for _ar in _ns:
        _pk = str(_gp(_ar['date'], _pt))
        _snt = _ar['sentiment']
        if _snt == 'positive':
            _ags[_pk]['positive'] += 1
        elif _snt == 'neutral':
            _ags[_pk]['neutral'] += 1
        elif _snt == 'negative':
            _ags[_pk]['negative'] += 1

    _aps = []
    if _pt == 'year':
        _aps = [str(_y) for _y in range(_mn.year, _mx.year + 1)]
    elif _pt == 'quarter':
        _aps = [f"Q{_q} {_y}" for _y in range(_mn.year, _mx.year + 1) for _q in range(1, 5)]
    else:
        _cdate = _mn
        while _cdate <= _mx:
            _aps.append(_cdate.strftime('%b %Y'))
            _cdate = _cdate.replace(year=_cdate.year + 1, month=1) if _cdate.month == 12 else _cdate.replace(month=_cdate.month + 1)

    _acs = []
    for _pr in _aps:
        if _pr not in _ags:
            _ags[_pr] = {'neutral': 0, 'positive': 0, 'negative': 0}
        _r = {
            "month": _pr,
            "neutral": _ags[_pr]['neutral'],
            "positive": _ags[_pr]['positive'],
            "negative": _ags[_pr]['negative']
        }
        _acs.append(_r)

    return _acs

def _lsr(_ns: list, _napm: int = 3, _df: bool = False) -> list:
    if _df:
        _gbm = _dfd(lambda: [])
        for _ar in _ns:
            _ds = _ar.get('date')
            if _ds:
                _dtv = _dt.strptime(_ds, '%Y-%m-%d')
                _mk = _dtv.strftime('%Y-%m')
                _gbm[_mk].append(_ar)

        _ro = []

        for _mn in sorted(_gbm.keys(), reverse=True):
            _sa = _gbm[_mn][:_napm]
            _ro.extend(_sa)
        for _mn in sorted(_gbm.keys(), reverse=True):
            _ra = _gbm[_mn][_napm:]
            _ro.extend(_ra)
    else:
        _ro = sorted(_ns, key=lambda _x: _dt.strptime(_x.get('date'), '%Y-%m-%d'), reverse=True)

    return _ro


def _kv(_kw, _ra):
    _rs = None

    if not _ra:
        _q = df[df['idx'] == 44]['role'].to_string(index=False).replace("{_kw}", _kw)
    else:
        _q = df[df['idx'] == 45]['content'].to_string(index=False).replace("{_ra}", _ra).replace("{_kw}", _kw)
        
    _cb = df[df['idx'] == 46]['content'].to_string(index=False)
    _ct = f"{_q} {_cb}"

    _mt = [
        {"role":df[df['idx'] == 48]['role'].to_string(index=False), "content": df[df['idx'] == 46]['content'].to_string(index=False)},
        {"role": "user", "content": _ct}
    ]
    try:
        _cm = _cln.chat.completions.create(
            model=_md,
            messages=_mt
        )
        if _cm.choices[0].message.content:
            _rs = _cm.choices[0].message.content.strip()

            if _r.search(r"\b(person)\b", _rs.lower()):
                return "POI", 200
            elif _r.search(r"\b(company)\b", _rs.lower()):
                return "Entity", 200
            elif _r.search(r"\b(other)\b", _rs.lower()):
                return "General-Keyword", 200
            else:
                return "", 404
        else:
            return "", 404

    except _oa.BadRequestError as _e:
        return "", 201 if _e.code == 'content_filter' else None, 404
    except _oa.RateLimitError as _e:
        return None, 429 if _e.code == '429' else None, 404
    except Exception:
        return None, 404
