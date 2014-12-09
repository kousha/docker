#!/bin/bash

function hostname_hash() {
  hash=$(md5sum <<< "$1" | cut -b 1-6)
  echo $((0x${hash%% *}))
}

hostname="${1:-localhost}"
cd "${KAFKA_HOME}"

sed -i "s/#advertised.host.name.*/advertised.host.name=${hostname}/" "${KAFKA_HOME}/config/server.properties"

sed -i "s/broker.id=0/broker.id=$(hostname_hash ${hostname})/" "${KAFKA_HOME}/config/server.properties"

exec bin/kafka-server-start.sh config/server.properties
