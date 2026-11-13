"""Build the C12 handoff from completed runtime evidence (not simulated data)."""
import collections, hashlib, json, pathlib, re, subprocess, tomllib
OUT=pathlib.Path(__file__).resolve().parent
ROOT=OUT.parents[2]
subprocess.run(['python3',str(OUT/'summarize.py')],check=True)
rows=json.loads((OUT/'verdicts.json').read_text())
assets=[{k:v for k,v in x.items() if k!='metadata'} for x in json.loads((OUT/'assets.json').read_text())]
base=subprocess.check_output(['git','rev-parse','origin/main'],cwd=ROOT,text=True).strip()
coverage=[]
for row in rows:
    lane=row['lane']; item={'lane':lane}
    for phase in ['smoke','client-smoke']:
        record=json.loads((OUT/lane/phase/'result.json').read_text())
        assert record['exit_code']==0
        audit=json.loads((OUT/lane/phase/'generated/authored-block-audit.json').read_text())
        item[phase]={k:v for k,v in audit.items() if not isinstance(v,list)}
        for f in (OUT/lane/phase).glob('lua-*.json'):
            lua=json.loads(f.read_text())
            assert lua['generatedAt']/1000 >= record['started_at'], 'stale harness Lua report'
            item[phase]['lua']={'generatedAt':lua['generatedAt'],'computerID':lua['computerID'],'peripheral_count':len(lua['peripherals'])}
    for prefix in ['upgrade']+(['old-world'] if lane.startswith('minimal') else []):
        before=json.loads((OUT/lane/(prefix+'-before')/'upgrade-probes.json').read_text())
        after=json.loads((OUT/lane/(prefix+'-after')/'upgrade-probes.json').read_text())
        bm={(e['kind'],e['upgrade']):e for e in before};am={(e['kind'],e['upgrade']):e for e in after}
        assert len(bm)==len(before) and bm.keys()==am.keys()
        assert len(before)==(59 if lane.startswith('minimal') else 63)
        changed=[]
        for key,b in bm.items():
            a=am[key]
            if b.get('lua',{}).get('typeAfter')!=a.get('lua',{}).get('typeAfter'):changed.append(list(key))
            if a.get('lua'):assert a['lua']['generatedAt']>b['lua']['generatedAt']
        item[prefix]={'count':len(before),'kinds':dict(collections.Counter(e['kind'] for e in before)), 'same_upgrade_ids':True,'changed_peripheral_types':changed}
        if prefix=='old-world':
            migration=json.loads((OUT/lane/'old-world/result.json').read_text())
            assert migration['baseline_smoke']==migration['new_probe_command_exit']==0
            assert migration['baseline_commit']==base and migration['reprovisioned_after_switch'] is False
            old_artifacts=json.loads((OUT/lane/'old-world/before-switch/artifacts.json').read_text())
            new_artifacts=json.loads((OUT/lane/'old-world/after-switch/artifacts.json').read_text())
            assert len(old_artifacts)==len(new_artifacts)==5
            expected={a['name']:a['sha256'] for a in assets}
            assert all(expected[a['name']]==a['sha256'] for a in new_artifacts)
            item[prefix]['migration']=migration
            item[prefix]['baseline_artifacts']=old_artifacts
            item[prefix]['new_artifacts']=new_artifacts
    coverage.append(item)
