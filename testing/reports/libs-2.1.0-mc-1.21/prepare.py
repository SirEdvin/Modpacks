"""Prepare only C13 packs; retain exact baseline before edits and verify releases."""
import hashlib,json,pathlib,subprocess,urllib.request,zipfile,tomllib,tarfile
ROOT=pathlib.Path(__file__).resolve().parents[3];OUT=pathlib.Path(__file__).resolve().parent
packs=['FabricCreative-1.21','FabricMinimal-1.21','NeoForgeCreative-1.21','NeoForgeMinimal-1.21']
def run(args,**kw):return subprocess.check_output(args,cwd=ROOT,text=True,**kw)
(OUT/'baseline').mkdir(exist_ok=True)
assert not (OUT/'baseline/minimal-packs.tar').exists()
(OUT/'baseline/commit.txt').write_text(run(['git','rev-parse','origin/main']))
with (OUT/'baseline/minimal-packs.tar').open('wb') as f:subprocess.run(['git','archive','origin/main','FabricMinimal-1.21','NeoForgeMinimal-1.21'],cwd=ROOT,stdout=f,check=True)
assets=[]
for repo,ver in [('UnlimitedPeripheralWorks','1.10.0'),('Turtlematic','1.5.1'),('CloudSolutions','0.4.0'),('DigitalItems','0.6.0')]:
 release=json.loads(run(['gh','api',f'repos/SirEdvin/{repo}/releases/tags/v1.21.1-{ver}']))
 for a in release['assets']:
  p=OUT/'downloads'/a['name'];p.parent.mkdir(exist_ok=True)
  urllib.request.urlretrieve(a['browser_download_url'],p)
  sha=hashlib.sha256(p.read_bytes()).hexdigest();assert a['digest']=='sha256:'+sha
  with zipfile.ZipFile(p) as z:
   meta={n:z.read(n).decode() for n in ['fabric.mod.json','META-INF/neoforge.mods.toml'] if n in z.namelist()}
  assets.append(dict(repo=repo,version=ver,name=p.name,url=a['browser_download_url'],sha256=sha,metadata=meta))
(OUT/'assets.json').write_text(json.dumps(assets,indent=2)+'\n')
for pack in packs:
 p=ROOT/pack/'Makefile';text=p.read_text()
 for old,new in [('cloudsolutionsVersion = 0.3.4','cloudsolutionsVersion = 0.4.0'),('turtlematicVersion = 1.4.10','turtlematicVersion = 1.5.1'),('peripheralWorksVersion = 1.9.2','peripheralWorksVersion = 1.10.0'),('digitalItemsVersion = 0.5.8','digitalItemsVersion = 0.6.0')]:assert old in text;text=text.replace(old,new)
 if pack.startswith('Fabric'):
  text='\n'.join(line for line in text.splitlines() if not line.startswith('smartHomeAppliancesVersion') and not line.startswith('smarthome:') and 'SmartHome-Appliances' not in line)+'\n'
  text=text.replace(' cloudsolutions smarthome',' cloudsolutions')
  (ROOT/pack/'mods/smarthome-appliances.pw.toml').unlink()
 p.write_text(text)
 with (OUT/(pack+'-updates.log')).open('w') as log:subprocess.run(['make','turtlematic','upw','digitems','cloudsolutions'],cwd=ROOT/pack,stdout=log,stderr=subprocess.STDOUT,check=True)
 for mod in ['unlimitedperipheralworks','turtlematic','cloudsolutions','digitalitems']:
  m=tomllib.loads((ROOT/pack/f'mods/{mod}.pw.toml').read_text());a=next(a for a in assets if a['name']==m['filename']);assert m['download']['hash']==a['sha256'] and m['download']['hash-format']=='sha256'
print('Prepared four packs; eight downloaded GitHub assets verified',flush=True)
for a in assets:print(a['name'],a['sha256'],a['metadata'])
