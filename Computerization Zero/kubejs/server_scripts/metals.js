

function compactingRecipe(event, small, big) {
    event.shapeless(Item.of(small, 9), [big])
    event.shaped(Item.of(big), ['AAA', 'AAA', 'AAA'], {A: small})
}

function metalRecipes(event, nugget, ingot, block) {
    compactingRecipe(event, nugget, ingot)
    compactingRecipe(event, ingot, block)
}


ServerEvents.recipes(event => {
    metalRecipes(event, "kubejs:nugget_aurichalcum", "kubejs:ingot_aurichalcum", "kubejs:aurichalcum_block")
    metalRecipes(event, "kubejs:nugget_aurichalcum_fancy", "kubejs:ingot_aurichalcum_fancy", "kubejs:aurichalcum_block_fancy")
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
})