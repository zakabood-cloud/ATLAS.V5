#!/usr/bin/env python3
"""Paired local checker defects. No model calls; no research-quality score."""
import copy
import csv
import json
from pathlib import Path, PurePosixPath
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import zipfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from atlas.archive import extract_checked
from atlas.demo import evidence_fixture, complete
from atlas.evidence import validate_evidence
from atlas.io import AtlasError, atomic_json, file_hash, read_json, now
from atlas.project import Project
from atlas.structure import check
from scripts.release_common import release_files

ROOT=Path(__file__).resolve().parents[1]


def extract_original(dest):
    manifest=read_json(ROOT/'reference/original_manifest.json'); archive=ROOT/'reference/ORIGINAL_ATLAS_UNMODIFIED.zip'
    if file_hash(archive)!=manifest['archive_sha256']: raise AtlasError('Original archive changed')
    with zipfile.ZipFile(archive) as z:
        extract_checked(z,dest)
    expected={row['path']:row['sha256'] for row in manifest['files']}
    actual={p.relative_to(dest).as_posix():file_hash(p) for p in dest.rglob('*') if p.is_file()}
    if expected!=actual: raise AtlasError('Original manifest mismatch')
    return dest/'ATLAS_Claude_Code_Research_OS_Repository'


def original_project(root,case):
    p=root/'research_os/projects/case'; p.mkdir(parents=True)
    stage='BANANA' if case=='arbitrary_stage' else 'COMPLETE' if case=='empty_completion_artifacts' else 'AUDIT'
    atomic_json(p/'state.json',{'stage':stage})
    source={'source_id':'S1','source_url_or_file':'local:synthetic-fixture','original_origin_group':'fixture'}
    claim={'claim_id':'C1','claim_text':'Synthetic fixture reports ten.','verification_status':'V2','source_ids':'S1','materiality':'critical'}
    sources=[source]; claims=[claim]
    if case=='fabricated_source_self_attested_v2': source['source_url_or_file']='https://fabricated.invalid/source'
    if case=='critical_claim_without_source': claim['source_ids']=''
    if case=='blank_claim_identifier': claim['claim_id']=''
    if case=='missing_source_reference': claim['source_ids']='MISSING'
    if case=='duplicate_source_id': sources.append(copy.deepcopy(source))
    if case=='unverified_critical_claim': claim['verification_status']='V0'
    if case=='invalid_enums': claim.update(materiality='banana',verification_status='world-best')
    for name,rows in [('source_registry.csv',sources),('claim_ledger.csv',claims)]:
        out=p/'03_research'/name; out.parent.mkdir(exist_ok=True)
        with out.open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    if case=='corrupted_state': (p/'state.json').write_text('{invalid')
    if stage=='COMPLETE':
        for name in ['01_intake/deliverables_contract.md','04_audit/quality_gate_decision.md','05_deliverables/deliverable_manifest.md']:
            q=p/name; q.parent.mkdir(exist_ok=True); q.write_text('')
    return p


def upgraded_project(root,case):
    if case=='arbitrary_stage':
        try: Project.create(root,'case','Synthetic','general').advance('BANANA')
        except AtlasError as e: return False,str(e)
    if case=='corrupted_state':
        p=Project.create(root,'case','Synthetic','general'); p.db.write_bytes(b'corrupted')
        try: p.status()
        except AtlasError as e: return False,str(e)
    if case=='empty_completion_artifacts':
        p=complete(root); p.reopen('DELIVER','Inject empty output'); (p.path/'outputs/demo-report.md').write_text('')
        try: p.advance('MEMORY')
        except AtlasError as e: return False,str(e)
    d=evidence_fixture(root)
    if case=='fabricated_source_self_attested_v2': d['sources'][0].update(source_type='web',url='https://fabricated.invalid/source')
    if case=='critical_claim_without_source': d['claims'][0]['source_ids']=[]
    if case=='blank_claim_identifier': d['claims'][0]['id']=''
    if case=='missing_source_reference': d['claims'][0]['source_ids']=['MISSING']
    if case=='duplicate_source_id': d['sources'].append(copy.deepcopy(d['sources'][0]))
    if case=='unverified_critical_claim': d['assessments']=[]
    if case=='invalid_enums': d['claims'][0]['kind']='world-best'
    result=validate_evidence(d,root)
    return result['ok'],result['errors']


