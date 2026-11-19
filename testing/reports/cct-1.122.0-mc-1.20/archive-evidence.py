"""Archive only report evidence, never runtime caches or credential files."""
import hashlib,json,pathlib,tarfile
OUT=pathlib.Path(__file__).resolve().parent;archive=OUT.parent/'cct-1.122.0-mc-1.20-evidence.tar.gz'
files=[]
for f in OUT.rglob('*'):
 if not f.is_file() or f.is_symlink():continue
 rel=f.relative_to(OUT)
 if 'fresh-runtime' in rel.parts or 'new-FabricMinimal-1.20' in rel.parts or 'new-ForgeMinimal-1.20' in rel.parts or '__pycache__' in rel.parts:continue
 if f.name in ['evidence-archive.json','evidence-files.json']:continue
 if f.suffix in ['.jar','.env'] or f.name in ['server.properties','usercache.json','accounts.json']:raise RuntimeError('Unexpected sensitive/runtime file '+str(rel))
 files.append(dict(path=str(rel),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
(OUT/'evidence-files.json').write_text(json.dumps(files,indent=2)+'\n')
with tarfile.open(archive,'w:gz') as t:
 for row in files:t.add(OUT/row['path'],arcname=OUT.name+'/'+row['path'])
 t.add(OUT/'evidence-files.json',arcname=OUT.name+'/evidence-files.json')
with tarfile.open(archive) as t:
 for row in files:
  f=t.extractfile(OUT.name+'/'+row['path']);assert f is not None
  assert hashlib.sha256(f.read()).hexdigest()==row['sha256']
record=dict(filename=archive.name,bytes=archive.stat().st_size,sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),files=len(files)+1,excluded=['runtime caches/JARs','fresh-runtime backup','RCON .env','account files'],verified_members=True)
(OUT/'evidence-archive.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2));assert archive.stat().st_size<25*1024*1024
