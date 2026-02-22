#!/usr/bin/env node
/**
 * Venus withdraw helper (BNB Chain).
 * Default mode is simulate (no tx broadcast).
 */
const { ethers } = require('ethers');

const API_BASE = 'https://api.venus.io';
const DEFAULT_RPC = 'https://bsc-dataseed.binance.org/';

const VTOKEN_ABI = [
  'function decimals() view returns (uint8)',
  'function symbol() view returns (string)',
  'function balanceOf(address) view returns (uint256)',
  'function exchangeRateStored() view returns (uint256)',
  'function redeem(uint256) returns (uint256)',
  'function redeemUnderlying(uint256) returns (uint256)'
];

const ERC20_ABI = [
  'function decimals() view returns (uint8)',
  'function symbol() view returns (string)',
  'function balanceOf(address) view returns (uint256)'
];

function parseArgs() {
  const args = process.argv.slice(2);
  const out = { mode: 'simulate', by: 'underlying', rpc: DEFAULT_RPC };
  for (let i = 0; i < args.length; i++) {
    const k = args[i];
    const v = args[i + 1];
    if (k === '--asset') out.asset = v;
    if (k === '--amount') out.amount = v;
    if (k === '--wallet') out.wallet = v;
    if (k === '--private-key') out.privateKey = v;
    if (k === '--rpc-url') out.rpc = v;
    if (k === '--mode') out.mode = v;
    if (k === '--by') out.by = v; // underlying | vtoken
    if (k === '--confirm') out.confirm = v;
    if (k.startsWith('--')) i++;
  }
  return out;
}

async function fetchMarket(assetSymbol) {
  const url = `${API_BASE}/markets?chainId=56&limit=200&symbol=${encodeURIComponent(assetSymbol)}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`market api failed: ${res.status}`);
  const data = await res.json();
  const m = (data.result || [])[0];
  if (!m) throw new Error(`market not found for symbol ${assetSymbol}`);
  return m;
}

async function main() {
  const a = parseArgs();
  if (!a.asset || !a.amount) {
    console.log('Usage: node venus_withdraw.js --asset vUSDC --amount 1 --wallet 0x... [--by underlying|vtoken] [--mode simulate|broadcast] [--private-key 0x...] [--confirm YES]');
    process.exit(1);
  }

  const provider = new ethers.JsonRpcProvider(a.rpc);
  const market = await fetchMarket(a.asset);
  const vTokenAddr = market.address;
  const underlyingAddr = market.underlyingAddress;

  const walletAddr = a.wallet || (a.privateKey ? new ethers.Wallet(a.privateKey).address : null);
  if (!walletAddr) throw new Error('wallet required (or provide --private-key)');

  const vToken = new ethers.Contract(vTokenAddr, VTOKEN_ABI, provider);
  const vBal = await vToken.balanceOf(walletAddr);
  const exRate = await vToken.exchangeRateStored(); // scaled by 1e18

  const erc20 = new ethers.Contract(underlyingAddr, ERC20_ABI, provider);
  const uDec = Number(await erc20.decimals());
  const uBalBefore = await erc20.balanceOf(walletAddr);

  const amountUnderlying = ethers.parseUnits(a.amount, uDec);
  const vDec = Number(await vToken.decimals());
  const amountVToken = ethers.parseUnits(a.amount, vDec);

  // rough convertible underlying from vToken balance
  const estUnderlyingFromV = (vBal * exRate) / (10n ** 18n);

  const out = {
    mode: a.mode,
    by: a.by,
    asset: a.asset,
    amountInput: a.amount,
    wallet: walletAddr,
    vToken: vTokenAddr,
    underlying: underlyingAddr,
    steps: [
      { action: 'check_vtoken_balance', vTokenBalance: vBal.toString() },
      { action: 'check_underlying_balance_before', underlyingBalance: uBalBefore.toString() },
      { action: 'check_exchange_rate', exchangeRateStored: exRate.toString() },
      { action: 'estimate_underlying_from_vtoken', estimatedUnderlyingRaw: estUnderlyingFromV.toString() }
    ]
  };

  if (a.mode === 'broadcast') {
    if (!a.privateKey) throw new Error('broadcast mode requires --private-key');
    if (a.confirm !== 'YES') throw new Error('broadcast mode requires --confirm YES');

    const signer = new ethers.Wallet(a.privateKey, provider);
    const v = new ethers.Contract(vTokenAddr, VTOKEN_ABI, signer);

    let tx;
    if ((a.by || 'underlying') === 'vtoken') {
      tx = await v.redeem(amountVToken);
      out.steps.push({ action: 'redeem_vtoken', amount: amountVToken.toString(), txHash: tx.hash });
    } else {
      tx = await v.redeemUnderlying(amountUnderlying);
      out.steps.push({ action: 'redeem_underlying', amount: amountUnderlying.toString(), txHash: tx.hash });
    }

    const rc = await tx.wait();
    out.steps.push({ action: 'confirm', status: rc.status, txHash: tx.hash });

    const uBalAfter = await erc20.balanceOf(walletAddr);
    out.steps.push({ action: 'check_underlying_balance_after', underlyingBalance: uBalAfter.toString() });
  } else {
    out.steps.push({ action: 'preview', note: 'No tx sent in simulate mode' });
  }

  console.log(JSON.stringify(out, null, 2));
}

main().catch((e) => {
  console.error(JSON.stringify({ error: e.message }, null, 2));
  process.exit(1);
});
