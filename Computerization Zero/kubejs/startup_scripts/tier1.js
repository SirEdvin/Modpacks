// 6F4E37

StartupEvents.registry('fluid', event => {
    let coffee = event.create("liquid_coffee").thickTexture(0x6F4E37)
    .bucketColor(0x6F4E37)
    .displayName('Coffee')

    coffee.bucketItem.food(food => {
        food.effect('minecraft:speed', 600, 0, 1)
      .removeEffect('minecraft:poison')
      .alwaysEdible()
      .fastToEat()
    })

    event.create('deluted_generation_fluid')
    .displayName('Deluted generation fluid')
    .stillTexture('kubejs:block/fluid_strange_pale')
    .flowingTexture('kubejs:block/fluid_strange_pale')
    .bucketColor(0x99bbcc)
})