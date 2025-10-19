ServerEvents.recipes(event => {
    event.recipes.mbd2.compute_normal()
        .id("mbd2:compute_normal/coffee_production")
        .duration(10)
        .inputItems(Item.of("actuallyadditions:coffee_beans", 64))
        .inputFluids(Fluid.of("minecraft:water", 5000))
        .inputFE(5000)
        .outputFluids(Fluid.of("kubejs:liquid_coffee", 5000))

    event.recipes.create.filling(Item.of("actuallyadditions:coffee_cup", {
        1: {Duration: 120, ID: "minecraft:strength", Amplifier: 2},
        2: {Duration: 120, ID: "minecraft:speed", Amplifier: 2},
        3: {Duration: 360, ID: "minecraft:night_vision", Amplifier: 1},
        Counter: 3
    }), [
        Fluid.of("kubejs:liquid_coffee", 500),
        Item.of("actuallyadditions:empty_cup"),
    ]);

    
    event.recipes.create.mixing(Fluid.of("kubejs:deluted_generation_fluid", 1000), [
      Fluid.of("kubejs:liquid_coffee", 1000),
      Fluid.of("kubejs:molten_silica", 100),
    ])
})