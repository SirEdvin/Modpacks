"""Reduce actual saved runtime evidence; missing evidence never passes."""
import collections,json,pathlib,re,sys
from typing import Any
OUT=pathlib.Path(__file__).resolve().parent
LANES=sys.argv[1:] or ['fabric-1.20','forge-1.20','minimal-fabric-1.20','minimal-forge-1.20']
def load(p) -> Any:return json.loads(p.read_text()) if p.exists() else None
def verdict(reasons,**kw) -> Any:return dict(verdict='FAIL' if reasons else 'PASS',failures=reasons,**kw)
def probe(p,roundtrip=False,stack=False):
 data=load(p/('all-stacks/results.json' if stack else 'upgrade-probes.json'))
 if not data:return dict(verdict='NOT RUN',path=str(p.relative_to(OUT)))
 bad=[]
 for e in data:
  d=e.get('lua',{}); reasons=[]
  if not e.get('upgrade_in_nbt'):reasons.append('equipped upgrade absent in live NBT')
  if not d or d.get('missing'):reasons.append('missing Lua')
  elif stack:
   if not d.get('present') or not d.get('methods') or not d.get('wrapOK'):reasons.append('peripheral unavailable')
   if roundtrip:
    if not d.get('callOK') or d.get('result')!='true':reasons.append('count-two native equip failed')
    if e['kind']=='turtle':
     expected_item=(e.get('item') or '')
     if expected_item and d.get('input',{}).get('name')!=expected_item:reasons.append('wrong input item')
     if d.get('input',{}).get('count')!=2 or d.get('input',{}).get('maxCount',0)<2 or d.get('remaining',{}).get('count')!=1:reasons.append('legal input count-two/remaining-one gate')
    elif 'Count: 1b' not in (e.get('remaining_input') or ''):reasons.append('remaining input not count one')
  else:
   if not d.get('presentAfter') or not d.get('methodsAfter') or not d.get('wrapOK'):reasons.append('peripheral unavailable')
   if roundtrip and not all(d.get(k) for k in ['unequipOK','equipOK','roundtripOK']):reasons.append('native single-item roundtrip failed')
   if d.get('typeBefore')!=d.get('typeAfter'):reasons.append('type changed during probe')
  if reasons:bad.append(dict(kind=e['kind'],upgrade=e['upgrade'],reasons=reasons))
 lifecycle=load(p/'lifecycle-result.json')
 if stack:
  manifest=load(p/'generated/authored-blocks.json');skipped=load(p/'all-stacks/nonstackable.json')
  if not manifest or skipped is None or len(data)+len(skipped)!=len(manifest['turtle_cells'])+len(manifest['pocket_cells'])+2:bad.append('stackable + nonstackable fixture coverage mismatch')
 expected_source=load(OUT/('baseline-artifacts.json' if p.name=='old-world-before' else 'assets.json')) or []
 expected={e['name']:e['sha256'] for e in expected_source};artifacts=load(p/'artifacts.json')
 if not artifacts or len(artifacts)!=10 or any(expected.get(e['name'])!=e['sha256'] for e in artifacts):bad.append('native phase installed JAR hash gate')
 if lifecycle is None or lifecycle['exit_code']:bad.append(dict(lifecycle=lifecycle))
 return verdict(bad,count=len(data),kinds=dict(collections.Counter(e['kind'] for e in data)),path=str(p.relative_to(OUT)))
def pair(p,prefix,stack=False):
 b=p/(prefix+'-before');a=p/(prefix+'-after');before=probe(b,True,stack);after=probe(a,False,stack)
 reasons=[]
 if before['verdict']!='PASS' or after['verdict']!='PASS':reasons.append('before/after gate')
 filename='all-stacks/results.json' if stack else 'upgrade-probes.json'
 bd=load(b/filename);ad=load(a/filename)
 if bd and ad:
  bm={(e['kind'],e['upgrade']):e for e in bd};am={(e['kind'],e['upgrade']):e for e in ad}
  if bm.keys()!=am.keys() or len(bm)!=len(bd):reasons.append('fixture identity mismatch')
  for key,e in bm.items():
   f=am.get(key,{});x=e.get('lua',{});y=f.get('lua',{})
   field='types' if stack else 'typeAfter'
   if x.get(field)!=y.get(field):reasons.append(str(key)+' changed peripheral types')
   if y.get('generatedAt',0)<=x.get('generatedAt',0):reasons.append(str(key)+' stale after-restart Lua')
 return verdict(reasons,before=before,after=after)
