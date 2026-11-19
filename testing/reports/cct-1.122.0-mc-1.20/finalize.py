"""Final evidence validation and authorized draft-PR publication.
Run only once after ALL four lane pipelines have finished.
"""
import hashlib,json,pathlib,subprocess,sys
OUT=pathlib.Path(__file__).resolve().parent;ROOT=OUT.parents[2]
def run(args,**kw):
 kw.setdefault('cwd',ROOT)
 return subprocess.run(args,check=True,**kw)
def output(args):return subprocess.check_output(args,cwd=ROOT,text=True).strip()
assert not any('mc-test-' in line for line in output(['docker','ps','--format','{{.Names}}']).splitlines()),'test containers still running'
with (OUT/'regression-tests.log').open('w') as f:run([sys.executable,'-m','unittest','discover','-s','testing/tests','-v'],stdout=f,stderr=subprocess.STDOUT)
for pack in ['FabricCreative','ForgeCreative','FabricMinimal-1.20','ForgeMinimal-1.20']:
 before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/pack).rglob('*') if p.is_file()}
 for _ in range(2):
  with (OUT/(pack+'-final-refresh.log')).open('a') as f:run(['packwiz','refresh'],cwd=ROOT/pack,stdout=f,stderr=subprocess.STDOUT)
 after={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/pack).rglob('*') if p.is_file()}
 assert before==after,pack+' did not restore/refresh deterministically'
run([sys.executable,str(OUT/'build-report.py')])
rows=json.loads((OUT/'verdicts.json').read_text());assert len(rows)==4
checks=[]
for lane in ['minimal-fabric-1.20','minimal-forge-1.20']:
 p=OUT/lane;before=json.loads((p/'old-world-before/generated/authored-blocks.json').read_text());after=json.loads((p/'old-world-after/generated/authored-blocks.json').read_text())
 audit=json.loads((p/'old-world-after/generated/authored-block-audit.json').read_text())
 assert before['cells']==after['cells'] and before['turtle_cells']==after['turtle_cells'] and before['pocket_cells']==after['pocket_cells']
 checks.append(dict(lane=lane,same_manifest=True,blocks_survived=audit['placed_and_verified'],wired_peripherals_survived=audit['wired_peripheral_count'],turtles_survived=audit['single_upgrade_turtles_verified'],pocket_displays_survived=audit['single_upgrade_pockets_on_lecterns_verified'],removed_or_failed_ids=[]))
(OUT/'old-world-survival.json').write_text(json.dumps(checks,indent=2)+'\n')
critical=[]
for r in rows:
 lane=r['lane'];phases=['smoke','client-smoke','upgrade-before','upgrade-after']+(['single-before','single-after'] if lane=='fabric-1.20' else [])+(['old-world-before','old-world-after'] if lane.startswith('minimal') else [])
 for phase in phases:
  for f in (OUT/lane/phase).rglob('latest.log'):
   text=f.read_text(errors='replace').lower()
   for pattern in ['ExceptionInInitializerError','Could not initialize class','Network Protocol Error','Error constructing UpgradeData','Critical error while reloading','Preparing crash report','Encountered an unexpected exception']:
    if pattern.lower() in text:critical.append(dict(path=str(f.relative_to(OUT)),pattern=pattern))
(OUT/'critical-log-scan.json').write_text(json.dumps(critical,indent=2)+'\n')
assert not critical,'critical diagnostics require review before publishing recommendation'
run(['git','diff','--check']);assert not output(['git','status','--short']),'unexpected tracked modifications'
run([sys.executable,str(OUT/'archive-evidence.py')])
compact=[p for p in OUT.iterdir() if p.is_file() and (p.suffix in ['.py','.json'] or p.name=='README.md') and p.name not in ['evidence-files.json','pr-receipt.json']]
compact += [OUT/r['lane']/'verdict.json' for r in rows]
run(['git','add','-f',*[str(p.relative_to(ROOT)) for p in compact]])
run(['git','diff','--cached','--check'])
run(['git','commit','-m','test: record CC:Tweaked 1.122.0 four-lane 1.20.1 retest'])
head=output(['git','rev-parse','HEAD']);branch=output(['git','branch','--show-current'])
run(['git','push','--set-upstream','origin',branch])
url=output(['gh','pr','create','--repo','SirEdvin/Modpacks','--base','main','--head',branch,'--draft','--title','test: verify CC:Tweaked 1.122.0 on Minecraft 1.20.1','--body-file',str(OUT/'README.md')])
pr=json.loads(output(['gh','pr','view',url,'--repo','SirEdvin/Modpacks','--json','number,url,state,isDraft,headRefOid,baseRefName']))
assert pr['headRefOid']==head and pr['baseRefName']=='main' and pr['state']=='OPEN' and pr['isDraft']
(OUT/'pr-receipt.json').write_text(json.dumps(pr,indent=2)+'\n')
print('PUBLISHED',json.dumps(pr));print('SURVIVAL',json.dumps(checks));print('RECOMMENDATION','READY for MC 1.20.1' if all(r['verdict']=='PASS' for r in rows) else 'NOT READY');print('ARCHIVE', (OUT/'evidence-archive.json').read_text())
