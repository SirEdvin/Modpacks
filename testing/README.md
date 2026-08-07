# Manual Minecraft Mod Testing Playground

This directory runs one disposable, low-memory dedicated server at a time for the eight Packwiz test packs in this repository. It is intentionally a manual tool: there is no CI workflow and no always-on server fleet.

## Lanes

| Lane | Pack | Loader | Java in container | Port | Heap limit |
|---|---|---|---:|---:|---:|
| `fabric-1.20` | `FabricCreative` | Fabric 0.17.2 / MC 1.20.1 | 17 | 25570 | 1536M |
| `forge-1.20` | `ForgeCreative` | Forge 47.4.10 / MC 1.20.1 | 17 | 25571 | 2G |
| `fabric-1.21` | `FabricCreative-1.21` | Fabric 0.19.3 / MC 1.21.1 | 21 | 25572 | 1536M |
| `neoforge-1.21` | `NeoForgeCreative-1.21` | NeoForge 21.1.244 / MC 1.21.1 | 21 | 25573 | 2G |
| `minimal-fabric-1.20` | `FabricMinimal-1.20` | Fabric 0.17.2 / MC 1.20.1 | 17 | 25574 | 1536M |
| `minimal-forge-1.20` | `ForgeMinimal-1.20` | Forge 47.4.10 / MC 1.20.1 | 17 | 25575 | 2G |
| `minimal-fabric-1.21` | `FabricMinimal-1.21` | Fabric 0.19.3 / MC 1.21.1 | 21 | 25576 | 1536M |
| `minimal-neoforge-1.21` | `NeoForgeMinimal-1.21` | NeoForge 21.1.244 / MC 1.21.1 | 21 | 25577 | 2G |

The `itzg/minecraft-server` image selects the Java runtime required by the Minecraft version. Packwiz installs server-side files directly from the checked-out pack through an internal HTTP container.

## Requirements

- Docker with Compose v2
- Internet access on the first start for the server, loader, libraries, and mods
- A client installed from the matching Packwiz pack when joining manually

No host Java installation is required for the server.

## Quick start

From the repository root:

```bash
./testing/bin/mc-test lanes
./testing/bin/mc-test start fabric-1.20
./testing/bin/mc-test provision fabric-1.20
```

Join `localhost:25570` with the matching `FabricCreative` client. The server uses Mojang authentication (`online-mode=true`).

When finished:

```bash
./testing/bin/mc-test stop fabric-1.20
```

Server data remains under `testing/runtime/fabric-1.20/data`, so the next start reuses loader files, downloaded mods, and the playground. Generated state is ignored by Git.

## Commands

```text
mc-test lanes
mc-test start <lane>
mc-test provision <lane>
mc-test blocks <lane>
mc-test audit <lane>
mc-test status [lane]
mc-test logs <lane>
mc-test console <lane>
mc-test command <lane> <minecraft command...>
mc-test stop <lane>
mc-test reset <lane>
mc-test smoke <lane>
mc-test smoke-all
mc-test client-smoke <lane>
mc-test client-smoke-all
```

Examples:

```bash
# Follow startup or mod logs
./testing/bin/mc-test logs neoforge-1.21

# Run a command without entering the console
./testing/bin/mc-test command forge-1.20 'time set midnight'

# Open the real interactive server console; detach with Ctrl-P, Ctrl-Q
./testing/bin/mc-test console fabric-1.21

# Start, wait, provision, save diagnostics, and stop
./testing/bin/mc-test smoke neoforge-1.21

# Run that smoke cycle sequentially for all eight lanes
./testing/bin/mc-test smoke-all

# Install and launch a matching headless client, then join the filled playground
./testing/bin/mc-test client-smoke minimal-fabric-1.20

# Run the client world-join smoke sequentially across all eight lanes
./testing/bin/mc-test client-smoke-all
```

Both matrix commands are deliberately sequential to keep RAM consumption low.

## Client-side smoke test

`client-smoke` performs the same deterministic playground setup before launching a matching physical client:

1. starts the selected server in temporary offline mode;
2. creates the empty vanilla superflat/void world and provisions all fixtures;
3. verifies authored blocks, wired peripherals, turtles, and pockets through RCON;
4. installs the Packwiz pack with `side=client` into an isolated HeadlessMC home;
5. installs the exact Fabric, Forge, or NeoForge loader declared by the lane;
6. launches Minecraft headlessly and quick-joins the filled playground;
7. requires both client advancement synchronization and a server-side join event;
8. captures client/server logs, stops the client, and shuts the stack down cleanly.

