#!/usr/bin/env python3
"""Read Venus wallet exposure from chain via vToken getAccountSnapshot.

No private key required. Read-only JSON-RPC calls.
"""
import argparse
import json
import urllib.parse
import urllib.request
from decimal import Decimal, getcontext

getcontext().prec = 50

DEFAULT_API = "https://api.venus.io"
DEFAULT_RPC = "https://bsc-dataseed.binance.org/"

SEL_GET_ACCOUNT_SNAPSHOT = "c37f68e2"  # getAccountSnapshot(address)


def api_get(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "venus-skill/1.2"})
    with urllib.request.urlopen(req, timeout=12) as r:
        return json.loads(r.read().decode("utf-8"))


def rpc_call(rpc_url: str, to: str, data: str):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_call",
        "params": [{"to": to, "data": data}, "latest"],
    }
    req = urllib.request.Request(
        rpc_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=8) as r:
        out = json.loads(r.read().decode("utf-8"))
    if "error" in out:
        raise RuntimeError(out["error"])
    return out.get("result", "0x")


def pad_addr(addr: str) -> str:
    return addr.lower().replace("0x", "").rjust(64, "0")


def decode_uint256_words(hexdata: str):
    raw = hexdata[2:] if hexdata.startswith("0x") else hexdata
    if len(raw) % 64 != 0:
        return []
    return [int(raw[i : i + 64], 16) for i in range(0, len(raw), 64)]


def classify(health: Decimal) -> str:
    if health < Decimal("1.15"):
        return "HIGH"
    if health < Decimal("1.35"):
        return "MEDIUM"
    return "LOW"


def main():
    p = argparse.ArgumentParser(description="Onchain Venus wallet exposure")
    p.add_argument("--wallet", required=True)
    p.add_argument("--chain-id", type=int, default=56)
    p.add_argument("--api-base", default=DEFAULT_API)
    p.add_argument("--rpc-url", default=DEFAULT_RPC)
    p.add_argument("--limit", type=int, default=300)
    args = p.parse_args()

    wallet = args.wallet
    markets_url = (
        args.api_base.rstrip("/")
        + "/markets?"
        + urllib.parse.urlencode({"chainId": args.chain_id, "limit": args.limit, "page": 0})
    )
    markets_resp = api_get(markets_url)
    markets = markets_resp.get("result", [])

    positions = []
    total_supply_usd = Decimal("0")
    total_borrow_usd = Decimal("0")
    weighted_collateral_usd = Decimal("0")

    for m in markets:
        vtoken = m.get("address")
        if not vtoken:
            continue

        call_data = "0x" + SEL_GET_ACCOUNT_SNAPSHOT + pad_addr(wallet)
        try:
            ret = rpc_call(args.rpc_url, vtoken, call_data)
        except Exception:
            continue

        words = decode_uint256_words(ret)
        if len(words) < 4:
            continue

        err, token_balance, borrow_balance, exchange_rate = words[:4]
        if err != 0:
            continue

        # Skip empty markets for this wallet
        if token_balance == 0 and borrow_balance == 0:
            continue

        underlying_decimals = int(m.get("underlyingDecimal") or 18)
        price_usd = Decimal(str(float(m.get("tokenPriceCents", 0.0)) / 100.0))

        supplied_underlying = (
            Decimal(token_balance) * Decimal(exchange_rate) / (Decimal(10) ** 18) / (Decimal(10) ** underlying_decimals)
        )
        borrowed_underlying = Decimal(borrow_balance) / (Decimal(10) ** underlying_decimals)

        supply_usd = supplied_underlying * price_usd
        borrow_usd = borrowed_underlying * price_usd

        cf = Decimal(str(float(m.get("collateralFactorMantissa", 0.0)))) / (Decimal(10) ** 18)
        lt = Decimal(str(float(m.get("liquidationThresholdMantissa", 0.0)))) / (Decimal(10) ** 18)
        weight = lt if lt > 0 else cf

        weighted_collateral_usd += supply_usd * weight
        total_supply_usd += supply_usd
        total_borrow_usd += borrow_usd

        positions.append(
            {
                "symbol": m.get("symbol") or m.get("underlyingSymbol"),
                "vToken": vtoken,
                "suppliedUnderlying": float(round(supplied_underlying, 10)),
                "borrowedUnderlying": float(round(borrowed_underlying, 10)),
                "priceUsd": float(round(price_usd, 8)),
                "supplyUsd": float(round(supply_usd, 6)),
                "borrowUsd": float(round(borrow_usd, 6)),
                "collateralFactor": float(cf),
                "liquidationThreshold": float(lt),
            }
        )

    health = Decimal("Infinity") if total_borrow_usd == 0 else (weighted_collateral_usd / total_borrow_usd)

    out = {
        "wallet": wallet,
        "chainId": args.chain_id,
        "source": {
            "markets": markets_url,
            "rpc": args.rpc_url,
        },
        "summary": {
            "totalSupplyUsd": float(round(total_supply_usd, 6)),
            "totalBorrowUsd": float(round(total_borrow_usd, 6)),
            "weightedCollateralUsd": float(round(weighted_collateral_usd, 6)),
            "health": ("inf" if health.is_infinite() else float(round(health, 6))),
            "risk": ("LOW" if health.is_infinite() else classify(health)),
            "notes": [
                "Onchain balances via getAccountSnapshot",
                "Weighted collateral uses liquidationThreshold when available, else collateralFactor",
            ],
        },
        "positions": positions,
    }

    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
