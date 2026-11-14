# Libraries 2.1.0 / Minecraft 1.21.1 integration verdict

Baseline: `5514734c1effd5728d526e31956c34fb3122d2d4`. Java 21; CC:Tweaked **1.121.0**; UPW **1.10.0**, Turtlematic **1.5.1**, CloudSolutions **0.4.0**, DigitalItems **0.6.0**. GitHub release jars only. No mod source, public platform release, or unrelated pack was changed.

## Verdicts

| Lane | Overall | Server | Physical client | Count-1 equip | Restart | Count-2 pockets | Old world |
|---|---|---|---|---|---|---|---|
| fabric-1.21 | FAIL | PASS | FAIL | PASS | PASS | FAIL | N/A |
| neoforge-1.21 | FAIL | FAIL | FAIL | NOT RUN | NOT RUN | NOT RUN | N/A |
| minimal-fabric-1.21 | FAIL | PASS | PASS | PASS | PASS | FAIL | PASS |
| minimal-neoforge-1.21 | FAIL | PASS | PASS | PASS | PASS | FAIL | PASS |

## Findings and exact scope

- Count-2 `pocket.equipBack()` is a separate regression probe, not inferred from the 1.20 result. Four inputs: UPW universal scanner, CloudSolutions statsd bridge, DigitalItems digitizer, and vanilla CC wireless modem. See each `upgrade-after/stack-equip/results.json`. A vanilla control implicates the shared CC equip path, but final root-cause attribution is not claimed.
- Fabric creative can join while REI creative-tab collection fails. The first initializer exception points through CloudSolutions creative-tab enumeration, Tweakium `ComputerPlatformRegistries`, DigitalItems platform delegation, and Broccolium `FabricPlatformToolkit.lookup` NPE. Later NoClassDefFoundError messages are consequences. A successful client command is not treated as a clean pass.
- NeoForge creative fails during server startup: UPW `apprentice_magic_tome` rejects its default Ars Nouveau apprentice spell book while Tweakium `CreativeTabUtil.addPocket` calls CC `UpgradeData.ofDefault`. CC rebuilds creative tabs in its server-start hook. A preceding Done marker does not mean stable startup. Client and native upgrades cannot be verified when this server cannot remain up; no Ars removal or version downgrade was attempted.
- See `diagnostics.json` for line-numbered join, failure and shutdown excerpts. Full raw logs and per-host Lua/JSON are in the evidence archive; per-phase paths below are relative to this directory.

## Upgrade and migration inventory

- `fabric-1.21`: new-world/native count-1 before `PASS`, after restart `PASS`; persistence `{"after": 59, "before": 59, "failures": [], "survived": 59, "verdict": "PASS"}`.
- `neoforge-1.21`: new-world/native count-1 before `NOT RUN`, after restart `NOT RUN`; persistence `{"verdict": "NOT RUN"}`.
- `minimal-fabric-1.21`: new-world/native count-1 before `PASS`, after restart `PASS`; persistence `{"after": 59, "before": 59, "failures": [], "survived": 59, "verdict": "PASS"}`.
  - Previous-release same-world migration: `{"after": 59, "before": 59, "failures": [], "survived": 59, "verdict": "PASS"}`; baseline native setup `PASS`, post-switch observation `PASS`. No reprovisioning after source switch. Before/after worlds are retained locally, not committed as pack source.
  - Standalone old-world blocks: 23/27 retained; 18 wired peripheral registrations. Missing blocks: `[{"block": "smarthome_appliances:lamp", "now_air": true}, {"block": "smarthome_appliances:led_panel", "now_air": true}, {"block": "smarthome_appliances:smooth_led_panel", "now_air": true}, {"block": "smarthome_appliances:switch", "now_air": true}]`. Explicit post-switch queries are in `old-world-after/block-retention.json`. The blanket legacy audit can fail on deliberately removed SmartHome IDs; this is reported separately from four-mod upgrade survival.
- `minimal-neoforge-1.21`: new-world/native count-1 before `PASS`, after restart `PASS`; persistence `{"after": 59, "before": 59, "failures": [], "survived": 59, "verdict": "PASS"}`.
  - Previous-release same-world migration: `{"after": 59, "before": 59, "failures": [], "survived": 59, "verdict": "PASS"}`; baseline native setup `PASS`, post-switch observation `PASS`. No reprovisioning after source switch. Before/after worlds are retained locally, not committed as pack source.
  - Standalone old-world blocks: 23/23 retained; 18 wired peripheral registrations. Missing blocks: `[]`. Explicit post-switch queries are in `old-world-after/block-retention.json`. The blanket legacy audit can fail on deliberately removed SmartHome IDs; this is reported separately from four-mod upgrade survival.

## Reproduction and evidence

