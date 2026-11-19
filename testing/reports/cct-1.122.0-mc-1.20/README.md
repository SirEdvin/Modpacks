# C14 — CC:Tweaked 1.122.0 / Minecraft 1.20.1 retest

**Recommendation: READY for public release within the tested scope.**

Baseline: `origin/main` at `5514734c1effd5728d526e31956c34fb3122d2d4`. Pack source under test: `2ad96aca30e50053da6ca6706fc4438ea20d3300`. Four lanes executed strictly sequentially. No mod code changes, no downgrades, no unrelated dependency bumps, and no CurseForge/Modrinth publication. The four SirEdvin releases were already on the baseline; this update changes CC:Tweaked 1.121.0 → 1.122.0.

## Verdicts

| Lane | Server | Client | Single equip | Restart | All count-2 equip | Count-2 restart | Pocket regression/control | Old world | Overall |
|---|---|---|---|---|---|---|---|---|---|
| fabric-1.20 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | N/A | PASS |
| forge-1.20 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | N/A | PASS |
| minimal-fabric-1.20 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| minimal-forge-1.20 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |

Smoke requires startup, complete fixture audit, fresh in-world Lua output, saved-world shutdown, and installed target-JAR hashes. Client requires fresh advancement synchronization/server join markers, 30 seconds stability, and no packet-handler/crash/critical initializer errors in the final runtime client log. It does not mean every ERROR log is absent.

## Upgrade coverage

The original NBT fixture checks are supplemented with real Lua running in every authored turtle and in pockets ticked by a real offline headless player. Single-item checks unequip/re-equip, enumerate types/methods and wrap peripherals. Separate hosts equip from count-two input, with a vanilla CC wireless modem control for both turtle and pocket. Those exact count-two hosts are observed after stop/start without replacement. Count-two acceptance applies only to items whose actual native `getItemDetail(...,true).maxCount` is greater than one; nonstackable terminals, tools and automata cores are covered by the complete single-item equip/restart checks and explicitly listed in `all-stacks/nonstackable.json`. Input count two and remaining count one are verified.

- **fabric-1.20:** single-item `{'turtle': 51, 'pocket': 12}`; count-two (including one vanilla modem control per host kind) `{'turtle': 19, 'pocket': 11}`. Single-item PASS; count-two/restart PASS. Exact failures: `[]`. See `fabric-1.20/{upgrade-before,upgrade-after}/{upgrade-probes.json,all-stacks/results.json}`.
- **forge-1.20:** single-item `{'turtle': 51, 'pocket': 12}`; count-two (including one vanilla modem control per host kind) `{'turtle': 19, 'pocket': 11}`. Single-item PASS; count-two/restart PASS. Exact failures: `[]`. See `forge-1.20/{upgrade-before,upgrade-after}/{upgrade-probes.json,all-stacks/results.json}`.
- **minimal-fabric-1.20:** single-item `{'turtle': 49, 'pocket': 10}`; count-two (including one vanilla modem control per host kind) `{'turtle': 19, 'pocket': 11}`. Single-item PASS; count-two/restart PASS. Exact failures: `[]`. See `minimal-fabric-1.20/{upgrade-before,upgrade-after}/{upgrade-probes.json,all-stacks/results.json}`.
  - Old world: PASS, 59 same single-item hosts audited. Failed hosts: `[]`. Baseline/source-switch records and pre/post saved-world snapshots: `minimal-fabric-1.20/old-world/`. No reprovision after switching.
- **minimal-forge-1.20:** single-item `{'turtle': 49, 'pocket': 10}`; count-two (including one vanilla modem control per host kind) `{'turtle': 19, 'pocket': 11}`. Single-item PASS; count-two/restart PASS. Exact failures: `[]`. See `minimal-forge-1.20/{upgrade-before,upgrade-after}/{upgrade-probes.json,all-stacks/results.json}`.
  - Old world: PASS, 59 same single-item hosts audited. Failed hosts: `[]`. Baseline/source-switch records and pre/post saved-world snapshots: `minimal-forge-1.20/old-world/`. No reprovision after switching.

**Fabric acceptance paths:** final native single-item evidence is `fabric-1.20/single-before` and `single-after` (fresh computer IDs 40000/41000). Count-two acceptance is `fabric-1.20/upgrade-before` and `upgrade-after/all-stacks`. The native subsection of that repeated upgrade trial swapped the Crafka/KV pocket upgrades while reusing earlier computer IDs; it is retained as a diagnostic, not selected as native acceptance. A fresh-ID native pair passed before and after a real server restart; the precise reuse-race cause was not investigated in mod code.


## Previous regression and applicability

See per-lane `upgrade-after/stack-equip/results.json` for the original universal scanner / StatsD / digitizer / vanilla modem count-two regression, and `all-stacks/results.json` for every active authored upgrade. The pocket regression column above states whether all four now equip and expose their peripherals. Missing/non-passing results are never interpreted as fixed.

Fabric creative-tab initializer/critical resource reload failures from C13 are explicitly checked in the actual 1.20.1 logs; consult `log-diagnostics.json`. The NeoForge UPW Ars magic-tome crash is **not applicable/not tested**: these lanes run Fabric/Forge 1.20.1, not NeoForge 1.21.1. Its absence here is not evidence of a 1.21 fix.

## Old-world semantics

Minimal baseline packs were archived from the exact baseline commit before edits. Each baseline world was provisioned, single-item native programs were exercised, and the cleanly stopped same data was started with the new pack. The actual before/after server and client target JAR hashes are in each probe phase `artifacts.json`. Here origin/main already contained the new four SirEdvin releases, so this is a CC:Tweaked 1.121.0 → 1.122.0 existing-world migration, not a four-mod version migration. Count-two hosts are only fresh-world coverage; old-world survival uses the original single-item hosts, authored blocks, wired registrations and pocket displays.

