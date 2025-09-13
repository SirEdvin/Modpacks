const AE2_ONLY_CASUAL_ITEMS = [
    "ae2:pattern_provider",
    "advanced_ae:adv_pattern_provider",
    "advanced_ae:small_adv_pattern_provider",
    "expatternprovider:ex_pattern_provider",
    "megacells:mega_pattern_provider",
]

const AE2_PROTECTED_ITEMS = [
    "ae2:controller",
    "ae2:drive",
    "expatternprovider:ex_drive",
]

const AE2_BANNED_ITEMS = [
    "ae2:interface"
]

const AE2_BANNED_CABLE_PARTS = {
    "appeng.parts.automation.ExportBusPart": true,
    "appeng.parts.automation.ImportBusPart": true,
}

const AE2_PROCTECTED_CABLE_PARTS = {
    "appeng.parts.storagebus.StorageBusPart": true,
    "com.glodblock.github.extendedae.common.parts.PartTagStorageBus": true,
    "com.glodblock.github.extendedae.common.parts.PartModStorageBus": true,
    "com.glodblock.github.extendedae.common.parts.PartPreciseStorageBus": true,
}

const AE2_ONLY_CASUAL_CABLE_PARTS = {
    "net.pedroksl.advanced_ae.common.parts.AdvPatternProviderPart": true,
    "net.pedroksl.advanced_ae.common.parts.SmallAdvPatternProviderPart": true,
    "appeng.parts.crafting.PatternProviderPart": true,
    "com.glodblock.github.extendedae.common.parts.PartExPatternProvider": true,
    "gripe._90.megacells.item.part.MEGAPatternProviderPart": true,
}

const ae2SelectedRole = "comzero_ae2_selected_role"

const AE2_CASUAL_ROLE = "ae2:casual"
const AE2_SEMICASUAL_ROLE = "ae2:semicasual"
const AE2_HARDCORE_ROLE = "ae2:hardcore"

for (let bannedItem of AE2_BANNED_ITEMS) {
    BlockEvents.placed(bannedItem, ae2GenericRefuse)
    BlockEvents.rightClicked(bannedItem, ae2GenericRefuse)
}

function ae2GenericRefuse(event) {
    if (event.player != null) {
        event.player.tell("Nope, you can't use this. Use computers and peripherals intead!")
        event.cancel()
    }
}

function ae2ProtectedItemHandler(event) {
    if (event.player != null) {
        let playerRole = event.player.persistentData.getString(ae2SelectedRole)
        if (playerRole == "") {
            event.player.tell("You still need to choose your path")
            event.cancel()
        } else if (playerRole == AE2_HARDCORE_ROLE) {
            console.info(event)
            console.info(event.block.id)
            event.player.tell("You took an oath to never use this item! You can take it back in quest book, of course..")
            event.cancel()
        }
    }
}

for (let ae2ProtectedItem of AE2_PROTECTED_ITEMS) {
    BlockEvents.placed(ae2ProtectedItem, ae2ProtectedItemHandler)
    BlockEvents.rightClicked(ae2ProtectedItem, ae2ProtectedItemHandler)
}

function ae2CasualItemHandler(event) {
    if (event.player != null) {
        let playerRole = event.player.persistentData.getString(ae2SelectedRole)
        if (playerRole == "") {
            event.player.tell("You still need to choose your path")
            event.cancel()
        } else if (playerRole != AE2_CASUAL_ROLE) {
            event.player.tell("You took an oath to never use this item! You can take it back in quest book, of course..")
            event.cancel()
        }
    }
}

for (let ae2OnlyCasualItem of AE2_ONLY_CASUAL_ITEMS) {
    BlockEvents.placed(ae2OnlyCasualItem, ae2CasualItemHandler)
    BlockEvents.rightClicked(ae2OnlyCasualItem, ae2CasualItemHandler)
}


function handleCableBus(event) {
    let cableBus = event.block.entity.getCableBus()
    for (let key in Direction.ALL) {
        let part = cableBus.getPart(key)
        if (part != null) {
            let className = part.getClass().getName()
            if (AE2_BANNED_CABLE_PARTS[className]) {
                ae2GenericRefuse(event)
            } else if (AE2_PROCTECTED_CABLE_PARTS[className]){
                ae2ProtectedItemHandler(event)
            } else if (AE2_ONLY_CASUAL_CABLE_PARTS[className]){
                ae2CasualItemHandler(event)
            } else {
                console.info(className)
            }
        }
    }
}

BlockEvents.placed("ae2:cable_bus", handleCableBus)
BlockEvents.rightClicked("ae2:cable_bus", handleCableBus)

ServerEvents.customCommand('ae2_casual', event => {
  let playerRole = event.player.persistentData.getString(ae2SelectedRole)
  if (playerRole == "") {
    event.player.persistentData.putString(ae2SelectedRole, AE2_CASUAL_ROLE)
    event.server.runCommandSilent(`titles add ${event.player.username} kubejs:ae2_casual`)
  } else {
    // TODO: add some extra command usage, like making fun on player or something else
    event.player.persistentData.putString(ae2SelectedRole, AE2_CASUAL_ROLE)
  }
})

ServerEvents.customCommand('ae2_semi_casual', event => {
  let playerRole = event.player.persistentData.getString(ae2SelectedRole)
  if (playerRole == "") {
    event.player.persistentData.putString(ae2SelectedRole, AE2_SEMICASUAL_ROLE)
    event.server.runCommandSilent(`titles add ${event.player.username} kubejs:ae2_semi_casual`)
  } else {
    // TODO: add some extra command usage, like making fun on player or something else
    // And also I should take title away
    event.player.persistentData.putString(ae2SelectedRole, AE2_SEMICASUAL_ROLE)
  }
})

ServerEvents.customCommand('ae2_hardcore', event => {
  let playerRole = event.player.persistentData.getString(ae2SelectedRole)
  if (playerRole == "") {
    event.player.persistentData.putString(ae2SelectedRole, AE2_HARDCORE_ROLE)
    event.server.runCommandSilent(`titles add ${event.player.username} kubejs:ae2_hardcore`)
  } else {
    // TODO: add some extra command usage, like making fun on player or something else
    // And also I should take title away
    event.player.persistentData.putString(ae2SelectedRole, AE2_HARDCORE_ROLE)
  }
})