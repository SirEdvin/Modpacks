"""Count-two equip of EVERY active authored upgrade plus CC modem controls.

Hosts are distinct from the single-item fixture and persist across restart.
Requires a live disposable offline headless player. Never reprovisions in observe.
"""
from snbt_fields import equipped_upgrade
import json,pathlib,socket,struct,subprocess,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[3];OUT=pathlib.Path(__file__).resolve().parent
lane,mode,label=sys.argv[1:4];runtime=ROOT/'testing/runtime'/lane;dest=OUT/lane/label/'all-stacks';dest.mkdir(parents=True,exist_ok=True)
class Rcon:
 def __init__(self):
  d=json.loads(subprocess.check_output(['docker','inspect','mc-test-'+lane.replace('.','-')+'-minecraft-1']))[0]
  ip=next(iter(d['NetworkSettings']['Networks'].values()))['IPAddress'];env=dict(x.split('=',1) for x in d['Config']['Env'] if '=' in x)
  self.s=socket.create_connection((ip,25575),15);self.s.settimeout(30);self.i=0
  assert self.packet(3,env['RCON_PASSWORD'])[0]!=-1
 def recv(self,n):
  data=b''
  while len(data)<n:
   chunk=self.s.recv(n-len(data))
   if not chunk:raise RuntimeError('RCON closed')
   data+=chunk
  return data
 def packet(self,kind,text):
  self.i+=1;data=struct.pack('<ii',self.i,kind)+text.encode()+b'\0\0';self.s.sendall(struct.pack('<i',len(data))+data);p=self.recv(struct.unpack('<i',self.recv(4))[0]);return struct.unpack('<i',p[:4])[0],p[8:-2].decode()
 def command(self,text):return self.packet(2,text)[1]
r=Rcon();manifest=json.loads((runtime/'generated/authored-blocks.json').read_text());entries=[]
for i,e in enumerate(manifest['turtle_cells']):entries.append(dict(e,kind='turtle',cid=34000+i,y=e['y']+3))
entries.append(dict(id='computercraft:wireless_modem_normal',item='computercraft:wireless_modem_normal',kind='turtle',cid=34999,x=56,y=67,z=0))
slots=[i for i in range(1,36) if i not in range(9,9+len(manifest['pocket_cells']))]
assert len(slots)>=len(manifest['pocket_cells'])+1
for i,e in enumerate(manifest['pocket_cells']):entries.append(dict(e,kind='pocket',cid=35000+i,slot=slots[i]))
entries.append(dict(id='computercraft:wireless_modem_normal',item='computercraft:wireless_modem_normal',kind='pocket',cid=35999,slot=slots[len(manifest['pocket_cells'])]))
program='''local f=fs.open("stack-config.json","r") local c=textutils.unserializeJSON(f.readAll()) f.close()
local side=turtle and "left" or "back"
local d={generatedAt=os.epoch("utc"),id=os.getComputerID(),phase=c.phase,observe=c.observe,upgrade=c.upgrade}
if not c.observe then
 if turtle then turtle.select(1) d.input=turtle.getItemDetail(1,true) end
 local ok,value,message=pcall(turtle and turtle.equipLeft or pocket.equipBack)
 d.callOK=ok d.result=tostring(value) d.message=tostring(message)
 if turtle then d.remaining=turtle.getItemDetail(1,true) end
end
d.present=peripheral.isPresent(side) d.types={peripheral.getType(side)} d.methods=peripheral.getMethods(side) or {} d.wrapOK=not d.present or peripheral.wrap(side)~=nil
local f=fs.open("all-stacks.json","w") f.write(textutils.serializeJSON(d)) f.close()
'''
commands=[];setup_remaining={}
limits=json.loads((OUT/lane/label/'item-stack-limits.json').read_text())['limits']
skipped=[dict(kind=e['kind'],upgrade=e['id'],item=e['item'],reason='item maxCount=1; covered by native single-item equip/restart') for e in entries if limits[e['item']]==1]
entries=[e for e in entries if limits[e['item']]>1]
(dest/'nonstackable.json').write_text(json.dumps(skipped,indent=2)+'\n')
def command(text):
 response=r.command(text);commands.append(dict(command=text,response=response));return response
def directory(e):return runtime/f'data/playground/computercraft/computer/{e["cid"]}'
for e in entries:
 p=directory(e);p.mkdir(parents=True,exist_ok=True);(p/'startup.lua').write_text(program)
 (p/'stack-config.json').write_text(json.dumps(dict(upgrade=e['id'],phase=label,observe=mode!='setup')))
 (p/'all-stacks.json').unlink(missing_ok=True)
 if mode=='setup':
  if e['kind']=='turtle':
   command(f'setblock {e["x"]} {e["y"]} {e["z"]} minecraft:air')
   command(f'setblock {e["x"]} {e["y"]} {e["z"]} computercraft:turtle_advanced{{ComputerId:{e["cid"]},On:1b,Items:[{{Slot:0b,id:"{e["item"]}",count:2}}]}}')
  else:
   command(f'item replace entity @a[limit=1] container.0 with {e["item"]} 2')
   command(f'item replace entity @a[limit=1] container.{e["slot"]} with computercraft:pocket_computer_advanced[computercraft:computer_id={e["cid"]},computercraft:on=true]')
  for _ in range(150):
   if (p/'all-stacks.json').exists():break
   time.sleep(.1)
  if e['kind']=='pocket':setup_remaining[e['cid']]=command('data get entity @a[limit=1] Inventory[{Slot:0b}]')
 else:command(f'computercraft shutdown #{e["cid"]}')
if mode!='setup':
 time.sleep(1)
 for e in entries:command(f'computercraft turn-on #{e["cid"]}')
end=time.time()+60
while time.time()<end and not all((directory(e)/'all-stacks.json').exists() for e in entries):time.sleep(.5)
rows=[]
for e in entries:
 p=directory(e);report=p/'all-stacks.json';lua=json.loads(report.read_text()) if report.exists() else {'missing':True}
 if e['kind']=='turtle':nbt=command(f'data get block {e["x"]} {e["y"]} {e["z"]}')
 else:nbt=command(f'data get entity @a[limit=1] Inventory[{{Slot:{e["slot"]}b}}]')
 rows.append(dict(upgrade=e['id'],item=e['item'],kind=e['kind'],cid=e['cid'],lua=lua,live_nbt=nbt,upgrade_in_nbt=equipped_upgrade(nbt,e['kind'])==e['id'],remaining_input=setup_remaining.get(e['cid'])))
 cfg=json.loads((p/'stack-config.json').read_text());cfg['observe']=True;(p/'stack-config.json').write_text(json.dumps(cfg))
(dest/'results.json').write_text(json.dumps(rows,indent=2)+'\n');(dest/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
failed=[dict(upgrade=e['upgrade'],kind=e['kind'],lua=e['lua']) for e in rows if not e['upgrade_in_nbt'] or e['lua'].get('missing') or (mode=='setup' and (not e['lua'].get('callOK') or e['lua'].get('result')!='true'))]
print('ALL STACKS',lane,mode,'total',len(rows),'failed',json.dumps(failed),flush=True)