The test intentionally joins the server-created world instead of automating Minecraft's world-creation GUI. This keeps the client view and server fixture byte-for-byte aligned while still exercising physical-client initialization, resource/model loading, networking, registry synchronization, chunk rendering setup, and a real world join. HeadlessMC, Mojang assets, loader libraries, and Packwiz downloads are cached under `testing/runtime/shared-cache`; each lane retains isolated mods, configuration, options, and logs under `testing/runtime/<lane>/client`.

Reports are written to:

```text
testing/reports/<lane>/client.log
testing/reports/<lane>/client-server.log
```

## Void world

The server requests a vanilla superflat world with:

- no terrain layers;
- `minecraft:the_void` biome;
- no structures;
- view distance 4;
- simulation distance 4;
- peaceful difficulty and disabled mob spawning.

`provision` creates a 49×49 laboratory platform and force-loads only its compact chunk area. If a generated world predates these generator settings, use `reset`, then start and provision it again.

## Playground layout

The playground is rebuilt idempotently from `playground/provision.mcfunction`:

- **center:** CC:Tweaked advanced computer and control desk;
- **west:** vanilla inventory and redstone fixtures;
- **east/purple:** separated quartz benches for peripherals under test;
- **south/green:** advanced turtle movement and block-interaction track;
- **north/orange:** wired-network cable bench.

Use the creative inventory to place each mod peripheral on an east-side bench. Keeping devices separated makes attachment names and test results easier to understand. The fixture itself uses stable vanilla and CC:Tweaked registry IDs so it can be shared across all four loaders.

On the control computer, useful discovery snippets are:

```lua
peripheral.getNames()

for _, name in ipairs(peripheral.getNames()) do
  print(name, table.concat({peripheral.getType(name)}, ", "))
end

local name = peripheral.getNames()[1]
textutils.pagedTabulate(peripheral.getMethods(name))
```

For a device placed next to the control computer:

```lua
local device = peripheral.find("replace_with_peripheral_type")
print(textutils.serialize(device, { compact = false }))
```

## Authored-mod block fixture

Every `provision` run dynamically scans the installed server JARs for blockstate definitions from these SirEdvin-authored projects:

- Cloud Solutions
- Digital Items
- Unlimited Peripheral Works
- Turtlematic
- Smart Home Appliances, when present

Turtlematic currently contributes turtle upgrades/items but no standalone registered blocks. The generator does not maintain a fragile hard-coded registry list: `testing/bin/generate-authored-blocks.py` reads `assets/<namespace>/blockstates/*.json` from the exact installed JARs.

The generated fixture is east of the original laboratory. Each block has its own full wired modem on the west side, connected downward to a shared underfloor cable bus. Modems are created with both networking and peripheral sharing enabled. Ordinary blocks remain display fixtures; blocks that expose a CC:Tweaked peripheral are registered on the shared network.

Commands:

```bash
# Base playground + regenerate/place/verify all authored blocks
./testing/bin/mc-test provision forge-1.20

# Rebuild only the authored block fixture after changing a mod JAR
./testing/bin/mc-test blocks forge-1.20

# Recheck exact block IDs and wired registrations, then rerun Lua
./testing/bin/mc-test audit forge-1.20
```

Generated evidence is stored under the ignored lane runtime:

```text
testing/runtime/<lane>/generated/
├── authored-blocks.mcfunction   # exact placement commands
├── authored-blocks.json         # JAR inventory; block and upgrade coordinates
├── authored-block-audit.json   # block, turtle, pocket, and wired verification
└── attached-peripherals.tsv
```

Each upgrade is represented by a specialized host rather than being treated as an ordinary block or loose item:

- Turtle upgrade JSONs are discovered from `data/<namespace>/computercraft/turtle_upgrades/*.json` on Minecraft 1.20.1 and `data/<namespace>/computercraft/turtle_upgrade/*.json` on Minecraft 1.21.1.
- Every active turtle upgrade gets one advanced turtle with that registry ID on the left side and no right-side upgrade.
- Pocket upgrade JSONs are discovered from the equivalent `pocket_upgrades`/`pocket_upgrade` paths.
- Every active pocket upgrade gets one advanced pocket computer containing only that upgrade, rendered by a fixed item-display directly on its own lectern. Vanilla lecterns cannot store arbitrary pocket-computer items, so the lectern is the physical stand and the item-display is the persistent visible item.
- Optional upgrade definitions are included only when their declared dependency mod is installed.

