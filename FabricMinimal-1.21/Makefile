ccTweakedVersion = 1.122.0
cloudsolutionsVersion = 0.4.1
turtlematicVersion = 1.5.2
peripheralWorksVersion = 1.10.1
digitalItemsVersion = 0.6.1

turtlematic:
	packwiz url add turtlematic https://github.com/SirEdvin/Turtlematic/releases/download/v1.21.1-${turtlematicVersion}/turtlematic-fabric-1.21.1-${turtlematicVersion}.jar

upw:
	packwiz url add unlimitedperipheralworks https://github.com/SirEdvin/UnlimitedPeripheralWorks/releases/download/v1.21.1-${peripheralWorksVersion}/peripheralworks-fabric-1.21.1-${peripheralWorksVersion}.jar

digitems:
	packwiz url add digitalitems https://github.com/SirEdvin/DigitalItems/releases/download/v1.21.1-${digitalItemsVersion}/digitalitems-fabric-1.21.1-${digitalItemsVersion}.jar

cloudsolutions:
	packwiz url add cloudsolutions https://github.com/SirEdvin/CloudSolutions/releases/download/v1.21.1-${cloudsolutionsVersion}/cloudsolutions-fabric-1.21.1-${cloudsolutionsVersion}.jar


update:
	packwiz update --all

all: turtlematic upw digitems cloudsolutions

# Exact release selected for this Minecraft/loader line.
cctweaked:
	packwiz modrinth add cc-tweaked --version-filename cc-tweaked-1.21.1-fabric-${ccTweakedVersion}.jar -y
