#!/usr/bin/env python3
import argparse
import json
import urllib.request


def fetch_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "venus-skill/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    p = argparse.ArgumentParser(description="Fetch Venus market snapshot from API endpoint")
    p.add_argument("--api-url", required=True, help="Endpoint returning market list JSON")
    args = p.parse_args()

    data = fetch_json(args.api_url)

    # Keep output schema stable for downstream scripts/use.
    out = {
        "source": args.api_url,
        "markets": data.get("markets", data),
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
