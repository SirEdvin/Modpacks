"""Reduce saved evidence to bounded, machine-readable lane verdicts."""
import collections,hashlib,json,pathlib,re
OUT=pathlib.Path(__file__).resolve().parent
LANES=['fabric-1.21','neoforge-1.21','minimal-fabric-1.21','minimal-neoforge-1.21']
def load(p):return json.loads(p.read_text()) if p.exists() else None
def check_probe(p,roundtrip=False):
 data=load(p/'upgrade-probes.json')
 if data is None:return {'verdict':'NOT RUN','path':str(p.relative_to(OUT))}
 bad=[]
 manifest=load(p/'generated/authored-blocks.json')
 if manifest:
  expected={(kind,e['id']) for kind,key in [('turtle','turtle_cells'),('pocket','pocket_cells')] for e in manifest[key]}
  actual={(e['kind'],e['upgrade']) for e in data}
  if actual!=expected or len(data)!=len(expected):bad.append({'inventory_mismatch':True,'expected':len(expected),'actual':len(data)})
 for e in data:
  d=e.get('lua',{})
  reasons=[]
  if not e.get('upgrade_in_nbt'):reasons.append('upgrade absent in live NBT')
  if e['kind']=='turtle' and 'RightUpgrade' in e.get('live_nbt',''):reasons.append('unexpected right upgrade')
  if not d:reasons.append('no Lua result')
  else:
   if not d.get('presentAfter'):reasons.append('peripheral absent')
   if not d.get('methodsAfter'):reasons.append('no peripheral methods')
   if not d.get('wrapOK'):reasons.append('peripheral.wrap failed')
   if d.get('phase')!=p.name:reasons.append('stale Lua report phase')
   if roundtrip and (not d.get('unequipOK') or not d.get('equipOK') or not d.get('roundtripOK')):reasons.append('native equip round-trip failed')
   if d.get('typeBefore')!=d.get('typeAfter'):reasons.append('peripheral type changed within probe')
  if reasons:bad.append({'kind':e['kind'],'upgrade':e['upgrade'],'reasons':reasons})
 return dict(verdict='FAIL' if bad else 'PASS',count=len(data),kinds=dict(collections.Counter(e['kind'] for e in data)),failures=bad,path=str(p.relative_to(OUT)),min_generatedAt=min((e['lua']['generatedAt'] for e in data if 'lua' in e),default=None))
def smoke(p,client=False):
 d=load(p/'result.json')
 if not d:return {'verdict':'NOT RUN'}
 reasons=[]
 if d['exit_code']:reasons.append(f'command exit {d["exit_code"]}')
 sides={'client','server'} if client else {'server'}
 artifacts=[a for a in d['artifacts'] if a['side'] in sides]
 if len(artifacts)!=(10 if client else 5) or not all(a['matches_pack'] for a in artifacts):reasons.append('installed artifact gate failed')
 if client:
  f=p/'client-logs/latest.log'
  text=f.read_text(errors='replace') if f.exists() else ''
  patterns=['Network Protocol Error','Preparing crash report','Exception in thread','Error executing task on Client','Reported exception thrown','Caught exception in thread','Error whilst processing packet','Encountered an unexpected exception','Critical error while reloading','Failed to collect creative tab','Could not initialize class site.siredvin']
  for pattern in patterns:
   if pattern.lower() in text.lower():reasons.append(pattern)
 return dict(verdict='FAIL' if reasons else 'PASS',exit_code=d['exit_code'],reasons=reasons,seconds=d['seconds'],artifacts=artifacts,path=str(p.relative_to(OUT)))
def persistence(before,after):
 a=load(before/'upgrade-probes.json');b=load(after/'upgrade-probes.json')
 if a is None or b is None:return dict(verdict='NOT RUN')
 index={(e['kind'],e['upgrade'],e['cid']):e for e in b}
 failures=[];survived=0
 for e in a:
  key=(e['kind'],e['upgrade'],e['cid']);v=index.get(key,{})
  if v.get('upgrade_in_nbt') and v.get('lua',{}).get('presentAfter') and v.get('lua',{}).get('typeAfter')==e.get('lua',{}).get('typeAfter') and v.get('lua',{}).get('methodsAfter'):
   survived+=1
  else:failures.append(dict(kind=e['kind'],upgrade=e['upgrade'],cid=e['cid']))
 return dict(verdict='PASS' if not failures and len(a)==len(b) else 'FAIL',before=len(a),after=len(b),survived=survived,failures=failures)
results=[]
for lane in LANES:
 p=OUT/lane
 a=smoke(p/'smoke');b=smoke(p/'client-smoke',True)
 before=check_probe(p/'upgrade-before',True);after=check_probe(p/'upgrade-after')
 upgrade=dict(verdict='PASS' if before['verdict']==after['verdict']=='PASS' else 'FAIL',before=before,after=after)
 upgrade['persistence']=persistence(p/'upgrade-before',p/'upgrade-after')
 if upgrade['persistence']['verdict']!='PASS':upgrade['verdict']='FAIL'
 stack=load(p/'upgrade-after/stack-equip/results.json')
 if stack is not None:
  upgrade['stack_equip']={'verdict':'PASS' if len(stack)==4 and all(e['lua'].get('callOK') and e['lua'].get('result')=='true' and e['lua'].get('present') for e in stack) else 'FAIL','results':stack}
  if upgrade['stack_equip']['verdict']=='FAIL':upgrade['verdict']='FAIL'
 old=None
 if lane.startswith('minimal'):
  ob=check_probe(p/'old-world-before',True);oa=check_probe(p/'old-world-after')
  old=dict(verdict='PASS' if ob['verdict']==oa['verdict']=='PASS' else 'FAIL',before=ob,after=oa)
  old['persistence']=persistence(p/'old-world-before',p/'old-world-after')
  if old['persistence']['verdict']!='PASS':old['verdict']='FAIL'
  blocks=load(p/'old-world-after/block-retention.json')
  if blocks is not None:
   target=[e for e in blocks if not e['block'].startswith('smarthome_appliances:')]
   prior=load(p/'old-world/before-switch/generated/authored-block-audit.json')
   old['block_retention']=dict(target_count=len(target),target_retained=sum(e['retained'] for e in target),wired=sum(e['wired'] for e in target),expected_wired=prior['wired_peripheral_count'] if prior else None,intentionally_removed=[e['block'] for e in blocks if not e['retained'] and e['block'].startswith('smarthome_appliances:')])
   if not all(e['retained'] for e in target) or prior and old['block_retention']['wired']!=prior['wired_peripheral_count']:old['verdict']='FAIL'
 verdict='PASS' if a['verdict']==b['verdict']==upgrade['verdict']=='PASS' and (old is None or old['verdict']=='PASS') else 'FAIL'
 results.append(dict(lane=lane,verdict=verdict,server_smoke=a,client_smoke=b,upgrade_checks=upgrade,old_world=old))
(OUT/'verdicts.json').write_text(json.dumps(results,indent=2)+'\n')
for e in results: print(e['lane'],e['verdict'],'server='+e['server_smoke']['verdict'],'client='+e['client_smoke']['verdict'],'upgrades='+e['upgrade_checks']['verdict'],'old='+('N/A' if e['old_world'] is None else e['old_world']['verdict']))
