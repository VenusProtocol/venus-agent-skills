# Venus Agent Skills (Venus Core + Flux)

Risk-first DeFi operations toolkit on BNB Chain for OpenClaw.

This repository provides a production-oriented skill with **dual protocol support**:
- **Venus Core Pool** operations and risk checks
- **Flux (Fluid on BSC)** market/position/lend/withdraw workflows

---

## Skill Location

- `skills/venus-protocol-ops/`

## Packaged Artifact

- `dist/venus-protocol-ops.skill`

---

## What the Skill Can Do

### Venus (Core default)
- Live market snapshot and ranking
- Onchain wallet exposure (supply/borrow/HF)
- Borrow what-if simulation
- Safe execution flows: deposit / withdraw / borrow / repay
- Collateral enable/disable
- HF monitoring

### Flux (Fluid on BSC)
- Market snapshot
- Wallet position query
- Lend (simulate / broadcast)
- Withdraw (simulate / broadcast)
- Input/signer safety checks for broadcast

---

## Core Scripts

### Venus scripts
- `skills/venus-protocol-ops/scripts/fetch_markets.py`
- `skills/venus-protocol-ops/scripts/wallet_onchain_exposure.py`
- `skills/venus-protocol-ops/scripts/venus_check.py`
- `skills/venus-protocol-ops/scripts/venus_deposit.js`
- `skills/venus-protocol-ops/scripts/venus_withdraw.js`
- `skills/venus-protocol-ops/scripts/venus_borrow.js`
- `skills/venus-protocol-ops/scripts/venus_repay.js`
- `skills/venus-protocol-ops/scripts/venus_collateral.js`
- `skills/venus-protocol-ops/scripts/hf_monitor.py`

### Flux scripts
- `skills/venus-protocol-ops/scripts/flux/fetch_markets.js`
- `skills/venus-protocol-ops/scripts/flux/position.js`
- `skills/venus-protocol-ops/scripts/flux/lend.js`
- `skills/venus-protocol-ops/scripts/flux/withdraw.js`
- `skills/venus-protocol-ops/scripts/flux/self_test.sh`
- `skills/venus-protocol-ops/scripts/flux/README.md`

---

## Safety Defaults

- Execution defaults to `--mode simulate`
- Broadcast requires explicit `--confirm YES`
- Flux broadcast enforces signer-wallet address match
- Risk-first guidance; no guaranteed return claims

---

## Quick Start

### 1) Install dependencies (workspace root)

```bash
cd ~/.openclaw/workspace
npm install
```

### 2) Verify Venus (read-only)

```bash
python skills/venus-protocol-ops/scripts/fetch_markets.py --chain-id 56 --limit 20
python skills/venus-protocol-ops/scripts/wallet_onchain_exposure.py --wallet 0xYourWallet
```

### 3) Verify Flux (read-only)

```bash
node skills/venus-protocol-ops/scripts/flux/fetch_markets.js
node skills/venus-protocol-ops/scripts/flux/position.js --wallet 0xYourWallet
```

### 4) Verify Flux execution (simulate only)

```bash
node skills/venus-protocol-ops/scripts/flux/lend.js --asset fUSDC --amount 1 --wallet 0xYourWallet --mode simulate
node skills/venus-protocol-ops/scripts/flux/withdraw.js --asset fUSDC --amount 1 --wallet 0xYourWallet --mode simulate
```

### 5) Run Flux self-test

```bash
./skills/venus-protocol-ops/scripts/flux/self_test.sh 0xYourWallet
```

---

## Install in Another OpenClaw Workspace

### Option A: Copy skill folder
Copy `skills/venus-protocol-ops` into the target workspace `skills/` directory.

### Option B: Import packaged file
Import `dist/venus-protocol-ops.skill`.

---

## Runtime Notes

- Network: BNB Chain (`chainId=56`)
- Default RPC: `https://bsc-dataseed.binance.org/`
- Venus Market API: `https://api.venus.io`
- Keep secrets local (`.env` / `.environment`), never commit private keys
