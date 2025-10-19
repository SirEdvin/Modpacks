function compactingRecipe(event, small, big) {
    event.shapeless(Item.of(small, 9), [big])
    event.shaped(Item.of(big), ['AAA', 'AAA', 'AAA'], {A: small})
}

function metalRecipes(event, nugget, ingot, block, fluid) {
    compactingRecipe(event, nugget, ingot)
    compactingRecipe(event, ingot, block)
    if (fluid != null) {
        event.custom({
            "type": "tconstruct:melting",
            "ingredient": {
                "item": nugget
            },
            "result": {
                "amount": 10,
                "fluid": fluid
            },
            "temperature": 950,
            "time": 18
        })
        event.custom({
            "type": "tconstruct:melting",
            "ingredient": {
                "item": ingot
            },
            "result": {
                "amount": 90,
                "fluid": fluid
            },
            "temperature": 950,
            "time": 54
        })
        event.custom({
            "type": "tconstruct:melting",
            "ingredient": {
                "item": block
            },
            "result": {
                "amount": 810,
                "fluid": fluid
            },
            "temperature": 950,
            "time": 151
        })
        event.custom({
            "type": "tconstruct:casting_basin",
            "cooling_time": 161,
            "fluid": {
                "amount": 810,
                "fluid": fluid
            },
            "result": {
                "item": block
            }
        })
        event.custom({
            "type": "tconstruct:casting_table",
            "cast": {
                "tag": "tconstruct:casts/multi_use/ingot"
            },
            "cooling_time": 54,
            "fluid": {
                "amount": 90,
                "fluid": fluid
            },
            "result": {
                "item": ingot
            }
        })
        event.custom({
            "type": "tconstruct:casting_table",
            "cast": {
                "tag": "tconstruct:casts/multi_use/nugget"
            },
            "cooling_time": 18,
            "fluid": {
                "amount": 10,
                "fluid": fluid
            },
            "result": {
                "item": nugget
            }
        })
    }
}


ServerEvents.recipes(event => {
    metalRecipes(event, "kubejs:nugget_aurichalcum", "kubejs:ingot_aurichalcum", "kubejs:aurichalcum_block", null)
    metalRecipes(event, "kubejs:nugget_aurichalcum_fancy", "kubejs:ingot_aurichalcum_fancy", "kubejs:aurichalcum_block_fancy", "kubejs:motlen_aurichalcum_fancy")
    metalRecipes(event, "kubejs:nugget_overcomplicatium", "kubejs:ingot_overcomplicatium", "kubejs:overcomplicatium_block", "kubejs:molten_overcomplicatium")

    //MARK: aurichalcum craft
    event.shapeless(Item.of("kubejs:aurichalcum_sulfur"), [
        "theurgy:alchemical_sulfur_sapphire",
        "theurgy:alchemical_sulfur_diamond",
        "theurgy:alchemical_sulfur_gold",
        "theurgy:alchemical_sulfur_silver",
        "theurgy:alchemical_sulfur_nickel",
        "theurgy:alchemical_sulfur_lead",
        "theurgy:alchemical_sulfur_zinc",
        "theurgy:alchemical_sulfur_netherite",
        "theurgy:alchemical_sulfur_tin",
    ])
    event.custom({
        "type": "theurgy:incubation",
        "incubation_time": 100,
        "mercury": {
            "item": "theurgy:mercury_shard"
        },
        "result": {
            "count": 1,
            "item": "kubejs:ingot_aurichalcum"
        },
        "salt": {
            "item": "theurgy:alchemical_salt_mineral"
        },
        "sulfur": {
            "item": "kubejs:aurichalcum_sulfur"
        }
    })
    event.custom({
        "type": "theurgy:reformation",
        "mercury_flux": 150,
        "reformation_time": 100,
        "result": {
            "Count": 1,
            "id": "kubejs:aurichalcum_sulfur"
        },
        "sources": [
            {
            "tag": "theurgy:alchemical_sulfurs/metals/precious"
            }
        ],
        "target": {
            "item": "kubejs:aurichalcum_sulfur"
        }
    })
    event.custom({
        "type": "theurgy:liquefaction",
        "ingredient": {
            "item": "kubejs:ingot_aurichalcum"
        },
        "liquefaction_time": 100,
        "result": {
            "count": 1,
            "item": "kubejs:aurichalcum_sulfur",
        },
        "solvent": {
            "fluid": "theurgy:sal_ammoniac"
        },
        "solvent_amount": 15
    })
    event.custom({
        "type": "theurgy:reformation",
        "mercury_flux": 150,
        "reformation_time": 100,
        "result": {
            "Count": 1,
            "id": "kubejs:aurichalcum_sulfur"
        },
        "sources": [
            {
                "item": "theurgy:alchemical_sulfur_metals_precious"
            }
        ],
        "target": {
            "item": "kubejs:aurichalcum_sulfur"
        }
    })

    // MARK: overcomplicatium craft

    event.custom({
        "type": "minecraft:crafting_shaped",
        "key": {
            "A": {
                "type": "forge:nbt",
                "item": "tconstruct:tough_handle",
                "nbt": {
                    "Material": "tconstruct:queens_slime"
                }
            },
            "B": {
                "type": "forge:nbt",
                "item": "tconstruct:tough_handle",
                "nbt": {
                    "Material": "tconstruct:cinderslime"
                }
            },
            "C": "tconstruct:blazing_bone",
            "D": {
                "type": "forge:nbt",
                "item": "tconstruct:tough_handle",
                "nbt": {
                    "Material": "tconstruct:hepatizon"
                }
            },
            "E": {
                "type": "forge:nbt",
                "item": "tconstruct:tough_handle",
                "nbt": {
                    "Material": "tconstruct:manyullyn"
                }
            },
        },
        "pattern": [
            "BAD",
            "ECE",
            "DAB"
        ],
        "result": {
            "count": 1,
            "item": "kubejs:overcomplicatium_slug"
        }
    })

    event.custom({
        "type": "tconstruct:melting",
        "ingredient": {
            "item": "kubejs:overcomplicatium_slug"
        },
        "result": {
            "amount": 90,
            "fluid": "kubejs:molten_overcomplicatium"
        },
        "temperature": 950,
        "time": 130
    })

    event.recipes.create
    .mixing(Fluid.of("kubejs:motlen_aurichalcum_fancy", 180), [
      Item.of("kubejs:ingot_aurichalcum"),
      Item.of("kubejs:ingot_overcomplicatium"),
    ])
    .superheated();

    event.custom({
        "type": "tconstruct:alloy",
        "inputs": [
            {
                "amount": 180,
                "fluid": "kubejs:motlen_aurichalcum_fancy"
            },
            {
                "amount": 180,
                "fluid": "kubejs:molten_silica"
            },
        ],
        "result": {
            "amount": 180,
            "fluid": "kubejs:motlen_aurichalcum_fancy"
        },
        "temperature": 1400
    })
})