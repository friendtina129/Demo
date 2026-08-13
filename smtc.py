#!/usr/bin/env python3
"""
smtc.py — 抓取台積電（2330.TW）股價並可選擇存成 CSV

用法:
  python smtc.py
  python smtc.py --symbol 2330.TW --out prices.csv
  python smtc.py --json
"""
import urllib.request
import json
import datetime
import argparse
import os
import csv
import sys

def fetch_price(symbol='2330.TW', timeout=10):
    url = f'https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}'
    req = urllib.request.Request(url, headers={'User-Agent': 'python-urllib/3'})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.load(resp)

    res = data.get('quoteResponse', {}).get('result')
    if not res:
        raise RuntimeError(f'No quote found for {symbol}')
    r = res[0]
    price = r.get('regularMarketPrice')
    ts = r.get('regularMarketTime')
    currency = r.get('currency')
    dt = datetime.datetime.fromtimestamp(ts) if ts else datetime.datetime.utcnow()
    return {'symbol': r.get('symbol'), 'price': price, 'currency': currency, 'time': dt.isoformat()}

def append_csv(path, row, headers=('symbol','price','currency','time')):
    exists = os.path.exists(path)
    with open(path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if not exists:
            writer.writeheader()
        writer.writerow(row)

def main():
    p = argparse.ArgumentParser(description='Fetch TSMC (2330.TW) price from Yahoo Finance')
    p.add_argument('--symbol', default='2330.TW', help='Ticker symbol (default: 2330.TW)')
    p.add_argument('--out', help='Append result to CSV file')
    p.add_argument('--json', action='store_true', help='Print JSON output')
    args = p.parse_args()

    try:
        info = fetch_price(args.symbol)
    except Exception as e:
        print('Error fetching price:', e, file=sys.stderr)
        sys.exit(1)

    if args.out:
        append_csv(args.out, info)
        print(f"Wrote {info['price']} to {args.out}")
    elif args.json:
        print(json.dumps(info, ensure_ascii=False, indent=2))
    else:
        print(f"{info['symbol']} {info['price']} {info['currency']} at {info['time']}")

if __name__ == '__main__':
    main()
