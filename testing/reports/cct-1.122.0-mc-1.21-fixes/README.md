# Minecraft 1.21.1 — patched release retest (C20)

CC:Tweaked **1.122.0**, UPW **1.10.1**, CloudSolutions **0.4.1**, DigitalItems **0.6.1**, Turtlematic **1.5.2**.

## Verdicts

| Lane | Overall | Server | Client | Native + restart | Legal stacked equip + restart | PR #8 old world |
|---|---|---|---|---|---|---|
| fabric-1.21 | PASS | PASS | PASS | PASS | PASS | N/A |
| neoforge-1.21 | FAIL | PASS | PASS | FAIL | NOT RUN | N/A |
| minimal-fabric-1.21 | PASS | PASS | PASS | PASS | PASS | PASS |
| minimal-neoforge-1.21 | PASS | PASS | PASS | PASS | PASS | PASS |

**Recommendation: Minecraft 1.21.1 NOT ready for public release.**

## Scope and evidence

All lanes ran sequentially. Each lane runs server smoke, a matching physical HeadlessMC client joining the dedicated server, native Lua equip/unequip for every active authored upgrade, real-player pocket ticking, legal count-two equip with vanilla modem controls, then observation of the same hosts after clean server restart (no reprovisioning). Nonstackable items are explicitly excluded from illegal count-two stacks and covered by single-item round trips.

Minimal migrations start from exact PR #8 pack source at `b962c082a1c75ad43238dea7a367df42b5edf3dc`, not main. Saved worlds are retained before/after switching releases. The migration probes never reprovision after the switch. The final independent audit checks blocks, wired attachments, upgraded turtles, pocket displays/lecterns and fresh control-computer Lua.

A read-only Java instrumentation observer captures the actual loaded Fabric EMI index; it does not patch game or mod classes. Its source is `EmiObserver.java`; compile with `javac --release 21 EmiObserver.java`, then `jar cfm emi-observer.jar observer-manifest.txt EmiObserver.class`. `extend-lane.py` injects it only into Fabric creative client probe runs. Normal client-smoke is uninstrumented.

No exhaustive peripheral method behavior, manual visual/rendering inspection, survival progression, CurseForge or Modrinth publication was performed. Headless index enumeration is recipe-viewer content evidence, not a screenshot. CC 1.122.0 upstream MC1.21.1 artifacts are beta-channel despite the exact requested version.

## Per-lane evidence

### `fabric-1.21` — PASS
- Detailed verdict: `fabric-1.21/verdict.json`.
- Smoke/client command logs: `fabric-1.21/smoke/command.log`, `fabric-1.21/client-smoke/command.log`.
- Fresh client log: `fabric-1.21/client-smoke/client-logs/latest.log`.
- Native/restart logs and raw Lua/NBT: `fabric-1.21/upgrade-before/`, `fabric-1.21/upgrade-after/`.
- Regression tests: `fabric-1.21-regression-tests.log`.
- single_item_and_restart: PASS; before 59 / after 59 hosts.
- all_stacks_and_restart: PASS; before 30 / after 30 hosts.
- EMI index gate: PASS; `fabric-1.21/upgrade-before/emi-index-observation.tsv` and exact upgrade coverage in verdict JSON.

Commands (actual exit codes):

| Command | Exit | Seconds |
|---|---:|---:|
| `/home/siredvin/.hermes/installs/3b54febdd738fbcc/environments/aa74021dd42641c39e844bb5d3f4589f/venv/bin/python3 run-lane.py fabric-1.21` | 0 | 380.2 |
| `/home/siredvin/.hermes/installs/3b54febdd738fbcc/environments/aa74021dd42641c39e844bb5d3f4589f/venv/bin/python3 extend-lane.py fabric-1.21` | 1 | 90.1 |
| `/home/siredvin/.hermes/installs/3b54febdd738fbcc/environments/aa74021dd42641c39e844bb5d3f4589f/venv/bin/python3 -m unittest discover -s testing/tests -v` | 0 | 0.1 |
| `/home/siredvin/.hermes/installs/3b54febdd738fbcc/environments/aa74021dd42641c39e844bb5d3f4589f/venv/bin/python3 summarize.py fabric-1.21` | 0 | 0.0 |
| `python3 testing/reports/cct-1.122.0-mc-1.21-fixes/extend-lane.py fabric-1.21` | 0 | 373.51420545578003 |

