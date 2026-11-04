"""Deterministic regressions for audited v3 defects; not live research evaluation."""
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from atlas.adapters import search, http_json
from atlas.archive import checked_members, manifest_index
from atlas.budget import Budget
from atlas.evaluation import evaluate_cases, compare_runs, evaluate_retrieval
from atlas.ingest import ingest
from atlas.io import AtlasError, atomic_json, file_hash, parse_json
from atlas.memory import promote
from atlas.memory_search import retrieve_ranked
from atlas.methodology import score_methods
from atlas.project_archive import restore
from atlas.retrieval import bm25_search, canonical_url, coverage_audit, expand_queries
from atlas.sourcegraph import group_origins, contradictions


class RetrievalAndMethods(unittest.TestCase):
    def test_query_budget_covers_all_dimensions_first(self):
        rows=expand_queries("research",["accuracy","coverage","alternatives"],max_queries=3)
        self.assertEqual({row["dimension"] for row in rows},{"accuracy","coverage","alternatives"})

    def test_query_budget_includes_counterevidence_fairly(self):
        rows=expand_queries("research",["accuracy","coverage","alternatives"],max_queries=9)
        for dimension in ("accuracy","coverage","alternatives"):
            self.assertEqual({r["strategy"] for r in rows if r["dimension"]==dimension},
                             {"coverage","primary_source","counterevidence"})

    def test_impossible_budget_and_malformed_synonyms_fail(self):
        for kwargs in ({"max_queries":1},{"synonyms":{"A":"wrong"}},{"max_queries":True}):
            with self.subTest(kwargs=kwargs), self.assertRaises(AtlasError):
                expand_queries("research",["A","B"],**kwargs)

    def test_missing_origin_never_becomes_independence(self):
        rows=[{"dimension":"A","source_id":"one"},{"dimension":"A","source_id":"two","origin_group":None}]
        result=coverage_audit(["A"],rows)["dimensions"][0]
        self.assertEqual(result["distinct_origin_count"],0)
        self.assertEqual(result["status"],"untraced")
        self.assertEqual(result["untraced_source_ids"],["one","two"])

    def test_bm25_rejects_invalid_parameters(self):
        for kwargs in ({"b":2},{"b":float("nan")},{"k1":0},{"limit":True}):
            with self.subTest(kwargs=kwargs), self.assertRaises(AtlasError):
                bm25_search("query",[{"id":"a","text":"query"}],**kwargs)

    def test_canonical_url_preserves_semantic_ref_and_ipv6(self):
        self.assertEqual(canonical_url("https://[2001:4860:4860::8888]:443/x?ref=study&utm_source=x"),
                         "https://[2001:4860:4860::8888]/x?ref=study")

    def test_doi_aliases_and_lineage_collapse(self):
        sources=[{"id":"A","doi":"https://doi.org/10.1234/ABC","origin_group":"a"},
                 {"id":"B","doi":"DOI:10.1234/abc","origin_group":"b"},
                 {"id":"C","derived_from":["B"]}]
        self.assertEqual(group_origins(sources)["groups"],[["A","B","C"]])

    def test_unknown_cyclic_and_duplicate_lineage_fail(self):
        for rows in ([{"id":"A"},{"id":"A"}],[{"id":"A","derived_from":["missing"]}],
                     [{"id":"A","derived_from":["B"]},{"id":"B","derived_from":["A"]}]):
            with self.subTest(rows=rows), self.assertRaises(AtlasError):
                group_origins(rows)

    def test_long_lineage_does_not_depend_on_python_recursion_limit(self):
        rows=[{"id":str(index),"derived_from":[str(index-1)] if index else []} for index in range(1500)]
        self.assertEqual(group_origins(rows)["distinct_origin_clusters"],1)

    def test_negative_only_assessment_is_visible(self):
        self.assertEqual(contradictions({"assessments":[{"claim_id":"C","source_id":"S","verdict":"contradicts"}]})[0]["claim_id"],"C")

    def test_infeasible_method_cannot_win(self):
        rows=[{"name":"glossy","pilot":{"quality":1.},"pilot_evidence":"observed.json","feasible":False,"infeasibility_reason":"Required data unavailable"},
              {"name":"simple","pilot":{"quality":.7},"pilot_evidence":"other.json"}]
        result=score_methods(rows,{"quality":1.})
        self.assertEqual(result["selected"],"simple")
        self.assertEqual(len(result["excluded"]),1)
        self.assertFalse(score_methods(rows,{"quality":1.},{"quality":.9})["ok"])

    def test_boolean_weight_is_rejected(self):
        with self.assertRaises(AtlasError): score_methods([],{"quality":True})


