"""One lane, durable sequential steps, retain failures and run regression suite."""
import json,pathlib,subprocess,sys,time
OUT=pathlib.Path(__file__).resolve().parent;ROOT=OUT.parents[2];lane=sys.argv[1]
steps=[[sys.executable,str(OUT/'run-lane.py'),lane],[sys.executable,str(OUT/'extend-lane.py'),lane]]
if lane.startswith('minimal'):
 steps += [[sys.executable,str(OUT/'old-world.py'),lane],[sys.executable,str(OUT/'audit-old-fixtures.py'),lane]]
steps += [[sys.executable,'-m','unittest','discover','-s','testing/tests','-v'],[sys.executable,str(OUT/'summarize.py'),lane]]
records=[]
for i,args in enumerate(steps):
 name=pathlib.Path(args[1]).name if args[1]!='-m' else 'regression-tests'
 print('START',lane,name,flush=True);started=time.time();logpath=OUT/f'{lane}-{name}.log'
 with logpath.open('w') as log:
  rc=subprocess.run(args,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT).returncode
 records.append(dict(command=args,exit_code=rc,seconds=round(time.time()-started,1),log=str(logpath.relative_to(OUT))))
 (OUT/f'{lane}-commands.json').write_text(json.dumps(records,indent=2)+'\n')
 print('END',lane,name,rc,flush=True)
print('LANE COMPLETE',lane,flush=True)
