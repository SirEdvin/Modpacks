# C15 — CC:Tweaked 1.122.0 / Minecraft 1.21.1 retest

**Recommendation: NOT ready for public release. Keep the PR draft; do not merge.**

Baseline: `origin/main` `8d0955a38b32f6a47d0d7d2f7b54486b0ac5fdf8`. Starting changes merged from PR #6 head `8621f6a63de0a0dae2b011aaa3c2cf3bb31731a1`; PR #6 remains open. Four lanes executed strictly sequentially. Java 21; Fabric 0.19.3; target NeoForge 21.1.265 (inherited metadata-required update from PR #6). No mod source changes, downgrades, CurseForge/Modrinth publication, or changes to unrelated packs.

## Verdicts

| Lane | Server (exit) | Client (exit) | Single equip/restart | Count-two equip/restart | Pocket regression/control | Old world | Overall |
|---|---|---|---|---|---|---|---|
| fabric-1.21 | PASS (0) | FAIL (0) | PASS | PASS | PASS | N/A | **FAIL** |
| neoforge-1.21 | FAIL (1) | FAIL (1) | NOT RUN | NOT RUN | NOT RUN | N/A | **FAIL** |
| minimal-fabric-1.21 | PASS (0) | PASS (0) | PASS | PASS | PASS | PASS | **PASS** |
| minimal-neoforge-1.21 | PASS (0) | PASS (0) | PASS | PASS | PASS | PASS | **PASS** |

Client success requires more than the harness exit code: the final fresh client log is checked for critical initializer/reload/packet failures as well as a real server join and advancement synchronization. NOT RUN is unverified due to an earlier failure, never a pass or proof a regression reproduced.

## C12/C13 regressions

- **Fabric Creative:** the C13 creative-tab initializer error still reproduces. The physical client joins and the harness exits 0, but REI fails to collect creative tabs and EMI reload fails. First initializer path: CloudSolutions creative-tab enumeration → Tweakium `ComputerPlatformRegistries.<clinit>` → DigitalItems platform delegation → Broccolium `FabricPlatformToolkit.lookup:68` NPE. Suspected area: bundled Fabric platform registry lookup/lifecycle in Broccolium/Tweakium 2.1.0, not proven to be a new CC regression. Evidence: `fabric-1.21/client-smoke/client-logs/latest.log:389-422`, plus `diagnostics.json`.
- **NeoForge Creative:** the C13 Ars integration crash still reproduces before stable server startup. UPW `peripheralworks:apprentice_magic_tome` rejects its default `ars_nouveau:apprentice_spell_book` while Tweakium `CreativeTabUtil.addPocket` calls CC `UpgradeData.ofDefault` during server-start creative-tab rebuilding. Suspected area: UPW Ars upgrade suitability/default-item integration. Exact exception: `Error constructing UpgradeData for peripheralworks:apprentice_magic_tome: Item 1 ars_nouveau:apprentice_spell_book is not suitable for this upgrade.` A preceding Done marker does not make the server usable. Client launch and native equips are unverified, because the server cannot stay up. Evidence: `neoforge-1.21/smoke/command.log:352-456` and other phase command/lifecycle logs.
- **Stacked pocket equip:** see the per-lane pocket regression column above. PASS means every active stackable authored pocket fixture plus CC wireless-modem control equipped from two input items, consumed one, exposed the expected peripheral, and survived a restart. NeoForge Creative has no runnable probe and therefore no fix claim.

## Native coverage

The harness NBT fixtures are supplemented by real Lua on every active turtle and pocket upgrade discovered from the exact installed target JARs. Pockets tick in a disposable real headless player inventory, not an item display. Count-one probes unequip/re-equip, enumerate types/methods, and wrap the peripheral. Separate count-two hosts verify native input count/maxCount, successful equip and remaining count one, plus exact live upgrade data. A clean server stop/start then observes the SAME computer IDs without reprovisioning or re-equipping. Peripheral types and fresh generatedAt timestamps are compared. Optional integrations are included only where their dependencies are installed.

Nonstackable items are measured at native `turtle.getItemDetail(1,true).maxCount=1` from legal count-one inputs and covered by single-item probes; no illegal forced tool/core/terminal stacks are used for acceptance. Per-phase `item-stack-limits.json` and `all-stacks/nonstackable.json` list the exact limits/exclusions. MC 1.21 pocket data components and compound turtle LeftUpgrade data are parsed explicitly.
- `fabric-1.21`: single `{'turtle': 49, 'pocket': 10}`; count-two including vanilla controls `{'turtle': 19, 'pocket': 11}`. Detailed gates and any failed IDs are in `fabric-1.21/verdict.json`.
- `neoforge-1.21`: single `None`; count-two including vanilla controls `None`. Detailed gates and any failed IDs are in `neoforge-1.21/verdict.json`.
- `minimal-fabric-1.21`: single `{'turtle': 49, 'pocket': 10}`; count-two including vanilla controls `{'turtle': 19, 'pocket': 11}`. Detailed gates and any failed IDs are in `minimal-fabric-1.21/verdict.json`.
- `minimal-neoforge-1.21`: single `{'turtle': 49, 'pocket': 10}`; count-two including vanilla controls `{'turtle': 19, 'pocket': 11}`. Detailed gates and any failed IDs are in `minimal-neoforge-1.21/verdict.json`.

