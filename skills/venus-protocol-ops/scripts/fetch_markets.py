#!/usr/bin/env python3
"""Fetch Venus markets from official API and output normalized risk-friendly fields."""
import argparse
import json
import math
import urllib.parse
import urllib.request

DEFAULT_BASE = "https://api.venus.io"


def fetch_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "venus-skill/1.1"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode("utf-8"))


def to_float(v, default=0.0):
    try:
        return float(v)
    except Exception:
        return default


def normalize_market(m: dict):
    supply = to_float(m.get("totalSupplyUnderlyingCents")) / 100.0
    borrows = to_float(m.get("totalBorrowCents")) / 100.0
    liquidity = to_float(m.get("liquidityCents")) / 100.0
    util = (borrows / supply) if supply > 0 else 0.0

    return {
        "symbol": m.get("symbol") or m.get("underlyingSymbol"),
        "marketAddress": m.get("address"),
        "poolComptroller": m.get("poolComptrollerAddress"),
        "isListed": m.get("isListed"),
        "isBorrowable": m.get("isBorrowable"),
        "canBeCollateral": m.get("canBeCollateral"),
        "supplyApy": to_float(m.get("supplyApy")),
        "borrowApy": to_float(m.get("borrowApy")),
        "totalSupplyUsd": round(supply, 2),
        "totalBorrowUsd": round(borrows, 2),
        "liquidityUsd": round(liquidity, 2),
        "utilization": round(util, 6),
        "collateralFactor": to_float(m.get("collateralFactorMantissa")),
        "liquidationThreshold": to_float(m.get("liquidationThresholdMantissa")),
        "borrowCap": to_float(m.get("borrowCapsMantissa")),
        "supplyCap": to_float(m.get("supplyCapsMantissa")),
        "priceInvalid": bool(m.get("isPriceInvalid")),
    }


def main():
    p = argparse.ArgumentParser(description="Fetch Venus market snapshot")
    p.add_argument("--base-url", default=DEFAULT_BASE)
    p.add_argument("--chain-id", type=int, default=56)
    p.add_argument("--limit", type=int, default=200)
    p.add_argument("--page", type=int, default=0)
    p.add_argument("--symbol", default=None, help="Optional market symbol filter")
    args = p.parse_args()

    query = {
        "chainId": args.chain_id,
        "limit": args.limit,
        "page": args.page,
    }
    if args.symbol:
        query["symbol"] = args.symbol

    url = args.base_url.rstrip("/") + "/markets?" + urllib.parse.urlencode(query)
    data = fetch_json(url)
    rows = [normalize_market(x) for x in data.get("result", [])]

    out = {
        "source": url,
        "total": data.get("total", len(rows)),
        "returned": len(rows),
        "markets": rows,
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
