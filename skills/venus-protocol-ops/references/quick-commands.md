# Quick Commands

## 1) Check USDT market now
```bash
python scripts/venus_check.py --symbol vUSDT
```

## 2) Check market + your current risk (manual exposure)
```bash
python scripts/venus_check.py \
  --symbol vUSDT \
  --wallet 0xYourWallet \
  --weighted-collateral 1500 \
  --debt 1000
```

## 3) What-if borrow simulation
```bash
python scripts/venus_check.py \
  --symbol vUSDT \
  --wallet 0xYourWallet \
  --weighted-collateral 1500 \
  --debt 1000 \
  --extra-borrow 120 \
  --target-health 1.30
```

## Notes
- `weighted-collateral` and `debt` are in USD.
- Until wallet position API is finalized, use manual values for reliable simulations.
- BNB Chain mainnet uses `--chain-id 56` (default).
