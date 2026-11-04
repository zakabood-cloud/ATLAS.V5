"""Synthetic integration only; no real research or billable Copilot execution."""
import asyncio
import shutil
import tempfile
import unittest
from pathlib import Path
from atlas.demo import prepare_research,coverage_fixture
from atlas.scheduler import FixtureWorker,run_ready
from atlas.io import atomic_json,now,AtlasError

REPO=Path(__file__).resolve().parents[1]

class SchedulerIntegration(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);shutil.copytree(REPO/'methods',self.root/'methods')
        self.project=prepare_research(self.root)
    def test_fixture_dispatch_persists_output(self):
        r=asyncio.run(run_ready(self.project,FixtureWorker(),max_workers=2))
        self.assertEqual(r['completed'],['collect'])
        task=self.project.status()['tasks'][0]
        self.assertEqual(task['status'],'done')
        self.assertTrue((self.project.path/task['output']['path']).is_file())
        self.assertEqual(self.project.status()['state'],'RESEARCH')
    def test_blocked_critical_task_cannot_pass_gate(self):
        self.project.task('collect','blocked',reason='Access unavailable; cannot establish research')
        atomic_json(self.project.path/'coverage.json',{'items':[{'dimension':'fixture_support','status':'gap','basis':'Access blocked','decision_impact':'Cannot conclude'}], 'stopping_decision':'Blocked'})
        atomic_json(self.project.path/'search_log.json',{'queries':[{'query':'Test','tool':'fixture','at':now(),'outcome':'Blocked'}]})
        with self.assertRaises(AtlasError):self.project.advance('VERIFY')
    def test_noncritical_skipped_has_impact(self):
        self.project.reopen('ORCHESTRATE','Make a noncritical test task')
        from atlas.io import read_json
        p=read_json(self.project.path/'plan.json');p['tasks'][0]['critical']=False;atomic_json(self.project.path/'plan.json',p)
        self.project.advance('RESEARCH')
        self.project.task('collect','skipped',reason='Synthetic nonessential retrieval omitted')
        coverage_fixture(self.project,gap=True)
        self.project.advance('VERIFY')
        self.assertEqual(self.project.status()['state'],'VERIFY')
