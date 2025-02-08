peripheraliumVersion = 0.7.0
cloudsolutionsVersion = 0.1.0
turtlematicVersion = 1.3.1
peripheralWorksVersion = 1.4.5
digitalItemsVersion = 0.3.0


peripheralium:
	packwiz url add peripheralium https://github.com/SirEdvin/Peripheralium/releases/download/v1.20.1-${peripheraliumVersion}/peripheralium-fabric-1.20.1-${peripheraliumVersion}.jar

turtlematic:
	packwiz url add turtlematic https://github.com/SirEdvin/Turtlematic/releases/download/v1.20.1-${turtlematicVersion}/turtlematic-fabric-1.20.1-${turtlematicVersion}.jar

upw:
	packwiz url add unlimitedperipheralworks https://github.com/SirEdvin/UnlimitedPeripheralWorks/releases/download/v1.20.1-${peripheralWorksVersion}/peripheralworks-fabric-1.20.1-${peripheralWorksVersion}.jar
digitems:
	packwiz url add digitalitems https://github.com/SirEdvin/DigitalItems/releases/download/v1.20.1-${digitalItemsVersion}/digitalitems-fabric-1.20.1-${digitalItemsVersion}.jar
cloudsolutions:
	packwiz url add cloudsolutions https://github.com/SirEdvin/CloudSolutions/releases/download/v1.20.1-${cloudsolutionsVersion}/cloudsolutions-fabric-1.20.1-${cloudsolutionsVersion}.jar

update:
	packwiz update --all

all: peripheralium turtlematic upw digitems cloudsolutions

modrinth:
	packwiz modrinth add peripheralium
	packwiz modrinth add unlimitedperipheralworks
	packwiz modrinth add turtlematic
