"""Render compact human report and diagnostics from saved C20 evidence."""
import pathlib,json,collections,re
OUT=pathlib.Path(__file__).resolve().parent;rows=json.loads((OUT/'verdicts.json').read_text());assets=json.loads((OUT/'assets.json').read_text())
lines=['# Minecraft 1.21.1 — patched release retest (C20)','','CC:Tweaked **1.122.0**, UPW **1.10.1**, CloudSolutions **0.4.1**, DigitalItems **0.6.1**, Turtlematic **1.5.2**.','','## Verdicts','','| Lane | Overall | Server | Client | Native + restart | Legal stacked equip + restart | PR #8 old world |','|---|---|---|---|---|---|---|']
for r in rows:
 lines.append('| '+' | '.join([r['lane'],r['verdict'],r['server_smoke']['verdict'],r['client_smoke']['verdict'],r['single_item_and_restart']['verdict'],r['all_stacks_and_restart']['verdict'],r['old_world']['verdict'] if r['old_world'] else 'N/A'])+' |')
ready=all(r['verdict']=='PASS' for r in rows)
lines+=['','**Recommendation: Minecraft 1.21.1 '+('ready for public release within the tested scope.' if ready else 'NOT ready for public release.')+'**','','## Scope and evidence','','All lanes ran sequentially. Each lane runs server smoke, a matching physical HeadlessMC client joining the dedicated server, native Lua equip/unequip for every active authored upgrade, real-player pocket ticking, legal count-two equip with vanilla modem controls, then observation of the same hosts after clean server restart (no reprovisioning). Nonstackable items are explicitly excluded from illegal count-two stacks and covered by single-item round trips.','', 'Minimal migrations start from exact PR #8 pack source at `'+(OUT/'baseline/commit.txt').read_text().strip()+'`, not main. Saved worlds are retained before/after switching releases. The migration probes never reprovision after the switch. The final independent audit checks blocks, wired attachments, upgraded turtles, pocket displays/lecterns and fresh control-computer Lua.','','A read-only Java instrumentation observer captures the actual loaded Fabric EMI index; it does not patch game or mod classes. Its source is `EmiObserver.java`; compile with `javac --release 21 EmiObserver.java`, then `jar cfm emi-observer.jar observer-manifest.txt EmiObserver.class`. `extend-lane.py` injects it only into Fabric creative client probe runs. Normal client-smoke is uninstrumented.','','No exhaustive peripheral method behavior, manual visual/rendering inspection, survival progression, CurseForge or Modrinth publication was performed. Headless index enumeration is recipe-viewer content evidence, not a screenshot. CC 1.122.0 upstream MC1.21.1 artifacts are beta-channel despite the exact requested version.','','## Per-lane evidence']
for r in rows:
 lane=r['lane'];p=OUT/lane;lines+=['',f'### `{lane}` — {r["verdict"]}',f'- Detailed verdict: `{lane}/verdict.json`.',f'- Smoke/client command logs: `{lane}/smoke/command.log`, `{lane}/client-smoke/command.log`.',f'- Fresh client log: `{lane}/client-smoke/client-logs/latest.log`.',f'- Native/restart logs and raw Lua/NBT: `{lane}/upgrade-before/`, `{lane}/upgrade-after/`.',f'- Regression tests: `{lane}-regression-tests.log`.']
 for key in ['single_item_and_restart','all_stacks_and_restart']:
  e=r[key];lines.append(f'- {key}: {e["verdict"]}; before {e["before"].get("count",0)} / after {e["after"].get("count",0)} hosts.')
 if r.get('creative_emi_index'):lines.append('- EMI index gate: '+r['creative_emi_index']['verdict']+'; `fabric-1.21/upgrade-before/emi-index-observation.tsv` and exact upgrade coverage in verdict JSON.')
 if r.get('ars_magic_tomes'):lines.append('- Ars presence and all four magic-tome native round trips: '+r['ars_magic_tomes']['verdict']+'.')
 if r['old_world']:lines.append(f'- Migration: `{lane}/old-world/`, `{lane}/old-world-before/`, `{lane}/old-world-after/`, `{lane}/old-world-fixture-audit/`.')
 if (p/'failure.json').exists():
  failure=json.loads((p/'failure.json').read_text())
  lines += ['- Failing step: '+failure['step']+'.','- Suspected mod: '+failure['suspected_mod']+'.','- Log excerpt: `'+failure['excerpt']+'`.', '- Unverified dependent checks: '+', '.join(failure['blocked_checks'])+'.']
  if failure.get('additional_harness_limit'):lines.append('- Separate harness limitation: '+failure['additional_harness_limit'])
 if r['verdict']=='FAIL':
  for key,value in r.items():
   if isinstance(value,dict) and value.get('verdict') not in [None,'PASS']:lines.append('- Failing gate `'+key+'`: `'+json.dumps(value.get('failures',value),ensure_ascii=False)+'`.')
 lines+=['','Commands (actual exit codes):','','| Command | Exit | Seconds |','|---|---:|---:|']
 for c in json.loads((OUT/f'{lane}-commands.json').read_text()):
  cmd=' '.join(c['command']).replace(str(OUT)+'/','');lines.append(f'| `{cmd}` | {c["exit_code"]} | {c["seconds"]} |')
lines+=['','## Exact artifacts','','All eight patched mod JAR SHA-256 values matched the parent handoffs and downloaded GitHub release bytes. Both CC artifacts were re-downloaded and verified against C15 hashes. Phase-specific installed server/client digest gates are in result/artefact JSON.','','| Artifact | SHA-256 |','|---|---|']
for a in assets:lines.append(f'| `{a["name"]}` | `{a["sha256"]}` |')
lines+=['','## Reproduction','','```sh','python3 testing/reports/cct-1.122.0-mc-1.21-fixes/setup.py','# Compile the read-only EMI observer (above), then run ONE lane at a time:','python3 testing/reports/cct-1.122.0-mc-1.21-fixes/execute-lane.py fabric-1.21','python3 testing/reports/cct-1.122.0-mc-1.21-fixes/execute-lane.py neoforge-1.21','python3 testing/reports/cct-1.122.0-mc-1.21-fixes/execute-lane.py minimal-fabric-1.21','python3 testing/reports/cct-1.122.0-mc-1.21-fixes/execute-lane.py minimal-neoforge-1.21','python3 testing/reports/cct-1.122.0-mc-1.21-fixes/summarize.py','python3 testing/reports/cct-1.122.0-mc-1.21-fixes/acceptance.py','python3 testing/reports/cct-1.122.0-mc-1.21-fixes/static-checks.py','```','','Use a fresh worktree for reproduction; old-world source swaps deliberately refuse to overwrite existing migration evidence. Full phase logs and Lua/NBT snapshots are in the sibling evidence archive. Runtime caches, account files, environment/password files, and JARs are excluded.']
(OUT/'README.md').write_text('\n'.join(lines)+'\n')
diag=[]
for r in rows:
 for f in (OUT/r['lane']).glob('*/**/latest.log'):
  matches=[dict(line=i,text=line) for i,line in enumerate(f.read_text(errors='replace').splitlines(),1) if re.search(r'ERROR|FATAL|Exception|Failed to collect creative|Critical error',line)]
  if matches:diag.append(dict(path=str(f.relative_to(OUT)),matches=matches))
(OUT/'diagnostics.json').write_text(json.dumps(diag,indent=2)+'\n')
print('Report rendered:',len(rows),'lanes; recommendation:',ready)