```sh
python3 -m unittest discover -s testing/tests -v
python3 testing/reports/libs-2.1.0-mc-1.21/run-lane.py <lane>
python3 testing/reports/libs-2.1.0-mc-1.21/extend-lane.py <lane>
python3 testing/reports/libs-2.1.0-mc-1.21/old-world.py <minimal-lane>
python3 testing/reports/libs-2.1.0-mc-1.21/summarize.py
```

`run-lane.py` executes `./testing/bin/mc-test smoke <lane>` then `client-smoke <lane>`, preserves command exit codes, fresh logs after shutdown, generated manifests, Lua audit and actual installed server/client artifact digests. `extend-lane.py` runs native Lua on each discovered host, using a real disposable player inventory for pockets, serializes pocket equip, saves, stops, restarts without provisioning, and re-observes the same computer IDs. The count-2 probe includes a vanilla control. All lanes ran sequentially.

`old-world.py` extracts the immutable baseline minimal packs, provisions their previous-release worlds, runs native equip probes, restores new pack source in finally, then starts the SAME server data and observes without reprovisioning. NeoForge baseline uses 21.1.244 and target uses 21.1.265, as required by target mod metadata. SmartHome Appliances is deliberately removed from both target Fabric packs; its four standalone blocks are not part of the four-mod upgrade-survival count.

Python regression tests: **7/7 PASS** (`python-tests.log`). Final Packwiz double-refresh evidence is `refresh-verification.json`; `git diff --check` must pass before commit. Unrelated dependencies are unchanged. An unintended Packwiz Fabric API update was reverted before acceptance; its exploratory result remains separately labelled `exploratory-fabric-api-0.116.18`, not counted as a final lane.

Per lane: `<lane>/smoke/command.log`, `<lane>/client-smoke/command.log`, `<lane>/client-smoke/client-logs/latest.log`, `<lane>/upgrade-{before,after}/lifecycle.log`, `upgrade-probes.json`, and `<minimal-lane>/old-world/{commands.log,result.json}` plus `<minimal-lane>/old-world-{before,after}/`. `verdicts.json`, `verdict-table.json`, `coverage.json`, `diagnostics.json`, and `artifact-inventory.json` provide bounded summaries. Failed command logs are preserved even when no fixture manifest can be generated.

## Artifact SHA-256

| Asset | SHA-256 |
|---|---|
| `cc-tweaked-1.21.1-fabric-1.121.0.jar` | `aefaa822cf4c7b035c4504ac36bdd5f52a81faf91ab3470ddbc571300d2eb077` |
| `cc-tweaked-1.21.1-forge-1.121.0.jar` | `bf8dd119701560ea60085cf8c1076d32ffc99a1be5f8b99f6f3b174a88a208f8` |
| `cloudsolutions-fabric-1.21.1-0.4.0.jar` | `0facc5e105ae72deddc42cc7f0833b0c4eb2407b6c5f51377024ba89712f7f67` |
| `cloudsolutions-forge-1.21.1-0.4.0.jar` | `df62be3c3ad52fc03ecbb69dc24a0572bc5ebb1c8d7ce145f0c2d969bf78f43c` |
| `digitalitems-fabric-1.21.1-0.6.0.jar` | `90a967ca589b22a77d76eb0bfe378b1938046868423c5c5356269990e6d5a287` |
| `digitalitems-forge-1.21.1-0.6.0.jar` | `e87f203132eb91856d86930e1d308be9127f28e0372bbe9ceda4edf3fce9ef03` |
| `peripheralworks-fabric-1.21.1-1.10.0.jar` | `af6b59f74b8de42067f0d7307f065826e81f83f2b5a1fa8c0a39c649031209c8` |
| `peripheralworks-forge-1.21.1-1.10.0.jar` | `d8baf9a532dae9aae9bc6eedbddd7a1bc55f04a9024264b2fbcee7fd4c0a5290` |
| `turtlematic-fabric-1.21.1-1.5.1.jar` | `cd61dc56fa969ff4b561d561d0b0438d0e3d4e59cd5e933315538b7a6ce1134d` |
| `turtlematic-forge-1.21.1-1.5.1.jar` | `61ba0054fb71c165ed440afb49daedf8fd2c269aece13e59d683ad6faac3250e` |

All eight GitHub asset digests were independently downloaded and matched before pack edits; runtime target JARs are checked against Packwiz metadata. `assets.json` preserves exact release URLs and embedded loader metadata. Turtlematic 1.5.1 follows the coordinator override, not the original 1.5.0 handoff.

## Limits / recommendation

This is API equip/peripheral-exposure, restart/migration and headless client-join smoke coverage, not visual inspection or exhaustive calls to every peripheral method. GTCEu is not installed, so no GTCEu-specific methods were tested. Failures prevent a blanket compatibility claim. **NOT ready for public release. Keep the PR draft and do not merge under this card’s all-pass rule.**
