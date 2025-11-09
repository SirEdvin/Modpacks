if(Platform.isLoaded("aquaculture")) {
    unregistered_axes.push("aquaculture:neptunium_axe")

    ServerEvents.recipes(event => {
        event.recipes.create.crushing([Item.of(Item.of("aquaculture:neptunium_ingot", 2)), Item.of(Item.of("aquaculture:neptunium_nugget", 5)).withChance(.5)], "aquaculture:neptunes_bounty").processingTime(500)

        // Note: This does disable the recipe but strangely does not hide it from the recipe viewer
        // Fortunately this can be done by the config
        event.remove({ id: "aquaculture:fish_fillet" })

        // Add all fillet recipes to the cutting board

        let fillet_recipe = (name, count) => {
            event.custom({
                type: "farmersdelight:cutting",
                ingredients: [
                    { item: name }
                ],
                tool: { tag: "forge:tools/knives" },
                result: [
                    { item: "aquaculture:fish_fillet_raw", count: count },
                    { item: "minecraft:bone_meal"}
                ]
            })
        }

        fillet_recipe("minecraft:pufferfish", 1)
        fillet_recipe("aquaculture:atlantic_cod", 6)
        fillet_recipe("aquaculture:blackfish", 2)
        fillet_recipe("aquaculture:pacific_halibut", 12)
        fillet_recipe("aquaculture:atlantic_halibut", 14)
        fillet_recipe("aquaculture:atlantic_herring", 1)
        fillet_recipe("aquaculture:pink_salmon", 2)
        fillet_recipe("aquaculture:pollock", 2)
        fillet_recipe("aquaculture:rainbow_trout", 2)
        fillet_recipe("aquaculture:bayad", 4)
        fillet_recipe("aquaculture:boulti", 1)
        fillet_recipe("aquaculture:capitaine", 10)
        fillet_recipe("aquaculture:synodontis", 1)
        fillet_recipe("aquaculture:smallmouth_bass", 2)
        fillet_recipe("aquaculture:bluegill", 1)
        fillet_recipe("aquaculture:brown_trout", 2)
        fillet_recipe("aquaculture:carp", 2)
        fillet_recipe("aquaculture:catfish", 6)
        fillet_recipe("aquaculture:gar", 4)
        fillet_recipe("aquaculture:muskellunge", 3)
        fillet_recipe("aquaculture:perch", 1)
        fillet_recipe("aquaculture:arapaima", 10)
        fillet_recipe("aquaculture:piranha", 1)
        fillet_recipe("aquaculture:tambaqui", 3)
        fillet_recipe("aquaculture:red_grouper", 3)
        fillet_recipe("aquaculture:tuna", 10)

        // Remove aquaculture fillet knives as farmer's delight knives are identical in function now
        event.remove({ id: "aquaculture:wooden_fillet_knife" })
        event.remove({ id: "aquaculture:stone_fillet_knife" })
        event.remove({ id: "aquaculture:iron_fillet_knife" })
        event.remove({ id: "aquaculture:gold_fillet_knife" })
        event.remove({ id: "aquaculture:diamond_fillet_knife" })

        // Fix neptunium knife not being unbreakable
        event.replaceOutput({ id: "aquaculture:neptunium_fillet_knife" }, "aquaculture:neptunium_fillet_knife", Item.of("aquaculture:neptunium_fillet_knife").withNBT({Unbreakable:1, HideFlags:4}))
    })

    ServerEvents.tags("item", event => {
        // Adds tags to fish fillet items to allow for their use in more recipes
        event.add("forge:raw_fishes", "aquaculture:fish_fillet_raw")
        event.add("farmersdelight:cabbage_roll_ingredients", "aquaculture:fish_fillet_raw")
        event.add("forge:cooked_fishes", "aquaculture:fish_fillet_cooked")

        // Remove knife tags to prevent them from showing up in EMI
        event.get("forge:tools/knives")
            .remove("aquaculture:wooden_fillet_knife")
            .remove("aquaculture:stone_fillet_knife")
            .remove("aquaculture:iron_fillet_knife")
            .remove("aquaculture:gold_fillet_knife")
            .remove("aquaculture:diamond_fillet_knife")

        event.get("farmersdelight:tools/knives")
            .add("aquaculture:neptunium_fillet_knife")
    })

    // Give neptunium knifes the unbreakable tag so that they don't break when used by deployers
    PlayerEvents.inventoryChanged("aquaculture:neptunium_fillet_knife", event => {
        let nbt = event.item.getNbt() || {};
        nbt.Unbreakable = 1;
        nbt.HideFlags = 4;
        event.item.setNbt(nbt);
        return;
    })
}
