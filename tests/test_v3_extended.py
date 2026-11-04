import json
import shutil
import tempfile
import unittest
from pathlib import Path
from atlas.io import AtlasError,atomic_json
from atlas.demo import prepare_research
from atlas.project_archive import backup,restore
from atlas.ingest import ingest
from atlas.experiment import evsi_binary
from atlas.decision import correlated_simulation
from atlas.quant import run_analysis

REPO=Path(__file__).resolve().parents[1]

class Extended3(unittest.TestCase):
    def test_project_backup_restore_full_content(self):
        with tempfile.TemporaryDirectory() as t:
            base=Path(t);root=base/'repo';root.mkdir();shutil.copytree(REPO/'methods',root/'methods')
            p=prepare_research(root)
            s=p.path/'branches'/'artifact.txt';s.write_text('Research file\n')
            dest=base/'archive.zip';receipt=backup(p.path,dest,quiesced=True)
            self.assertTrue(dest.is_file());self.assertGreater(receipt['files'],5)
            out=base/'restored';restored=restore(dest,out)
            self.assertEqual((out/'branches/artifact.txt').read_text(),'Research file\n')
            self.assertTrue((out/'state.sqlite3').is_file())
            with self.assertRaises(AtlasError): restore(dest,out)
    def test_backup_quiescence_required(self):
        with self.assertRaises(AtlasError): backup('/missing','/tmp/out.zip')
    def test_plain_text_and_html_ingestion(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'source.html';p.write_text('<script>steal</script><div>Primary Data</div>')
            record=ingest(p)
            self.assertIn('Primary Data',record['text']);self.assertNotIn('steal',record['text'])
            self.assertTrue(record['sha256']);self.assertEqual(record['format'],'.html')
    def test_disallow_unsafe_file_ingestion(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'execute.py';p.write_text('print("test")')
            with self.assertRaises(AtlasError): ingest(p)
    def test_evsi_model(self):
        spec={'prior_h':.5,'p_positive_if_h':1,'p_positive_if_not_h':0,
              'payoffs':{'enter':{'h':100,'not_h':-100},'wait':{'h':0,'not_h':0}},
              'experiment_cost':10}
        r=evsi_binary(spec)
        self.assertEqual(r['evsi'],'50.0');self.assertEqual(r['net_value_of_experiment'],'40.0')
    def test_evsi_in_run_analysis(self):
        s={'kind':'evsi_binary','units':'USD','assumptions':['Fixture'],'prior_h':.5,
           'p_positive_if_h':1,'p_positive_if_not_h':0,
           'payoffs':{'x':{'h':100,'not_h':-100},'y':{'h':0,'not_h':0}}}
        self.assertEqual(run_analysis(s)['result'] if 'result' in run_analysis(s) else run_analysis(s)['output']['evsi'],'50.0')
    def test_correlated_pd_validation(self):
        s={'seed':1,'draws':200,'variables':{'a':{'distribution':'normal','mean':10,'sd':1},
             'b':{'distribution':'normal','mean':4,'sd':1}},'coefficients':{'a':1,'b':-1},
             'latent_correlation':[[1,.4],[.4,1]]}
        result=correlated_simulation(s);self.assertEqual(result['latent_correlation_matrix'],[[1.0,.4],[.4,1.0]])
        s['latent_correlation']=[[1,2],[2,1]]
        with self.assertRaises(AtlasError): correlated_simulation(s)