(OUT/'coverage.json').write_text(json.dumps(coverage,indent=2)+'\n')
(OUT/'artifact-inventory.json').write_text(json.dumps(assets,indent=2)+'\n')
summary=[{'lane':r['lane'],'overall':r['verdict'],'server_smoke':r['server_smoke']['verdict'],'client_smoke':r['client_smoke']['verdict'],'single_item_equip':r['upgrade_checks']['before']['verdict'],'restart':r['upgrade_checks']['after']['verdict'],'stacked_pocket_equip':r['upgrade_checks']['stack_equip']['verdict'],'upgrade_checks':r['upgrade_checks']['verdict'],'old_world':r['old_world']['verdict'] if r['old_world'] else 'N/A'} for r in rows]
(OUT/'verdict-table.json').write_text(json.dumps(summary,indent=2)+'\n')
text=['# C12 — libs 2.1.0 / Minecraft 1.20.1 validation','', '**Recommendation: NOT ready for public release. Keep this PR draft; do not merge.**','',f'Baseline: `origin/main` at `{base}`. Pack changes were tested at `796a20c`; this report commit only adds evidence/probe sources. All game processes ran sequentially. No mod source was changed, no version downgraded to pass, and nothing was published to CurseForge or Modrinth.','', '## Verdicts','', '| Lane | Server smoke | Physical client smoke | Single-item equip | Restart | Count-2 pocket equip | Old world | Overall |','|---|---|---|---|---|---|---|---|']
for r in summary:text.append('| '+' | '.join(r[k] for k in ['lane','server_smoke','client_smoke','single_item_equip','restart','stacked_pocket_equip','old_world','overall'])+' |')
text+=['','Smoke PASS means startup, fixture auditing and real client world join passed, not an error-free log or exhaustive gameplay proof. Each server phase verified all five target JAR hashes; every physical-client phase verified all ten server/client JAR hashes. See `verdicts.json`, `coverage.json` and `artifact-inventory.json`.','', '## Release-blocking failure','', 'On all four lanes, a native `pocket.equipBack()` against a stack of **two** valid items throws:', '', '```text','java.lang.IllegalArgumentException: Error constructing UpgradeData for','peripheralworks:universal_scanner: Item 2 universal_scanner must be of size 1.','```','', 'Also reproduced independently with `cloudsolutions:statsd_bridge`, `digitalitems:digitizer`, and the vanilla `computercraft:wireless_modem_normal` control. The item stack remains count 2 and the empty pocket has no peripheral. The vanilla control implicates the shared CC:Tweaked equip/UpgradeData path; attribution to a particular library is not established. The separate single-item round-trips succeed. Turtlematic has no pocket fixtures in this test.','', 'Exact evidence per lane: `<lane>/upgrade-after/stack-equip/results.json` plus `lifecycle.log`. Diagnosis follow-up: Kanban `t_5c2566be` (Albina), after the 1.21 matrix.','', '## Upgrade and old-world coverage','']
for r in rows:
    lane=r['lane'];u=r['upgrade_checks']
    text.append(f'- **{lane}:** {u["before"]["kinds"]} single-item hosts; native unequip/equip + peripheral enumeration/wrap: {u["before"]["verdict"]}; same-host post-stop/start observation: {u["after"]["verdict"]}.')
    if r['old_world']:
        old=r['old_world']; count=old['after']['count'];failed=old['after']['failures']
        text.append(f'  - Old-world before: {old["before"]["verdict"]}; after: {old["after"]["verdict"]}; {count-len(failed)}/{count} retained working upgrades. Failed IDs/reasons: {json.dumps(failed)}. No fixtures were reprovisioned after the version switch. Evidence: `{lane}/old-world-before`, `{lane}/old-world-after`, `{lane}/old-world/{{before-switch,after-switch}}` (artifact inventories and saved-world snapshots).')
text+=['', 'Old-world packs are the exact tracked minimal packs archived from the baseline commit. The baseline server was provisioned with previous releases, native fixture programs were exercised, and the cleanly stopped **same server data** was started against new source. The physical client used for pocket ticking is the new client in both old/new server phases; baseline proof is therefore server-data migration coverage, not an old-client compatibility test.','', 'Previous versions (from baseline pack metadata):','']
for pack in ['FabricMinimal-1.20','ForgeMinimal-1.20']:
    names=[]
    for mod in ['unlimitedperipheralworks','turtlematic','cloudsolutions','digitalitems','cc-tweaked']:
        raw=subprocess.check_output(['git','show',f'{base}:{pack}/mods/{mod}.pw.toml'],cwd=ROOT,text=True)
        names.append(tomllib.loads(raw)['filename'])
    text.append('- '+pack+': '+', '.join('`'+n+'`' for n in names))
