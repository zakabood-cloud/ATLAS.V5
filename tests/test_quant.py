import copy
import unittest
from atlas.quant import run_analysis, D
from atlas.io import AtlasError


class QuantTests(unittest.TestCase):
    def run_spec(self,kind,**kw): return run_analysis(dict(kind=kind,units="USD per declared period",assumptions=["Synthetic test assumptions"],**kw))["output"]
    def test_unit_economics_known_answer(self):
        r=self.run_spec("unit_economics",price_gross="120",vat_rate="0.2",landed_cost="30",fulfillment="10",fee_rate_on_net="0.15",ad_cost_per_order="20",fixed_cost_per_period="1000",units_per_period="100")
        self.assertEqual(D(r["contribution_per_order"]),D(25)); self.assertEqual(D(r["period_profit"]),D(1500)); self.assertEqual(r["break_even_units"],"40")
    def test_negative_contribution_no_break_even(self):
        r=self.run_spec("unit_economics",price_gross="10",landed_cost="20"); self.assertIsNone(r["break_even_units"])
    def test_invalid_rate(self):
        with self.assertRaises(AtlasError): self.run_spec("unit_economics",price_gross="10",vat_rate="2")
    def test_nonfinite(self):
        with self.assertRaises(AtlasError): self.run_spec("unit_economics",price_gross="NaN")
    def test_cashflow_timing_and_npv(self):
        r=self.run_spec("cashflow",opening_cash="100",initial_investment="100",discount_rate_per_period="0",periods=[{"inflow":"0","outflow":"150"},{"inflow":"200","outflow":"0"}])
        self.assertEqual(r["minimum_cash"],"-50"); self.assertEqual(r["npv"],"-50")
    def test_mc_reproducible_and_exact_ev(self):
        kw=dict(seed=42,draws=1000,scenarios=[{"net_value":"-100","probability":"0.25"},{"net_value":"100","probability":"0.75"}])
        a=self.run_spec("monte_carlo",**kw); b=self.run_spec("monte_carlo",**kw)
        self.assertEqual(a,b); self.assertEqual(D(a["exact_scenario_expected_value"]),D(50)); self.assertGreater(a["loss_probability"],.2); self.assertLess(a["loss_probability"],.3)
    def test_probability_sum(self):
        with self.assertRaises(AtlasError): self.run_spec("monte_carlo",seed=1,scenarios=[{"net_value":1,"probability":.5}])
    def test_mc_seed_required(self):
        with self.assertRaises(AtlasError): self.run_spec("monte_carlo",scenarios=[{"net_value":1,"probability":1}])
    def test_mcda_direction(self):
        r=self.run_spec("mcda",criteria=[{"name":"cost","weight":1,"low":0,"high":100,"direction":"cost"}],alternatives={"cheap":{"cost":10},"expensive":{"cost":80}})
        self.assertEqual(r["ranking"][0]["name"],"cheap"); self.assertEqual(D(r["ranking"][0]["score"]),D(".9"))
    def test_mcda_bounds(self):
        with self.assertRaises(AtlasError): self.run_spec("mcda",criteria=[{"name":"x","weight":1,"low":0,"high":0,"direction":"cost"}],alternatives={"a":{"x":0},"b":{"x":0}})
    def test_bayes(self):
        r=self.run_spec("bayes",prior="0.5",p_e_given_h="0.8",p_e_given_not_h="0.2"); self.assertEqual(D(r["posterior"]),D(".8"))
    def test_impossible_evidence(self):
        with self.assertRaises(AtlasError): self.run_spec("bayes",prior="0.5",p_e_given_h=0,p_e_given_not_h=0)
    def test_evpi(self):
        r=self.run_spec("evpi",probabilities=["0.5","0.5"],payoffs={"a":[100,0],"b":[0,100]})
        self.assertEqual(D(r["evpi_upper_bound"]),D(50))
    def test_missing_units(self):
        with self.assertRaises(AtlasError): run_analysis({"kind":"bayes","assumptions":["a"]})
    def test_boolean_not_number(self):
        with self.assertRaises(AtlasError): D(True)


if __name__=="__main__": unittest.main()
