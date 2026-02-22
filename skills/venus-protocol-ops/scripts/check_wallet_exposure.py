#!/usr/bin/env python3
import argparse
import json
import urllib.request


def fetch_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "venus-skill/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    p = argparse.ArgumentParser(description="Fetch wallet exposure snapshot")
    p.add_argument("--api-url", required=True, help="Base API URL")
    p.add_argument("--wallet", required=True, help="Wallet address")
    args = p.parse_args()

    url = args.api_url.rstrip("/") + f"/wallet/{args.wallet}"
    data = fetch_json(url)
    out = {
        "wallet": args.wallet,
        "source": url,
        "collateral_usd": data.get("collateral_usd"),
        "weighted_collateral_usd": data.get("weighted_collateral_usd"),
        "debt_usd": data.get("debt_usd"),
        "health": data.get("health"),
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