def smoke(p,client=False):
 d=load(p/'result.json');reasons=[]
 if not d:return dict(verdict='NOT RUN')
 if d['exit_code']:reasons.append('command exit '+str(d['exit_code']))
 artifacts=[e for e in d['artifacts'] if client or e['side']=='server']
 if len(artifacts)!=(10 if client else 5) or not all(e['matches_pack'] for e in artifacts):reasons.append('installed JAR hash gate')
 audit=load(p/'generated/authored-block-audit.json')
 if not audit:reasons.append('no fixture audit')
 else:
  for x,y in [('discovered','placed_and_verified'),('turtle_upgrades_discovered','single_upgrade_turtles_verified'),('pocket_upgrades_discovered','single_upgrade_pockets_on_lecterns_verified')]:
   if audit[x]!=audit[y]:reasons.append('fixture count mismatch '+x)
 lua=[load(f) for f in p.glob('lua-*.json')]
 if not lua or not all(e['generatedAt']/1000>=d['started_at'] for e in lua):reasons.append('missing/stale harness Lua')
 server=(p/'server-logs/latest.log').read_text(errors='replace') if (p/'server-logs/latest.log').exists() else ''
 if 'Saving chunks' not in server:reasons.append('missing clean world-save marker')
 if client:
  f=p/'client-logs/latest.log';text=f.read_text(errors='replace') if f.exists() else ''
  for pattern in ['Network Protocol Error','Preparing crash report','Exception in thread','Error executing task on Client','Reported exception thrown','Caught exception in thread','Error whilst processing packet','Encountered an unexpected exception','Critical error while reloading','ExceptionInInitializerError','Could not initialize class']:
   if pattern.lower() in text.lower():reasons.append(pattern)
  if not re.search(r'Loaded \d+ advancements|Recipes synchronized',text):reasons.append('missing fresh client join marker')
  if not re.search(r'joined the game|logged in with entity id',server):reasons.append('missing server join marker')
 return verdict(reasons,exit_code=d['exit_code'],seconds=d['seconds'],artifacts=artifacts,audit=audit,path=str(p.relative_to(OUT)))
rows=[]
for lane in LANES:
 p=OUT/lane;s=smoke(p/'smoke');c=smoke(p/'client-smoke',True);u=pair(p,'single' if lane=='fabric-1.20' else 'upgrade');stack=pair(p,'upgrade',True)
 control=load(p/'upgrade-after/stack-equip/results.json')
 single_prefix='single' if lane=='fabric-1.20' else 'upgrade'
 singles=load(p/(single_prefix+'-after')/'upgrade-probes.json') or []
 single_types={(e['kind'],e['upgrade']):e.get('lua',{}).get('typeAfter') for e in singles}
 for e in load(p/'upgrade-after/all-stacks/results.json') or []:
  expected=['modem'] if e['upgrade']=='computercraft:wireless_modem_normal' else single_types.get((e['kind'],e['upgrade']))
  if e.get('lua',{}).get('types')!=expected:
   stack['failures'].append('stack host peripheral does not match single-item host: '+e['upgrade']);stack['verdict']='FAIL'
 cv='PASS' if control and all(e['lua'].get('callOK') and e['lua'].get('result')=='true' and e['lua'].get('present') for e in control) else 'FAIL'
 old=pair(p,'old-world') if lane.startswith('minimal') else None
 checks=[s,c,u,stack]+([old] if old else [])
 overall='PASS' if all(e['verdict']=='PASS' for e in checks) and cv=='PASS' else 'FAIL'
 row=dict(lane=lane,verdict=overall,server_smoke=s,client_smoke=c,single_item_and_restart=u,all_stacks_and_restart=stack,stacked_pocket_regression=cv,old_world=old)
 if old:
  migration=load(p/'old-world/result.json');row['migration']=migration
  if not migration or migration['baseline_smoke']!=0 or migration['new_probe_command_exit']!=0 or migration['reprovisioned_after_switch']:row['old_world']['verdict']='FAIL';row['verdict']='FAIL'
 (p/'verdict.json').write_text(json.dumps(row,indent=2)+'\n');rows.append(row)
 print(lane,row['verdict'],'server='+s['verdict'],'client='+c['verdict'],'single/restart='+u['verdict'],'all-stacks/restart='+stack['verdict'],'pocket-control='+cv,'old='+str(old and old['verdict']),flush=True)
(OUT/'verdicts.json').write_text(json.dumps(rows,indent=2)+'\n')
