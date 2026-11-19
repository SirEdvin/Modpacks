import pathlib, subprocess, json, time, shutil, hashlib, tomllib, os, sys
ROOT=pathlib.Path(__file__).resolve().parents[3]
OUT=pathlib.Path(__file__).resolve().parent
packs={'fabric-1.21':'FabricCreative-1.21','neoforge-1.21':'NeoForgeCreative-1.21','minimal-fabric-1.21':'FabricMinimal-1.21','minimal-neoforge-1.21':'NeoForgeMinimal-1.21'}
lane=sys.argv[1]; pack=packs[lane]
results=[]
for phase in ['smoke','client-smoke']:
 dest=OUT/lane/phase;dest.mkdir(parents=True,exist_ok=True)
 runtime=ROOT/'testing/runtime'/lane
 start=time.time()
 print(f'START {lane} {phase}',flush=True)
 with (dest/'command.log').open('w') as log:
  try:
   rc=subprocess.run([str(ROOT/'testing/bin/mc-test'),phase,lane],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=2400,env={**os.environ,'MC_TEST_CLIENT_STABILITY_SECONDS':'30'}).returncode
  except subprocess.TimeoutExpired:
   rc=124
   subprocess.run([str(ROOT/'testing/bin/mc-test'),'stop',lane],stdout=log,stderr=subprocess.STDOUT)
 fresh=[]
 for base,label in [(ROOT/'testing/reports'/lane,'harness'),(runtime/'generated','generated'),(runtime/'data/logs','server-logs'),(runtime/'data/crash-reports','server-crash-reports'),(runtime/'client/.minecraft/logs','client-logs'),(runtime/'client/.minecraft/crash-reports','client-crash-reports')]:
  if base.exists():
   for src in base.rglob('*'):
    if src.is_file() and not src.is_symlink() and src.stat().st_mtime>=start:
     target=dest/label/src.relative_to(base);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,target);fresh.append(str(target.relative_to(dest)))
 for src in (runtime/'data/playground/computercraft/computer').glob('*/authored-peripherals.json'):
  if src.stat().st_mtime>=start: shutil.copy2(src,dest/('lua-'+src.parent.name+'.json'))
 artifacts=[]
 for mod in ['unlimitedperipheralworks','turtlematic','cloudsolutions','digitalitems','cc-tweaked']:
  metadata=tomllib.loads((ROOT/pack/f'mods/{mod}.pw.toml').read_text())
  for side,base in [('server',runtime/'data/mods'),('client',runtime/'client/.minecraft/mods')]:
   jar=base/metadata['filename']
   if jar.exists():
    data=jar.read_bytes(); digest=hashlib.new(metadata['download']['hash-format'],data).hexdigest()
    artifacts.append({'mod':mod,'side':side,'name':jar.name,'sha256':hashlib.sha256(data).hexdigest(),'matches_pack':digest==metadata['download']['hash']})
 record={'lane':lane,'phase':phase,'exit_code':rc,'started_at':start,'seconds':round(time.time()-start,1),'fresh_files':fresh,'artifacts':artifacts}
 (dest/'result.json').write_text(json.dumps(record,indent=2)+'\n')
 results.append({k:v for k,v in record.items() if k not in ['artifacts','fresh_files']})
 (OUT/lane/'matrix.json').write_text(json.dumps(results,indent=2)+'\n')
 print(f'END {lane} {phase} rc={rc} seconds={record["seconds"]} artifacts={len(artifacts)} match={all(a["matches_pack"] for a in artifacts)}',flush=True)
print('LANE PHASES COMPLETE',flush=True)