class Evaluations(unittest.TestCase):
    def setUp(self):
        self.cases=[{"id":"A","expected":"yes"},{"id":"B","expected":"no"}]

    def test_duplicate_and_unknown_results_rejected(self):
        for results in ([{"id":"A"},{"id":"A"}],[{"id":"absent","answer":"yes"}]):
            with self.subTest(results=results), self.assertRaises(AtlasError):
                evaluate_cases(self.cases,results)

    def test_duplicate_cases_rejected(self):
        with self.assertRaises(AtlasError): evaluate_cases([self.cases[0],self.cases[0]],[])

    def test_missing_failed_and_boolean_answers_are_not_correct(self):
        result=evaluate_cases(self.cases,[{"id":"A","status":"failed"}])
        self.assertEqual(result["accuracy_over_all"],0)
        self.assertEqual(result["failed"],1)
        self.assertEqual(result["abstained"],1)
        self.assertEqual(evaluate_cases([{"id":"A","expected":1}],[{"id":"A","answer":True}])["accuracy_over_all"],0)

    def test_paired_case_sets_and_truth_must_match(self):
        left=evaluate_cases(self.cases,[])
        right=evaluate_cases(self.cases[:1],[])
        with self.assertRaises(AtlasError): compare_runs(left,right)
        right=evaluate_cases([{"id":"A","expected":"changed"},self.cases[1]],[])
        with self.assertRaises(AtlasError): compare_runs(left,right)

    def test_paired_forged_correctness_rejected(self):
        left=evaluate_cases(self.cases,[]); right=copy.deepcopy(left)
        right["per_case"][0]["correct"]=True
        with self.assertRaises(AtlasError): compare_runs(left,right)

    def test_binary_brier_and_coverage(self):
        result=evaluate_cases([{"id":"A","expected":True},{"id":"B","expected":False}],
                              [{"id":"A","answer":True,"probability":.8},{"id":"B","answer":False,"probability":.2}])
        self.assertAlmostEqual(result["calibration"]["brier_score"],.04)
        self.assertEqual(result["calibration"]["coverage"],1.)
        self.assertEqual(sum(b["count"] for b in result["calibration"]["bins"]),2)

    def test_uncalibrated_confidence_is_not_a_binary_outcome(self):
        with self.assertRaises(AtlasError): evaluate_cases(self.cases,[{"id":"A","probability":.8}])
        with self.assertRaises(AtlasError):
            evaluate_cases([{"id":"A","expected":True}],[{"id":"A","probability":float("nan")}])

    def test_retrieval_metrics_include_missing_query(self):
        queries=[{"id":"A","relevant_ids":["hit"]},{"id":"B","relevant_ids":["second"]}]
        result=evaluate_retrieval(queries,[{"id":"A","ranked_ids":["miss","hit"]}],k=2)
        self.assertEqual(result["macro_precision_at_k"],.25)
        self.assertEqual(result["macro_recall_at_k"],.5)
        self.assertEqual(result["mrr"],.25)

    def test_duplicate_retrieval_cannot_inflate_recall(self):
        with self.assertRaises(AtlasError):
            evaluate_retrieval([{"id":"A","relevant_ids":["hit"]}],[{"id":"A","ranked_ids":["hit","hit"]}])