## Exact old-world survival

Both minimal worlds are provisioned with immutable origin/main pack source, exercised natively, saved and stopped. The same server data is then started with new packs and observed without provisioning or replacing the native hosts. This IS a four-mod migration: UPW 1.9.2 → 1.10.0; Turtlematic 1.4.10 → 1.5.1; CloudSolutions 0.3.4 → 0.4.0; DigitalItems 0.5.8 → 0.6.0; CC:Tweaked 1.120.0 → 1.122.0. NeoForge also changes 21.1.244 → 21.1.265; Fabric API changes 0.116.14 → 0.116.18. Baseline asset digests are `baseline-artifacts.json`, source snapshot is `baseline/minimal-packs.tar`, and actual installed before/after target JAR digests are saved in each phase. Old-world coverage is single-item hosts and authored fixtures, not count-two old-world hosts.

- `minimal-fabric-1.21`: `{"blocks": {"expected_wired": 18, "intentionally_removed": ["smarthome_appliances:lamp", "smarthome_appliances:led_panel", "smarthome_appliances:smooth_led_panel", "smarthome_appliances:switch"], "target_count": 23, "target_retained": 23, "unexpected_missing": [], "wired": 18}, "complete_fixture_audit": {"control_peripherals": 20, "lecterns_verified": 10, "missing_or_changed_control_types": [], "pocket_displays": 10, "turtles_verified": 49, "verdict": "PASS"}, "failed": [], "lane": "minimal-fabric-1.21", "migration": {"baseline_commit": "8d0955a38b32f6a47d0d7d2f7b54486b0ac5fdf8", "baseline_smoke": 0, "lane": "minimal-fabric-1.21", "new_probe_command_exit": 0, "reprovisioned_after_switch": false}, "native_after": 59, "native_before": 59, "survived": 59, "verdict": "PASS"}`.
- `minimal-neoforge-1.21`: `{"blocks": {"expected_wired": 18, "intentionally_removed": [], "target_count": 23, "target_retained": 23, "unexpected_missing": [], "wired": 18}, "complete_fixture_audit": {"control_peripherals": 20, "lecterns_verified": 10, "missing_or_changed_control_types": [], "pocket_displays": 10, "turtles_verified": 49, "verdict": "PASS"}, "failed": [], "lane": "minimal-neoforge-1.21", "migration": {"baseline_commit": "8d0955a38b32f6a47d0d7d2f7b54486b0ac5fdf8", "baseline_smoke": 0, "lane": "minimal-neoforge-1.21", "new_probe_command_exit": 0, "reprovisioned_after_switch": false}, "native_after": 59, "native_before": 59, "survived": 59, "verdict": "PASS"}`.

SmartHome Appliances is deliberately removed from both target Fabric packs. Its four old-world blocks becoming air is an expected discontinued-content removal, NOT preservation of that content. Every old position/modem is queried explicitly in `old-world-after/block-retention.json`; target-mod blocks and wired registrations are gated separately. The blanket old-manifest audit may fail on intentionally removed IDs and is recorded as such.

## Versions and SHA-256

Latest non-prerelease GitHub releases for Minecraft 1.21.1 were resolved at preparation time (`releases.json`). All eight downloaded asset digests matched GitHub. **Modrinth labels both 1.21.1 CC:Tweaked 1.122.0 builds as beta** (Fabric KN2WFTly, NeoForge 2jhB1Ii4); these are the exact user-requested version, not the 1.20.1 release-channel binaries. Modrinth SHA-1/SHA-512 and independent SHA-256 were checked, then installed server/client bytes were verified for exercised phases. Bundled SirEdvin libraries are 2.1.0.

| Tag | Upstream asset | SHA-256 |
|---|---|---|
| `v1.21.1-1.10.0` | `peripheralworks-fabric-1.21.1-1.10.0.jar` | `af6b59f74b8de42067f0d7307f065826e81f83f2b5a1fa8c0a39c649031209c8` |
| `v1.21.1-1.10.0` | `peripheralworks-forge-1.21.1-1.10.0.jar` | `d8baf9a532dae9aae9bc6eedbddd7a1bc55f04a9024264b2fbcee7fd4c0a5290` |
| `v1.21.1-1.5.1` | `turtlematic-fabric-1.21.1-1.5.1.jar` | `cd61dc56fa969ff4b561d561d0b0438d0e3d4e59cd5e933315538b7a6ce1134d` |
| `v1.21.1-1.5.1` | `turtlematic-forge-1.21.1-1.5.1.jar` | `61ba0054fb71c165ed440afb49daedf8fd2c269aece13e59d683ad6faac3250e` |
| `v1.21.1-0.4.0` | `cloudsolutions-fabric-1.21.1-0.4.0.jar` | `0facc5e105ae72deddc42cc7f0833b0c4eb2407b6c5f51377024ba89712f7f67` |
| `v1.21.1-0.4.0` | `cloudsolutions-forge-1.21.1-0.4.0.jar` | `df62be3c3ad52fc03ecbb69dc24a0572bc5ebb1c8d7ce145f0c2d969bf78f43c` |
| `v1.21.1-0.6.0` | `digitalitems-fabric-1.21.1-0.6.0.jar` | `90a967ca589b22a77d76eb0bfe378b1938046868423c5c5356269990e6d5a287` |
| `v1.21.1-0.6.0` | `digitalitems-forge-1.21.1-0.6.0.jar` | `e87f203132eb91856d86930e1d308be9127f28e0372bbe9ceda4edf3fce9ef03` |
| `1.122.0` | `cc-tweaked-1.21.1-fabric-1.122.0.jar` | `76c3ae07d20e75f155c94f200549f495b690bac8341d164203f1567611fa4388` |
| `1.122.0` | `cc-tweaked-1.21.1-forge-1.122.0.jar` | `d3b1153054d136dac1319c6d3c085865b7d174e40686aa1dc1f077d5485b8df0` |

