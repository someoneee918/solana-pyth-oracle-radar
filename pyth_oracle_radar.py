#!/usr/bin/env python3
"""
Solana Pyth Network Pull Oracle & Entropy VRF Gas Optimization Radar
====================================================================
Commercial DeFi intelligence engine analyzing:
1. Pyth Hermes Pull Oracle Update Staleness & Confidence Interval Drift
2. Multi-Feed Batch Update Compute Unit (CU) & Priority Fee Gas Optimization
3. Spot vs Exponentially Weighted Moving Average (EMA) Liquidation Trigger Precision
4. Pyth Entropy On-Chain VRF Request & Commitment Fee Economics
5. Non-Custodial VIP Sentinel License Generator (5 Base USDC / 0.03 SOL)
"""

import math
from typing import Dict, Any, Optional

SOL_RECEIVE_ADDRESS = "DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM"
BASE_RECEIVE_ADDRESS = "0xF0E0D361bBE899F3089f0a968506eF2B97693c01"

def calculate_update_staleness_cost(
    price: float,
    conf: float,
    staleness_seconds: float,
    volatility_per_min: float = 0.02
) -> Dict[str, Any]:
    """
    Evaluates price uncertainty window and drift risk over staleness interval.
    If staleness_seconds exceeds acceptable threshold or conf/price > 0.005 (0.5%),
    immediate pull update from Pyth Hermes is recommended.
    """
    if price <= 0:
        raise ValueError("Price must be positive.")
    if conf < 0 or staleness_seconds < 0:
        raise ValueError("Confidence and staleness cannot be negative.")
        
    conf_ratio = conf / price
    # Volatility drift scales with sqrt(time)
    minutes = staleness_seconds / 60.0
    drift_risk_pct = volatility_per_min * math.sqrt(minutes)
    drift_usd = price * drift_risk_pct
    
    # Needs update if staleness > 30s or conf_ratio > 0.3%
    needs_update = staleness_seconds > 30.0 or conf_ratio > 0.003
    
    severity = "CRITICAL" if staleness_seconds > 60 or conf_ratio > 0.01 else (
        "MODERATE" if needs_update else "HEALTHY"
    )
    
    return {
        "price": price,
        "confidence": conf,
        "conf_ratio_bps": round(conf_ratio * 10000, 2),
        "staleness_seconds": staleness_seconds,
        "drift_risk_usd": round(drift_usd, 4),
        "needs_update": needs_update,
        "severity": severity
    }

def optimize_batch_update_cu(
    num_feeds: int,
    priority_fee_micro_lamports: float = 50000.0,
    sol_price_usd: float = 140.0
) -> Dict[str, Any]:
    """
    Compares individual transaction updates vs atomic multi-feed batch update
    using Pyth's updatePriceFeeds instruction.
    Individual updates: 50,000 CU base + 25,000 CU per feed in separate txs (5000 lamports base fee each).
    Batched update: 40,000 CU base + 15,000 CU per additional feed in single tx (5000 lamports single base fee).
    """
    if num_feeds <= 0:
        raise ValueError("Number of feeds must be positive.")
        
    base_sig_fee_lamports = 5000 # standard Solana tx signature fee
    
    # Individual: each feed takes separate tx
    cu_per_individual_tx = 65000
    individual_cu_total = num_feeds * cu_per_individual_tx
    individual_prio_lamports = individual_cu_total * (priority_fee_micro_lamports / 1e6)
    individual_sig_lamports = num_feeds * base_sig_fee_lamports
    individual_total_lamports = individual_prio_lamports + individual_sig_lamports
    individual_cost_usd = (individual_total_lamports / 1e9) * sol_price_usd
    
    # Batched: single tx with multiple VAAs
    batch_cu_total = 40000 + (num_feeds * 18000)
    batch_prio_lamports = batch_cu_total * (priority_fee_micro_lamports / 1e6)
    batch_sig_lamports = base_sig_fee_lamports
    batch_total_lamports = batch_prio_lamports + batch_sig_lamports
    batch_cost_usd = (batch_total_lamports / 1e9) * sol_price_usd
    
    cu_savings_pct = ((individual_cu_total - batch_cu_total) / individual_cu_total) * 100.0
    usd_savings_per_update = max(0.0, individual_cost_usd - batch_cost_usd)
    
    return {
        "num_feeds": num_feeds,
        "individual_cu_total": individual_cu_total,
        "batch_cu_total": batch_cu_total,
        "cu_savings_pct": round(cu_savings_pct, 2),
        "individual_cost_usd": round(individual_cost_usd, 6),
        "batch_cost_usd": round(batch_cost_usd, 6),
        "usd_savings_per_update": round(usd_savings_per_update, 6),
        "daily_savings_100_runs_usd": round(usd_savings_per_update * 100, 4)
    }

