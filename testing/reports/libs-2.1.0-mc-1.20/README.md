# C12 — libs 2.1.0 / Minecraft 1.20.1 validation

**Recommendation: NOT ready for public release. Keep this PR draft; do not merge.**

Baseline: `origin/main` at `d6c5efbec8ae1e5c6d61a9b78b2ef7f73253e84a`. Pack changes were tested at `796a20c`; this report commit only adds evidence/probe sources. All game processes ran sequentially. No mod source was changed, no version downgraded to pass, and nothing was published to CurseForge or Modrinth.

## Verdicts

| Lane | Server smoke | Physical client smoke | Single-item equip | Restart | Count-2 pocket equip | Old world | Overall |
|---|---|---|---|---|---|---|---|
| fabric-1.20 | PASS | PASS | PASS | PASS | FAIL | N/A | FAIL |
| forge-1.20 | PASS | PASS | PASS | PASS | FAIL | N/A | FAIL |
| minimal-fabric-1.20 | PASS | PASS | PASS | PASS | FAIL | PASS | FAIL |
| minimal-forge-1.20 | PASS | PASS | PASS | PASS | FAIL | PASS | FAIL |

Smoke PASS means startup, fixture auditing and real client world join passed, not an error-free log or exhaustive gameplay proof. Each server phase verified all five target JAR hashes; every physical-client phase verified all ten server/client JAR hashes. See `verdicts.json`, `coverage.json` and `artifact-inventory.json`.

## Release-blocking failure

On all four lanes, a native `pocket.equipBack()` against a stack of **two** valid items throws:

```text
java.lang.IllegalArgumentException: Error constructing UpgradeData for
peripheralworks:universal_scanner: Item 2 universal_scanner must be of size 1.
```

Also reproduced independently with `cloudsolutions:statsd_bridge`, `digitalitems:digitizer`, and the vanilla `computercraft:wireless_modem_normal` control. The item stack remains count 2 and the empty pocket has no peripheral. The vanilla control implicates the shared CC:Tweaked equip/UpgradeData path; attribution to a particular library is not established. The separate single-item round-trips succeed. Turtlematic has no pocket fixtures in this test.

Exact evidence per lane: `<lane>/upgrade-after/stack-equip/results.json` plus `lifecycle.log`. Diagnosis follow-up: Kanban `t_5c2566be` (Albina), after the 1.21 matrix.

## Upgrade and old-world coverage

- **fabric-1.20:** {'turtle': 51, 'pocket': 12} single-item hosts; native unequip/equip + peripheral enumeration/wrap: PASS; same-host post-stop/start observation: PASS.
- **forge-1.20:** {'turtle': 51, 'pocket': 12} single-item hosts; native unequip/equip + peripheral enumeration/wrap: PASS; same-host post-stop/start observation: PASS.
- **minimal-fabric-1.20:** {'turtle': 49, 'pocket': 10} single-item hosts; native unequip/equip + peripheral enumeration/wrap: PASS; same-host post-stop/start observation: PASS.
  - Old-world before: PASS; after: PASS; 59/59 retained working upgrades. Failed IDs/reasons: []. No fixtures were reprovisioned after the version switch. Evidence: `minimal-fabric-1.20/old-world-before`, `minimal-fabric-1.20/old-world-after`, `minimal-fabric-1.20/old-world/{before-switch,after-switch}` (artifact inventories and saved-world snapshots).
- **minimal-forge-1.20:** {'turtle': 49, 'pocket': 10} single-item hosts; native unequip/equip + peripheral enumeration/wrap: PASS; same-host post-stop/start observation: PASS.
  - Old-world before: PASS; after: PASS; 59/59 retained working upgrades. Failed IDs/reasons: []. No fixtures were reprovisioned after the version switch. Evidence: `minimal-forge-1.20/old-world-before`, `minimal-forge-1.20/old-world-after`, `minimal-forge-1.20/old-world/{before-switch,after-switch}` (artifact inventories and saved-world snapshots).

Old-world packs are the exact tracked minimal packs archived from the baseline commit. The baseline server was provisioned with previous releases, native fixture programs were exercised, and the cleanly stopped **same server data** was started against new source. The physical client used for pocket ticking is the new client in both old/new server phases; baseline proof is therefore server-data migration coverage, not an old-client compatibility test.

Previous versions (from baseline pack metadata):

- FabricMinimal-1.20: `peripheralworks-fabric-1.20.1-1.9.2.jar`, `turtlematic-fabric-1.20.1-1.4.10.jar`, `cloudsolutions-fabric-1.20.1-0.3.4.jar`, `digitalitems-fabric-1.20.1-0.5.8.jar`, `cc-tweaked-1.20.1-fabric-1.120.0.jar`
- ForgeMinimal-1.20: `peripheralworks-forge-1.20.1-1.9.2.jar`, `turtlematic-forge-1.20.1-1.4.10.jar`, `cloudsolutions-forge-1.20.1-0.3.4.jar`, `digitalitems-forge-1.20.1-0.5.8.jar`, `cc-tweaked-1.20.1-forge-1.120.0.jar`

## Commands and runtime

```sh
python3 -m unittest discover -s testing/tests -v  # 7/7 PASS
for lane in fabric-1.20 forge-1.20 minimal-fabric-1.20 minimal-forge-1.20; do
  ./testing/bin/mc-test smoke "$lane"         # all exit 0
  ./testing/bin/mc-test client-smoke "$lane"  # all exit 0
done
# Additional native probes (sequential orchestration, see scripts):
python3 <report>/extend-lane.py <lane>
python3 <report>/old-world.py <minimal-lane>
```

