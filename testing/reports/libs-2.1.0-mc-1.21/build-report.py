"""Build bounded review artifacts from real, preserved C13 outputs."""
import collections,hashlib,json,pathlib,re,subprocess
OUT=pathlib.Path(__file__).resolve().parent;ROOT=OUT.parents[2]
subprocess.run(['python3',str(OUT/'summarize.py')],check=True)
rows=json.loads((OUT/'verdicts.json').read_text());assert len(rows)==4
coverage=[];diagnostics=[];artifacts={};table=[]
for e in rows:
 lane=e['lane'];u=e['upgrade_checks'];o=e['old_world']
 table.append(dict(lane=lane,overall=e['verdict'],server_smoke=e['server_smoke']['verdict'],client_smoke=e['client_smoke']['verdict'],single_item_equip=u['before']['verdict'],restart=u['after']['verdict'],stacked_pocket_equip=u.get('stack_equip',{}).get('verdict','NOT RUN'),old_world=o['verdict'] if o else 'N/A'))
 for phase in ['smoke','client-smoke','upgrade-before','upgrade-after','old-world-before','old-world-after']:
  p=OUT/lane/phase
  m=p/'generated/authored-blocks.json'
  if m.exists():
   d=json.loads(m.read_text());coverage.append(dict(lane=lane,phase=phase,blocks=d['block_count'],turtles=d['turtle_upgrade_count'],pockets=d['pocket_upgrade_count'],skipped_blocks=d.get('skipped_blocks',[])))
  q=p/'result.json'
  if q.exists():
   for a in json.loads(q.read_text()).get('artifacts',[]):artifacts[a['name']]=a['sha256']
  for source in ['server-logs/latest.log','client-logs/latest.log','lifecycle.log']:
   f=p/source
   if not f.exists():continue
   lines=f.read_text(errors='replace').splitlines()
   important=[dict(line=i+1,text=l[:1000]) for i,l in enumerate(lines) if any(x in l for x in ['Done (','joined the game','logged in with entity id','Loaded 2 advancements','All dimensions are saved','All chunks are saved','Stopping server','must be of size 1','not suitable for this upgrade','Failed to collect creative tab','Could not initialize class site.siredvin','ComputerPlatformRegistries.<clinit>','FabricPlatformToolkit.lookup','Encountered an unexpected exception','Preparing crash report'])]
   diagnostics.append(dict(lane=lane,phase=phase,path=str(f.relative_to(OUT)),evidence=important))
(OUT/'verdict-table.json').write_text(json.dumps(table,indent=2)+'\n')
(OUT/'coverage.json').write_text(json.dumps(coverage,indent=2)+'\n')
(OUT/'artifact-inventory.json').write_text(json.dumps(artifacts,indent=2)+'\n')
(OUT/'diagnostics.json').write_text(json.dumps(diagnostics,indent=2)+'\n')
assets=json.loads((OUT/'assets.json').read_text())
lines=['# Libraries 2.1.0 / Minecraft 1.21.1 integration verdict','','Baseline: `'+(OUT/'baseline/commit.txt').read_text().strip()+'`. Java 21; CC:Tweaked **1.121.0**; UPW **1.10.0**, Turtlematic **1.5.1**, CloudSolutions **0.4.0**, DigitalItems **0.6.0**. GitHub release jars only. No mod source, public platform release, or unrelated pack was changed.','','## Verdicts','','| Lane | Overall | Server | Physical client | Count-1 equip | Restart | Count-2 pockets | Old world |','|---|---|---|---|---|---|---|---|']
for e in table:lines.append('| '+' | '.join(e[k] for k in ['lane','overall','server_smoke','client_smoke','single_item_equip','restart','stacked_pocket_equip','old_world'])+' |')
lines+=['','## Findings and exact scope','',
'- Count-2 `pocket.equipBack()` is a separate regression probe, not inferred from the 1.20 result. Four inputs: UPW universal scanner, CloudSolutions statsd bridge, DigitalItems digitizer, and vanilla CC wireless modem. See each `upgrade-after/stack-equip/results.json`. A vanilla control implicates the shared CC equip path, but final root-cause attribution is not claimed.',
'- Fabric creative can join while REI creative-tab collection fails. The first initializer exception points through CloudSolutions creative-tab enumeration, Tweakium `ComputerPlatformRegistries`, DigitalItems platform delegation, and Broccolium `FabricPlatformToolkit.lookup` NPE. Later NoClassDefFoundError messages are consequences. A successful client command is not treated as a clean pass.',
'- NeoForge creative fails during server startup: UPW `apprentice_magic_tome` rejects its default Ars Nouveau apprentice spell book while Tweakium `CreativeTabUtil.addPocket` calls CC `UpgradeData.ofDefault`. CC rebuilds creative tabs in its server-start hook. A preceding Done marker does not mean stable startup. Client and native upgrades cannot be verified when this server cannot remain up; no Ars removal or version downgrade was attempted.',
'- See `diagnostics.json` for line-numbered join, failure and shutdown excerpts. Full raw logs and per-host Lua/JSON are in the evidence archive; per-phase paths below are relative to this directory.',
'','## Upgrade and migration inventory','']
for e in rows:
 u=e['upgrade_checks'];o=e['old_world'];lines.append(f'- `{e["lane"]}`: new-world/native count-1 before `{u["before"]["verdict"]}`, after restart `{u["after"]["verdict"]}`; persistence `{json.dumps(u["persistence"],sort_keys=True)}`.')
 if o:lines.append('  - Previous-release same-world migration: `'+json.dumps(o['persistence'],sort_keys=True)+'`; baseline native setup `'+o['before']['verdict']+'`, post-switch observation `'+o['after']['verdict']+'`. No reprovisioning after source switch. Before/after worlds are retained locally, not committed as pack source.')
 if o:
  f=OUT/e['lane']/'old-world-after/block-retention.json'
  if f.exists():
   blocks=json.loads(f.read_text());removed=[dict(block=b['block'],now_air=b['now_air']) for b in blocks if not b['retained']]
   lines.append(f'  - Standalone old-world blocks: {sum(b["retained"] for b in blocks)}/{len(blocks)} retained; {sum(b["wired"] for b in blocks)} wired peripheral registrations. Missing blocks: `{json.dumps(removed,sort_keys=True)}`. Explicit post-switch queries are in `old-world-after/block-retention.json`. The blanket legacy audit can fail on deliberately removed SmartHome IDs; this is reported separately from four-mod upgrade survival.')
