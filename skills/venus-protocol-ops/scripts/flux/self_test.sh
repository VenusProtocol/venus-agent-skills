#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
WALLET="${1:-0xF54A4Ff2d00c45F07eBA4949F2B266554F3fE3bF}"

echo "[1/4] fetch_markets"
node "$ROOT/fetch_markets.js" >/tmp/flux_markets_test.json

echo "[2/4] position"
node "$ROOT/position.js" --wallet "$WALLET" >/tmp/flux_position_test.json

echo "[3/4] lend simulate"
node "$ROOT/lend.js" --asset fUSDC --amount 0.01 --wallet "$WALLET" --mode simulate >/tmp/flux_lend_sim_test.json

echo "[4/4] withdraw simulate"
node "$ROOT/withdraw.js" --asset fUSDC --amount 0.01 --wallet "$WALLET" --mode simulate >/tmp/flux_withdraw_sim_test.json

echo "Flux self-test passed"
