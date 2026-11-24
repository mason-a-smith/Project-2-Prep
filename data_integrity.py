"""Fail-closed frozen data and committee-artifact checks; no network refresh."""
import csv
from datetime import datetime
import hashlib
from io import StringIO
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
MANIFEST_SHA256 = '5328aa7958c77a9603f3c7d97e8c5b7c04d81533c9b559739ef5bd13c1cc7c52'
TICKERS = ['SGOV','VGIT','VCIT','ACWI']


def parse_prices(data):
    """Validate original headers before pandas can rename duplicate columns."""
    text = data.decode('utf-8-sig') if isinstance(data,bytes) else data
    header = next(csv.reader(StringIO(text)),[])
    if (not 4<=len(header)<=7 or header[0].strip().lower()!='date' or
            any(not x.strip() or x!=x.strip() for x in header) or len(set(header))!=len(header)):
        raise ValueError('STOP: CSV requires date first and 3–6 unique, nonempty ticker columns.')
    frame = pd.read_csv(StringIO(text),index_col=0)
    dates = pd.to_datetime(frame.index,errors='raise')
    if dates.tz is not None or dates.isna().any() or not dates.is_monotonic_increasing or dates.to_period('M').has_duplicates:
        raise ValueError('STOP: unique timezone-free increasing monthly dates required.')
    if len(frame)<3 or not np.all(np.diff(dates.to_period('M').astype('int64'))==1):
        raise ValueError('STOP: consecutive monthly observations required; no filling allowed.')
    frame = frame.apply(pd.to_numeric,errors='raise')
    if not np.isfinite(frame.to_numpy()).all() or (frame<=0).any().any():
        raise ValueError('STOP: prices must be present, finite and positive.')
    frame.index = dates
    return frame


def verify(root=None, decision='2026-11-17T00:00:00+00:00'):
    root = Path(root) if root is not None else ROOT
    raw = (root/'integrity-manifest.json').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=MANIFEST_SHA256:
        raise ValueError('STOP: integrity manifest hash differs from the reviewed release.')
    manifest = json.loads(raw)
    for name,digest in manifest['sha256'].items():
        if hashlib.sha256((root/name).read_bytes()).hexdigest()!=digest:
            raise ValueError(f'STOP: source or frozen committee hash differs: {name}')
    metadata = json.loads((root/'data_sources.json').read_text(encoding='utf-8'))
    cutoff = datetime.fromisoformat(decision.replace('Z','+00:00'))
    downloaded = datetime.fromisoformat(metadata['downloaded_at_utc'].replace('Z','+00:00'))
    if cutoff.tzinfo is None or downloaded.tzinfo is None or cutoff<=downloaded:
        raise ValueError('STOP: decision must be timezone-aware and strictly after the recorded snapshot download.')
    prices = parse_prices((root/'prices.csv').read_bytes())
    if list(prices.columns)!=TICKERS or len(prices)!=61 or metadata['price_rows']!=61 or metadata['monthly_return_rows']!=60:
        raise ValueError('STOP: frozen universe or row counts disagree with provenance.')
    if metadata['provider']!='Yahoo Finance via yfinance' or metadata['field']!='Adj Close' or metadata['auto_adjust'] is not False:
        raise ValueError('STOP: adjusted-price source definition changed.')
    if [str(prices.index[0].date()),str(prices.index[-1].date())]!=['2021-09-30','2026-09-30']:
        raise ValueError('STOP: frozen date boundaries changed.')
    reconstructed = {}
    for ticker in TICKERS:
        if metadata['sources'][ticker]!=f'https://finance.yahoo.com/quote/{ticker}/history/':
            raise ValueError('STOP: source URL changed.')
        daily = pd.read_csv(root/f'evidence/lab 15/raw/{ticker}_daily.csv',parse_dates=['Date'])
        if daily.Date.isna().any() or daily.Date.duplicated().any() or not daily.Date.is_monotonic_increasing:
            raise ValueError('STOP: invalid raw daily dates.')
        if not np.isfinite(daily['Adj Close']).all() or (daily['Adj Close']<=0).any():
            raise ValueError('STOP: invalid raw adjusted closes.')
        if daily.Date.min()<pd.Timestamp(metadata['request_start_inclusive']) or daily.Date.max()>=pd.Timestamp(metadata['request_end_exclusive']):
            raise ValueError('STOP: raw data outside requested boundaries.')
        observed = daily.groupby(daily.Date.dt.to_period('M'),sort=True).tail(1)
        if not pd.DatetimeIndex(observed.Date).equals(prices.index):
            raise ValueError('STOP: last observed trading dates do not reproduce monthly dates.')
        if not np.allclose(observed['Adj Close'],prices[ticker],atol=1e-10,rtol=0):
            raise ValueError('STOP: raw adjusted closes do not reproduce monthly prices.')
        reconstructed[ticker] = len(observed)
    return {'status':'PASS','downloaded_at_utc':metadata['downloaded_at_utc'],
            'decision_cutoff':cutoff.isoformat(),'prices':prices,'reconstructed_rows':reconstructed,
            'verified_hashes':manifest['sha256'],
            'limitation':'Recorded retrieval timestamp and snapshot bytes verified locally, not independently authenticated provider timestamps or historical adjusted-price vintages.'}


def load_committee(root=None):
    root = Path(root) if root is not None else ROOT
    audit = verify(root)
    result = json.loads((root/'outputs/committee_snapshot.json').read_text(encoding='utf-8'))
    if result['sha256']['prices.csv']!=audit['verified_hashes']['prices.csv']:
        raise ValueError('STOP: committee result data hash mismatch.')
    return result