lines+=['','## Reproduction and evidence','',
'```sh','python3 -m unittest discover -s testing/tests -v','python3 testing/reports/libs-2.1.0-mc-1.21/run-lane.py <lane>','python3 testing/reports/libs-2.1.0-mc-1.21/extend-lane.py <lane>','python3 testing/reports/libs-2.1.0-mc-1.21/old-world.py <minimal-lane>','python3 testing/reports/libs-2.1.0-mc-1.21/summarize.py','```','',
'`run-lane.py` executes `./testing/bin/mc-test smoke <lane>` then `client-smoke <lane>`, preserves command exit codes, fresh logs after shutdown, generated manifests, Lua audit and actual installed server/client artifact digests. `extend-lane.py` runs native Lua on each discovered host, using a real disposable player inventory for pockets, serializes pocket equip, saves, stops, restarts without provisioning, and re-observes the same computer IDs. The count-2 probe includes a vanilla control. All lanes ran sequentially.',
'',
'`old-world.py` extracts the immutable baseline minimal packs, provisions their previous-release worlds, runs native equip probes, restores new pack source in finally, then starts the SAME server data and observes without reprovisioning. NeoForge baseline uses 21.1.244 and target uses 21.1.265, as required by target mod metadata. SmartHome Appliances is deliberately removed from both target Fabric packs; its four standalone blocks are not part of the four-mod upgrade-survival count.',
'',
'Python regression tests: **7/7 PASS** (`python-tests.log`). Final Packwiz double-refresh evidence is `refresh-verification.json`; `git diff --check` must pass before commit. Unrelated dependencies are unchanged. An unintended Packwiz Fabric API update was reverted before acceptance; its exploratory result remains separately labelled `exploratory-fabric-api-0.116.18`, not counted as a final lane.',
'',
'Per lane: `<lane>/smoke/command.log`, `<lane>/client-smoke/command.log`, `<lane>/client-smoke/client-logs/latest.log`, `<lane>/upgrade-{before,after}/lifecycle.log`, `upgrade-probes.json`, and `<minimal-lane>/old-world/{commands.log,result.json}` plus `<minimal-lane>/old-world-{before,after}/`. `verdicts.json`, `verdict-table.json`, `coverage.json`, `diagnostics.json`, and `artifact-inventory.json` provide bounded summaries. Failed command logs are preserved even when no fixture manifest can be generated.',
'','## Artifact SHA-256','', '| Asset | SHA-256 |','|---|---|']
for name,sha in sorted(artifacts.items()):lines.append(f'| `{name}` | `{sha}` |')
lines+=['','All eight GitHub asset digests were independently downloaded and matched before pack edits; runtime target JARs are checked against Packwiz metadata. `assets.json` preserves exact release URLs and embedded loader metadata. Turtlematic 1.5.1 follows the coordinator override, not the original 1.5.0 handoff.','','## Limits / recommendation','','This is API equip/peripheral-exposure, restart/migration and headless client-join smoke coverage, not visual inspection or exhaustive calls to every peripheral method. GTCEu is not installed, so no GTCEu-specific methods were tested. Failures prevent a blanket compatibility claim. **NOT ready for public release. Keep the PR draft and do not merge under this card’s all-pass rule.**','']
(OUT/'README.md').write_text('\n'.join(lines))
print(json.dumps(table,indent=2))
