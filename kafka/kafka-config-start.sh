#!/bin/bash

function hostname_hash() {
  hash=$(md5sum <<< "$1" | cut -b 1-6)
  echo $((0x${hash%% *}))
}

hostname="${HOSTNAME:-localhost}"
server_properties="${KAFKA_HOME}/config/server.properties"
cd "${KAFKA_HOME}"

sed -i "s/#advertised.host.name.*/advertised.host.name=${hostname}/" "${server_properties}"

sed -i "s/broker.id=0/broker.id=$(hostname_hash ${hostname})/" "${server_properties}"

echo "auto.leader.rebalance.enable=true" >> "${server_properties}"

exec "$@"
