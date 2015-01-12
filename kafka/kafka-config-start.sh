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

if ! grep -q "auto.leader.rebalance.enable=true" "${server_properties}"; then
  echo "auto.leader.rebalance.enable=true" >> "${server_properties}"
fi

if ! grep -q "delete.topic.enable=true" "${server_properties}"; then
  echo "delete.topic.enable=true" >> "${server_properties}"
fi

if ! [[ -z "${ZOOKEEPERS}" ]] ; then
  sed -i "s/zookeeper.connect=zookeeper:2181/zookeeper.connect=${ZOOKEEPERS}/" "${server_properties}"
fi

exec "$@"
