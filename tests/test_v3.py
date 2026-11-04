import asyncio
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from atlas.io import AtlasError, atomic_json
from atlas.retrieval import canonical_url,expand_queries,bm25_search,coverage_audit
from atlas.methodology import score_methods
from atlas.verification import report_audit,review_packet
from atlas.budget import Budget
from atlas.scheduler import FixtureWorker,run_ready
from atlas.adapters import search,http_json
from atlas.decision import ecommerce_economics,correlated_simulation,reverse_stress
from atlas.evaluation import evaluate_cases,compare_runs
from atlas.sourcegraph import group_origins,contradictions
from atlas.memory_search import retrieve_ranked
from atlas.structure import check
from atlas.quant import run_analysis
from atlas.project import Project
from atlas import __version__

class TestRetrieval(unittest.TestCase):
    def test_queries_are_bounded_and_include_counterevidence(self):
        q=expand_queries('best market',['demand','competition'],{'demand':['search volume']},['UAE','USA'],20)
        self.assertLessEqual(len(q),20)
        self.assertTrue(any(x['strategy']=='counterevidence' for x in q))
    def test_bm25(self):
        rows=bm25_search('customer profitability',[{'id':'x','text':'customer profitability in UAE'},{'id':'y','text':'weather forecast'}])
        self.assertEqual(rows[0]['id'],'x')
    def test_url(self):
        self.assertEqual(canonical_url('https://EXAMPLE.org/p?utm_source=x&a=1#main'),'https://example.org/p?a=1')
        with self.assertRaises(AtlasError): canonical_url('file:///etc/passwd')
    def test_coverage(self):
        o=coverage_audit(['A','B'],[{'dimension':'A','source_id':'s','origin_group':'g'}])
        self.assertEqual(o['uncovered'],['B'])

class TestMethods(unittest.TestCase):
    def test_pilots(self):
        rows=[{'name':'A','pilot':{k:0.9 for k in ['evidence_quality','coverage','reproducibility','feasibility','cost_efficiency']},'pilot_evidence':'A.json'},
              {'name':'B','pilot':{k:0.2 for k in ['evidence_quality','coverage','reproducibility','feasibility','cost_efficiency']},'pilot_evidence':'B.json'}]
        self.assertEqual(score_methods(rows)['selected'],'A')
        with self.assertRaises(AtlasError): score_methods(rows[:1])

class TestClaims(unittest.TestCase):
    def test_report_audit(self):
        e={'claims':[{'id':'A','material':True,'author':'a','source_ids':['S']}],'sources':[{'id':'S'}],
           'assessments':[{'claim_id':'A','source_id':'S','verdict':'supports','independent':True,'reviewer':'b'}]}
        self.assertTrue(report_audit('Finding [[claim:A]]',e)['ok'])
        self.assertFalse(report_audit('Finding [[claim:MISSING]]',e)['ok'])
        self.assertFalse(report_audit('The market is profitable and more competitive than last year.',e)['ok'])

class TestBudget(unittest.TestCase):
    def test_reserve_and_settle(self):
        with tempfile.TemporaryDirectory() as td:
            b=Budget(Path(td)/'budget.sqlite3','12')
            with self.assertRaises(AtlasError): b.reserve('a','5','vendor')
            b.reserve('a','5','vendor',True)
            self.assertTrue(b.reserve('a','5','vendor',True)['idempotent'])
            with self.assertRaises(AtlasError): b.reserve('b','8','vendor',True)
            b.settle('a','4')
            self.assertEqual(b.status()['remaining_usd'],'8')
            b.reserve('b','6','vendor',True); b.cancel('b')
            self.assertEqual(b.status()['remaining_usd'],'8')

class TestAdapters(unittest.TestCase):
    def test_schema_and_no_redirect(self):
        with patch('atlas.adapters.http_json',return_value={'results':[{'display_name':'Test','id':'https://openalex.org/W123'}]}):
            result=search('openalex','oral health',1)
        self.assertEqual(result['items'][0]['title'],'Test')
        with self.assertRaises(AtlasError): http_json('http://169.254.169.254/latest','crossref')

class TestDecision(unittest.TestCase):
    def test_ecommerce(self):
        r=ecommerce_economics({'price_gross':'40','orders':10,'unit_landed':11,'ads_per_order':12})
        self.assertEqual(r['contribution_per_order'],'17')
    def test_mc(self):
        spec={'seed':17,'draws':200,'variables':{'a':{'distribution':'uniform','low':0,'high':1}},'coefficients':{'a':4}}
        self.assertEqual(correlated_simulation(spec),correlated_simulation(spec))
        self.assertEqual(reverse_stress({'current_acquisition_cost':10,'contribution_per_order':5})['acquisition_cost_at_zero_contribution'],'15')
    def test_cli_run_analysis(self):
        spec={'kind':'ecommerce_economics','units':'USD','assumptions':['Prices held fixed'],'price_gross':40,'orders':5}
        self.assertEqual(run_analysis(spec)['engine'],'atlas.quant/4.0.0')
        self.assertEqual(run_analysis(spec,engine='atlas.quant/3.0.0')['engine'],'atlas.quant/3.0.0')

class TestEvaluation(unittest.TestCase):
    def test_pair(self):
        cases=[{'id':'a','expected':'x'},{'id':'b','expected':'z'}]
        x=evaluate_cases(cases,[{'id':'a','answer':'x'}]);y=evaluate_cases(cases,[{'id':'b','answer':'z'}])
        self.assertEqual(compare_runs(x,y)['left_only_correct'],['a'])
        self.assertEqual(x['coverage_rate'],.5)

class TestGraph(unittest.TestCase):
    def test_duplicate_origins(self):
        self.assertEqual(group_origins([{'id':'s1','doi':'a'},{'id':'s2','doi':'a'},{'id':'s3','doi':'b'}])['distinct_origin_clusters'],2)
        self.assertEqual(len(contradictions({'assessments':[{'claim_id':'a','verdict':'supports','source_id':'x'}, {'claim_id':'a','verdict':'contradicts','source_id':'y'}]})),1)

class TestScheduler(unittest.TestCase):
    def test_fixture_worker_is_explicitly_synthetic(self):
        result=asyncio.run(FixtureWorker().execute({'id':'sample','objective':'Test task'},{}))
        self.assertEqual(result['worker'],'fixture')
        self.assertIn('NOT a research result',result['warning'])
    def test_fixture_with_project(self):
        # Project.create requires root schema; use complete checkout and temporary project path under copied root.
        import shutil
        src=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            shutil.copytree(src/'methods',root/'methods')
            (root/'projects').mkdir()
            p=Project.create(root,'fixture-run','test question','general')
            # Test task orchestration by constructing the minimum normal RESEARCH state through controlled DB.
            # Direct fixture mutation would violate ledger; use public API with complete inputs in integration tests instead.
            self.assertEqual(p.status()['state'],'INTAKE')
            self.assertEqual(__version__,'5.0.0')

if __name__=='__main__': unittest.main()
