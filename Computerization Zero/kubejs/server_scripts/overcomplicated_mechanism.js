ServerEvents.recipes((event) => {
  // Silicon line
  event.recipes.create.mixing("kubejs:dirty_silica", [
    Item.of("minecraft:sand", 8),
    Item.of("minecraft:quartz"),
  ]);
  event.recipes.create.filling("kubejs:silica", [
    Fluid.water(100),
    "kubejs:dirty_silica",
  ]);
  event.recipes.create
    .mixing(Fluid.of("kubejs:molten_silica", 250), [
      Item.of("kubejs:silica", 4),
      Fluid.of("minecraft:lava", 1000),
    ])
    .heated();
  event.recipes.create.filling("kubejs:silicon_wafer", [
    Fluid.of("kubejs:molten_silica", 1000),
    Item.of("create:sturdy_sheet"),
  ]);
  event.recipes.create.cutting(Item.of("kubejs:mechanism_base", 8), [
    "kubejs:silicon_wafer",
  ]);
  // Bulbs
  let inner = "kubejs:unfinished_raw_complicated_bulb";
  let bulbs = [
    Item.of("kubejs:raw_complicated_bulb_0").withChance(100),
    Item.of("kubejs:raw_complicated_bulb_1").withChance(100),
    Item.of("kubejs:raw_complicated_bulb_2").withChance(100),
    Item.of("kubejs:raw_complicated_bulb_3").withChance(100),
    Item.of("kubejs:raw_complicated_bulb_4").withChance(100),
    Item.of("kubejs:raw_complicated_bulb_5").withChance(100),
  ];
  event.recipes.create
    .sequenced_assembly(bulbs, "create:nixie_tube", [
      event.recipes.createFilling(inner, [
        inner,
        Fluid.of("minecraft:lava", 250),
      ]),
      event.recipes.createPressing(inner, inner),
      event.recipes.createCutting(inner, inner),
      event.recipes.createDeploying(inner, [
        inner,
        Item.of("minecraft:iron_ingot"),
      ]),
      event.recipes.createDeploying(inner, [
        inner,
        Item.of("minecraft:copper_ingot"),
      ]),
      event.recipes.createDeploying(inner, [
        inner,
        Item.of("create:zinc_ingot"),
      ]),
    ])
    .transitionalItem(inner)
    .loops(8);

    for (let i = 0; i< 6; i++) {
        event.recipes.create.mechanical_crafting(`kubejs:finished_complicated_bulb_${i}`, [
            "  Q  ",
            "  A  ",
            "QABAQ",
            "  A  ",
            "  Q  "
        ], {
            Q: "minecraft:quartz",
            A: "minecraft:amethyst_shard",
            B: `kubejs:raw_complicated_bulb_${i}`
        })
    }
    // 0 - A
    // 1 - B
    // 2 - D
    // 3 - E
    // 4 - F
    // 5 - G
    // chip - C 
    // brass ingot - I
    // mechanism - M
    event.recipes.create.mechanical_crafting("kubejs:overcomplicated_mechanism", [
        "CCACC",
        "EFMBD",
        "GMIMG",
        "DBMFE",
        "CCACC"
    ], {
        A: "kubejs:finished_complicated_bulb_0",
        B: "kubejs:finished_complicated_bulb_1",
        D: "kubejs:finished_complicated_bulb_2",
        E: "kubejs:finished_complicated_bulb_3",
        F: "kubejs:finished_complicated_bulb_4",
        G: "kubejs:finished_complicated_bulb_5",
        C: "kubejs:mechanism_base",
        I: "create:brass_sheet",
        M: "create:precision_mechanism",
    })
});
