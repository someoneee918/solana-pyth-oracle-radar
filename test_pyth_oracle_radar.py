#!/usr/bin/env python3
"""
Unit Tests for Solana Pyth Network Pull Oracle & Entropy Gas Optimization Radar
"""

import unittest
from pyth_oracle_radar import (
    calculate_update_staleness_cost,
    optimize_batch_update_cu,
    evaluate_liquidation_trigger,
    calculate_entropy_request_cost,
    generate_vip_sentinel_script,
    SOL_RECEIVE_ADDRESS,
    BASE_RECEIVE_ADDRESS
)

class TestPythOracleRadar(unittest.TestCase):

    def test_update_staleness_cost(self):
        # Case 1: Fresh price feed (10 seconds stale, tight confidence)
        fresh = calculate_update_staleness_cost(price=140.0, conf=0.05, staleness_seconds=10.0)
        self.assertFalse(fresh["needs_update"])
        self.assertEqual(fresh["severity"], "HEALTHY")
        self.assertAlmostEqual(fresh["conf_ratio_bps"], 3.57, places=1)
        
        # Case 2: Stale price feed (45 seconds stale)
        stale = calculate_update_staleness_cost(price=140.0, conf=0.05, staleness_seconds=45.0)
        self.assertTrue(stale["needs_update"])
        self.assertEqual(stale["severity"], "MODERATE")
        
        # Case 3: High uncertainty feed (conf 2.0 on 140 -> 1.4% confidence ratio)
        uncertain = calculate_update_staleness_cost(price=140.0, conf=2.0, staleness_seconds=15.0)
        self.assertTrue(uncertain["needs_update"])
        self.assertEqual(uncertain["severity"], "CRITICAL")

    def test_batch_update_cu_optimization(self):
        # 5 feeds batched together
        res = optimize_batch_update_cu(num_feeds=5, priority_fee_micro_lamports=50000.0, sol_price_usd=140.0)
        self.assertEqual(res["num_feeds"], 5)
        # Individual: 5 * 65000 = 325,000 CU
        self.assertEqual(res["individual_cu_total"], 325000)
        # Batched: 40,000 + 5 * 18,000 = 130,000 CU
        self.assertEqual(res["batch_cu_total"], 130000)
        # Savings: (325k - 130k) / 325k = 60.0%
        self.assertEqual(res["cu_savings_pct"], 60.0)
        self.assertGreater(res["usd_savings_per_update"], 0.0)
        self.assertGreater(res["daily_savings_100_runs_usd"], 0.0)

    def test_liquidation_trigger_precision(self):
        # 10 SOL collateral @ $140 = $1400 nominal. Liquidation threshold 0.85 -> max borrow $1190.
        # Debt: $1150.
        # Case A: Spot evaluation without confidence deduction
        # Nominal HF = 1190 / 1150 = 1.0348 (Safe)
        # With confidence conf=5.0: conservative price $135 -> val $1350 * 0.85 = $1147.5 -> HF = 1147.5 / 1150 = 0.9978 (Liquidatable!)
        res = evaluate_liquidation_trigger(
            oracle_price=140.0,
            oracle_conf=5.0,
            collateral_amount=10.0,
            debt_amount=1150.0,
            liquidation_threshold=0.85,
            use_ema=False
        )
        self.assertAlmostEqual(res["nominal_health_factor"], 1.0348, places=3)
        self.assertAlmostEqual(res["conservative_health_factor"], 0.9978, places=3)
        self.assertTrue(res["is_liquidatable"])
        self.assertGreater(res["debt_deficit_usd"], 0.0)

    def test_entropy_request_cost(self):
        entropy = calculate_entropy_request_cost(num_random_bytes=32, provider_fee_sol=0.001, sol_price_usd=140.0)
        self.assertEqual(entropy["num_random_bytes"], 32)
        self.assertAlmostEqual(entropy["total_cost_sol"], 0.001005, places=6)
        self.assertAlmostEqual(entropy["total_cost_usd"], 0.1407, places=3)

    def test_generate_vip_script(self):
        script = generate_vip_sentinel_script(SOL_RECEIVE_ADDRESS, BASE_RECEIVE_ADDRESS)
        self.assertIn("HermesClient", script)
        self.assertIn(SOL_RECEIVE_ADDRESS, script)
        self.assertIn(BASE_RECEIVE_ADDRESS, script)
        self.assertIn("updatePriceFeeds", script)

if __name__ == "__main__":
    unittest.main()
