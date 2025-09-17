// priority: 0

// Visit the wiki for more info - https://kubejs.com/

const bannedFromPlacing = [
    "minecraft:hopper",
    "pneumaticcraft:omnidirectional_hopper",
    "embers:fluid_pipe"
]

const hopperPlaceTriggerData = "comzero_tried_to_place_hopper"

for (let bannedItem of bannedFromPlacing) {
    BlockEvents.placed(bannedItem, event => {
        if (!event.player.persistentData.getBoolean(hopperPlaceTriggerData)) {
            event.player.tell("Sadly, in this modpacks you can't use hopper! Use computers or something else, that is allowed!")
            event.player.persistentData.putBoolean(hopperPlaceTriggerData, true);
            event.server.runCommandSilent("heracles complete understanding_the_basics " + event.player.username)
        } else {
            event.player.tell("You already know this is not gonna work, stop trying!")
        }
        event.cancel()
    })
}


ServerEvents.recipes(event => {
    // Remove recipes for item moving items that can be removed
  event.remove({ output: 'essentials:sorting_hopper' })
  event.remove({ output: 'essentials:speed_hopper' })
  event.remove({ output: 'essentials:hopper_filter' })
  event.remove({ output: 'pneumaticcraft:liquid_hopper' })
  event.remove({ output: 'sophisticatedstorage:hopper_upgrade' })
  event.remove({ output: 'sophisticatedstorage:advanced_hopper_upgrade' })
  event.remove({ output: 'biomancy:maw_hopper' })
  event.remove({id: "occultism:recipe/summon_foliot_transport_items"})
  event.remove({id: "occultism:recipe/summon_djinni_manage_machine"})
  event.remove({ output: 'industrialforegoing:conveyor' })
  event.remove({ output: "actuallyadditions:laser_relay_item"})
  event.remove({ output: "actuallyadditions:laser_relay_item_advanced"})
  event.remove({ output: "actuallyadditions:laser_relay_fluids"})
  event.remove({ output: "actuallyadditions:laser_relay_fluids_advanced"})
  event.remove({ output: "enderio:fluid_conduit"})
  event.remove({ output: "enderio:pressurized_fluid_conduit"})
  event.remove({ output: "enderio:ender_fluid_conduit"})
  event.remove({ output: "enderio:item_conduit"})
  event.remove({ output: "enderio:impulsive_hopper"})
  event.remove({ output: "embers:item_pipe"})
  event.remove({ output: "embers:item_extractor"})
  event.remove({ output: "embers:item_transfer"})
  event.remove({ output: "embers:item_vacuum"})
  event.remove({ output: "embers:item_dropper"})
  event.remove({ output: "embers:fluid_transfer"})
  event.remove({ output: "embers:fluid_extractor"})
  // Blocks with no meaning now
  event.remove({ output: "actuallyadditions:item_interface"})
  event.remove({ output: "actuallyadditions:hopping_item_interface"})
  // Block placers
  event.remove({ output: "industrialforegoing:block_placer"})
  event.remove({ output: "actuallyadditions:placer"})
  event.remove({ output: "actuallyadditions:fluid_placer"})
  event.remove({ output: "actuallyadditions:phantom_placer"})
  // block breakers
  event.remove({ output: "industrialforegoing:breaker"})
  event.remove({ output: "actuallyadditions:long_range_breaker"})
  event.remove({ output: "actuallyadditions:breaker"})
  event.remove({ output: "actuallyadditions:phantom_breaker"})
  event.remove({ output: "actuallyadditions:vertical_digger"})
  event.remove({ output: "actuallyadditions:fluid_collector"}) // TOOD: ???
  // Remove any chunk loading...
  event.remove({ output: 'advancedperipherals:chunk_controller' })
  event.remove({ output: 'turtlematic:chunk_vial' })
  event.remove({ output: 'pneumaticcraft:chunkloader_upgrade' })
  // Items that I consider slighly OP for this modpack
  event.remove({ output: "peripherals:spawner_card"})
  // Add some interchange between chunk loaders
  event.shapeless(Item.of("advancedperipherals:chunk_controller"), ["turtlematic:chunk_vial"])
  event.shapeless(Item.of("turtlematic:chunk_vial"), ["advancedperipherals:chunk_controller"])
})

const computerScientist = "advancedperipherals:computer_scientist"

MoreJSEvents.villagerTrades((event) => {
    // TODO: probably restore all other trades, my goal is only to remove chunk loader
    event.removeModdedTrades([computerScientist], 4);
})