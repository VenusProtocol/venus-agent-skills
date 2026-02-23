# Venus Protocol Ops

Risk-first Venus Protocol operations toolkit on BNB Chain.

This repo contains an OpenClaw skill for:
- market analytics
- wallet exposure + health checks
- borrow what-if simulation
- safe execution flows for deposit / withdraw / borrow / repay
- collateral management (enable/disable)
- HF threshold monitoring

## Skill location

- `skills/venus-protocol-ops/`

## Packaged artifact

- `dist/venus-protocol-ops.skill`

## Core scripts

- `scripts/fetch_markets.py` — live market snapshot
- `scripts/wallet_onchain_exposure.py` — onchain wallet exposure
- `scripts/venus_check.py` — one-command market + wallet + simulation
- `scripts/venus_deposit.js` — deposit flow (simulate/broadcast)
- `scripts/venus_withdraw.js` — withdraw flow (simulate/broadcast)
- `scripts/venus_borrow.js` — borrow flow (simulate/broadcast)
- `scripts/venus_repay.js` — repay flow (simulate/broadcast)
- `scripts/venus_collateral.js` — collateral enable/disable
- `scripts/hf_monitor.py` — health-factor monitor

## Safety defaults

- Execution scripts default to `simulate`
- Real transactions require explicit `--confirm YES`
- Risk-first guidance; no guaranteed return claims

## Quick start

### 1) Check market + wallet (brief)

```bash
python skills/venus-protocol-ops/scripts/venus_check.py \
  --symbol vUSDC \
  --wallet 0xYourWallet \
  --output brief --lang en
```

### 2) Deposit preview

```bash
node skills/venus-protocol-ops/scripts/venus_deposit.js \
  --asset vUSDC --amount 10 --wallet 0xYourWallet --mode simulate
```

### 3) Withdraw preview

```bash
node skills/venus-protocol-ops/scripts/venus_withdraw.js \
  --asset vUSDC --amount 1 --wallet 0xYourWallet --mode simulate
```

## Install in another agent

### Option A: copy skill folder
Copy `skills/venus-protocol-ops` into another OpenClaw workspace `skills/` directory.

### Option B: use packaged file
Import `dist/venus-protocol-ops.skill`.

## Notes

- Network: BNB Chain (`chainId=56`)
- Default RPC: `https://bsc-dataseed.binance.org/`
- Market API: `https://api.venus.io`
