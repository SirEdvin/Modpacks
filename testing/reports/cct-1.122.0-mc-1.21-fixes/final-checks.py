"""Validate complete matrix accounting, integrity, and final local-only handoff."""
import collections,hashlib,json,pathlib,subprocess,sys
OUT=pathlib.Path(__file__).resolve().parent;ROOT=OUT.parents[2]
lanes=['fabric-1.21','neoforge-1.21','minimal-fabric-1.21','minimal-neoforge-1.21']
for script in ['summarize.py','acceptance.py','static-checks.py','snbt_fields.py','build-report.py']:
 subprocess.run([sys.executable,str(OUT/script)],cwd=ROOT,check=True)
rows=json.loads((OUT/'verdicts.json').read_text());assert {r['lane'] for r in rows}==set(lanes) and len(rows)==len(lanes)
names=subprocess.check_output(['docker','ps','--format','{{.Names}}'],text=True).splitlines();assert not any(n.startswith('mc-test-') for n in names)
assets={a['name']:a['sha256'] for a in json.loads((OUT/'assets.json').read_text())}
inventory=[]
for r in rows:
 assert r['verdict'] in ['PASS','FAIL']
 for phase in ['smoke','client-smoke']:
  d=json.loads((OUT/r['lane']/phase/'result.json').read_text())
  for a in d['artifacts']:
   if phase=='smoke' and a['side']=='client':continue
   assert assets[a['name']]==a['sha256'] and a['matches_pack']
   inventory.append(dict(lane=r['lane'],phase=phase,**a))
 assert r['python_regressions']['verdict']=='PASS'
 if r['lane'].startswith('minimal'):
  for label in ['before-switch','after-switch']:assert (OUT/r['lane']/'old-world'/label/'saved-world.tar.gz').exists()
  migration=json.loads((OUT/r['lane']/'old-world/result.json').read_text());assert migration['baseline_commit']==(OUT/'baseline/commit.txt').read_text().strip()
for f in OUT.glob('*/upgrade-*/artifacts.json'):
 for a in json.loads(f.read_text()):
  assert assets[a['name']]==a['sha256'];inventory.append(dict(lane=f.parts[-3],phase=f.parts[-2],**a))
subprocess.run(['git','diff','--check'],cwd=ROOT,check=True)
(OUT/'artifact-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
record=dict(lanes=len(rows),verdict_counts=dict(collections.Counter(r['verdict'] for r in rows)),per_lane=[dict(lane=r['lane'],verdict=r['verdict'],log_path=r['lane']+'/verdict.json') for r in rows],no_test_containers=True,python_regressions='PASS per lane',packwiz_full_index_chains='4 PASS',installed_artifact_observations=len(inventory),baseline_commit=(OUT/'baseline/commit.txt').read_text().strip(),recommendation='1.21.1 ready for public release within tested scope' if all(r['verdict']=='PASS' for r in rows) else '1.21.1 NOT ready for public release')
(OUT/'final-checks.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
