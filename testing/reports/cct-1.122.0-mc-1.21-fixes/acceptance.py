"""Supplement C15 reducers with creative gates, regressions, all client-phase logs."""
import pathlib,json,re,collections,sys
OUT=pathlib.Path(__file__).resolve().parent
lanes=sys.argv[1:] or ['fabric-1.21','neoforge-1.21','minimal-fabric-1.21','minimal-neoforge-1.21']
rows=[]
critical=['Failed to collect creative tab','ComputerPlatformRegistries','Critical error while reloading','Network Protocol Error','Preparing crash report','Error executing task on Client','Reported exception thrown','ExceptionInInitializerError','Could not initialize class','Error whilst processing packet','Encountered an unexpected exception']
for lane in lanes:
 p=OUT/lane;row=json.loads((p/'verdict.json').read_text());checks=[]
 for f in p.glob('*/client-logs/latest.log'):
  text=f.read_text(errors='replace');hits=[dict(line=i,text=line) for i,line in enumerate(text.splitlines(),1) if any(s.lower() in line.lower() for s in critical)]
  checks.append(dict(path=str(f.relative_to(OUT)),critical_hits=hits))
 row['all_client_log_scan']=dict(verdict='PASS' if checks and not any(c['critical_hits'] for c in checks) else 'FAIL',logs=checks)
 commands=json.loads((OUT/f'{lane}-commands.json').read_text());reg=[c for c in commands if c['command'][1:3]==['-m','unittest']]
 row['python_regressions']=dict(verdict='PASS' if len(reg)==1 and reg[0]['exit_code']==0 else 'FAIL',commands=reg)
 if lane=='fabric-1.21':
  f=p/'upgrade-before/emi-index-observation.tsv';text=f.read_text() if f.exists() else ''
  manifest=json.loads((p/'upgrade-before/generated/authored-blocks.json').read_text())
  evidence=[]
  for kind,key,prefix in [('turtle','turtle_cells','computercraft:turtle_'),('pocket','pocket_cells','computercraft:pocket_computer_')]:
   for e in manifest[key]:
    # Exact namespaced IDs in actual EMI component changes; never infer from installed JARs.
    matches=[s for s in text.splitlines() if s.startswith(prefix) and re.search(re.escape(e['id'])+r'(?=[^a-z0-9_/.\-]|$)',s)]
    evidence.append(dict(kind=kind,upgrade=e['id'],observed=bool(matches),variants=len(matches)))
  row['creative_emi_index']=dict(verdict='PASS' if text and evidence and all(e['observed'] for e in evidence) else 'FAIL',source=str(f.relative_to(OUT)),total_line=text.splitlines()[0] if text else None,upgrades=evidence)
 if lane=='neoforge-1.21':
  f=p/'upgrade-before/upgrade-probes.json';data=json.loads(f.read_text()) if f.exists() else []
  ids=['peripheralworks:'+tier+'_magic_tome' for tier in ['novice','apprentice','archmage','caster']]
  tomes=[e for e in data if e['upgrade'] in ids and e['kind']=='pocket']
  ars=[a.name for a in (OUT.parents[2]/'testing/runtime'/lane/'data/mods').glob('ars_nouveau*.jar')]
  row['ars_magic_tomes']=dict(verdict='PASS' if len(tomes)==4 and ars and all(e.get('lua',{}).get('equipOK') and e['lua'].get('unequipOK') and e['lua'].get('presentAfter') for e in tomes) else 'FAIL',ars_jars=ars,upgrades=[dict(upgrade=e['upgrade'],lua=e.get('lua')) for e in tomes])
 gates=[v for k,v in row.items() if k in ['all_client_log_scan','python_regressions','creative_emi_index','ars_magic_tomes']]
 if any(e['verdict']!='PASS' for e in gates):row['verdict']='FAIL'
 (p/'verdict.json').write_text(json.dumps(row,indent=2)+'\n');rows.append(row)
 print(lane,row['verdict'],'extra gates',[(k,v['verdict']) for k,v in row.items() if k in ['all_client_log_scan','python_regressions','creative_emi_index','ars_magic_tomes']])
(OUT/'verdicts.json').write_text(json.dumps(rows,indent=2)+'\n')
