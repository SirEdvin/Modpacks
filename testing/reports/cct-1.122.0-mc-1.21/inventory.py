"""Collect exact target JAR/dependency digests and execution toolchain."""
import hashlib,json,pathlib,platform,subprocess,tomllib,urllib.request
OUT=pathlib.Path(__file__).resolve().parent;ROOT=OUT.parents[2]
rows=[]
for pack in ['FabricCreative-1.21','NeoForgeCreative-1.21','FabricMinimal-1.21','NeoForgeMinimal-1.21']:
 for mod in ['unlimitedperipheralworks','turtlematic','cloudsolutions','digitalitems','cc-tweaked']+(['fabric-api'] if pack.startswith('Fabric') else []):
  m=tomllib.loads((ROOT/pack/f'mods/{mod}.pw.toml').read_text());data=urllib.request.urlopen(m['download']['url'],timeout=120).read()
  assert hashlib.new(m['download']['hash-format'],data).hexdigest()==m['download']['hash']
  rows.append(dict(pack=pack,mod=mod,name=m['filename'],sha256=hashlib.sha256(data).hexdigest(),pack_hash_format=m['download']['hash-format'],pack_hash=m['download']['hash']))
(OUT/'artifact-inventory.json').write_text(json.dumps(rows,indent=2)+'\n')
def out(args):return subprocess.check_output(args,cwd=ROOT,text=True).strip()
tools={'python':platform.python_version(),'docker':out(['docker','version','--format','{{.Server.Version}}']),'compose':out(['docker','compose','version']),'packwiz_sha256':hashlib.sha256(pathlib.Path(__import__('shutil').which('packwiz')).read_bytes()).hexdigest(),'baseline':(OUT/'baseline/commit.txt').read_text().strip(),'lane_config':(ROOT/'testing/lib/lanes.sh').read_text(),'started_at':out(['date','--iso-8601=seconds'])}
(OUT/'toolchain.json').write_text(json.dumps(tools,indent=2)+'\n')
print('Verified',len(rows),'pack target/dependency digests')