### `neoforge-1.21` — FAIL
- Detailed verdict: `neoforge-1.21/verdict.json`.
- Smoke/client command logs: `neoforge-1.21/smoke/command.log`, `neoforge-1.21/client-smoke/command.log`.
- Fresh client log: `neoforge-1.21/client-smoke/client-logs/latest.log`.
- Native/restart logs and raw Lua/NBT: `neoforge-1.21/upgrade-before/`, `neoforge-1.21/upgrade-after/`.
- Regression tests: `neoforge-1.21-regression-tests.log`.
- single_item_and_restart: FAIL; before 71 / after 0 hosts.
- all_stacks_and_restart: NOT RUN; before 0 / after 0 hosts.
- Ars presence and all four magic-tome native round trips: FAIL.
- Failing step: native pocket round-trip / remote-client container_set_slot decode.
- Suspected mod: UnlimitedPeripheralWorks AE2 wireless crafting terminal integration with CC:Tweaked 1.122.0.
- Log excerpt: `Caused by: java.lang.IllegalArgumentException: Error constructing UpgradeData for peripheralworks:ae2_wireless_crafting_terminal: Item 1 WirelessCraftingTerminalItem[wireless_crafting_terminal] is not suitable for this upgrade.`.
- Unverified dependent checks: remaining native pockets including four magic tomes, legal stacked-equip fixtures, same-host restart.
- Separate harness limitation: Stack fixture allocation asserts before filtering nonstackable entries: 18 native pockets leave 17 disjoint slots, but it requests 19. No stacked-equip acceptance was obtained; this is distinct from the earlier genuine AE2 client disconnect.
- Failing gate `single_item_and_restart`: `["before/after gate"]`.
- Failing gate `all_stacks_and_restart`: `["before/after gate"]`.
- Failing gate `all_client_log_scan`: `{"verdict": "FAIL", "logs": [{"path": "neoforge-1.21/client-smoke/client-logs/latest.log", "critical_hits": []}, {"path": "neoforge-1.21/upgrade-before/client-logs/latest.log", "critical_hits": [{"line": 640, "text": "[19Nov2026 22:27:16.037] [Netty Epoll Client IO #0/FATAL] [net.neoforged.neoforge.common.NeoForgeMod/]: Preparing crash report with UUID e038bb62-52a1-4c19-8d01-39bf2ab5bbac"}]}]}`.
- Failing gate `ars_magic_tomes`: `{"verdict": "FAIL", "ars_jars": ["ars_nouveau-1.21.1-5.12.1.jar"], "upgrades": [{"upgrade": "peripheralworks:apprentice_magic_tome", "lua": null}, {"upgrade": "peripheralworks:archmage_magic_tome", "lua": null}, {"upgrade": "peripheralworks:caster_magic_tome", "lua": null}, {"upgrade": "peripheralworks:novice_magic_tome", "lua": null}]}`.

Commands (actual exit codes):

| Command | Exit | Seconds |
|---|---:|---:|
| `/home/siredvin/.hermes/installs/3b54febdd738fbcc/environments/aa74021dd42641c39e844bb5d3f4589f/venv/bin/python3 run-lane.py neoforge-1.21` | 0 | 448.5 |
| `/home/siredvin/.hermes/installs/3b54febdd738fbcc/environments/aa74021dd42641c39e844bb5d3f4589f/venv/bin/python3 extend-lane.py neoforge-1.21` | 1 | 396.4 |
| `/home/siredvin/.hermes/installs/3b54febdd738fbcc/environments/aa74021dd42641c39e844bb5d3f4589f/venv/bin/python3 -m unittest discover -s testing/tests -v` | 0 | 0.1 |
| `/home/siredvin/.hermes/installs/3b54febdd738fbcc/environments/aa74021dd42641c39e844bb5d3f4589f/venv/bin/python3 summarize.py neoforge-1.21` | 0 | 0.0 |

