#!/usr/bin/env python3
"""Generate authored block, turtle-upgrade, and pocket-upgrade fixtures."""

from __future__ import annotations

import argparse
import json
import math
import re
import zipfile
from pathlib import Path
from typing import Any

AUTHORED_JAR_MARKERS = (
    "cloudsolutions",
    "digitalitems",
    "peripheralworks",
    "turtlematic",
    "smarthome_appliances",
)
BLOCKSTATE_RE = re.compile(r"assets/([^/]+)/blockstates/([^/]+)\.json$")
UPGRADE_RE = re.compile(
    r"data/([^/]+)/computercraft/(turtle_upgrades?|pocket_upgrades?)/([^/]+)\.json$"
)
MOD_ID_RE = re.compile(r"modId\s*=\s*[\"']([^\"']+)[\"']")


def authored_jars(mods_dir: Path) -> list[Path]:
    return [
        jar
        for jar in sorted(mods_dir.glob("*.jar"))
        if any(marker in jar.name.lower() for marker in AUTHORED_JAR_MARKERS)
    ]


def installed_mod_ids(mods_dir: Path) -> set[str]:
    result = {"minecraft", "computercraft"}
    for jar in sorted(mods_dir.glob("*.jar")):
        try:
            with zipfile.ZipFile(jar) as archive:
                if "fabric.mod.json" in archive.namelist():
                    result.add(json.loads(archive.read("fabric.mod.json"))["id"])
                for metadata in ("META-INF/mods.toml", "META-INF/neoforge.mods.toml"):
                    if metadata in archive.namelist():
                        result.update(MOD_ID_RE.findall(archive.read(metadata).decode(errors="replace")))
        except (OSError, zipfile.BadZipFile, KeyError, json.JSONDecodeError):
            continue
    return result


def condition_is_active(document: dict[str, Any], mod_ids: set[str]) -> bool:
    conditions: list[dict[str, Any]] = []
    for key in ("fabric:load_conditions", "forge:conditions", "neoforge:conditions"):
        value = document.get(key, [])
        if isinstance(value, list):
            conditions.extend(item for item in value if isinstance(item, dict))

    for condition in conditions:
        kind = str(condition.get("condition", condition.get("type", "")))
        if kind.endswith("all_mods_loaded"):
            required = condition.get("values", condition.get("mods", []))
            if not all(str(mod) in mod_ids for mod in required):
                return False
        elif kind.endswith("mod_loaded"):
            required = condition.get("modid", condition.get("mod", ""))
            if str(required) not in mod_ids:
                return False
    return True


def discover(mods_dir: Path) -> tuple[list[str], dict[str, list[str]], list[dict[str, str]], list[dict[str, str]]]:
    by_jar: dict[str, list[str]] = {}
    blocks: set[str] = set()
    turtle: dict[str, dict[str, str]] = {}
    pocket: dict[str, dict[str, str]] = {}
    mod_ids = installed_mod_ids(mods_dir)

    for jar in authored_jars(mods_dir):
        jar_blocks: set[str] = set()
        with zipfile.ZipFile(jar) as archive:
            for member in archive.namelist():
                block_match = BLOCKSTATE_RE.fullmatch(member)
                if block_match:
                    block_id = f"{block_match.group(1)}:{block_match.group(2)}"
                    jar_blocks.add(block_id)
                    blocks.add(block_id)
                    continue

                upgrade_match = UPGRADE_RE.fullmatch(member)
                if not upgrade_match:
                    continue
                try:
                    document = json.loads(archive.read(member))
                except json.JSONDecodeError:
                    continue
                if not condition_is_active(document, mod_ids):
                    continue
                namespace, kind, path = upgrade_match.groups()
                entry = {
                    "id": f"{namespace}:{path}",
                    "type": str(document.get("type", "")),
                    "item": str(document.get("item", "")),
                    "source_jar": jar.name,
                }
                target = turtle if kind.startswith("turtle") else pocket
                target[entry["id"]] = entry
        by_jar[jar.name] = sorted(jar_blocks)

    return sorted(blocks), by_jar, [turtle[key] for key in sorted(turtle)], [pocket[key] for key in sorted(pocket)]


def platform(commands: list[str], min_x: int, max_x: int, min_z: int, max_z: int) -> None:
    commands.extend(
        [
            f"forceload add {min_x} {min_z} {max_x} {max_z}",
            f"fill {min_x} 63 {min_z} {max_x} 63 {max_z} minecraft:deepslate_tiles",
            f"fill {min_x} 64 {min_z} {max_x} 67 {max_z} minecraft:air",
        ]
    )