class InputAndPersistence(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)

    def test_strict_json_all_entrypoints(self):
        for content in ('{"x":1e999}','{"x":1,"x":2}','{"x":NaN}'):
            with self.subTest(content=content), self.assertRaises(AtlasError): parse_json(content)
            path=self.root/"bad.json"; path.write_text(content)
            with self.assertRaises(AtlasError): ingest(path)

    def test_extraction_has_source_locations_and_truncation(self):
        path=self.root/"rows.csv"; path.write_text("name,value\n"+"sample,123\n"*500)
        result=ingest(path,max_chars=1000)
        self.assertTrue(result["truncated"])
        self.assertEqual(len(result["text"]),1000)
        self.assertEqual(result["segments"][0]["locator"],"table row 1")

    def test_pdf_truncation_is_not_hidden(self):
        class Page:
            def extract_text(self): return "x"*2000
        class Reader:
            is_encrypted=False
            pages=[Page(),Page()]
            def __init__(self,*args,**kwargs): pass
        path=self.root/"fake.pdf"; path.write_bytes(b"synthetic parser fixture")
        from types import SimpleNamespace
        with patch.dict("sys.modules",{"pypdf":SimpleNamespace(PdfReader=Reader)}):
            result=ingest(path,max_chars=1000)
        self.assertTrue(result["truncated"])
        self.assertEqual(result["pages_processed"],1)
        self.assertEqual(result["pages"],2)

    def test_budget_persists_limit_and_actual_overrun(self):
        path=self.root/"budget.sqlite3"; budget=Budget(path,"10")
        with self.assertRaises(AtlasError): Budget(path,"100")
        budget.reserve("one","5","provider",True)
        result=budget.settle("one","12")
        self.assertFalse(result["ok"])
        self.assertEqual(result["settled_usd"],"12")
        with self.assertRaises(AtlasError): budget.reserve("two","1","provider",True)
        with self.assertRaises(AtlasError): budget.amend_limit("20")
        self.assertTrue(budget.amend_limit("20",True)["ok"])

    def test_memory_corruption_is_not_silently_skipped(self):
        (self.root/"memory").mkdir()
        (self.root/"memory/corrupt.json").write_text("{broken")
        with self.assertRaises(AtlasError): retrieve_ranked(self.root,"question")

    def test_memory_exact_scope_and_receipt_revalidation(self):
        receipt=self.root/"validation.json"; atomic_json(receipt,{"passed":True,"tests":["fixture"],"limitations":"synthetic"})
        entry={"id":"method","kind":"method","method":"Check units","scope":"finance-extended","author":"author","reviewer":"reviewer",
               "expires_at":"2099-01-01","validation_artifact":"validation.json","validation_sha256":file_hash(receipt),"status":"validated"}
        promote(self.root,entry)
        self.assertEqual(retrieve_ranked(self.root,scope="finance"),[])
        self.assertEqual(len(retrieve_ranked(self.root,scope="finance-extended")),1)
        receipt.write_text("{}")
        with self.assertRaises(AtlasError): retrieve_ranked(self.root)

    def test_duplicate_backup_manifest_rejected_before_target_creation(self):
        row={"path":"state.sqlite3","size":1,"sha256":"a"*64}
        path=self.root/"bad.zip"
        with zipfile.ZipFile(path,"w") as output:
            output.writestr("MANIFEST.json",json.dumps({"schema_version":1,"files":[row,row]}))
            output.writestr("PROJECT/state.sqlite3","x")
        target=self.root/"restored"
        with self.assertRaises(AtlasError): restore(path,target)
        self.assertFalse(target.exists())

    def test_archive_path_aliases_and_case_collisions_rejected(self):
        for names in (["a//b"],["A","a"],["x","x/child"],["x","X/child"],["../escape"]):
            path=self.root/"unsafe.zip"
            with zipfile.ZipFile(path,"w") as output:
                for name in names: output.writestr(name,"x")
            with zipfile.ZipFile(path) as source, self.assertRaises(AtlasError):
                checked_members(source)

    def test_manifest_paths_are_portable_and_cannot_alias_directories(self):
        for names in (["A","a"],["x","X/child"]):
            with self.subTest(names=names),self.assertRaises(AtlasError):
                manifest_index([{"path":name,"size":1,"sha256":"a"*64} for name in names])

    def test_manifest_total_is_bounded(self):
        rows=[{"path":str(index),"size":100_000_000,"sha256":"a"*64} for index in range(6)]
        with self.assertRaises(AtlasError): manifest_index(rows)


class ProviderSchemas(unittest.TestCase):
    def test_malformed_response_is_not_empty_success(self):
        for response in ({},{"results":None},{"results":[None]},{"results":[{}]}):
            with self.subTest(response=response), patch("atlas.adapters.http_json",return_value=response), self.assertRaises(AtlasError):
                search("openalex","fixture")
        with patch("atlas.adapters.http_json",return_value={"results":[]}):
            self.assertEqual(search("openalex","fixture")["items"],[])

    def test_cursor_and_metadata_provenance(self):
        data={"message":{"items":[{"DOI":"10.1234/ABC","title":["Study"],"issued":{"date-parts":[[2020]]}}],
                         "total-results":11,"next-cursor":"next+cursor"}}
        with patch("atlas.adapters.http_json",return_value=data):
            result=search("crossref","fixture",cursor="*")
        self.assertIn("cursor=%2A",result["requested_url"])
        self.assertEqual(result["next_cursor"],"next+cursor")
        self.assertEqual(result["items"][0]["doi"],"10.1234/abc")
        self.assertEqual(result["items"][0]["publication_year"],2020)

    def test_endpoint_prefix_confusion_is_rejected(self):
        with self.assertRaises(AtlasError): http_json("https://api.crossref.org/works-unrelated","crossref")

    def test_http_body_uses_strict_json(self):
        class Response(io.BytesIO):
            headers={"Content-Type":"application/json"}
            status=200
        class Opener:
            def open(self,*args,**kwargs): return Response(b'{"x":1e999}')
        with self.assertRaises(AtlasError):
            http_json("https://api.crossref.org/works","crossref",opener=Opener())


if __name__=="__main__":
    unittest.main()