### `minimal-fabric-1.21` — PASS
- Detailed verdict: `minimal-fabric-1.21/verdict.json`.
- Smoke/client command logs: `minimal-fabric-1.21/smoke/command.log`, `minimal-fabric-1.21/client-smoke/command.log`.
- Fresh client log: `minimal-fabric-1.21/client-smoke/client-logs/latest.log`.
- Native/restart logs and raw Lua/NBT: `minimal-fabric-1.21/upgrade-before/`, `minimal-fabric-1.21/upgrade-after/`.
- Regression tests: `minimal-fabric-1.21-regression-tests.log`.
- single_item_and_restart: PASS; before 59 / after 59 hosts.
- all_stacks_and_restart: PASS; before 30 / after 30 hosts.
- Migration: `minimal-fabric-1.21/old-world/`, `minimal-fabric-1.21/old-world-before/`, `minimal-fabric-1.21/old-world-after/`, `minimal-fabric-1.21/old-world-fixture-audit/`.

Commands (actual exit codes):

| Command | Exit | Seconds |
|---|---:|---:|
| `/home/siredvin/.hermes/installs/3b54febdd738fbcc/environments/aa74021dd42641c39e844bb5d3f4589f/venv/bin/python3 run-lane.py minimal-fabric-1.21` | 0 | 368.9 |
| `/home/siredvin/.hermes/installs/3b54febdd738fbcc/environments/aa74021dd42641c39e844bb5d3f4589f/venv/bin/python3 extend-lane.py minimal-fabric-1.21` | 0 | 359.7 |
| `/home/siredvin/.hermes/installs/3b54febdd738fbcc/environments/aa74021dd42641c39e844bb5d3f4589f/venv/bin/python3 old-world.py minimal-fabric-1.21` | 0 | 481.0 |
| `/home/siredvin/.hermes/installs/3b54febdd738fbcc/environments/aa74021dd42641c39e844bb5d3f4589f/venv/bin/python3 audit-old-fixtures.py minimal-fabric-1.21` | 0 | 91.5 |
| `/home/siredvin/.hermes/installs/3b54febdd738fbcc/environments/aa74021dd42641c39e844bb5d3f4589f/venv/bin/python3 -m unittest discover -s testing/tests -v` | 0 | 0.1 |
| `/home/siredvin/.hermes/installs/3b54febdd738fbcc/environments/aa74021dd42641c39e844bb5d3f4589f/venv/bin/python3 summarize.py minimal-fabric-1.21` | 0 | 0.1 |

### `minimal-neoforge-1.21` — PASS
- Detailed verdict: `minimal-neoforge-1.21/verdict.json`.
- Smoke/client command logs: `minimal-neoforge-1.21/smoke/command.log`, `minimal-neoforge-1.21/client-smoke/command.log`.
- Fresh client log: `minimal-neoforge-1.21/client-smoke/client-logs/latest.log`.
- Native/restart logs and raw Lua/NBT: `minimal-neoforge-1.21/upgrade-before/`, `minimal-neoforge-1.21/upgrade-after/`.
- Regression tests: `minimal-neoforge-1.21-regression-tests.log`.
- single_item_and_restart: PASS; before 59 / after 59 hosts.
- all_stacks_and_restart: PASS; before 30 / after 30 hosts.
- Migration: `minimal-neoforge-1.21/old-world/`, `minimal-neoforge-1.21/old-world-before/`, `minimal-neoforge-1.21/old-world-after/`, `minimal-neoforge-1.21/old-world-fixture-audit/`.

Commands (actual exit codes):

