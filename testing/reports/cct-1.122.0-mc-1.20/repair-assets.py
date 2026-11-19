"""Recover incomplete Mojang assets from a read-only previous test cache.
Every copied byte is SHA-1 verified against the Mojang index, not trusted blindly.
"""
import hashlib,json,pathlib,shutil
p=pathlib.Path('/dest');source=pathlib.Path('/source');index=json.loads((p/'indexes/5.json').read_text());hashes=set(v['hash'] for v in index['objects'].values());copied=[];bad=[]
for h in hashes:
 target=p/'objects'/h[:2]/h
 if target.exists() and hashlib.sha1(target.read_bytes()).hexdigest()==h:continue
 src=source/h[:2]/h
 if not src.exists() or hashlib.sha1(src.read_bytes()).hexdigest()!=h:bad.append(h);continue
 target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,target);copied.append(h)
print(json.dumps(dict(unique_hashes=len(hashes),repaired=len(copied),bad=bad)))
assert not bad
