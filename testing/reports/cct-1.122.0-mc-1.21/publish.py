"""Publish verified C15 report as a draft; never merges or closes PR #6."""
import hashlib,json,pathlib,subprocess,sys
OUT=pathlib.Path(__file__).resolve().parent;ROOT=OUT.parents[2]
def run(args,**kw):return subprocess.run(args,cwd=ROOT,check=True,**kw)
def output(args):return subprocess.check_output(args,cwd=ROOT,text=True).strip()
run([sys.executable,str(OUT/'final-checks.py')])
rows=json.loads((OUT/'verdict-table.json').read_text());assert len(rows)==4
readme=OUT/'README.md';text=readme.read_text();text+='\n## Durable evidence\n\nThe full evidence archive is intentionally included with this PR as `testing/reports/cct-1.122.0-mc-1.21-evidence.tar.gz`; `evidence-archive.json` records its SHA-256 and verified member count. It contains only disposable test-world/report evidence, not mod JARs or runtime caches. It is also submitted to this task as an attachment.\n\nThe additional `audit-old-fixtures.py` observations are under each minimal lane’s `old-world-fixture-audit/`: exact pocket-display/lectern IDs, turtle upgrades, all original block positions/modems and a fresh wired-control Lua snapshot, compared against the pre-switch saved-world control report. No fixture is replaced.\n\nPreparation used `make cctweaked`, `make all`, and (for both Fabric packs) `packwiz modrinth add https://modrinth.com/mod/fabric-api/version/5SwzqWUu -y`, followed by refresh.\n'
readme.write_text(text)
run([sys.executable,str(OUT/'archive-evidence.py')])
archive=OUT.parent/'cct-1.122.0-mc-1.21-evidence.tar.gz'
compact=[p for p in OUT.iterdir() if p.is_file() and (p.suffix in ['.py','.json'] or p.name=='README.md') and p.name not in ['evidence-files.json','pr-receipt.json']]
compact += [OUT/r['lane']/'verdict.json' for r in rows]
run(['git','add','-f',*[str(p.relative_to(ROOT)) for p in compact],str(archive.relative_to(ROOT))])
run(['git','diff','--cached','--check'])
run(['git','commit','-m','test: record four-lane 1.21.1 CC:Tweaked retest evidence'])
head=output(['git','rev-parse','HEAD']);branch=output(['git','branch','--show-current'])
run(['git','push','--set-upstream','origin',branch])
url=output(['gh','pr','create','--repo','SirEdvin/Modpacks','--base','main','--head',branch,'--draft','--title','test: retest Minecraft 1.21.1 with CC:Tweaked 1.122.0','--body-file',str(readme)])
pr=json.loads(output(['gh','pr','view',url,'--repo','SirEdvin/Modpacks','--json','number,url,state,isDraft,headRefOid,baseRefName']))
assert pr['headRefOid']==head and pr['baseRefName']=='main' and pr['state']=='OPEN' and pr['isDraft']
body=f'C15 follow-up retest with CC:Tweaked 1.122.0 is {url} (head {head}). This branch merges this PR’s existing 1.21 updates as its starting point. See the new draft PR for exact per-lane verdicts and verified artifact/evidence digests. This PR remains open; no mod code was changed or downgraded.'
run(['gh','pr','comment','6','--repo','SirEdvin/Modpacks','--body',body])
comments=json.loads(output(['gh','api','repos/SirEdvin/Modpacks/issues/6/comments?per_page=100']))
comment=next(c for c in reversed(comments) if c['body']==body)
previous=json.loads(output(['gh','pr','view','6','--repo','SirEdvin/Modpacks','--json','state,isDraft,headRefOid']))
assert previous['state']=='OPEN' and previous['headRefOid']=='8621f6a63de0a0dae2b011aaa3c2cf3bb31731a1'
pr['previous_pr_comment_url']=comment['html_url'];pr['previous_pr']=previous
pr['archive']=json.loads((OUT/'evidence-archive.json').read_text())
pr['attachment_urls']={p.name:f'https://raw.githubusercontent.com/SirEdvin/Modpacks/{head}/{p.relative_to(ROOT)}' for p in [archive,readme,OUT/'artifact-inventory.json',OUT/'old-world-survival.json']}
(OUT/'pr-receipt.json').write_text(json.dumps(pr,indent=2)+'\n')
print('PUBLICATION RECEIPT',json.dumps(pr,indent=2));print('VERDICTS',json.dumps(rows));assert not output(['git','status','--short'])
