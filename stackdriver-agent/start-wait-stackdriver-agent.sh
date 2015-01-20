#!/bin/bash

PID_FILE=/var/run/stackdriver-agent.pid

if [ -z ${STACKDRIVER_API_KEY} ]; then
  echo "Need to specify STACKDRIVER_API_KEY as an environment variable."
  exit 1
else
  /opt/stackdriver/stack-config --api-key "${STACKDRIVER_API_KEY}"
  for file in /mnt/jmxtrans/conf/*; do
    sed -i -e "s/STACKDRIVER_API_KEY/${STACKDRIVER_API_KEY}/" "${file}"
  done
fi

#while [ -e "${PID_FILE}" ] ; do
#  sleep 1;
#done
echo "Starting jmxtrans."
java -Djmxtrans.log.dir='/mnt/jmxtrans/log' -jar /mnt/jmxtrans/jmxtrans-all.jar -j /mnt/jmxtrans/conf/
