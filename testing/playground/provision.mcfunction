# Re-running this file is safe: it rebuilds the same compact fixture.
gamerule doMobSpawning false
gamerule doWeatherCycle false
gamerule doDaylightCycle false
gamerule keepInventory true
gamerule commandBlockOutput false
time set day
weather clear
kill @e[type=minecraft:item]
fill -24 63 -24 24 63 24 minecraft:smooth_stone
fill -23 64 -23 23 64 23 minecraft:air
fill -2 64 -2 2 64 2 minecraft:polished_deepslate
setworldspawn 0 65 4
spawnpoint @a 0 65 4
# Control desk: an advanced computer, monitor wall, disk drive, printer, and speaker.
setblock 0 65 0 computercraft:computer_advanced
setblock -1 65 0 computercraft:disk_drive
setblock 1 65 0 computercraft:printer
setblock 2 65 0 computercraft:speaker
setblock -1 66 0 computercraft:monitor_advanced
setblock 0 66 0 computercraft:monitor_advanced
setblock 1 66 0 computercraft:monitor_advanced
# Inventory and redstone fixtures (west).
fill -20 64 -20 -4 64 -4 minecraft:light_blue_concrete
setblock -18 65 -18 minecraft:chest
setblock -16 65 -18 minecraft:barrel
setblock -14 65 -18 minecraft:hopper
setblock -12 65 -18 minecraft:dropper
setblock -10 65 -18 minecraft:dispenser
setblock -8 65 -18 minecraft:furnace
setblock -6 65 -18 minecraft:lever
setblock -5 65 -18 minecraft:redstone_lamp
# Peripheral placement benches (east), spaced to keep test devices isolated.
fill 4 64 -20 20 64 -4 minecraft:purple_concrete
fill 5 65 -19 7 65 -17 minecraft:quartz_block
fill 9 65 -19 11 65 -17 minecraft:quartz_block
fill 13 65 -19 15 65 -17 minecraft:quartz_block
fill 17 65 -19 19 65 -17 minecraft:quartz_block
fill 5 65 -14 7 65 -12 minecraft:quartz_block
fill 9 65 -14 11 65 -12 minecraft:quartz_block
fill 13 65 -14 15 65 -12 minecraft:quartz_block
fill 17 65 -14 19 65 -12 minecraft:quartz_block
# Turtle movement and block-interaction track (south).
fill -20 64 4 20 64 20 minecraft:lime_concrete
fill -18 65 16 18 65 18 minecraft:iron_block
setblock -18 66 17 computercraft:turtle_advanced
setblock -12 66 17 minecraft:oak_log
setblock -6 66 17 minecraft:stone
setblock 0 66 17 minecraft:chest
setblock 6 66 17 minecraft:crafting_table
setblock 12 66 17 minecraft:redstone_block
setblock 18 66 17 minecraft:diamond_block
# Network bench (northwest edge).
fill -20 64 -2 -4 64 2 minecraft:orange_concrete
fill -18 65 0 -6 65 0 computercraft:cable
setblock -18 65 0 computercraft:wired_modem_full
setblock -6 65 0 computercraft:wired_modem_full
# Keep only the compact laboratory area loaded.
forceload remove all
forceload add -2 -2 2 2
# Place the control computer last: monitor/network neighbor updates differ by CC version.
setblock 0 65 0 computercraft:computer_advanced
say Peripheral playground provisioned: control desk at 0 65 0; benches east; turtle track south.
