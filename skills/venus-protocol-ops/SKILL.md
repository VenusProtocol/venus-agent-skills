---
name: venus-protocol-ops
description: Analyze Venus Protocol lending/borrowing positions on BNB Chain with risk-first guidance. Use when users ask about Venus markets, collateral/borrow decisions, health factor, liquidation risk, APY/utilization comparison, isolated pools, or "can I borrow X safely" style what-if checks.
---

# Venus Protocol Ops

## Overview
Use this skill to provide **read-only**, risk-aware analysis for Venus Protocol. Prioritize liquidation safety, clarity, and explicit uncertainty over aggressive yield-chasing.

## Workflow

### 1) Classify user intent
Map request into one of these modes:
- **Market scan**: compare assets/pools (supply APY, borrow APY, utilization, caps)
- **Position check**: assess a wallet's current collateral/borrow health
- **What-if simulation**: estimate risk after a proposed borrow/supply/repay
- **Execution planning**: prepare step-by-step actions without broadcasting tx

If user asks for onchain execution, pause and request explicit confirmation + exact parameters.

### 2) Collect data
Use scripts first:
- `scripts/fetch_markets.py` for market snapshot (official API base: `https://api.venus.io`)
- `scripts/check_wallet_exposure.py` for wallet summary (API mode or manual mode)
- `scripts/simulate_borrow.py` for hypothetical borrow impact

Example market query:
- `python scripts/fetch_markets.py --chain-id 56 --limit 200`

If API is unavailable, continue with transparent assumptions and mark output as estimate.

### 3) Run risk rules
Apply rules from `references/risk-rules.md`:
- Compute health and safety buffer
- Flag borrow-cap / liquidity constraints
- Detect concentration risk (single volatile collateral)
- Classify risk: Low / Medium / High

### 4) Produce actionable output
Always include:
1. **Current state** (key numbers)
2. **Risk status** (Low/Medium/High + why)
3. **Safe range** (max suggested extra borrow or required extra collateral)
4. **Next best actions** (2-4 concrete steps)

Prefer concise bullets and exact numbers.

## Output format
Use this structure:
- **Summary**: one-line verdict
- **Metrics**: collateral, debt, health, utilization, APYs
- **Risk findings**: top 2-4 risks
- **Recommended plan**: concrete steps and limits
- **Assumptions**: data freshness, missing fields, estimate flags

## Guardrails
- Never claim guaranteed safety or returns.
- Never hide data gaps; explicitly note stale/missing data.
- Default to conservative thresholds when uncertain.
- Treat this as educational/risk tooling, not financial advice.

## References
- Protocol overview: `references/protocol-overview.md`
- Risk thresholds and formulas: `references/risk-rules.md`
- Contract/address notes: `references/bnbchain-contracts.md`
- Terminology: `references/glossary.md`
