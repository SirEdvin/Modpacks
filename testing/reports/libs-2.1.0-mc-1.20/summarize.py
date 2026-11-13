"""Reduce saved evidence to bounded, machine-readable lane verdicts."""
import collections,hashlib,json,pathlib,re
OUT=pathlib.Path(__file__).resolve().parent
LANES=['fabric-1.20','forge-1.20','minimal-fabric-1.20','minimal-forge-1.20']
def load(p):return json.loads(p.read_text()) if p.exists() else None
def check_probe(p,roundtrip=False):
 data=load(p/'upgrade-probes.json')
 if data is None:return {'verdict':'NOT RUN','path':str(p.relative_to(OUT))}
 bad=[]
 for e in data:
  d=e.get('lua',{})
  reasons=[]
  if not e.get('upgrade_in_nbt'):reasons.append('upgrade absent in live NBT')
  if not d:reasons.append('no Lua result')
  else:
   if not d.get('presentAfter'):reasons.append('peripheral absent')
   if not d.get('methodsAfter'):reasons.append('no peripheral methods')
   if not d.get('wrapOK'):reasons.append('peripheral.wrap failed')
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
  patterns=['Network Protocol Error','Preparing crash report','Exception in thread','Error executing task on Client','Reported exception thrown','Caught exception in thread','Error whilst processing packet','Encountered an unexpected exception','Critical error while reloading']
  for pattern in patterns:
   if pattern.lower() in text.lower():reasons.append(pattern)
 return dict(verdict='FAIL' if reasons else 'PASS',exit_code=d['exit_code'],reasons=reasons,seconds=d['seconds'],artifacts=artifacts,path=str(p.relative_to(OUT)))
results=[]
for lane in LANES:
 p=OUT/lane
 a=smoke(p/'smoke');b=smoke(p/'client-smoke',True)
 before=check_probe(p/'upgrade-before',True);after=check_probe(p/'upgrade-after')
 upgrade=dict(verdict='PASS' if before['verdict']==after['verdict']=='PASS' else 'FAIL',before=before,after=after)
 stack=load(p/'upgrade-after/stack-equip/results.json')
 if stack is not None:
  upgrade['stack_equip']={'verdict':'PASS' if all(e['lua'].get('callOK') and e['lua'].get('result')=='true' and e['lua'].get('present') for e in stack) else 'FAIL','results':stack}
  if upgrade['stack_equip']['verdict']=='FAIL':upgrade['verdict']='FAIL'
 old=None
 if lane.startswith('minimal'):
  ob=check_probe(p/'old-world-before',True);oa=check_probe(p/'old-world-after')
  old=dict(verdict='PASS' if ob['verdict']==oa['verdict']=='PASS' else 'FAIL',before=ob,after=oa)
 verdict='PASS' if a['verdict']==b['verdict']==upgrade['verdict']=='PASS' and (old is None or old['verdict']=='PASS') else 'FAIL'
 results.append(dict(lane=lane,verdict=verdict,server_smoke=a,client_smoke=b,upgrade_checks=upgrade,old_world=old))
(OUT/'verdicts.json').write_text(json.dumps(results,indent=2)+'\n')
for e in results: print(e['lane'],e['verdict'],'server='+e['server_smoke']['verdict'],'client='+e['client_smoke']['verdict'],'upgrades='+e['upgrade_checks']['verdict'],'old='+('N/A' if e['old_world'] is None else e['old_world']['verdict']))
