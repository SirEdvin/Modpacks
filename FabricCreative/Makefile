peripheraliumVersion = 0.6.5-pre.2
turtlematicVersion = 1.1.0-pre.2
peripheralWorksVersion = 1.1.0-pre.1


peripheralium:
	packwiz url add peripheralium https://github.com/SirEdvin/Peripheralium/releases/download/v1.20.1-${peripheraliumVersion}/peripheralium-fabric-1.20.1-${peripheraliumVersion}.jar

turtlematic:
	packwiz url add turtlematic https://github.com/SirEdvin/Turtlematic/releases/download/v1.20.1-${turtlematicVersion}/turtlematic-fabric-1.20.1-${turtlematicVersion}.jar

upw:
	packwiz url add unlimitedperipheralworks https://github.com/SirEdvin/UnlimitedPeripheralWorks/releases/download/v1.20.1-${peripheralWorksVersion}/peripheralworks-fabric-1.20.1-${peripheralWorksVersion}.jar

all: peripheralium turtlematic upw

modrinth:
	packwiz modrinth add peripheralium
	packwiz modrinth add unlimitedperipheralworks
	packwiz modrinth add turtlematic
