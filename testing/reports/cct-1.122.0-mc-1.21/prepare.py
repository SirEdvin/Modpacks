"""Resolve stable releases, verify downloaded assets, and refresh only four packs."""
import hashlib, io, json, pathlib, shutil, subprocess, tarfile, tomllib, urllib.request, urllib.parse, zipfile
ROOT=pathlib.Path(__file__).resolve().parents[3]; OUT=pathlib.Path(__file__).resolve().parent
PACKS=['FabricCreative-1.21','NeoForgeCreative-1.21','FabricMinimal-1.21','NeoForgeMinimal-1.21']
def get(url):
 return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'SirEdvin-Modpacks-validation'}),timeout=120).read()
def api(url):return json.loads(get(url))
def run(args,cwd=ROOT):subprocess.run(args,cwd=cwd,check=True)
base=subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip()
(OUT/'baseline').mkdir(exist_ok=True)
with (OUT/'baseline/minimal-packs.tar').open('wb') as f:subprocess.run(['git','archive',base,'FabricMinimal-1.21','NeoForgeMinimal-1.21'],stdout=f,check=True)
(OUT/'baseline/commit.txt').write_text(base+'\n')
assets=[]; releases=[]
for repo,slug,var in [('UnlimitedPeripheralWorks','peripheralworks','peripheralWorksVersion'),('Turtlematic','turtlematic','turtlematicVersion'),('CloudSolutions','cloudsolutions','cloudsolutionsVersion'),('DigitalItems','digitalitems','digitalItemsVersion')]:
 allreleases=api(f'https://api.github.com/repos/SirEdvin/{repo}/releases?per_page=100')
 release=max((r for r in allreleases if not r['prerelease'] and not r['draft'] and r['tag_name'].startswith('v1.21.1-')),key=lambda r:r['published_at'])
 tag=release['tag_name']; version=tag.removeprefix('v1.21.1-')
 releases.append(dict(repository='SirEdvin/'+repo,tag=tag,published_at=release['published_at'],url=release['html_url']))
 for loader in ['fabric','neoforge']:
  name=f'{slug}-{"forge" if loader=="neoforge" else loader}-1.21.1-{version}.jar';asset=next(a for a in release['assets'] if a['name']==name)
  data=get(asset['browser_download_url']);sha=hashlib.sha256(data).hexdigest()
  if asset.get('digest'):assert asset['digest']=='sha256:'+sha,(name,'GitHub digest mismatch')
  jar=zipfile.ZipFile(io.BytesIO(data)); metadata={n:jar.read(n).decode() for n in ['fabric.mod.json','META-INF/neoforge.mods.toml','META-INF/jarjar/metadata.json'] if n in jar.namelist()}
  assets.append(dict(repository='SirEdvin/'+repo,tag=tag,name=name,url=asset['browser_download_url'],sha256=sha,github_digest=asset.get('digest'),metadata=metadata))
 for pack in PACKS:
  p=ROOT/pack/'Makefile';text=p.read_text();import re
  text=re.sub(r'^'+var+r' = .*$',var+' = '+version,text,flags=re.M);p.write_text(text)
for loader in ['fabric','neoforge']:
 query=urllib.parse.urlencode({'game_versions':json.dumps(['1.21.1']),'loaders':json.dumps([loader])})
 version=next(v for v in api('https://api.modrinth.com/v2/project/cc-tweaked/version?'+query) if v['version_number']=='1.122.0')
 f=next(f for f in version['files'] if f['primary']);data=get(f['url'])
 for algorithm,value in f['hashes'].items():assert hashlib.new(algorithm,data).hexdigest()==value
 assets.append(dict(repository='cc-tweaked',tag='1.122.0',name=f['filename'],url=f['url'],sha256=hashlib.sha256(data).hexdigest(),modrinth_version_type=version['version_type'],modrinth_version_id=version['id'],provider_hashes=f['hashes']))
 for pack in [p for p in PACKS if p.lower().startswith(loader)]:
  p=ROOT/pack/'Makefile';text=p.read_text()
  if 'ccTweakedVersion =' not in text:text='ccTweakedVersion = 1.122.0\n'+text
  if '\ncctweaked:' not in text:text+='\n# Exact release selected for this Minecraft/loader line.\ncctweaked:\n\tpackwiz modrinth add cc-tweaked --version-filename '+f['filename'].replace('1.122.0','${ccTweakedVersion}')+' -y\n'
  p.write_text(text)
  run(['make','cctweaked'],ROOT/pack)
for pack in PACKS:
 run(['make','all'],ROOT/pack)
 for slug in ['unlimitedperipheralworks','turtlematic','cloudsolutions','digitalitems','cc-tweaked']:
  meta=tomllib.loads((ROOT/pack/f'mods/{slug}.pw.toml').read_text()); a=next(a for a in assets if a['name']==meta['filename'])
  data=get(meta['download']['url']); assert hashlib.sha256(data).hexdigest()==a['sha256']
  assert hashlib.new(meta['download']['hash-format'],data).hexdigest()==meta['download']['hash']
 run(['packwiz','refresh'],ROOT/pack)
 before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/pack/'index.toml',ROOT/pack/'pack.toml']}
 run(['packwiz','refresh'],ROOT/pack)
 assert before=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/pack/'index.toml',ROOT/pack/'pack.toml']}
 (OUT/f'{pack}-refresh.json').write_text(json.dumps(before,indent=2)+'\n')
(OUT/'assets.json').write_text(json.dumps(assets,indent=2)+'\n');(OUT/'releases.json').write_text(json.dumps(releases,indent=2)+'\n')
# Runtime probe sources are committed beside this script; do not overwrite
# them from a historical report when preparing a future rerun.
print('Prepared',len(assets),'verified assets; baseline',base,flush=True)
