"""Old-world migration on minimal lanes using exact origin/main pack source.

Temporarily swaps only the selected task-worktree pack directory. Always
restores the new source in finally. Server data is never reprovisioned after
the version switch. Keeps pre/post saved worlds and all logs for diagnosis.
"""
import hashlib,json,os,pathlib,shutil,subprocess,sys,tarfile,time
ROOT=pathlib.Path(__file__).resolve().parents[3];OUT=pathlib.Path(__file__).resolve().parent
lane=sys.argv[1]
pack={'minimal-fabric-1.21':'FabricMinimal-1.21','minimal-neoforge-1.21':'NeoForgeMinimal-1.21'}[lane]
runtime=ROOT/'testing/runtime'/lane;dest=OUT/lane/'old-world';dest.mkdir(parents=True,exist_ok=True)
mc=str(ROOT/'testing/bin/mc-test')
def run(args,log,**kw):return subprocess.run(args,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,**kw)
def snapshot(label):
 p=dest/label;p.mkdir(exist_ok=True)
 for src,name in [(runtime/'data/logs','server-logs'),(runtime/'generated','generated'),(runtime/'client/.minecraft/logs','client-logs')]:
  if src.exists():shutil.copytree(src,p/name,dirs_exist_ok=True)
 items=[]
 for f in (runtime/'data/mods').glob('*.jar'):
  if any(x in f.name for x in ['peripheralworks','cloudsolutions','digitalitems','turtlematic','cc-tweaked']):items.append(dict(name=f.name,sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
 (p/'artifacts.json').write_text(json.dumps(items,indent=2)+'\n')
 if (runtime/'data/playground').exists():
  with tarfile.open(p/'saved-world.tar.gz','w:gz') as t:t.add(runtime/'data/playground',arcname='playground')
new=OUT/'baseline'/('new-'+pack)
assert not new.exists(),'source swap already exists; recover it before retry'
lanes_file=ROOT/'testing/lib/lanes.sh'
new_lanes=lanes_file.read_text()
with (dest/'commands.log').open('w') as log:
 run([mc,'stop',lane],log,check=True)
 # HeadlessMC creates root-owned client files. Preserve/rename the old fresh
 # runtime instead of asking host rm to recursively delete container files.
 fresh=dest/'fresh-runtime'
 assert not fresh.exists(),'old-world fresh-runtime archive already exists'
 runtime.rename(fresh);runtime.mkdir()
 # The harness creates the top-level runtime as root. Rename of its client
 # child needs write permission on that parent, not on the child contents.
 run(['docker','run','--rm','--network','none','--user','0:0','-v',str(fresh)+':/saved','--entrypoint','chown','python:3.13-alpine',f'{os.getuid()}:{os.getgid()}','/saved','/saved/client'],log,check=True)
 if (fresh/'client').exists():(fresh/'client').rename(runtime/'client')
 (ROOT/pack).rename(new)
 try:
  if 'neoforge' in lane:lanes_file.write_text(new_lanes.replace('21.1.265','21.1.244'))
  with tarfile.open(OUT/'baseline/minimal-packs.tar') as t:
   members=[m for m in t.getmembers() if m.name==pack or m.name.startswith(pack+'/')]
   t.extractall(ROOT,members=members,filter='data')
  rc=run([mc,'smoke',lane],log,timeout=1800).returncode
  (dest/'baseline-smoke-exit.txt').write_text(str(rc)+'\n')
  snapshot('baseline-smoke')
  if rc==0:
   run([sys.executable,str(OUT/'extend-lane.py'),lane,'setup','old-world-before'],log,timeout=1800)
   snapshot('before-switch')
 finally:
  run([mc,'stop',lane],log,timeout=180)
  lanes_file.write_text(new_lanes)
  shutil.rmtree(ROOT/pack)
  new.rename(ROOT/pack)
 if rc==0:
  rc2=run([sys.executable,str(OUT/'extend-lane.py'),lane,'restart','old-world-after'],log,timeout=1800).returncode
  snapshot('after-switch')
 else: rc2=None
 (dest/'result.json').write_text(json.dumps(dict(lane=lane,baseline_smoke=rc,new_probe_command_exit=rc2,baseline_commit=subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip(),reprovisioned_after_switch=False),indent=2)+'\n')
 print(lane,'old-world commands completed',flush=True)
