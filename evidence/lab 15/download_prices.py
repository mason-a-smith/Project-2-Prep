"""Download Yahoo adjusted daily closes and retain actual last trading day each month."""
from pathlib import Path
from datetime import datetime, timezone
import json
import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parent
TICKERS = ['SGOV', 'VGIT', 'VCIT', 'ACWI']
# 61 month-end observations yield 60 returns, Oct 2021 through Sep 2026.
START, END = '2021-09-01', '2026-10-01'

def main():
    raw_dir = ROOT / 'raw'
    raw_dir.mkdir(exist_ok=True)
    monthly = {}
    actual_dates = {}
    for ticker in TICKERS:
        frame = yf.download(ticker, start=START, end=END, interval='1d',
                            auto_adjust=False, actions=True, progress=False, threads=False)
        if frame.empty:
            raise RuntimeError(f'Yahoo returned no data for {ticker}; no substitute prices created.')
        if isinstance(frame.columns, pd.MultiIndex):
            frame.columns = frame.columns.get_level_values(0)
        frame.to_csv(raw_dir / f'{ticker}_daily.csv', date_format='%Y-%m-%d')
        adjusted = frame['Adj Close'].dropna()
        adjusted.index = pd.to_datetime(adjusted.index).tz_localize(None)
        grouped = adjusted.groupby(adjusted.index.to_period('M'))
        monthly[ticker] = grouped.last()
        actual_dates[ticker] = grouped.apply(lambda s: s.index[-1].strftime('%Y-%m-%d'))
    prices = pd.DataFrame(monthly)
    expected = pd.period_range('2021-09', '2026-09', freq='M')
    if not prices.index.equals(expected) or prices.isna().any().any() or (prices <= 0).any().any():
        raise RuntimeError('Expected exactly 61 consecutive aligned month-end prices for every fund.')
    dates = pd.DataFrame(actual_dates)
    if not dates.eq(dates.iloc[:, 0], axis=0).all().all():
        raise RuntimeError('Month-end trading dates differ among funds.')
    prices.index = pd.to_datetime(dates.iloc[:, 0].values)
    prices.index.name = 'date'
    prices.to_csv(ROOT / 'prices.csv', float_format='%.12f', date_format='%Y-%m-%d')
    metadata = {
        'downloaded_at_utc': datetime.now(timezone.utc).isoformat(),
        'provider': 'Yahoo Finance via yfinance', 'yfinance_version': yf.__version__,
        'field': 'Adj Close', 'auto_adjust': False,
        'method': 'Last available daily adjusted close in each completed calendar month; no filling.',
        'request_start_inclusive': START, 'request_end_exclusive': END,
        'price_rows': len(prices), 'monthly_return_rows': len(prices) - 1,
        'sources': {t: f'https://finance.yahoo.com/quote/{t}/history/' for t in TICKERS},
    }
    (ROOT / 'data_sources.json').write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
    print(prices.iloc[[0, -1]].to_string())
    print(f'Saved {len(prices)} observed month-end prices; {len(prices)-1} monthly returns.')

if __name__ == '__main__':
    main()
