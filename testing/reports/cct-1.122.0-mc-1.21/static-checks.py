"""Check Packwiz's full authored index hash chain and deterministic refresh."""
import hashlib,json,pathlib,subprocess,tomllib
OUT=pathlib.Path(__file__).resolve().parent;ROOT=OUT.parents[2]
rows=[]
for pack in ['FabricCreative-1.21','NeoForgeCreative-1.21','FabricMinimal-1.21','NeoForgeMinimal-1.21']:
 base=ROOT/pack
 before={str(p.relative_to(base)):hashlib.sha256(p.read_bytes()).hexdigest() for p in base.rglob('*') if p.is_file()}
 with (OUT/(pack+'-static.log')).open('w') as f:
  for _ in range(2):subprocess.run(['packwiz','refresh'],cwd=base,stdout=f,stderr=subprocess.STDOUT,check=True)
 after={str(p.relative_to(base)):hashlib.sha256(p.read_bytes()).hexdigest() for p in base.rglob('*') if p.is_file()}
 assert before==after,pack+' refresh changed source'
 p=tomllib.loads((base/'pack.toml').read_text());index=base/p['index']['file']
 assert hashlib.new(p['index']['hash-format'],index.read_bytes()).hexdigest()==p['index']['hash']
 idx=tomllib.loads(index.read_text())
 for e in idx['files']:
  assert hashlib.new(e.get('hash-format',idx['hash-format']),(base/e['file']).read_bytes()).hexdigest()==e['hash'],(pack,e['file'])
 assert not (base/'mods/smarthome-appliances.pw.toml').exists() if pack.startswith('Fabric') else True
 rows.append(dict(pack=pack,index_files=len(idx['files']),pack_sha256=hashlib.sha256((base/'pack.toml').read_bytes()).hexdigest(),index_sha256=hashlib.sha256(index.read_bytes()).hexdigest(),deterministic_refresh=True))
(OUT/'refresh-verification.json').write_text(json.dumps(rows,indent=2)+'\n')
print('Verified four full Packwiz index chains and deterministic refreshes')
