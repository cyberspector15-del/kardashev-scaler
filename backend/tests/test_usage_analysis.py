"""Regression tests for Usage Intelligence's per-window energy ledger."""

import unittest

from app.services.usage_analysis import analyze_usage


class UsageAnalysisTests(unittest.TestCase):
    def test_full_profile_waste_reconciles_when_there_is_no_deficit(self) -> None:
        profile = [{"hour": hour, "demand_kwh": 8 / 24} for hour in range(24)]
        result = analyze_usage(captured_kwh=12, consumed_kwh=8, consumption_profile=profile)
        self.assertEqual(round(sum(item["waste_kwh"] for item in result["flagged_windows"]), 4), result["waste_kwh"])
        self.assertEqual(result["deficit_kwh"], 0)

    def test_window_ledger_reconciles_when_waste_and_deficit_coexist(self) -> None:
        profile = [{"hour": 0, "demand_kwh": 1}, {"hour": 1, "demand_kwh": 5}]
        result = analyze_usage(captured_kwh=6, consumed_kwh=6, consumption_profile=profile)
        window_waste = sum(item["waste_kwh"] for item in result["flagged_windows"])
        window_deficit = sum(item["deficit_kwh"] for item in result["deficit_windows"])
        self.assertAlmostEqual(window_waste - window_deficit, result["waste_kwh"] - result["deficit_kwh"], places=4)


if __name__ == "__main__":
    unittest.main()
