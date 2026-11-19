"""Prepare C20 using exact parent handoff release hashes and C15 probes."""
import pathlib,shutil,subprocess,re,json,hashlib,urllib.request,tomllib,zipfile,io
OUT=pathlib.Path(__file__).resolve().parent;ROOT=OUT.parents[2];OLD=OUT.with_name('cct-1.122.0-mc-1.21')
for name in ['run-lane.py','extend-lane.py','old-world.py','probe-upgrades.py','probe-all-stacks.py','measure-stack-limits.py','snbt_fields.py','summarize.py','verify-baseline.py','audit-old-fixtures.py']:
 if not (OUT/name).exists():shutil.copy2(OLD/name,OUT/name)
p=OUT/'old-world.py';s=p.read_text().replace('origin/main','origin/test/cct-1.122.0-mc-1.21').replace("if 'neoforge' in lane:lanes_file.write_text(new_lanes.replace('21.1.265','21.1.244'))","# PR #8 already uses NeoForge 21.1.265; retain exact loader.")
p.write_text(s)
base=subprocess.check_output(['git','rev-parse','origin/test/cct-1.122.0-mc-1.21'],text=True).strip();(OUT/'baseline').mkdir(exist_ok=True)
with (OUT/'baseline/minimal-packs.tar').open('wb') as f:subprocess.run(['git','archive',base,'FabricMinimal-1.21','NeoForgeMinimal-1.21'],stdout=f,check=True)
(OUT/'baseline/commit.txt').write_text(base+'\n')
releases=[('UnlimitedPeripheralWorks','peripheralworks','peripheralWorksVersion','1.10.1',['cf77870dae82a23e2d965698eed635a32959d1ed9a6e7664af7bb953dc72d343','74a94a9c77af04772163d6cb1d443a93f12d7b22c66263e853b69fdc03228810']),('CloudSolutions','cloudsolutions','cloudsolutionsVersion','0.4.1',['4c7f0285d6d5190d23ffc8d53b179556421c1f1f71eb739d0ea9b30027408357','c6cc23ff95428b7c768d2514ba530182edd513676b6dfce50af4f3c65b2cd7b0']),('DigitalItems','digitalitems','digitalItemsVersion','0.6.1',['3f934f122c5586ab8224cfe9ceab162b1146fd11fe96406505a52fccaa9cb481','cd2dec03bd1ddf97ebd9e922aa874f1003baab90e1218c8e844340a1e5929e7d']),('Turtlematic','turtlematic','turtlematicVersion','1.5.2',['decf4368eb9a961e98f6b4df0bbb3a9446c8dbedd54ea48a953762ec1bc20d07','c59b272f3d438c68c304c6e5947afdd0d1481968c89ed30422ee09bb8d52f0c7'])]
def get(url):return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Modpacks-C20'}),timeout=120).read()
assets=[]
for repo,slug,var,version,hashes in releases:
 release=json.loads(get(f'https://api.github.com/repos/SirEdvin/{repo}/releases/tags/v1.21.1-{version}'));assert not release['draft']
 for loader,expected in zip(['fabric','forge'],hashes):
  name=f'{slug}-{loader}-1.21.1-{version}.jar';a=next(a for a in release['assets'] if a['name']==name);data=get(a['browser_download_url']);sha=hashlib.sha256(data).hexdigest();assert sha==expected,(name,sha,expected)
  if a.get('digest'):assert a['digest']=='sha256:'+sha
  assets.append(dict(repository='SirEdvin/'+repo,tag=release['tag_name'],name=name,url=a['browser_download_url'],sha256=sha,parent_sha256=expected,release_url=release['html_url']))
for a in json.loads((OLD/'assets.json').read_text()):
 if a['repository']=='cc-tweaked':
  assert hashlib.sha256(get(a['url'])).hexdigest()==a['sha256'];assets.append(a)
for pack in ['FabricCreative-1.21','NeoForgeCreative-1.21','FabricMinimal-1.21','NeoForgeMinimal-1.21']:
 p=ROOT/pack/'Makefile';s=p.read_text()
 for repo,slug,var,version,hashes in releases:s=re.sub(r'^'+var+r' = .*$',var+' = '+version,s,flags=re.M)
 p.write_text(s)
 subprocess.run(['make','all'],cwd=ROOT/pack,check=True)
 for mod in ['unlimitedperipheralworks','cloudsolutions','digitalitems','turtlematic','cc-tweaked']:
  m=tomllib.loads((ROOT/pack/f'mods/{mod}.pw.toml').read_text());a=next(a for a in assets if a['name']==m['filename']);data=get(m['download']['url']);assert hashlib.sha256(data).hexdigest()==a['sha256'];assert hashlib.new(m['download']['hash-format'],data).hexdigest()==m['download']['hash']
 subprocess.run(['packwiz','refresh'],cwd=ROOT/pack,check=True)
 before={n:hashlib.sha256((ROOT/pack/n).read_bytes()).hexdigest() for n in ['index.toml','pack.toml']}
 subprocess.run(['packwiz','refresh'],cwd=ROOT/pack,check=True);assert before=={n:hashlib.sha256((ROOT/pack/n).read_bytes()).hexdigest() for n in before}
 (OUT/f'{pack}-refresh.json').write_text(json.dumps(before,indent=2)+'\n')
(OUT/'assets.json').write_text(json.dumps(assets,indent=2)+'\n')
subprocess.run(['python3',str(OUT/'verify-baseline.py')],check=True)
print('PASS: 8 parent SHA256s, 2 CC artifacts, 4 packs, double refresh, PR8 baseline',flush=True)
