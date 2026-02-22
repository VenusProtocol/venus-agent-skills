# Quick Commands

## 1) Check USDT market now
```bash
python scripts/venus_check.py --symbol vUSDT
```

## 2) Auto-read wallet exposure onchain (no manual numbers)
```bash
python scripts/venus_check.py \
  --symbol vUSDT \
  --wallet 0xYourWallet
```

## 3) Auto-read wallet + what-if borrow simulation
```bash
python scripts/venus_check.py \
  --symbol vUSDT \
  --wallet 0xYourWallet \
  --extra-borrow 120 \
  --target-health 1.30
```

## 4) Manual mode (fallback)
```bash
python scripts/venus_check.py \
  --symbol vUSDT \
  --wallet 0xYourWallet \
  --weighted-collateral 1500 \
  --debt 1000
```

## 5) English brief output (Telegram-friendly)
```bash
python scripts/venus_check.py --symbol vUSDT --wallet 0xYourWallet --output brief --lang en
```

## Notes
- Auto mode reads onchain balances via `getAccountSnapshot`.
- Manual mode expects USD values for `weighted-collateral` and `debt`.
- BNB Chain mainnet uses `--chain-id 56` (default).
- `--output brief --lang en` returns concise English summary lines.
