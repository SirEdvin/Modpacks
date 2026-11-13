"""Extra 1.20.1 runtime probes. Run only against a disposable mc-test lane.

The normal harness only checks NBT: these programs run inside every turtle
and pocket, enumerate peripheral methods and round-trip turtle equipment.
A real headless player inventory ticks the pockets (item displays do not).
"""
import json, os, pathlib, re, shutil, socket, struct, subprocess, sys, time
ROOT=pathlib.Path(__file__).resolve().parents[3]
OUT=pathlib.Path(__file__).resolve().parent
lane=sys.argv[1]; mode=sys.argv[2]; label=sys.argv[3] if len(sys.argv)>3 else 'upgrades'
runtime=ROOT/'testing/runtime'/lane
dest=OUT/lane/label; dest.mkdir(parents=True,exist_ok=True)
manifest=json.loads((runtime/'generated/authored-blocks.json').read_text())
class Rcon:
 def __init__(self):
  name='mc-test-'+lane.replace('.','-')+'-minecraft-1'
  d=json.loads(subprocess.check_output(['docker','inspect',name]))[0]
  ip=next(iter(d['NetworkSettings']['Networks'].values()))['IPAddress']
  env=dict(x.split('=',1) for x in d['Config']['Env'] if '=' in x)
  self.s=socket.create_connection((ip,25575),15);self.s.settimeout(30);self.i=0
  assert self.packet(3,env['RCON_PASSWORD'])[0]!=-1,'RCON auth failed'
 def recv(self,n):
  data=b''
  while len(data)<n:
   chunk=self.s.recv(n-len(data))
   if not chunk: raise RuntimeError('RCON closed')
   data+=chunk
  return data
 def packet(self,kind,text):
  self.i+=1;data=struct.pack('<ii',self.i,kind)+text.encode()+b'\0\0';self.s.sendall(struct.pack('<i',len(data))+data)
  n=struct.unpack('<i',self.recv(4))[0];p=self.recv(n)
  return struct.unpack('<i',p[:4])[0],p[8:-2].decode()
 def command(self,text):return self.packet(2,text)[1]
r=Rcon()
program='''local config = textutils.unserializeJSON(fs.open("probe-config.json", "r").readAll())
local report = {id=os.getComputerID(), upgrade=config.upgrade, kind=config.kind, generatedAt=os.epoch("utc"), phase=config.phase}
local side = turtle and "left" or "back"
report.presentBefore = peripheral.isPresent(side)
report.typeBefore = {peripheral.getType(side)}
report.methodsBefore = peripheral.getMethods(side) or {}
local roundtripOK,roundtripError = pcall(function()
 if turtle and config.roundtrip then
  turtle.select(1)
  report.unequipOK,report.unequipError = turtle.equipLeft()
  report.returnedItem = turtle.getItemDetail(1)
  report.equipOK,report.equipError = turtle.equipLeft()
 elseif pocket and config.roundtrip then
  report.unequipOK,report.unequipError = pocket.unequipBack()
  report.equipOK,report.equipError = pocket.equipBack()
 end
end)
report.roundtripOK = roundtripOK
if not roundtripOK then report.roundtripError = tostring(roundtripError) end
report.presentAfter = peripheral.isPresent(side)
report.typeAfter = {peripheral.getType(side)}
report.methodsAfter = peripheral.getMethods(side) or {}
report.wrapOK = not report.presentAfter or peripheral.wrap(side) ~= nil
local f=fs.open("upgrade-probe.json","w") f.write(textutils.serializeJSON(report)) f.close()
'''
def computer_dir(cid): return runtime/f'data/playground/computercraft/computer/{cid}'
def install(cid,entry,kind,roundtrip):
 p=computer_dir(cid);p.mkdir(parents=True,exist_ok=True)
 (p/'startup.lua').write_text(program)
 (p/'probe-config.json').write_text(json.dumps(dict(upgrade=entry['id'],kind=kind,roundtrip=roundtrip,phase=label)))
 (p/'upgrade-probe.json').unlink(missing_ok=True)
