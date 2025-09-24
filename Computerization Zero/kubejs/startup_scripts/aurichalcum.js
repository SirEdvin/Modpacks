// priority: 0

// Visit the wiki for more info - https://kubejs.com/

StartupEvents.registry('block', event => {
  event.create('aurichalcum_block')
    .displayName('Aurichalcum block')
    .soundType('metal')
    .hardness(1.0)
    .resistance(1.0)
    .requiresTool(true)
    .tagBlock('minecraft:mineable/pickaxe')
  event.create('aurichalcum_block_fancy') // Create a new block
    .displayName('Charged aurichalcum block') // Set a custom name
    .soundType('metal') // Set a material (affects the sounds and some properties)
    .hardness(1.0) // Set hardness (affects mining time)
    .resistance(1.0) // Set resistance (to explosions, etc)
    .requiresTool(true) // Requires a tool or it won't drop (see tags below)
    .tagBlock('minecraft:mineable/pickaxe') // or a pickaxe
})

StartupEvents.registry('item', event => {
  event.create("ingot_aurichalcum").displayName("Aurichalcum ingot")
  event.create("ingot_aurichalcum_fancy").displayName("Charged aurichalcum ingot")
  event.create("nugget_aurichalcum").displayName("Aurichalcum nugget")
  event.create("nugget_aurichalcum_fancy").displayName("Charged aurichalcum nugget")

  event.create('aurichalcum_sulfur', 'theurgy:alchemical_sulfur')
        .sourceItem('kubejs:ingot_aurichalcum')
        .sourceName("Aurichalcum ingot")
        .sulfurTier("precious")
        .sulfurType("metals")
})