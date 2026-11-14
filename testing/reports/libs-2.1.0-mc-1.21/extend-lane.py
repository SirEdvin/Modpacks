"""Run real upgrade programs before/after a clean dedicated-server restart.

Does not provision or replace fixtures on restart. For an old-world pair use
`... setup old-world-before`, switch Packwiz source, then `... restart old-world-after`.
"""
import json, os, pathlib, shutil, subprocess, sys, time
ROOT=pathlib.Path(__file__).resolve().parents[3];OUT=pathlib.Path(__file__).resolve().parent
lane=sys.argv[1]; mode=sys.argv[2] if len(sys.argv)>2 else 'pair'; label=sys.argv[3] if len(sys.argv)>3 else 'upgrade'
runtime=ROOT/'testing/runtime'/lane
mc=str(ROOT/'testing/bin/mc-test')
env={**os.environ,'MC_TEST_ONLINE_MODE':'false'}
compose=['docker','compose','--project-name','mc-test-'+lane.replace('.','-'),'--project-directory',str(ROOT/'testing'),'--env-file',str(ROOT/'testing/runtime'/f'{lane}.env'),'-f',str(ROOT/'testing/compose.yaml')]
def run(args,log,**kwargs): return subprocess.run(args,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env=env,**kwargs)
for phase,probe in ([('before','setup'),('after','restart')] if mode=='pair' else [(label,mode)]):
 dest=OUT/lane/(label+'-'+phase if mode=='pair' else label);dest.mkdir(parents=True,exist_ok=True)
 client=None; rc=1; started=time.time()
 with (dest/'lifecycle.log').open('w') as log:
  try:
   run([mc,'start',lane],log,check=True,timeout=1200)
   client=subprocess.check_output(compose+['--profile','client','run','-d','client'],env=env,stderr=log,text=True).strip()
   joined=False
   for _ in range(180):
    result=subprocess.run([mc,'command',lane,'list'],cwd=ROOT,capture_output=True,text=True,env=env)
    if 'There are 1 of' in result.stdout:joined=True;break
    running=subprocess.run(['docker','inspect','--format','{{.State.Running}}',client],capture_output=True,text=True)
    if running.stdout.strip()!='true':break
    time.sleep(3)
   if not joined: raise RuntimeError('No live headless player; pocket runtime probes cannot run')
   rc=run([sys.executable,str(OUT/'probe-upgrades.py'),lane,probe,str(dest.relative_to(OUT/lane))],log,timeout=180).returncode
   run([mc,'audit',lane],log,timeout=300)
   run([mc,'command',lane,'save-all flush'],log,timeout=60)
  except Exception as e:log.write(f'PROBE FAILURE: {type(e).__name__}: {e}\n');rc=1
  finally:
   if client:
    run(['docker','stop','--time','30',client],log,timeout=90)
    with (dest/'client-console.log').open('w') as c:run(['docker','logs',client],c)
    run(['docker','rm','-f',client],log)
   run([mc,'stop',lane],log,timeout=180)
   for base,name in [(runtime/'data/logs','server-logs'),(runtime/'client/.minecraft/logs','client-logs'),(runtime/'generated','generated')]:
    if base.exists():shutil.copytree(base,dest/name,dirs_exist_ok=True)
   if (runtime/'client/.minecraft/crash-reports').exists():shutil.copytree(runtime/'client/.minecraft/crash-reports',dest/'crash-reports',dirs_exist_ok=True)
 (dest/'lifecycle-result.json').write_text(json.dumps({'lane':lane,'phase':phase,'probe':probe,'exit_code':rc,'seconds':time.time()-started},indent=2)+'\n')
 print(lane,phase,'exit',rc,flush=True)
 if rc:break