text+=['', '## Commands and runtime','', '```sh','python3 -m unittest discover -s testing/tests -v  # 7/7 PASS','for lane in fabric-1.20 forge-1.20 minimal-fabric-1.20 minimal-forge-1.20; do','  ./testing/bin/mc-test smoke "$lane"         # all exit 0','  ./testing/bin/mc-test client-smoke "$lane"  # all exit 0','done','# Additional native probes (sequential orchestration, see scripts):','python3 <report>/extend-lane.py <lane>','python3 <report>/old-world.py <minimal-lane>','```','', 'The actual orchestration also snapshots every phase; `run-lane.py`, `extend-lane.py`, `probe-upgrades.py`, `probe-stack-equip.py` and `old-world.py` are included. Do not blindly rerun stateful recovery scripts. `prepare.py` is retained in the full evidence attachment, not needed to reproduce the runtime probes.','', 'Minecraft 1.20.1; Fabric Loader 0.17.2 or Forge 47.4.10; Java 17 container line (Forge log identifies Eclipse Adoptium 17.0.15). Packwiz executable digest is recorded in `toolchain.json`; this Packwiz binary exposes no version flag. Docker Compose version and container image IDs are also recorded there. Existing pack versions are unchanged. Packwiz refresh was run twice per updated pack and required deterministic manifest/index output; regression tests passed again after resumption.','', '## Tested assets (SHA-256)','', '| Asset | SHA-256 |','|---|---|']
for a in assets:text.append(f'| `{a["name"]}` | `{a["sha256"]}` |')
text+=['', 'The eight SirEdvin GitHub asset digests were compared with the parent handoffs and downloaded bytes, and checked against live GitHub release metadata again on resumption. CC:Tweaked 1.121.0 comes from exact Modrinth version IDs (Fabric `LFj8qZ7a`, Forge `Qm9iIIEY`). Bundled SirEdvin libraries are 2.1.0. No unrelated dependency/loader bumps were required.','', '## Log diagnostics and limits','', '- Forge Creative emits malformed JSON errors for four existing Create cutting recipes under `create:cutting/compat/immersiveengineering/wire_{aluminum,copper,lead,steel}`. These do not prevent startup/fixtures; no causal link to this update or baseline regression is established.','- Forge logs report missing `minVersion` in several mixin configs. Creative optional mixin class lookups also warn about absent integrations.','- Headless clients log offline authentication/profile-key failures, absent audio/narrator support, and an out-of-range simulation-distance option. These are retained, not claimed fixed. No packet-handler crash, network-protocol disconnect, or critical resource reload failure was found in the final smoke logs.','- The initial Forge observation missed four Lua reports because shutdown/turn-on commands are asynchronous. That trial is preserved under `forge-1.20/upgrade-after-async-trial`; the final observation uses a shutdown tick barrier against the same persisted world, without rebuilding fixtures.','- The initial old-world reset/rename hit root-owned HeadlessMC directories. Failed preparation logs are retained; ownership recovery is limited to disposable worktree directories. These preparation failures are not mod failures.','- Early Fabric exploratory/pocket-race/dirty-inventory trials are diagnostic only. Final acceptance uses `upgrade-before`, `upgrade-after`, `old-world-before`, and `old-world-after` exclusively.','- Peripheral exposure/method enumeration/wrap and equip persistence were exercised, not every peripheral method, HTTP endpoint, recipe, visual rendering detail, player-authentication flow, nested hub upgrade or real production-world migration. The old-world fixtures are disposable, command-provisioned minimal test worlds.','', '## Evidence map','', 'Raw logs remain under `testing/reports/libs-2.1.0-mc-1.20/` and are delivered as a task attachment with a SHA-256 manifest. Only compact verdicts, inventories and portable runtime probes are committed. Runtime/JAR caches, credentials, and live container environment files are excluded. Saved-world snapshots in the attachment contain only disposable offline test worlds. Per-lane `smoke/command.log`, `client-smoke/command.log`, `server-logs/latest.log`, `client-logs/latest.log`, upgrade `lifecycle.log`, `upgrade-probes.json`, and old-world artifact inventories are the primary evidence.','']
(OUT/'README.md').write_text('\n'.join(text))
print('Built report for',len(rows),'lanes; release verdict NOT READY')
