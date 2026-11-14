"""Package real C13 evidence, excluding downloads, caches and credentials."""
import hashlib,json,pathlib,tarfile
OUT=pathlib.Path(__file__).resolve().parent
files=[]
for p in sorted(OUT.rglob('*')):
 rel=p.relative_to(OUT)
 if not p.is_file() or p.is_symlink():continue
 if any(s in rel.parts for s in ['downloads','fresh-runtime','delivery','__pycache__']):continue
 if p.name in ['evidence-archive.json','SHA256SUMS']:continue
 files.append(p)
manifest={str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(OUT/'SHA256SUMS').write_text(''.join(f'{sha}  {name}\n' for name,sha in manifest.items()))
dest=OUT/'delivery/libs-2.1.0-mc-1.21-evidence.tar.gz';dest.parent.mkdir(exist_ok=True)
with tarfile.open(dest,'w:gz') as t:
 for p in files+[OUT/'SHA256SUMS']:t.add(p,arcname=str(p.relative_to(OUT)),recursive=False)
with tarfile.open(dest) as t:
 members=t.getmembers();assert len(members)==len(files)+1
 for m in members:
  if m.name=='SHA256SUMS':continue
  stream=t.extractfile(m);assert stream is not None
  assert hashlib.sha256(stream.read()).hexdigest()==manifest[m.name]
size=dest.stat().st_size
record=dict(filename=dest.name,sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),bytes=size,evidence_files=len(files),archive_members=len(members),verified_all_member_bytes=True)
assert size<=25*1024*1024,'attachment exceeds limit; split evidence rather than drop files'
(OUT/'evidence-archive.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
