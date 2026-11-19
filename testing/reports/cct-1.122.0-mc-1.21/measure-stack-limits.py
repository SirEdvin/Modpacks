"""Measure legal stack sizes with native turtle API, using count-one inputs."""
import json,pathlib,socket,struct,subprocess,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[3];OUT=pathlib.Path(__file__).resolve().parent
lane,label=sys.argv[1:];runtime=ROOT/'testing/runtime'/lane;dest=OUT/lane/label
# Import only the socket transport; do not execute another probe's module.
from typing import Any
source=(OUT/'probe-all-stacks.py').read_text();scope: dict[str,Any]=dict(json=json,socket=socket,struct=struct,subprocess=subprocess,lane=lane)
exec(source[source.index('class Rcon:'):source.index('r=Rcon()')],scope)
r=scope['Rcon']();manifest=json.loads((runtime/'generated/authored-blocks.json').read_text())
items=sorted({e['item'] for key in ['turtle_cells','pocket_cells'] for e in manifest[key]}|{'computercraft:wireless_modem_normal'})
p=runtime/'data/playground/computercraft/computer/36999';p.mkdir(parents=True,exist_ok=True)
(p/'startup.lua').write_text('''while true do
 local d=turtle.getItemDetail(1,true)
 if d then local f=fs.open("detail.json","w") f.write(textutils.serializeJSON(d)) f.close() end
 sleep(0.1)
end
''')
r.command('setblock 57 69 0 air');r.command('setblock 57 69 0 computercraft:turtle_advanced{ComputerId:36999,On:1b}')
limits={};details=[]
for item in items:
 response=r.command(f'item replace block 57 69 0 container.0 with {item} 1')
 for _ in range(100):
  try:
   d=json.loads((p/'detail.json').read_text())
   if d['name']==item:break
  except (FileNotFoundError,json.JSONDecodeError):pass
  time.sleep(.1)
 else:raise RuntimeError('No native item detail: '+item+' '+response)
 limits[item]=d['maxCount'];details.append(d)
r.command('setblock 57 69 0 air')
(dest/'item-stack-limits.json').write_text(json.dumps(dict(limits=limits,details=details),indent=2)+'\n')
print('MEASURED',len(limits),'items; stackable',sum(v>1 for v in limits.values()),flush=True)