def run():
    install_cases=['pristine_install','malformed_yaml_frontmatter','invalid_python_payload','missing_required_file','meaningless_policy_payload']
    project_cases=['arbitrary_stage','fabricated_source_self_attested_v2','critical_claim_without_source','blank_claim_identifier','missing_source_reference','duplicate_source_id','unverified_critical_claim','invalid_enums','corrupted_state','empty_completion_artifacts']
    records=[]
    with tempfile.TemporaryDirectory(dir=ROOT) as temp:
        tmp=Path(temp); original=extract_original(tmp/'original')
        for i,case in enumerate(install_cases+project_cases):
            old=tmp/f'old-{i}'; shutil.copytree(original,old)
            new=tmp/f'new-{i}'; new.mkdir()
            for source in release_files(ROOT):
                target=new/source.relative_to(ROOT)
                target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(source,target)
            if case in install_cases:
                if case=='malformed_yaml_frontmatter':
                    for base,rel in [(old,'.claude/agents/domain-researcher.md'),(new,'.github/agents/domain-researcher.agent.md')]:
                        (base/rel).write_text('---\nname: [invalid\ndescription: invalid YAML but enough bytes\n---\nInstructions.\n')
                elif case=='invalid_python_payload':
                    (old/'research_os/engine/audit_project.py').write_text('def broken(:\n'+'# invalid syntax padding\n'*3)
                    (new/'scripts/demo.py').write_text('def broken(:\n'+'# invalid syntax padding\n'*3)
                elif case=='missing_required_file':
                    (old/'CLAUDE.md').unlink(); (new/'AGENTS.md').unlink()
                elif case=='meaningless_policy_payload':
                    (old/'research_os/policies/SECURITY_AND_PERMISSIONS.md').write_text('meaningless content '*8)
                    (new/'docs/SECURITY.md').write_text('meaningless content '*8)
                cmd=[sys.executable,'research_os/engine/verify_install.py']; report=check(new); accepted=report['ok']; detail=report['errors']
            else:
                p=original_project(old,case); cmd=[sys.executable,'research_os/engine/audit_project.py',str(p)]
                accepted,detail=upgraded_project(new,case)
            result=subprocess.run(cmd,cwd=old,capture_output=True,text=True,timeout=30)
            expected=case in {'pristine_install','meaningless_policy_payload'}
            records.append({'case':case,'original_accepted':result.returncode==0,'original_exit_code':result.returncode,
              'original_stdout':result.stdout,'original_stderr':result.stderr,'upgraded_accepted':accepted,'upgraded_detail':detail,
              'expected_upgraded_accepted':expected,'upgraded_matches_expected':accepted==expected,
              'interpretation':'Known semantic limitation; not a valid policy' if case=='meaningless_policy_payload' else 'Paired local-control defect, not live research performance'})
    return {'at':now(),'python':sys.version,
      'baseline_identity':'Historical original Claude prototype; not the supplied ATLAS Copilot v3 repository',
      'scope':'15 deliberately selected paired control cases; schemas adapted, intended defect held constant; no model calls or quality score',
      'all_upgraded_expected':all(r['upgraded_matches_expected'] for r in records),'results':records}


if __name__=='__main__':
    result=run(); path=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'reports/paired_controls.json'; atomic_json(path,result)
    print(json.dumps({'path':str(path),'cases':len(result['results']),'all_upgraded_expected':result['all_upgraded_expected']},indent=2))
    sys.exit(0 if result['all_upgraded_expected'] else 1)
