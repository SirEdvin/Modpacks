"""Audit every saved old-world fixture, without replacing or provisioning it.

Run only after the lane's migration, with no other lane running. This adds an
independent same-world restart and exact lectern/display/control-Lua coverage.
"""
import hashlib,json,os,pathlib,shutil,socket,struct,subprocess,sys,tarfile,time
from snbt_fields import equipped_upgrade,fields
OUT=pathlib.Path(__file__).resolve().parent;ROOT=OUT.parents[2]
lane=sys.argv[1];runtime=ROOT/'testing/runtime'/lane;dest=OUT/lane/'old-world-fixture-audit';dest.mkdir(exist_ok=True)
manifest=json.loads((runtime/'generated/authored-blocks.json').read_text());mc=str(ROOT/'testing/bin/mc-test')
from typing import Any
source=(OUT/'probe-all-stacks.py').read_text();scope: dict[str,Any]=dict(json=json,socket=socket,struct=struct,subprocess=subprocess,lane=lane)
exec(source[source.index('class Rcon:'):source.index('r=Rcon()')],scope)
started=time.time();rc=1
with (dest/'command.log').open('w') as log:
 try:
  subprocess.run([mc,'start',lane],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=1200)
  r=scope['Rcon']();commands=[]
  def command(text):
   response=r.command(text);commands.append(dict(command=text,response=response));return response
  blocks=[];turtles=[];pockets=[]
  for e in manifest['cells']:
   pos=f'{e["x"]} {e["y"]} {e["z"]}';removed=e['block'].startswith('smarthome_appliances:')
   retained='Seed' in command(f'execute if block {pos} {e["block"]} run seed');air='Seed' in command(f'execute if block {pos} minecraft:air run seed')
   nbt=command(f'data get block {e["modem_x"]} {e["modem_y"]} {e["modem_z"]}');wired='PeripheralType' in nbt
   blocks.append(dict(id=e['block'],removed_intentionally=removed,retained=retained,now_air=air,wired=wired,ok=(air and not wired) if removed else retained))
  for e in manifest['turtle_cells']:
   nbt=command(f'data get block {e["x"]} {e["y"]} {e["z"]}')
   turtles.append(dict(id=e['id'],nbt=nbt,ok=equipped_upgrade(nbt,'turtle')==e['id']))
  for e in manifest['pocket_cells']:
   lectern='Seed' in command(f'execute if block {e["x"]} {e["y"]} {e["z"]} minecraft:lectern run seed')
   nbt=command(f'data get entity @e[type=minecraft:item_display,tag={e["entity_tag"]},limit=1]')
   try:upgrade=equipped_upgrade(fields(nbt)['item'],'pocket')
   except (KeyError,ValueError):upgrade=None
   pockets.append(dict(id=e['id'],lectern=lectern,nbt=nbt,ok=lectern and upgrade==e['id']))
  cid=manifest['control_computer']['id'];f=runtime/f'data/playground/computercraft/computer/{cid}/authored-peripherals.json';f.unlink(missing_ok=True)
  command(f'computercraft shutdown #{cid}');time.sleep(1);command(f'computercraft turn-on #{cid}')
  for _ in range(120):
   if f.exists():break
   time.sleep(.5)
  lua=json.loads(f.read_text());assert lua['generatedAt']/1000>=started
  (dest/'control-lua.json').write_text(json.dumps(lua,indent=2)+'\n')
  with tarfile.open(OUT/lane/'old-world/before-switch/saved-world.tar.gz') as t:
   member=t.extractfile(f'playground/computercraft/computer/{cid}/authored-peripherals.json');assert member is not None;baseline=json.load(member)
  current={e['name']:e for e in lua['peripherals']}
  missing=[e['name'] for e in baseline['peripherals'] if e['name'] not in current or current[e['name']]['types']!=e['types'] or not current[e['name']].get('methods')]
  prior=json.loads((OUT/lane/'old-world/before-switch/generated/authored-block-audit.json').read_text())
  wired=sum(e['wired'] for e in blocks)
  result=dict(lane=lane,verdict='PASS' if all(e['ok'] for e in blocks+turtles+pockets) and not missing and wired==prior['wired_peripheral_count'] else 'FAIL',blocks=blocks,turtles=turtles,pocket_displays=pockets,wired=wired,baseline_control_peripherals=len(baseline['peripherals']),current_control_peripherals=len(lua['peripherals']),missing_or_changed_control_types=missing,reprovisioned=False)
  (dest/'commands.json').write_text(json.dumps(commands,indent=2)+'\n');(dest/'result.json').write_text(json.dumps(result,indent=2)+'\n')
  rc=0 if result['verdict']=='PASS' else 1
  command('save-all flush')
 except Exception as e:log.write(f'FAILURE: {type(e).__name__}: {e}\n')
 finally:
  subprocess.run([mc,'stop',lane],stdout=log,stderr=subprocess.STDOUT,timeout=180)
  if (runtime/'data/logs').exists():shutil.copytree(runtime/'data/logs',dest/'server-logs',dirs_exist_ok=True)
(dest/'lifecycle-result.json').write_text(json.dumps(dict(exit_code=rc,started_at=started,seconds=time.time()-started),indent=2)+'\n')
print(lane,'full old-world fixture audit exit',rc,flush=True);sys.exit(rc)
