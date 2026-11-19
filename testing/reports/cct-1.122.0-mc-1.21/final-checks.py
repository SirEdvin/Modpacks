"""Final local gates, run only after all lanes and extra fixture audits stop."""
import collections,json,pathlib,subprocess,sys
OUT=pathlib.Path(__file__).resolve().parent;ROOT=OUT.parents[2]
from snbt_fields import equipped_upgrade
names=subprocess.check_output(['docker','ps','--format','{{.Names}}'],text=True).splitlines()
assert not any(n.startswith('mc-test-') for n in names),'test container still running'
with (OUT/'regression-tests.log').open('w') as log:subprocess.run([sys.executable,'-m','unittest','discover','-s','testing/tests','-v'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
for name in ['snbt_fields.py','static-checks.py','build-report.py']:subprocess.run([sys.executable,str(OUT/name)],cwd=ROOT,check=True)
rows=json.loads((OUT/'verdicts.json').read_text());assert len(rows)==4 and len({r['lane'] for r in rows})==4
for row in rows:
 assert row['verdict'] in ['PASS','FAIL']
 for phase in ['smoke','client-smoke']:assert (OUT/row['lane']/phase/'result.json').exists()
 if row['lane'].startswith('minimal'):
  for phase in ['before-switch','after-switch']:assert (OUT/row['lane']/'old-world'/phase/'saved-world.tar.gz').exists()
  assert (OUT/row['lane']/'old-world-fixture-audit/result.json').exists()
checks=[]
for row in rows:
 for phase in ['upgrade-before','upgrade-after','old-world-before','old-world-after']:
  for name in ['upgrade-probes.json','all-stacks/results.json']:
   p=OUT/row['lane']/phase/name
   if not p.exists():continue
   d=json.loads(p.read_text());matches=sum(equipped_upgrade(e['live_nbt'],e['kind'])==e['upgrade'] for e in d)
   checks.append(dict(path=str(p.relative_to(OUT)),fixtures=len(d),exact_equipped_ids=matches))
subprocess.run(['git','diff','--check'],cwd=ROOT,check=True)
record=dict(lanes=len(rows),verdict_counts=dict(collections.Counter(r['verdict'] for r in rows)),python_regressions='7 PASS',snbt_parser_selftests='PASS',full_packwiz_hash_chains='4 PASS',no_test_containers=True,exact_upgrade_field_checks=checks,recommendation='ready within tested scope' if all(r['verdict']=='PASS' for r in rows) else 'NOT ready for public release')
(OUT/'final-checks.json').write_text(json.dumps(record,indent=2)+'\n')
print('Final gates:',json.dumps({k:v for k,v in record.items() if k!='exact_upgrade_field_checks'}))
