cloudsolutionsVersion = 0.1.2
turtlematicVersion = 1.4.0
peripheralWorksVersion = 1.5.0
digitalItemsVersion = 0.4.0

turtlematic:
	packwiz url add turtlematic https://github.com/SirEdvin/Turtlematic/releases/download/v1.20.1-${turtlematicVersion}/turtlematic-forge-1.20.1-${turtlematicVersion}.jar

upw:
	packwiz url add unlimitedperipheralworks https://github.com/SirEdvin/UnlimitedPeripheralWorks/releases/download/v1.20.1-${peripheralWorksVersion}/peripheralworks-forge-1.20.1-${peripheralWorksVersion}.jar
digitems:
	packwiz url add digitalitems https://github.com/SirEdvin/DigitalItems/releases/download/v1.20.1-${digitalItemsVersion}/digitalitems-forge-1.20.1-${digitalItemsVersion}.jar
cloudsolutions:
	packwiz url add cloudsolutions https://github.com/SirEdvin/CloudSolutions/releases/download/v1.20.1-${cloudsolutionsVersion}/cloudsolutions-forge-1.20.1-${cloudsolutionsVersion}.jar

all: turtlematic upw digitems cloudsolutions

update:
	packwiz update --all

modrinth:
	packwiz modrinth add peripheralium
	packwiz modrinth add unlimitedperipheralworks
	packwiz modrinth add turtlematic