| Command | Exit | Seconds |
|---|---:|---:|
| `/home/siredvin/.hermes/installs/3b54febdd738fbcc/environments/aa74021dd42641c39e844bb5d3f4589f/venv/bin/python3 run-lane.py minimal-neoforge-1.21` | 0 | 391.0 |
| `/home/siredvin/.hermes/installs/3b54febdd738fbcc/environments/aa74021dd42641c39e844bb5d3f4589f/venv/bin/python3 extend-lane.py minimal-neoforge-1.21` | 0 | 391.7 |
| `/home/siredvin/.hermes/installs/3b54febdd738fbcc/environments/aa74021dd42641c39e844bb5d3f4589f/venv/bin/python3 old-world.py minimal-neoforge-1.21` | 0 | 522.3 |
| `/home/siredvin/.hermes/installs/3b54febdd738fbcc/environments/aa74021dd42641c39e844bb5d3f4589f/venv/bin/python3 audit-old-fixtures.py minimal-neoforge-1.21` | 0 | 91.6 |
| `/home/siredvin/.hermes/installs/3b54febdd738fbcc/environments/aa74021dd42641c39e844bb5d3f4589f/venv/bin/python3 -m unittest discover -s testing/tests -v` | 0 | 0.1 |
| `/home/siredvin/.hermes/installs/3b54febdd738fbcc/environments/aa74021dd42641c39e844bb5d3f4589f/venv/bin/python3 summarize.py minimal-neoforge-1.21` | 0 | 0.1 |

## Exact artifacts

All eight patched mod JAR SHA-256 values matched the parent handoffs and downloaded GitHub release bytes. Both CC artifacts were re-downloaded and verified against C15 hashes. Phase-specific installed server/client digest gates are in result/artefact JSON.

| Artifact | SHA-256 |
|---|---|
| `peripheralworks-fabric-1.21.1-1.10.1.jar` | `cf77870dae82a23e2d965698eed635a32959d1ed9a6e7664af7bb953dc72d343` |
| `peripheralworks-forge-1.21.1-1.10.1.jar` | `74a94a9c77af04772163d6cb1d443a93f12d7b22c66263e853b69fdc03228810` |
| `cloudsolutions-fabric-1.21.1-0.4.1.jar` | `4c7f0285d6d5190d23ffc8d53b179556421c1f1f71eb739d0ea9b30027408357` |
| `cloudsolutions-forge-1.21.1-0.4.1.jar` | `c6cc23ff95428b7c768d2514ba530182edd513676b6dfce50af4f3c65b2cd7b0` |
| `digitalitems-fabric-1.21.1-0.6.1.jar` | `3f934f122c5586ab8224cfe9ceab162b1146fd11fe96406505a52fccaa9cb481` |
| `digitalitems-forge-1.21.1-0.6.1.jar` | `cd2dec03bd1ddf97ebd9e922aa874f1003baab90e1218c8e844340a1e5929e7d` |
| `turtlematic-fabric-1.21.1-1.5.2.jar` | `decf4368eb9a961e98f6b4df0bbb3a9446c8dbedd54ea48a953762ec1bc20d07` |
| `turtlematic-forge-1.21.1-1.5.2.jar` | `c59b272f3d438c68c304c6e5947afdd0d1481968c89ed30422ee09bb8d52f0c7` |
| `cc-tweaked-1.21.1-fabric-1.122.0.jar` | `76c3ae07d20e75f155c94f200549f495b690bac8341d164203f1567611fa4388` |
| `cc-tweaked-1.21.1-forge-1.122.0.jar` | `d3b1153054d136dac1319c6d3c085865b7d174e40686aa1dc1f077d5485b8df0` |

## Reproduction

```sh
python3 testing/reports/cct-1.122.0-mc-1.21-fixes/setup.py
# Compile the read-only EMI observer (above), then run ONE lane at a time:
python3 testing/reports/cct-1.122.0-mc-1.21-fixes/execute-lane.py fabric-1.21
python3 testing/reports/cct-1.122.0-mc-1.21-fixes/execute-lane.py neoforge-1.21
python3 testing/reports/cct-1.122.0-mc-1.21-fixes/execute-lane.py minimal-fabric-1.21
python3 testing/reports/cct-1.122.0-mc-1.21-fixes/execute-lane.py minimal-neoforge-1.21
python3 testing/reports/cct-1.122.0-mc-1.21-fixes/summarize.py
python3 testing/reports/cct-1.122.0-mc-1.21-fixes/acceptance.py
python3 testing/reports/cct-1.122.0-mc-1.21-fixes/static-checks.py
```

Use a fresh worktree for reproduction; old-world source swaps deliberately refuse to overwrite existing migration evidence. Full phase logs and Lua/NBT snapshots are in the sibling evidence archive. Runtime caches, account files, environment/password files, and JARs are excluded.
