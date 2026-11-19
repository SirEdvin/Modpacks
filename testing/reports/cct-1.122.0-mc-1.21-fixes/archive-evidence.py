"""Archive and byte-verify C20 reports, never runtime caches or credentials."""
import hashlib
import json
import pathlib
import tarfile

OUT = pathlib.Path(__file__).resolve().parent
archive = OUT.parent / (OUT.name + '-evidence.tar.gz')
files = []
excluded = {'fresh-runtime', '__pycache__', 'new-FabricMinimal-1.21', 'new-NeoForgeMinimal-1.21'}
for f in sorted(OUT.rglob('*')):
    if not f.is_file() or f.is_symlink():
        continue
    rel = f.relative_to(OUT)
    if excluded.intersection(rel.parts) or f.suffix in {'.jar', '.class'}:
        continue
    if f.name in {'evidence-archive.json', 'evidence-files.json', 'delivery.json', 'pr-body.md'}:
        continue
    if f.suffix == '.env' or f.name in {'server.properties', 'usercache.json', 'accounts.json'}:
        raise RuntimeError('Unexpected sensitive/runtime file: ' + str(rel))
    files.append(dict(path=str(rel), bytes=f.stat().st_size, sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
(OUT / 'evidence-files.json').write_text(json.dumps(files, indent=2) + '\n')
with tarfile.open(archive, 'w:gz') as t:
    for row in files:
        t.add(OUT / row['path'], arcname=OUT.name + '/' + row['path'], recursive=False)
    t.add(OUT / 'evidence-files.json', arcname=OUT.name + '/evidence-files.json', recursive=False)
with tarfile.open(archive) as t:
    assert len(t.getmembers()) == len(files) + 1
    for row in files:
        member = t.extractfile(OUT.name + '/' + row['path'])
        assert member is not None
        assert hashlib.sha256(member.read()).hexdigest() == row['sha256'], row['path']
record = dict(filename=archive.name, bytes=archive.stat().st_size,
              sha256=hashlib.sha256(archive.read_bytes()).hexdigest(), files=len(files) + 1,
              excluded=['runtime caches/JARs/classes', 'fresh-runtime backup', 'RCON .env', 'account files'],
              verified_members=True)
(OUT / 'evidence-archive.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps(record, indent=2))
assert archive.stat().st_size < 25 * 1024 * 1024