The generated manifest identifies every upgrade ID, host type, coordinates, lectern coordinate where applicable, and item-display selector tag. Verification reads each turtle block entity and pocket item-display back from the live world. It fails if a turtle has a missing/wrong left upgrade, any right upgrade, a pocket loses its upgrade NBT/component, or a lectern/display is absent. Minecraft 1.20.1 pockets use legacy `tag.Upgrade`; Minecraft 1.21.1 pockets use the `computercraft:pocket_upgrade` item data component.

Each lane uses its port as a stable CC computer ID (`25570`–`25573`). The harness installs `testing/playground/audit.lua` as `audit.lua`, installs a startup script, and restarts that computer. The in-world report is:

```text
testing/runtime/<lane>/data/playground/computercraft/computer/<id>/authored-peripherals.json
```

It contains every peripheral name visible to the computer, its peripheral types, and method list. You can also inspect it interactively on the generated advanced computer:

```lua
shell.run("audit")
```

Verified fixture totals:

| Lane | Authored blocks | Wired peripherals | Single-upgrade turtles | Upgraded pockets on lecterns |
|---|---:|---:|---:|---:|
| `fabric-1.20` | 23 | 18 | 49 | 10 |
| `forge-1.20` | 23 | 18 | 49 | 10 |
| `fabric-1.21` | 27 | 18 | 49 | 10 |
| `neoforge-1.21` | 23 | 18 | 51 | 16 |
| `minimal-fabric-1.20` | 23 | 18 | 49 | 10 |
| `minimal-forge-1.20` | 23 | 18 | 49 | 10 |
| `minimal-fabric-1.21` | 27 | 18 | 49 | 10 |
| `minimal-neoforge-1.21` | 23 | 18 | 49 | 10 |

Fabric 1.21 has four additional Smart Home Appliances blocks. They are placed but do not expose CC peripherals. A block is counted as attached only when CC:Tweaked records a real `PeripheralType*` entry in the adjacent modem block entity; the cosmetic modem blockstate alone is not accepted as evidence.

## Updating a mod under test

Update the relevant Packwiz metadata first, then restart the lane:

```bash
cd ForgeCreative
make upw                 # example project-specific Make target
packwiz refresh
cd ..

./testing/bin/mc-test stop forge-1.20
./testing/bin/mc-test start forge-1.20
```

The Packwiz installer checks the pack on every container start. If loader or generated server state becomes suspicious, use the stronger reset:

```bash
./testing/bin/mc-test reset forge-1.20
./testing/bin/mc-test start forge-1.20
./testing/bin/mc-test provision forge-1.20
```

`reset` deletes only that lane. The shared download cache is retained.

## Memory tuning

Defaults are intentionally modest. A void world primarily saves chunk/world-generation memory; loaded mods still have a fixed baseline.

Change a lane's `MC_MEMORY` in `testing/lib/lanes.sh` if startup reports an out-of-memory failure. Avoid `AlwaysPreTouch`: it eagerly commits the full heap and works against low resident-memory goals.

Inspect live usage with:

```bash
container=$(docker compose \
  --project-name mc-test-fabric-1-20 \
  --project-directory testing \
  --env-file testing/runtime/fabric-1.20.env \
  -f testing/compose.yaml ps -q minecraft)
docker stats --no-stream "$container"
```

A `smoke` run writes the same Docker snapshot plus the full server log under `testing/reports/<lane>/`.

## Troubleshooting

### Startup takes a long time

The first start downloads Minecraft, the loader, libraries, and every server-side Packwiz file. The default readiness timeout is 15 minutes. Override it for a slow connection:

```bash
MC_TEST_TIMEOUT=1800 ./testing/bin/mc-test start neoforge-1.21
```

### A client-only mod crashes the server

Correct that mod's Packwiz metadata to `side = "client"`. Packwiz server mode intentionally excludes correctly classified client-only files.

### The world contains terrain

The world was probably generated before the void settings were active:

```bash
./testing/bin/mc-test reset <lane>
./testing/bin/mc-test start <lane>
./testing/bin/mc-test provision <lane>
```

### A provisioning command fails

Check the exact failing command manually with `mc-test command`. Registry names are shared by current CC:Tweaked versions, but a future major release may rename a block. Update `playground/provision.mcfunction` only after checking that exact game line.
