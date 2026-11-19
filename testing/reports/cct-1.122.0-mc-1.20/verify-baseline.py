"""Resolve and verify exact baseline artifact bytes from the archived pack source."""
import hashlib,json,pathlib,tarfile,tomllib,urllib.request
OUT=pathlib.Path(__file__).resolve().parent
rows=[]
with tarfile.open(OUT/'baseline/minimal-packs.tar') as archive:
 for pack in ['FabricMinimal-1.20','ForgeMinimal-1.20']:
  for mod in ['unlimitedperipheralworks','turtlematic','cloudsolutions','digitalitems','cc-tweaked']:
   f=archive.extractfile(f'{pack}/mods/{mod}.pw.toml');assert f is not None
   meta=tomllib.loads(f.read().decode());d=meta['download']
   data=urllib.request.urlopen(urllib.request.Request(d['url'],headers={'User-Agent':'Modpacks-release-validation'}),timeout=120).read()
   assert hashlib.new(d['hash-format'],data).hexdigest()==d['hash']
   rows.append(dict(pack=pack,mod=mod,name=meta['filename'],sha256=hashlib.sha256(data).hexdigest(),pack_hash_verified=True))
(OUT/'baseline-artifacts.json').write_text(json.dumps(rows,indent=2)+'\n');print('Verified baseline artifacts',len(rows))
