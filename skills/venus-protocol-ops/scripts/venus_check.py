#!/usr/bin/env python3
"""One-command Venus check.

Features:
- Fetch live market data (BNB chain by default)
- Optional symbol-specific output
- Optional wallet risk estimate (manual weighted collateral + debt)
- Optional what-if borrow simulation
"""
import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run_py(script: str, args: list[str]) -> str:
    cmd = ["python3", str(ROOT / script), *args]
    out = subprocess.check_output(cmd, text=True)
    return out.strip()


def main():
    p = argparse.ArgumentParser(description="One-command Venus checker")
    p.add_argument("--chain-id", type=int, default=56)
    p.add_argument("--symbol", default="vUSDT", help="Market symbol, e.g. vUSDT")

    # Optional wallet/risk inputs
    p.add_argument("--wallet", default=None)
    p.add_argument("--weighted-collateral", type=float, default=None)
    p.add_argument("--debt", type=float, default=None)
    p.add_argument("--rpc-url", default="https://bsc-dataseed.binance.org/")
    p.add_argument("--onchain-limit", type=int, default=120, help="Max markets scanned for onchain wallet mode")

    # Optional what-if
    p.add_argument("--extra-borrow", type=float, default=None)
    p.add_argument("--target-health", type=float, default=1.30)
    args = p.parse_args()

    market_raw = run_py("fetch_markets.py", ["--chain-id", str(args.chain_id), "--limit", "200", "--symbol", args.symbol])
    market = json.loads(market_raw)

    report = {
        "market": (market.get("markets") or [None])[0],
        "wallet": None,
        "simulation": None,
    }

    # Mode 1: onchain auto wallet read
    if args.wallet and args.weighted_collateral is None and args.debt is None:
        wallet_raw = run_py(
            "wallet_onchain_exposure.py",
            [
                "--wallet", args.wallet,
                "--chain-id", str(args.chain_id),
                "--rpc-url", args.rpc_url,
                "--scan-limit", str(args.onchain_limit),
            ],
        )
        wallet_obj = json.loads(wallet_raw)
        report["wallet"] = wallet_obj

        if args.extra_borrow is not None:
            wc = wallet_obj["summary"]["weightedCollateralUsd"]
            debt = wallet_obj["summary"]["totalBorrowUsd"]
            sim_raw = run_py(
                "simulate_borrow.py",
                [
                    "--weighted-collateral", str(wc),
                    "--current-debt", str(debt),
                    "--extra-borrow", str(args.extra_borrow),
                    "--target-health", str(args.target_health),
                ],
            )
            report["simulation"] = sim_raw

    # Mode 2: manual wallet exposure inputs
    elif args.weighted_collateral is not None and args.debt is not None:
        wallet_raw = run_py(
            "check_wallet_exposure.py",
            [
                "--wallet", args.wallet or "unknown",
                "--weighted-collateral", str(args.weighted_collateral),
                "--debt", str(args.debt),
            ],
        )
        report["wallet"] = json.loads(wallet_raw)

        if args.extra_borrow is not None:
            sim_raw = run_py(
                "simulate_borrow.py",
                [
                    "--weighted-collateral", str(args.weighted_collateral),
                    "--current-debt", str(args.debt),
                    "--extra-borrow", str(args.extra_borrow),
                    "--target-health", str(args.target_health),
                ],
            )
            report["simulation"] = sim_raw

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
