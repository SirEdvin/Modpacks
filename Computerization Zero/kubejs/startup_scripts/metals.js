// priority: 0

StartupEvents.registry('fluid', event => {
    event.create("molten_overcomplicatium").thickTexture(0x852297)
    .bucketColor(0x852297)
    .displayName('Molten overcomplicatium')
    event.create("motlen_aurichalcum_fancy").thickTexture(0xc1ae2a)
    .bucketColor(0xc1ae2a)
    .displayName('Molten refined aurichalcum')
    event.create("complification_mixtrure").thinTexture(0xa26760)
    .bucketColor(0xa26760)
    .displayName("Complification mixture")
})


StartupEvents.registry('block', event => {
  event.create('aurichalcum_block')
    .displayName('Aurichalcum block')
    .soundType('metal')
    .hardness(1.0)
    .resistance(1.0)
    .requiresTool(true)
    .tagBlock('minecraft:mineable/pickaxe')
  event.create('aurichalcum_block_fancy') // Create a new block
    .displayName('Refined aurichalcum block') // Set a custom name
    .soundType('metal') // Set a material (affects the sounds and some properties)
    .hardness(1.0) // Set hardness (affects mining time)
    .resistance(1.0) // Set resistance (to explosions, etc)
    .requiresTool(true) // Requires a tool or it won't drop (see tags below)
    .tagBlock('minecraft:mineable/pickaxe') // or a pickaxe

  event.create('overcomplicatium_block')
    .displayName('Overcomplicatiun block')
    .soundType('metal')
    .hardness(1.0)
    .resistance(1.0)
    .requiresTool(true)
    .tagBlock('minecraft:mineable/pickaxe')
})

StartupEvents.registry('item', event => {
  event.create("ingot_aurichalcum").displayName("Aurichalcum ingot")
  event.create("ingot_aurichalcum_fancy").displayName("Refined aurichalcum ingot")
  event.create("nugget_aurichalcum").displayName("Aurichalcum nugget")
  event.create("nugget_aurichalcum_fancy").displayName("Refined aurichalcum nugget")

  event.create('aurichalcum_sulfur', 'theurgy:alchemical_sulfur')
        .sourceItem('kubejs:ingot_aurichalcum')
        .sourceName("Aurichalcum ingot")
        .sulfurTier("precious")
        .sulfurType("metals")
  event.create("ingot_overcomplicatium").displayName("Overcomplicatium ingot")
  event.create("nugget_overcomplicatium").displayName("Overcomplicatium nugget")
  event.create("overcomplicatium_slug").displayName("Overcomplicatium slug")
})