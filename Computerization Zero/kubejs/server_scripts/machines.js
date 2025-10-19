const itemToDuplicate = [
    "minecraft:stone",
    "minecraft:cobblestone",
    "minecraft:basalt",
    "minecraft:andesite",
    "minecraft:diorite",
    "minecraft:granite",
]

ServerEvents.recipes(event => {
    event.recipes.create.mechanical_crafting("mbd2:compute_multiblock_tier_1", [
        "A   A",
        "A   A",
        "A   A",
        "A   A",
        "BBCBB"
    ], {
        C: "computercraft:computer_advanced",
        A: "kubejs:overcomplicated_mechanism",
        B: "kubejs:aurichalcum_block_fancy"
    })

    for (let item of itemToDuplicate) {
        event.recipes.mbd2.compute_normal()
            .id("mbd2:compute_normal/" + item.replace(":", "_"))    
            .duration(100)
            .inputItems(item)
            .inputFluids(Fluid.of("kubejs:deluted_generation_fluid", 100))
            .perTick(builder => {
                builder.inputFE(1000).outputItems(Item.of(item, 64))
            })
    }

    event.recipes.mbd2.compute_normal()
        .id("mbd2:compute_normal/hollow_brass_chunk_loader")
        .duration(100)
        .perTick(builder => {
            builder.inputFluids(Fluid.of("kubejs:molten_silica", 100)).inputItems(
                Item.of("kubejs:ingot_aurichalcum_fancy"), Item.of("kubejs:ingot_overcomplicatium")
            ).inputFE(1000)
        })
        .outputItems(Item.of("kubejs:hollow_brass_chunk_loader"))

    event.recipes.mbd2.compute_normal()
        .id("mbd2:compute_normal/brass_chunk_loader")
        .duration(10)
        .inputItems(Item.of("kubejs:overcomplicated_mechanism", 8), Item.of("kubejs:hollow_brass_chunk_loader"), Item.of("minecraft:ghast_tear", 8))
        .inputFE(50000)
        .inputFluids(Fluid.of("minecraft:lava"))
        .outputItems(Item.of("create_power_loader:brass_chunk_loader"))
})