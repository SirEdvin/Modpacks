peripheraliumVersion = 0.6.4-15
turtlematicVersion = 1.0.0-1
peripheralWorksVersion = 1.0.0-2


peripheralium:
	packwiz url add peripheralium https://mvn.siredvin.site/snapshots/site/siredvin/peripheralium-fabric-1.20.1/$(peripheraliumVersion)/peripheralium-fabric-1.20.1-$(peripheraliumVersion).jar

turtlematic:
	packwiz url add turtlematic https://mvn.siredvin.site/snapshots/site/siredvin/turtlematic-fabric-1.20.1/$(turtlematicVersion)/turtlematic-fabric-1.20.1-$(turtlematicVersion).jar

upw:
	packwiz url add unlimitedperipheralworks https://mvn.siredvin.site/snapshots/site/siredvin/peripheralworks-fabric-1.20.1/$(peripheralWorksVersion)/peripheralworks-fabric-1.20.1-$(peripheralWorksVersion).jar

all: peripheralium turtlematic upw

modrinth:
	packwiz modrinth add peripheralium
	packwiz modrinth add unlimitedperipheralworks
	packwiz modrinth add turtlematic
