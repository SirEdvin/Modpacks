"""Verify origin/main minimal-pack downloads before old-world setup."""
import hashlib,json,pathlib,tarfile,tomllib,urllib.request
OUT=pathlib.Path(__file__).resolve().parent
rows=[]
with tarfile.open(OUT/'baseline/minimal-packs.tar') as t:
 for member in t.getmembers():
  if any(member.name.endswith('/mods/'+mod+'.pw.toml') for mod in ['unlimitedperipheralworks','turtlematic','cloudsolutions','digitalitems','cc-tweaked']):
   m=tomllib.loads(t.extractfile(member).read().decode());data=urllib.request.urlopen(m['download']['url'],timeout=120).read()
   assert hashlib.new(m['download']['hash-format'],data).hexdigest()==m['download']['hash']
   rows.append(dict(name=m['filename'],sha256=hashlib.sha256(data).hexdigest(),source=member.name))
(OUT/'baseline-artifacts.json').write_text(json.dumps(rows,indent=2)+'\n')
print('Verified',len(rows),'baseline assets')
