"""Sequential C13 execution; full outputs remain in per-lane evidence."""
import json,pathlib,subprocess,sys,time
OUT=pathlib.Path(__file__).resolve().parent;ROOT=OUT.parents[2]
lanes=['fabric-1.21','neoforge-1.21','minimal-fabric-1.21','minimal-neoforge-1.21']
for lane in lanes:
 print('START LANE',lane,flush=True)
 for script,args in [('run-lane.py',[]),('extend-lane.py',[])]+([('old-world.py',[])] if lane.startswith('minimal') else []):
  dest=OUT/lane;dest.mkdir(exist_ok=True)
  with (dest/(script+'.log')).open('w') as log:
   start=time.time()
   try:r=subprocess.run([sys.executable,str(OUT/script),lane]+args,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=7200);rc=r.returncode
   except subprocess.TimeoutExpired:rc=124
  (dest/(script+'.result.json')).write_text(json.dumps(dict(exit_code=rc,seconds=time.time()-start),indent=2)+'\n')
  print(lane,script,rc,flush=True)
 subprocess.run([sys.executable,str(OUT/'summarize.py')],cwd=ROOT,check=True)
 print('LANE COMPLETE',lane,flush=True)
