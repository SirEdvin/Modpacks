const genericMetals = [
  { id: "powah:uraninite_raw", name: "Uraninite vein", chance: 0.5 },
  { id: "thermal:raw_tin", name: "Tin vein", chance: 0.5 },
  { id: "thermal:raw_lead", name: "Lead vein", chance: 0.2 },
  { id: "thermal:raw_silver", name: "Silver vein", chance: 0.2 },
  { id: "thermal:raw_nickel", name: "Nickel vein", chance: 0.2 },
  { id: "malum:raw_soulstone", name: "Soulstone vein", chance: 0.5 },
  { id: "bigreactors:raw_yellorium", name: "Yellorium vein", chance: 0.3 },
];

const baseMaterials = [
  { id: "minecraft:raw_iron", chance: 0.5 },
  { id: "minecraft:coal", chance: 1 },
  { id: "minecraft:raw_copper", chance: 1 },
  { id: "minecraft:diamond", chance: 0.5 },
  { id: "minecraft:emerald", chance: 0.5 },
  { id: "minecraft:redstone_block", chance: 0.8 },
  { id: "minecraft:lapis_block", chance: 0.5 },
  { id: "create:raw_zinc", chance: 0.5 },
  { id: "computercraft:computer_advanced", chance: 0.005 },
  { id: "minecraft:glowstone_dust", chance: 0.3 },
  { id: "minecraft:quartz", chance: 0.3 },
  { id: "minecraft:quartz", chance: 0.3 },
];

ServerEvents.recipes((event) => {
  for (let genericMetal of genericMetals) {
    let veinId = `kubejs:${genericMetal.name
      .toLowerCase()
      .replace(" ", "_")}`;
    event.recipes.createoreexcavation
      .vein(genericMetal.name, genericMetal.id)
      .placement(128, 8, 277506605)
      .biomeWhitelist("minecraft:is_overworld")
      .id(veinId);
    event.recipes.createoreexcavation
      .drilling(genericMetal.id, veinId, 100)
      .id(`${veinId}_drilling`);
  }
  const miningVeinID = "kubejs:mining_vein";
  const drillingOutput = [];
  for (let genericMetal of genericMetals) {
    drillingOutput
      .push(Item.of(genericMetal.id).withChance(genericMetal.chance))
  }
  for (let baseMaterial of baseMaterials) {
    drillingOutput
      .push(Item.of(baseMaterial.id).withChance(baseMaterial.chance))
  }
  // Cool vein in mining dimension, but finite
  event.recipes.createoreexcavation
    .vein("Mining vein", "minecraft:diamond")
    .placement(128, 8, 277506605)
    .veinSize(5, 20)
    .biomeBlacklist("minecraft:is_overworld")
    .id(miningVeinID);
  event.recipes.createoreexcavation
    .drilling(drillingOutput, miningVeinID, 100)
    .drill("createoreexcavation:diamond_drill")
    .fluid("minecraft:water")
    .id("kubejs:mining_vein_drilling");
});
