"""Native pocket.equipBack regression: a stack of two valid upgrade items.

These extra empty pockets live outside the persistent fixture slots, and the
original fixture pockets are not replaced. Also tests CC's own modem control.
"""
import json,pathlib,subprocess,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[3];OUT=pathlib.Path(__file__).resolve().parent
lane=sys.argv[1];label=sys.argv[2];dest=OUT/lane/label/'stack-equip';dest.mkdir(parents=True,exist_ok=True)
mc=str(ROOT/'testing/bin/mc-test');world=ROOT/'testing/runtime'/lane/'data/playground/computercraft/computer'
def command(text):return subprocess.check_output([mc,'command',lane,text],cwd=ROOT,text=True).strip()
rows=[]
for i,item in enumerate(['peripheralworks:universal_scanner','cloudsolutions:statsd_bridge','digitalitems:digitizer','computercraft:wireless_modem_normal']):
 cid=32000+i;p=world/str(cid);p.mkdir(parents=True,exist_ok=True)
 report=p/'stack-equip.json';report.unlink(missing_ok=True)
 (p/'startup.lua').write_text('''local ok,value,message=pcall(pocket.equipBack)
local d={generatedAt=os.epoch("utc"),callOK=ok,result=tostring(value),message=tostring(message),present=peripheral.isPresent("back"),types={peripheral.getType("back")}}
local f=fs.open("stack-equip.json","w") f.write(textutils.serializeJSON(d)) f.close()
''')
 input_response=command(f'item replace entity @a[limit=1] container.0 with {item} 2')
 pocket_response=command(f'item replace entity @a[limit=1] container.{i+1} with computercraft:pocket_computer_advanced[computercraft:computer_id={cid},computercraft:on=true]')
 for _ in range(150):
  if report.exists():break
  time.sleep(.1)
 result=json.loads(report.read_text()) if report.exists() else {'missing':True}
 row=dict(item=item,count=2,computer_id=cid,input_response=input_response,pocket_response=pocket_response,lua=result,pocket_nbt=command(f'data get entity @a[limit=1] Inventory[{{Slot:{i+1}b}}]'),remaining_input=command('data get entity @a[limit=1] Inventory[{Slot:0b}]'))
 rows.append(row)
 # No repeat of this action when the test player logs in later.
 (p/'startup.lua').write_text('-- stack equip probe already completed\n')
(dest/'results.json').write_text(json.dumps(rows,indent=2)+'\n')
print('STACK EQUIP',lane,[(r['item'],r['lua'].get('callOK'),r['lua'].get('result')) for r in rows],flush=True)
