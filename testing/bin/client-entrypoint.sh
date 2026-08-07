#!/usr/bin/env bash
set -Eeuo pipefail

HMC_VERSION="${HMC_VERSION:-2.10.0}"
HMC_JAR="/cache/headlessmc-launcher-wrapper-${HMC_VERSION}.jar"
PACKWIZ_BOOTSTRAP_VERSION="${PACKWIZ_BOOTSTRAP_VERSION:-0.0.3}"
PACKWIZ_INSTALLER="/cache/packwiz-installer-bootstrap-${PACKWIZ_BOOTSTRAP_VERSION}.jar"
GAME_DIR="/root/.minecraft"

mkdir -p "$GAME_DIR" /root/HeadlessMC /cache

# Share Mojang assets and loader libraries across lanes while keeping each
# lane's mods, configs, options and logs isolated.
for directory in assets libraries versions; do
  mkdir -p "/cache/minecraft/$directory"
  if [[ -d "$GAME_DIR/$directory" && ! -L "$GAME_DIR/$directory" ]]; then
    cp -a "$GAME_DIR/$directory/." "/cache/minecraft/$directory/"
    rm -rf "$GAME_DIR/$directory"
  fi
  ln -sfn "/cache/minecraft/$directory" "$GAME_DIR/$directory"
done

if [[ ! -s "$HMC_JAR" ]]; then
  curl -fsSL --retry 3 \
    "https://github.com/headlesshq/headlessmc/releases/download/${HMC_VERSION}/headlessmc-launcher-wrapper-${HMC_VERSION}.jar" \
    -o "${HMC_JAR}.tmp"
  mv "${HMC_JAR}.tmp" "$HMC_JAR"
fi

if [[ ! -s "$PACKWIZ_INSTALLER" ]]; then
  curl -fsSL --retry 3 \
    "https://github.com/packwiz/packwiz-installer-bootstrap/releases/download/v${PACKWIZ_BOOTSTRAP_VERSION}/packwiz-installer-bootstrap.jar" \
    -o "${PACKWIZ_INSTALLER}.tmp"
  mv "${PACKWIZ_INSTALLER}.tmp" "$PACKWIZ_INSTALLER"
fi

cd "$GAME_DIR"
java -jar "$PACKWIZ_INSTALLER" -g -s client "http://packwiz:8080/${PACK_DIR}/pack.toml"

case "$MC_TYPE" in
  FABRIC)
    install_command="fabric ${MC_VERSION} --uid ${LOADER_VERSION}"
    version="fabric-loader-${LOADER_VERSION}-${MC_VERSION}"
    ;;
  FORGE)
    install_command="forge ${MC_VERSION} --uid ${LOADER_VERSION}"
    version="${MC_VERSION}-forge-${LOADER_VERSION}"
    ;;
  NEOFORGE)
    install_command="neoforge ${MC_VERSION} --uid ${LOADER_VERSION}"
    version="neoforge-${LOADER_VERSION}"
    ;;
  *)
    printf 'Unsupported client loader: %s\n' "$MC_TYPE" >&2
    exit 2
    ;;
esac

cat >options.txt <<'EOF'
onboardAccessibility:false
pauseOnLostFocus:false
renderDistance:4
simulationDistance:4
maxFps:30
enableVsync:false
EOF

commands=$(printf '%s\nconfig --property hmc.assets.retry=5\nlaunch %s -offline -lwjgl --retries 3 --jvm "-Xms512M -Xmx%s -Djava.awt.headless=true" --game-args "--quickPlayMultiplayer minecraft:25565"\nquit\n' \
  "$install_command" "$version" "$CLIENT_MEMORY")
printf '%s' "$commands" | java -jar "$HMC_JAR"