The NeoForge assets retain upstream `-forge-` filenames. `artifact-inventory.json` includes every pack and the required Fabric API dependency digest. The only new dependency bump beyond PR #6 is **Fabric API 0.116.18+1.21.1** (5SwzqWUu): CC:Tweaked declares `fabric-api >=0.116.18` in its verified `fabric.mod.json` (`cc-fabric-dependencies.json`).

## Commands and evidence paths

```sh
python3 -m unittest discover -s testing/tests -v  # 7 tests
python3 testing/reports/cct-1.122.0-mc-1.21/snbt_fields.py
./testing/bin/mc-test smoke <lane>
./testing/bin/mc-test client-smoke <lane>
python3 testing/reports/cct-1.122.0-mc-1.21/extend-lane.py <lane>
python3 testing/reports/cct-1.122.0-mc-1.21/old-world.py <minimal-lane>
python3 testing/reports/cct-1.122.0-mc-1.21/static-checks.py
python3 testing/reports/cct-1.122.0-mc-1.21/build-report.py
git diff --check
```

`run-lane.py` invokes the two smoke commands in order and records each real exit code; native phases record lifecycle exits separately. The pipeline wrapper continues after failures, so its own exit zero is NOT a lane pass. `regression-tests.log`, `refresh-verification.json`, `toolchain.json`, per-lane `matrix.json`, `*-commands.json`, and `verdict.json` retain results. All four packs have verified full index hash chains and deterministic double refreshes.

Raw paths relative to this report: `<lane>/{smoke,client-smoke}/command.log`, `client-smoke/client-logs/latest.log`, `{upgrade-before,upgrade-after}/lifecycle.log`, `upgrade-probes.json`, `all-stacks/results.json`, and `<minimal-lane>/old-world/{commands.log,result.json,before-switch,after-switch}` plus `old-world-{before,after}`. `diagnostics.json` provides line-numbered excerpts and preserves exact source paths. Full evidence archive includes logs, manifests, native Lua/JSON, and pre/post saved-world snapshots; no runtime caches, mod JARs or credential files.

## Nonacceptance trials and limitations

- Initial Fabric Creative smoke/client attempts failed before launch on the old Fabric API dependency; retained in `fabric-1.21-dependency-trial`. Required dependency bump was applied before final acceptance.
- Initial NeoForge Creative installation trial rejected a stale Makefile index hash after correcting the upstream filename in its Make target; retained as `neoforge-1.21-index-trial`. Refresh corrected the harness packaging issue; the final run then reproduced the genuine UPW Ars crash.
- Fabric Creative original count-two report booleans used a legacy string LeftUpgrade checker. Actual raw NBT contains the correct 1.21 compound `{item:...,id:...}` and Lua passes. The final reducer re-parses the unchanged raw NBT with exact top-level SNBT fields; original booleans/log output are retained for traceability, not treated as game failures. The compound-field parser includes regression assertions.
- Offline headless authentication/profile-key and audio/narrator diagnostics are not authenticated or visual gameplay coverage. No exhaustive methods/recipes/network-service tests, production-world migration, nested-hub item behavior, or GTCEu integrations were exercised.
- No versions were downgraded and no mod repositories were changed to turn failures green.

## Durable evidence

The full evidence archive is intentionally included with this PR as `testing/reports/cct-1.122.0-mc-1.21-evidence.tar.gz`; `evidence-archive.json` records its SHA-256 and verified member count. It contains only disposable test-world/report evidence, not mod JARs or runtime caches. It is also submitted to this task as an attachment.

The additional `audit-old-fixtures.py` observations are under each minimal lane’s `old-world-fixture-audit/`: exact pocket-display/lectern IDs, turtle upgrades, all original block positions/modems and a fresh wired-control Lua snapshot, compared against the pre-switch saved-world control report. No fixture is replaced.

Preparation used `make cctweaked`, `make all`, and (for both Fabric packs) `packwiz modrinth add https://modrinth.com/mod/fabric-api/version/5SwzqWUu -y`, followed by refresh.