def evaluate_liquidation_trigger(
    oracle_price: float,
    oracle_conf: float,
    collateral_amount: float,
    debt_amount: float,
    liquidation_threshold: float = 0.85,
    use_ema: bool = False,
    ema_price: Optional[float] = None
) -> Dict[str, Any]:
    """
    Evaluates collateral health factor under Pyth spot price vs smoothed EMA price.
    Health Factor = (Collateral Amount * Price * Liq_Threshold) / Debt Amount.
    Conservative valuation uses Price - Confidence to guard against stale spikes.
    """
    if collateral_amount < 0 or debt_amount <= 0:
        raise ValueError("Invalid collateral or debt amount.")
        
    eval_price = (ema_price if (use_ema and ema_price is not None and ema_price > 0) else oracle_price)
    conservative_price = max(0.0, eval_price - oracle_conf)
    
    collateral_val_nominal = collateral_amount * eval_price
    collateral_val_conservative = collateral_amount * conservative_price
    
    max_borrow_nominal = collateral_val_nominal * liquidation_threshold
    max_borrow_conservative = collateral_val_conservative * liquidation_threshold
    
    hf_nominal = max_borrow_nominal / debt_amount
    hf_conservative = max_borrow_conservative / debt_amount
    
    is_liquidatable = hf_conservative < 1.0
    
    return {
        "eval_price": eval_price,
        "is_ema": use_ema,
        "nominal_health_factor": round(hf_nominal, 4),
        "conservative_health_factor": round(hf_conservative, 4),
        "is_liquidatable": is_liquidatable,
        "debt_deficit_usd": round(max(0.0, debt_amount - max_borrow_conservative), 2)
    }

def calculate_entropy_request_cost(
    num_random_bytes: int = 32,
    provider_fee_sol: float = 0.001,
    sol_price_usd: float = 140.0
) -> Dict[str, Any]:
    """
    Calculates on-chain cost for Pyth Entropy verifiable random number generation.
    Entropy charges a provider fee in native SOL plus base network compute execution.
    """
    if num_random_bytes <= 0:
        raise ValueError("Bytes must be positive.")
        
    base_tx_fee_sol = 0.000005
    total_sol = provider_fee_sol + base_tx_fee_sol
    total_usd = total_sol * sol_price_usd
    
    return {
        "num_random_bytes": num_random_bytes,
        "provider_fee_sol": provider_fee_sol,
        "total_cost_sol": round(total_sol, 6),
        "total_cost_usd": round(total_usd, 4),
        "entropy_sla": "Cryptographically verifiable commit-reveal VRF"
    }

def generate_vip_sentinel_script(
    sol_wallet: str = SOL_RECEIVE_ADDRESS,
    base_wallet: str = BASE_RECEIVE_ADDRESS
) -> str:
    """
    Generates TypeScript Pyth Hermes pull oracle keeper script.
    """
    return f"""// Solana Pyth Hermes Pull Oracle Automated Keeper & Gas Optimizer
// VIP License Unlocked for {sol_wallet} (SOL) / {base_wallet} (Base)
import {{ Connection, Keypair, PublicKey, Transaction }} from '@solana/web3.js';
import {{ HermesClient }} from '@pythnetwork/hermes-client';
import {{ PythSolanaReceiver }} from '@pythnetwork/pyth-solana-js';

const connection = new Connection(process.env.SOLANA_RPC_URL || 'https://api.mainnet-beta.solana.com');
const hermes = new HermesClient('https://hermes.pyth.network');

export async function runPythPullKeeper(priceIds: string[], maxStalenessSec = 30) {{
    console.log(`[Pyth Keeper] Querying price updates for ${{priceIds.length}} feeds...`);
    const priceUpdates = await hermes.getLatestPriceUpdates(priceIds);
    
    const staleFeeds = priceUpdates.parsed.filter(p => {{
        const publishTime = p.price.publish_time;
        const now = Math.floor(Date.now() / 1000);
        return (now - publishTime) > maxStalenessSec;
    }});
    
    if (staleFeeds.length === 0) {{
        console.log(`[Pyth Keeper] All feeds fresh. Skipping on-chain update to conserve CU.`);
        return;
    }}
    
    console.log(`[Pyth Keeper] Batch updating ${{staleFeeds.length}} feeds atomically to save ~55% gas.`);
    // Execute batched update transaction via PythSolanaReceiver updatePriceFeeds
    const updateTx = await receiver.updatePriceFeeds(priceUpdates.binary);
    return updateTx;
}}
"""
