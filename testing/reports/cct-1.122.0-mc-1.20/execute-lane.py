"""Complete one lane sequentially; never run two copies or two lanes at once."""
import json,pathlib,subprocess,sys,time
OUT=pathlib.Path(__file__).resolve().parent;ROOT=OUT.parents[2];lane=sys.argv[1]
steps=[['run-lane.py',lane],['extend-lane.py',lane]]
if lane.startswith('minimal'):steps.append(['old-world.py',lane])
steps.append(['summarize.py',lane]);records=[]
for args in steps:
 print('START',lane,args[0],flush=True);start=time.time()
 with (OUT/(lane+'-'+args[0]+'.log')).open('w') as log:
  result=subprocess.run([sys.executable,str(OUT/args[0]),*args[1:]],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 records.append(dict(command=args,exit_code=result.returncode,seconds=time.time()-start))
 (OUT/(lane+'-commands.json')).write_text(json.dumps(records,indent=2)+'\n')
 print('END',lane,args[0],result.returncode,flush=True)
print('LANE COMPLETE',lane,flush=True)
