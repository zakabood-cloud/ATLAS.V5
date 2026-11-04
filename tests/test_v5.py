"""ATLAS 5 targeted local tests; no external services or paid calls."""
import json
import tempfile
import shutil
import unittest
from pathlib import Path
from atlas.session import session_profile
from atlas.failures import decision
from atlas.claim_checks import check_claim_context
from atlas.analysis_inputs import validate_inputs
from atlas.model_research import ProviderRequest, execute, extract, build_request
from atlas.io import AtlasError
from atlas.budget import Budget
from atlas.structure import check
from atlas.project import Project

ROOT=Path(__file__).resolve().parents[1]

class V5SessionTests(unittest.TestCase):
    def test_sandbox_long_running_no_fixed_timeout(self):
        row=session_profile('copilot_sandbox')
        self.assertIsNone(row['hard_coded_cutoff_seconds'])
        self.assertIn('no one-hour',row['documented_duration'])
    def test_actions_is_distinguished_from_sandbox(self):
        row=session_profile('copilot_actions')
        self.assertIn('59-minute',row['documented_duration'])
        self.assertIsNone(row['hard_coded_cutoff_seconds'])
    def test_all_surfaces_have_recovery_guidance(self):
        for surface in ('copilot_sandbox','copilot_actions','copilot_cli','copilot_ide','claude_code','codex','unknown'):
            self.assertTrue(session_profile(surface)['continuation'])
    def test_invalid_surface_rejected(self):
        with self.assertRaises(AtlasError):session_profile('cloud-long')

class V5PolicyTests(unittest.TestCase):
    def test_optional_failure_does_not_hold_everything(self):
        d=decision('optional');self.assertFalse(d['pause_project']);self.assertTrue(d['pause_affected'])
    def test_critical_failure_requires_authorization(self):
        self.assertTrue(decision('critical')['pause_project'])
    def test_security_violation_prevents_retry(self):
        self.assertFalse(decision('security', approved_alternative=True)['retry'])
    def test_unknown_classification_rejected(self):
        with self.assertRaises(AtlasError):decision('unverified')
    def test_optional_access_block_does_not_create_global_hold(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d)/'methods').mkdir()
            shutil.copyfile(ROOT/'methods/domains.json',Path(d)/'methods/domains.json')
            project=Project.create(Path(d),'optional-case','Synthetic inquiry','general')
            project.block_access('https://example.invalid','read','temporarily inaccessible',
                                 'Optional corroborating source missing',severity='optional')
            status=project.status()
            self.assertIsNone(status.get('hold'))
            self.assertEqual(status['access_blocks'][0]['severity'],'optional')
    def test_critical_access_block_creates_hold(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d)/'methods').mkdir()
            shutil.copyfile(ROOT/'methods/domains.json',Path(d)/'methods/domains.json')
            project=Project.create(Path(d),'critical-case','Synthetic inquiry','general')
            project.block_access('https://example.invalid','read','unavailable',
                                 'Central measurement is missing',severity='critical')
            self.assertEqual(project.status()['hold']['category'],'access')
    def test_portable_profiles_are_packaged(self):
        self.assertTrue(check(ROOT)['ok'])
        self.assertTrue((ROOT/'.claude/agents/research-coordinator.md').is_file())
        self.assertTrue((ROOT/'.github/agents/research-coordinator.agent.md').is_file())
        self.assertIn('"agent"',(ROOT/'.github/agents/research-coordinator.agent.md').read_text())

class V5VerificationTests(unittest.TestCase):
    def test_lexical_check_never_claims_entailment(self):
        r=check_claim_context('Sales increased by 40%', ['Sales increased by 20%'])
        self.assertEqual(r['verdict'],'requires_independent_semantic_review')
        self.assertTrue(r['flags'])
    def test_claim_numbers_present_no_automatic_truth(self):
        r=check_claim_context('20%', ['The number was 20% in some cases'])
        self.assertTrue(r['lexical_only'])
        self.assertNotIn('verified',r['verdict'])
    def test_assumed_financial_input_requires_uncertainty(self):
        x=validate_inputs({'inputs':[{'name':'cac','value':20,'basis':'assumption','unit':'USD','time_period':'2027'}]})
        self.assertFalse(x['ok'])
    def test_observed_input_needs_source_hash(self):
        x=validate_inputs({'inputs':[{'name':'sales','value':20,'basis':'observed','unit':'orders','time_period':'2026'}]})
        self.assertFalse(x['ok'])
    def test_correct_financial_input_metadata(self):
        x=validate_inputs({'inputs':[{'name':'cac','value':20,'basis':'assumption','unit':'USD','time_period':'2027','uncertainty':'10..40'}]})
        self.assertTrue(x['ok'])

class V5ProviderTests(unittest.TestCase):
    def request(self,provider='openai',authorized=True,private_data_approved=True):
        return ProviderRequest(provider,'test-model-1','Evaluate a test question','req111','0.05',authorized,private_data_approved)
    def test_no_approval_is_not_bypassed_by_python(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(AtlasError):
                execute(self.request(private_data_approved=False),budget_file=Path(d)/'budget.db',ceiling_usd='2',result_path=Path(d)/'out.json',credential='FAKE',transport=lambda *args: {})
    def test_invalid_model_path_rejected(self):
        req=ProviderRequest('gemini','..','test','req100','0.01',True,True)
        with self.assertRaises(AtlasError):build_request(req,'FAKE')
    def test_model_budget_guard(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(AtlasError):
                execute(self.request(),budget_file=Path(d)/'b.db',ceiling_usd='0',result_path=Path(d)/'o.json',credential='FAKE',transport=lambda *args:{})
    def test_openai_provider_mock_with_local_reservation(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'out.json'; budget=Path(d)/'budget.db'
            fake={'output':[{'type':'message','content':[{'type':'output_text','text':'Model hypothesis','annotations':[{'type':'url_citation','url':'https://example.org/x','title':'X'}]}]}]}
            result=execute(self.request(),budget_file=budget,ceiling_usd='1.0',result_path=out,credential='FAKE',transport=lambda *args:fake)
            self.assertEqual(result['verification_level'],'provider_response_only')
            self.assertEqual(result['citations'],1)
            self.assertTrue(out.is_file())
            self.assertEqual(Budget(budget,'1.0').status()['reserved_usd'],'0.05')
            with self.assertRaises(AtlasError):
                execute(self.request(),budget_file=budget,ceiling_usd='1.0',result_path=out,credential='FAKE',transport=lambda *args:fake)
    def test_gemini_grounding_is_only_source_lead(self):
        r=extract({'candidates':[{'content':{'parts':[{'text':'Candidate hypothesis'}]},'groundingMetadata':{'groundingChunks':[{'web':{'uri':'https://example.org','title':'A'}}]}}]},'gemini')
        self.assertEqual(len(r['citations']),1)
        self.assertIn('independently verify',r['warning'])

if __name__=='__main__':unittest.main()
