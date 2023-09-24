peripheraliumVersion = 0.6.13
datafortressVersion = 0.1.0-pre.1
turtlematicVersion = 1.2.4
peripheralWorksVersion = 1.4.0
digitalItemsVersion = 0.3.0


peripheralium:
	packwiz url add peripheralium https://github.com/SirEdvin/Peripheralium/releases/download/v1.20.1-${peripheraliumVersion}/peripheralium-fabric-1.20.1-${peripheraliumVersion}.jar

turtlematic:
	packwiz url add turtlematic https://github.com/SirEdvin/Turtlematic/releases/download/v1.20.1-${turtlematicVersion}/turtlematic-fabric-1.20.1-${turtlematicVersion}.jar

upw:
	packwiz url add unlimitedperipheralworks https://github.com/SirEdvin/UnlimitedPeripheralWorks/releases/download/v1.20.1-${peripheralWorksVersion}/peripheralworks-fabric-1.20.1-${peripheralWorksVersion}.jar
digitems:
	packwiz url add digitalitems https://github.com/SirEdvin/DigitalItems/releases/download/v1.20.1-${digitalItemsVersion}/digitalitems-fabric-1.20.1-${digitalItemsVersion}.jar
datafortress:
	packwiz url add datafortress https://github.com/SirEdvin/DataFortress/releases/download/v1.20.1-${datafortressVersion}/datafortress-fabric-1.20.1-${datafortressVersion}.jar

all: peripheralium turtlematic upw digitems datafortress

modrinth:
	packwiz modrinth add peripheralium
	packwiz modrinth add unlimitedperipheralworks
	packwiz modrinth add turtlematic
