# shellcheck shell=bash

lane_config() {
  local lane="$1"

  PACK_DIR=""
  MC_TYPE=""
  MC_VERSION=""
  LOADER_VERSION=""
  MC_PORT=""
  MC_MEMORY=""
  JAVA_IMAGE_TAG=""

  case "$lane" in
    fabric-1.20)
      PACK_DIR="FabricCreative"
      MC_TYPE="FABRIC"
      MC_VERSION="1.20.1"
      LOADER_VERSION="0.17.2"
      MC_PORT="25570"
      MC_MEMORY="1536M"
      JAVA_IMAGE_TAG="java17"
      ;;
    forge-1.20)
      PACK_DIR="ForgeCreative"
      MC_TYPE="FORGE"
      MC_VERSION="1.20.1"
      LOADER_VERSION="47.4.10"
      MC_PORT="25571"
      MC_MEMORY="2G"
      JAVA_IMAGE_TAG="java17"
      ;;
    fabric-1.21)
      PACK_DIR="FabricCreative-1.21"
      MC_TYPE="FABRIC"
      MC_VERSION="1.21.1"
      LOADER_VERSION="0.19.3"
      MC_PORT="25572"
      MC_MEMORY="1536M"
      JAVA_IMAGE_TAG="java21"
      ;;
    neoforge-1.21)
      PACK_DIR="NeoForgeCreative-1.21"
      MC_TYPE="NEOFORGE"
      MC_VERSION="1.21.1"
      LOADER_VERSION="21.1.244"
      MC_PORT="25573"
      MC_MEMORY="2G"
      JAVA_IMAGE_TAG="java21"
      ;;
    minimal-fabric-1.20)
      PACK_DIR="FabricMinimal-1.20"
      MC_TYPE="FABRIC"
      MC_VERSION="1.20.1"
      LOADER_VERSION="0.17.2"
      MC_PORT="25574"
      MC_MEMORY="1536M"
      JAVA_IMAGE_TAG="java17"
      ;;
    minimal-forge-1.20)
      PACK_DIR="ForgeMinimal-1.20"
      MC_TYPE="FORGE"
      MC_VERSION="1.20.1"
      LOADER_VERSION="47.4.10"
      MC_PORT="25575"
      MC_MEMORY="2G"
      JAVA_IMAGE_TAG="java17"
      ;;
    minimal-fabric-1.21)
      PACK_DIR="FabricMinimal-1.21"
      MC_TYPE="FABRIC"
      MC_VERSION="1.21.1"
      LOADER_VERSION="0.19.3"
      MC_PORT="25576"
      MC_MEMORY="1536M"
      JAVA_IMAGE_TAG="java21"
      ;;
    minimal-neoforge-1.21)
      PACK_DIR="NeoForgeMinimal-1.21"
      MC_TYPE="NEOFORGE"
      MC_VERSION="1.21.1"
      LOADER_VERSION="21.1.244"
      MC_PORT="25577"
      MC_MEMORY="2G"
      JAVA_IMAGE_TAG="java21"
      ;;
    *)
      return 1
      ;;
  esac
}

all_lanes() {
  printf '%s\n' \
    fabric-1.20 forge-1.20 fabric-1.21 neoforge-1.21 \
    minimal-fabric-1.20 minimal-forge-1.20 minimal-fabric-1.21 minimal-neoforge-1.21
}