entries=[]
for i,e in enumerate(manifest['turtle_cells']):entries.append(dict(e,cid=30000+i,kind='turtle'))
for i,e in enumerate(manifest['pocket_cells']):entries.append(dict(e,cid=31000+i,kind='pocket',slot=i+9))
responses=[]
if mode=='setup':
 # Start with an empty disposable player inventory: equipBack chooses the
 # first suitable item, not necessarily the item just unequipped.
 responses.append(dict(command='clear @a',response=r.command('clear @a')))
 for e in entries:
  install(e['cid'],e,e['kind'],True)
  if e['kind']=='turtle':
   # Create the active probe host with its ID from the outset. Some upgrades
   # create a server computer while still off; changing only ComputerId NBT
   # would then leave that live instance using its earlier filesystem.
   r.command(f'setblock {e["x"]} {e["y"]} {e["z"]} minecraft:air')
   cmd=f'setblock {e["x"]} {e["y"]} {e["z"]} computercraft:turtle_advanced{{ComputerId:{e["cid"]},LeftUpgrade:"{e["id"]}",On:1b}}'
  else:
   cmd=f'item replace entity @a[limit=1] container.{e["slot"]} with computercraft:pocket_computer_advanced{{ComputerId:{e["cid"]},Upgrade:"{e["id"]}",On:1b}}'
  responses.append(dict(upgrade=e['id'],command=cmd,response=r.command(cmd)))
  if e['kind']=='pocket':
   # Native pocket.equipBack scans the shared player inventory. Serialize
   # round-trips so two pockets cannot steal each other's unequipped item.
   for _ in range(100):
    if (computer_dir(e['cid'])/'upgrade-probe.json').exists():break
    time.sleep(0.1)
 for e in entries:
  if e['kind']=='turtle':r.command(f'computercraft turn-on #{e["cid"]}')
elif mode=='restart':
 for e in entries:
  install(e['cid'],e,e['kind'],False)
  r.command(f'computercraft shutdown #{e["cid"]}')
 # Shutdown/turn-on commands are asynchronous computer-thread requests.
 # Give shutdown a tick barrier before issuing turn-on, or it may be ignored
 # while the machine is still on and then leave the computer powered off.
 time.sleep(1)
 for e in entries:r.command(f'computercraft turn-on #{e["cid"]}')
elif mode!='read': raise SystemExit('mode must be setup, restart or read')
start=time.time()
while time.time()-start<60:
 if all((computer_dir(e['cid'])/'upgrade-probe.json').exists() for e in entries):break
 time.sleep(1)
results=[]
for e in entries:
 p=computer_dir(e['cid'])/'upgrade-probe.json'
 result=dict(upgrade=e['id'],kind=e['kind'],cid=e['cid'])
 if p.exists():
  result['lua']=json.loads(p.read_text());shutil.copy2(p,dest/f'{e["cid"]}.json')
 else:result['missing_lua']=True
 if e['kind']=='turtle':cmd=f'data get block {e["x"]} {e["y"]} {e["z"]}'
 else:cmd=f'data get entity @a[limit=1] Inventory[{{Slot:{e["slot"]}b}}]'
 result['live_nbt']=r.command(cmd)
 result['upgrade_in_nbt']=e['id'] in result['live_nbt']
 results.append(result)
(dest/'commands.json').write_text(json.dumps(responses,indent=2)+'\n')
(dest/'upgrade-probes.json').write_text(json.dumps(results,indent=2)+'\n')
# The next boot must only observe persisted upgrades. In particular, do not
# let all pockets re-run equipBack concurrently when their owner logs in.
for e in entries:
 cfg=computer_dir(e['cid'])/'probe-config.json'
 if cfg.exists():
  value=json.loads(cfg.read_text());value['roundtrip']=False;cfg.write_text(json.dumps(value))
print(json.dumps(dict(lane=lane,phase=label,fixtures=len(results),lua=sum('lua' in e for e in results),nbt_present=sum(e['upgrade_in_nbt'] for e in results),peripherals=sum(e.get('lua',{}).get('presentAfter',False) for e in results),equip_failed=[e['upgrade'] for e in results if e.get('lua',{}).get('equipOK') is False],missing=[e['upgrade'] for e in results if 'lua' not in e]),indent=2))
if mode=='restart':
 subprocess.run([sys.executable,str(OUT/'probe-stack-equip.py'),lane,label],check=True)