The actual orchestration also snapshots every phase; `run-lane.py`, `extend-lane.py`, `probe-upgrades.py`, `probe-stack-equip.py` and `old-world.py` are included. Do not blindly rerun stateful recovery scripts. `prepare.py` is retained in the full evidence attachment, not needed to reproduce the runtime probes.

Minecraft 1.20.1; Fabric Loader 0.17.2 or Forge 47.4.10; Java 17 container line (Forge log identifies Eclipse Adoptium 17.0.15). Packwiz executable digest is recorded in `toolchain.json`; this Packwiz binary exposes no version flag. Docker Compose version and container image IDs are also recorded there. Existing pack versions are unchanged. Packwiz refresh was run twice per updated pack and required deterministic manifest/index output; regression tests passed again after resumption.

## Tested assets (SHA-256)

| Asset | SHA-256 |
|---|---|
| `peripheralworks-fabric-1.20.1-1.10.0.jar` | `1da8c9a8e22a76f19e77c881b7438d28a7f98900c2ef4f7bbc56c02d1752bafa` |
| `peripheralworks-forge-1.20.1-1.10.0.jar` | `fd773e10861f4b1d06206f204c2b001fad1c26ba2a04edcf3d48226eacf5b583` |
| `turtlematic-fabric-1.20.1-1.5.0.jar` | `190f63f552d9e072af542524932aa0008586fcbe0f6c16a648db19dc9c481f9d` |
| `turtlematic-forge-1.20.1-1.5.0.jar` | `c5478f872b23a48c88111d022ccb613378661e50f64e2ec29551bdc28dd57d5c` |
| `cloudsolutions-fabric-1.20.1-0.4.0.jar` | `34862e08301d14fb2e42dc992b9b3b709e6a4a1f4895b068cdc9f329830bf1fd` |
| `cloudsolutions-forge-1.20.1-0.4.0.jar` | `944bd6f76429a564f8204af4c6eab46e60085565c88a7cd2e8c2aa555405ed46` |
| `digitalitems-fabric-1.20.1-0.6.0.jar` | `5d90d9a0d83ad5c1483e7d4a5c26bd9a9cc5e3b59422a899f9727d0d6a35076f` |
| `digitalitems-forge-1.20.1-0.6.0.jar` | `b9573d3dac4a0c07629ec3ca7b284885ab45568255a9314697a4ce5e243d09e0` |
| `cc-tweaked-1.20.1-fabric-1.121.0.jar` | `74ea3efd7aa5a2f5b0b53832dc5cb480a195d2979d95b150b7b60c0d299ad3c1` |
| `cc-tweaked-1.20.1-forge-1.121.0.jar` | `a95ba58640db0198c86f0be99154af92fda17a78975c88aa45ffc430159a6fe9` |

The eight SirEdvin GitHub asset digests were compared with the parent handoffs and downloaded bytes, and checked against live GitHub release metadata again on resumption. CC:Tweaked 1.121.0 comes from exact Modrinth version IDs (Fabric `LFj8qZ7a`, Forge `Qm9iIIEY`). Bundled SirEdvin libraries are 2.1.0. No unrelated dependency/loader bumps were required.

## Log diagnostics and limits

- Forge Creative emits malformed JSON errors for four existing Create cutting recipes under `create:cutting/compat/immersiveengineering/wire_{aluminum,copper,lead,steel}`. These do not prevent startup/fixtures; no causal link to this update or baseline regression is established.
- Forge logs report missing `minVersion` in several mixin configs. Creative optional mixin class lookups also warn about absent integrations.
- Headless clients log offline authentication/profile-key failures, absent audio/narrator support, and an out-of-range simulation-distance option. These are retained, not claimed fixed. No packet-handler crash, network-protocol disconnect, or critical resource reload failure was found in the final smoke logs.
- The initial Forge observation missed four Lua reports because shutdown/turn-on commands are asynchronous. That trial is preserved under `forge-1.20/upgrade-after-async-trial`; the final observation uses a shutdown tick barrier against the same persisted world, without rebuilding fixtures.
- The initial old-world reset/rename hit root-owned HeadlessMC directories. Failed preparation logs are retained; ownership recovery is limited to disposable worktree directories. These preparation failures are not mod failures.
- Early Fabric exploratory/pocket-race/dirty-inventory trials are diagnostic only. Final acceptance uses `upgrade-before`, `upgrade-after`, `old-world-before`, and `old-world-after` exclusively.
- Peripheral exposure/method enumeration/wrap and equip persistence were exercised, not every peripheral method, HTTP endpoint, recipe, visual rendering detail, player-authentication flow, nested hub upgrade or real production-world migration. The old-world fixtures are disposable, command-provisioned minimal test worlds.

## Evidence map

Raw logs remain under `testing/reports/libs-2.1.0-mc-1.20/` and are delivered as a task attachment with a SHA-256 manifest. Only compact verdicts, inventories and portable runtime probes are committed. Runtime/JAR caches, credentials, and live container environment files are excluded. Saved-world snapshots in the attachment contain only disposable offline test worlds. Per-lane `smoke/command.log`, `client-smoke/command.log`, `server-logs/latest.log`, `client-logs/latest.log`, upgrade `lifecycle.log`, `upgrade-probes.json`, and old-world artifact inventories are the primary evidence.
