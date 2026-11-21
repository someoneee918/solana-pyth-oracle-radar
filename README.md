# Solana Pyth Network Pull Oracle & Entropy VRF Gas Optimization Radar

[![Python Unit Tests](https://img.shields.io/badge/Unit%20Tests-5%2F5%20Passing-brightgreen.svg)]()
[![Solana](https://img.shields.io/badge/Solana-Mainnet--Beta-blueviolet.svg)]()
[![Pyth Hermes](https://img.shields.io/badge/Pyth-Hermes%20Pull%20Oracle-purple.svg)]()
[![Live Dashboard](https://img.shields.io/badge/Live%20Visualizer-GitHub%20Pages-blue.svg)](https://someoneee918.github.io/solana-pyth-oracle-radar/)

Commercial DeFi intelligence engine analyzing:
1. **Pyth Hermes Pull Oracle Update Staleness & Confidence Interval Drift**
2. **Multi-Feed Atomic Batch Update Compute Unit (CU) & Priority Fee Gas Optimization (~60% CU Savings)**
3. **Spot vs Exponentially Weighted Moving Average (EMA) Liquidation Trigger Precision**
4. **Pyth Entropy On-Chain VRF Request & Commitment Fee Economics**
5. **Non-Custodial VIP Sentinel License Generator (5 Base USDC / 0.03 SOL)**

---

## Live Interactive Dashboard
🌐 **Access the live dashboard at**: [https://someoneee918.github.io/solana-pyth-oracle-radar/](https://someoneee918.github.io/solana-pyth-oracle-radar/)

---

## Key Mathematical Models

### 1. Multi-Feed Atomic Batch CU Optimization
Individual updates on Solana require 65,000 CU per transaction with independent 5,000 lamport base signature fees:
$$CU_{indiv} = N \times 65,000$$

Atomic batched updates via Pyth's `updatePriceFeeds` instruction share base transaction overhead:
$$CU_{batch} = 40,000 + (N \times 18,000)$$

For $N = 5$ feeds:
- Individual: $325,000\text{ CU}$
- Batched: $130,000\text{ CU}$
- **Savings: 60.0% compute budget and transaction fee reduction.**

### 2. Conservative Liquidation Evaluation
To guard against flash-loan oracle latency manipulation, health factor is evaluated conservatively:
$$P_{conservative} = \max(0, P_{eval} - \sigma_{conf})$$
$$HF_{conservative} = \frac{\text{Collateral} \times P_{conservative} \times LTV_{threshold}}{\text{Debt}}$$

If $HF_{conservative} < 1.0$, liquidation is immediately eligible.

---

## Unit Test Verification
Run the 5/5 unit test suite:
```bash
python3 -m unittest test_pyth_oracle_radar.py
```

---

## Non-Custodial VIP Sentinel License
Unlock automated TypeScript `@pythnetwork/pyth-solana-js` Hermes keeper bots and Jito bundle integration by sending **5 Base USDC** or **0.03 SOL** to our verified receive addresses:
- **Solana:** `DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM`
- **Base EVM:** `0xF0E0D361bBE899F3089f0a968506eF2B97693c01`