## Commands

```sh
python3 -m unittest discover -s testing/tests -v
python3 testing/reports/cct-1.122.0-mc-1.20/prepare.py  # one-time preparation; stateful
for lane in fabric-1.20 forge-1.20 minimal-fabric-1.20 minimal-forge-1.20; do
  ./testing/bin/mc-test smoke "$lane"
  ./testing/bin/mc-test client-smoke "$lane"
  python3 testing/reports/cct-1.122.0-mc-1.20/extend-lane.py "$lane"
done
python3 testing/reports/cct-1.122.0-mc-1.20/old-world.py minimal-fabric-1.20
python3 testing/reports/cct-1.122.0-mc-1.20/old-world.py minimal-forge-1.20
```

Actual invocation order completes old-world work before moving to the next lane. `run-lane.py` snapshots both smoke commands and preserves their exits/timings. Extended lifecycle results and Lua records—not wrapper exit alone—determine verdicts. Regression test output is in `regression-tests.log`. Docker Compose v5.7.0 provides the required modern `docker compose` interface. Minecraft 1.20.1, Java17 image, Fabric 0.17.2 / Forge 47.4.10; exact image IDs and Packwiz digest in `toolchain.json`.

## Exact release assets (SHA-256)

| Release tag | Asset | SHA-256 |
|---|---|---|
| `v1.20.1-1.10.0` | `peripheralworks-fabric-1.20.1-1.10.0.jar` | `1da8c9a8e22a76f19e77c881b7438d28a7f98900c2ef4f7bbc56c02d1752bafa` |
| `v1.20.1-1.10.0` | `peripheralworks-forge-1.20.1-1.10.0.jar` | `fd773e10861f4b1d06206f204c2b001fad1c26ba2a04edcf3d48226eacf5b583` |
| `v1.20.1-1.5.0` | `turtlematic-fabric-1.20.1-1.5.0.jar` | `190f63f552d9e072af542524932aa0008586fcbe0f6c16a648db19dc9c481f9d` |
| `v1.20.1-1.5.0` | `turtlematic-forge-1.20.1-1.5.0.jar` | `c5478f872b23a48c88111d022ccb613378661e50f64e2ec29551bdc28dd57d5c` |
| `v1.20.1-0.4.0` | `cloudsolutions-fabric-1.20.1-0.4.0.jar` | `34862e08301d14fb2e42dc992b9b3b709e6a4a1f4895b068cdc9f329830bf1fd` |
| `v1.20.1-0.4.0` | `cloudsolutions-forge-1.20.1-0.4.0.jar` | `944bd6f76429a564f8204af4c6eab46e60085565c88a7cd2e8c2aa555405ed46` |
| `v1.20.1-0.6.0` | `digitalitems-fabric-1.20.1-0.6.0.jar` | `5d90d9a0d83ad5c1483e7d4a5c26bd9a9cc5e3b59422a899f9727d0d6a35076f` |
| `v1.20.1-0.6.0` | `digitalitems-forge-1.20.1-0.6.0.jar` | `b9573d3dac4a0c07629ec3ca7b284885ab45568255a9314697a4ce5e243d09e0` |
| `1.122.0` | `cc-tweaked-1.20.1-fabric-1.122.0.jar` | `534076610b154e512d91eaa173aa50d207d9b1f9eca540820501e21b10f7a3cc` |
| `1.122.0` | `cc-tweaked-1.20.1-forge-1.122.0.jar` | `4a559841ed40c832979c1799e98a3466a62192d7ac6321faac6c27c09907168f` |

Latest stable non-prerelease GitHub releases were resolved for this Minecraft line at preparation time (`releases.json`). GitHub-provided asset digests when present and all Modrinth SHA-1/SHA-512 hashes were checked against downloaded bytes. Installed hashes are checked separately. Bundled SirEdvin libraries remain 2.1.0. Packwiz refresh ran twice per pack with deterministic index/pack hashes.

## Infrastructure retry and limitations

- Initial Fabric physical-client attempt timed out while downloading Mojang assets after HTTP/2 EOF failures; its complete evidence remains in `fabric-1.20/client-smoke-asset-timeout`. Recovered 220 partial assets from a read-only previous disposable cache, verifying all 3577 unique asset SHA-1s against Mojang’s index. Final acceptance uses a new complete physical-client invocation, never the failed download trial.
- An exploratory Fabric count-two trial forced illegal stacks of nonstackable items; bare AE2 terminals also lack the canonical `peripheralworks_display` item tag. Native single-item AE2 roundtrips retain that tag and pass. That test-input failure is preserved under `fabric-1.20/invalid-stack-trial`; final count-two acceptance only uses genuinely stackable items, with every nonstackable still covered by single-item native equip/restart. No mod code or version was changed.
- `log-diagnostics.json` preserves ERROR contexts for review. Offline profile-key/authentication and absent headless sound/narrator errors are infrastructure limitations, not a claim of authenticated or visual gameplay coverage.
- Equip, peripheral exposure/enumeration/wrap and persistence are tested, not every peripheral method, network service, recipe, nested hub item, real production world or visual rendering. Optional upgrade integrations are tested only where their dependency is installed.

## Evidence retention

Compact report/verdicts/asset hashes/probe sources are committed here. Raw logs, per-host Lua/command records, generated manifests, and disposable pre/post saved worlds are in the separately attached evidence archive. `evidence-archive.json` identifies its bytes. Runtime caches, JARs, account files and RCON environment files are excluded.