def generate(lane: str, computer_id: int, data_dir: Path, output_dir: Path) -> None:
    mods_dir = data_dir / "mods"
    if not mods_dir.is_dir():
        raise SystemExit(f"Missing installed mods directory: {mods_dir}. Start the lane first.")

    blocks, by_jar, turtle_upgrades, pocket_upgrades = discover(mods_dir)
    if not blocks:
        raise SystemExit(f"No authored-mod blocks discovered in {mods_dir}")
    modern = ".21" in lane
    commands: list[str] = []

    # Block/peripheral network zone.
    block_columns = 6
    block_rows = math.ceil(len(blocks) / block_columns)
    block_start_x = 32
    block_start_z = -block_rows
    control = {"x": block_start_x - 3, "y": 66, "z": block_start_z}
    block_cells = []
    for index, block_id in enumerate(blocks):
        x = block_start_x + (index % block_columns) * 3
        z = block_start_z + (index // block_columns) * 2
        block_cells.append({
            "index": index + 1, "block": block_id, "x": x, "y": 66, "z": z,
            "modem_x": x - 1, "modem_y": 66, "modem_z": z,
        })
    block_min_x = control["x"] - 2
    block_max_x = block_start_x + (block_columns - 1) * 3 + 2
    block_min_z = block_start_z - 2
    block_max_z = block_start_z + (block_rows - 1) * 2 + 2
    platform(commands, block_min_x, block_max_x, block_min_z, block_max_z)
    commands.extend([
        f"fill {block_min_x} 65 {block_min_z} {block_max_x} 65 {block_max_z} computercraft:cable[cable=true]",
        f"setblock {control['x'] - 1} 66 {control['z']} computercraft:wired_modem_full[modem=true,peripheral=true]",
        f"setblock {control['x']} 66 {control['z']} minecraft:air",
        f"setblock {control['x']} 66 {control['z']} computercraft:computer_advanced{{ComputerId:{computer_id},On:1b}}",
    ])
    for cell in block_cells:
        commands.extend([
            f"setblock {cell['x']} 66 {cell['z']} {cell['block']}",
            f"setblock {cell['modem_x']} 66 {cell['modem_z']} computercraft:wired_modem_full[modem=true,peripheral=true]",
        ])

    # One turtle with only a left upgrade for every active authored turtle upgrade.
    turtle_columns = 8
    turtle_rows = max(1, math.ceil(len(turtle_upgrades) / turtle_columns))
    turtle_start_x = 58
    turtle_start_z = -turtle_rows
    platform(commands, turtle_start_x - 1, turtle_start_x + (turtle_columns - 1) * 2 + 1, turtle_start_z - 1, turtle_start_z + (turtle_rows - 1) * 2 + 1)
    turtle_cells = []
    for index, upgrade in enumerate(turtle_upgrades):
        x = turtle_start_x + (index % turtle_columns) * 2
        z = turtle_start_z + (index // turtle_columns) * 2
        turtle_cells.append({"index": index + 1, "x": x, "y": 64, "z": z, **upgrade})
        commands.extend([
            f"setblock {x} 64 {z} minecraft:air",
            f"setblock {x} 64 {z} computercraft:turtle_advanced{{LeftUpgrade:\"{upgrade['id']}\"}}",
        ])

    # One upgraded pocket computer displayed over one lectern per active pocket upgrade.
    pocket_columns = 8
    pocket_rows = max(1, math.ceil(len(pocket_upgrades) / pocket_columns))
    pocket_start_x = 58
    pocket_start_z = 10
    platform(commands, pocket_start_x - 1, pocket_start_x + (pocket_columns - 1) * 2 + 1, pocket_start_z - 1, pocket_start_z + (pocket_rows - 1) * 2 + 1)
    commands.append("kill @e[type=minecraft:item_display,tag=mc_test_authored_pocket]")
    pocket_cells = []
    for index, upgrade in enumerate(pocket_upgrades):
        x = pocket_start_x + (index % pocket_columns) * 2
        z = pocket_start_z + (index // pocket_columns) * 2
        tag = f"mc_test_pocket_{index + 1}"
        pocket_cells.append({"index": index + 1, "x": x, "y": 64, "z": z, "entity_tag": tag, **upgrade})
        if modern:
            item = f'{{id:"computercraft:pocket_computer_advanced",count:1,components:{{"computercraft:pocket_upgrade":{{id:"{upgrade["id"]}"}}}}}}'
        else:
            item = f'{{id:"computercraft:pocket_computer_advanced",Count:1b,tag:{{Upgrade:"{upgrade["id"]}"}}}}'
        commands.extend([
            f"setblock {x} 64 {z} minecraft:lectern[facing=south]",
            f"summon minecraft:item_display {x + 0.5} 65.15 {z + 0.5} {{Tags:[\"mc_test_authored_pocket\",\"{tag}\"],Invulnerable:1b,item:{item},item_display:\"fixed\",transformation:{{translation:[0.0f,0.0f,0.0f],scale:[0.8f,0.8f,0.8f],left_rotation:[0.0f,0.0f,0.0f,1.0f],right_rotation:[0.0f,0.0f,0.0f,1.0f]}}}}",
        ])

    all_min_x = min(block_min_x, turtle_start_x - 1, pocket_start_x - 1)
    all_max_x = max(block_max_x, turtle_start_x + 15, pocket_start_x + 15)
    all_min_z = min(block_min_z, turtle_start_z - 1)
    all_max_z = max(block_max_z, pocket_start_z + (pocket_rows - 1) * 2 + 1)
    commands.extend([
        f"forceload add {all_min_x} {all_min_z} {all_max_x} {all_max_z}",
        f"say Authored fixture for {lane}: {len(blocks)} blocks, {len(turtle_upgrades)} turtles, {len(pocket_upgrades)} pocket computers.",
    ])

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "authored-blocks.mcfunction").write_text("\n".join(commands) + "\n", encoding="utf-8")
    manifest = {
        "lane": lane,
        "block_count": len(blocks),
        "turtle_upgrade_count": len(turtle_upgrades),
        "pocket_upgrade_count": len(pocket_upgrades),
        "control_computer": {**control, "id": computer_id},
        "jars": by_jar,
        "cells": block_cells,
        "turtle_cells": turtle_cells,
        "pocket_cells": pocket_cells,
    }
    (output_dir / "authored-blocks.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(blocks)} blocks, {len(turtle_upgrades)} turtles, and {len(pocket_upgrades)} pocket computers for {lane} in {output_dir}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lane", required=True)
    parser.add_argument("--computer-id", type=int, required=True)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    generate(args.lane, args.computer_id, args.data_dir, args.output_dir)


if __name__ == "__main__":
    main()
