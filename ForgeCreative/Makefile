peripheraliumVersion = 0.6.3-3
turtlematicVersion = 0.7.3-1
peripheralWorksVersion = 0.5.2-1

peripheralium:
	packwiz url add peripheralium https://mvn.siredvin.site/snapshots/site/siredvin/peripheralium-forge-1.20.1/$(peripheraliumVersion)/peripheralium-forge-1.20.1-$(peripheraliumVersion).jar

turtlematic:
	packwiz url add turtlematic https://mvn.siredvin.site/snapshots/site/siredvin/turtlematic-forge-1.20.1/$(turtlematicVersion)/turtlematic-forge-1.20.1-$(turtlematicVersion).jar
	
upw:
	packwiz url add unlimitedperipheralworks https://mvn.siredvin.site/snapshots/site/siredvin/peripheralworks-forge-1.20.1/$(peripheralWorksVersion)/peripheralworks-forge-1.20.1-$(peripheralWorksVersion).jar

all: peripheralium turtlematic upw

modrinth:
	packwiz modrinth add peripheralium
	packwiz modrinth add unlimitedperipheralworks
	packwiz modrinth add turtlematic
