FROM debian:wheezy
MAINTAINER Kousha Najafi <kousha@lazyhack.com>

RUN apt-get update && apt-get install -y curl openjdk-7-jre-headless


RUN curl --silent -o /etc/apt/sources.list.d/stackdriver.list https://repo.stackdriver.com/wheezy.list
RUN curl --silent https://app.stackdriver.com/RPM-GPG-KEY-stackdriver | apt-key add -

RUN apt-get update && apt-get install -y stackdriver-agent

COPY start-wait-stackdriver-agent.sh /opt/stackdriver/start-wait-stackdriver-agent.sh

RUN mkdir -p /mnt/jmxtrans/conf /mnt/jmxtrans/log
RUN curl --silent -o /mnt/jmxtrans/jmxtrans-all.jar https://s3.amazonaws.com/stackrpms/jmxtrans/jmxtrans-all.jar

COPY *.json /mnt/jmxtrans/conf/
COPY *.conf /opt/stackdriver/collectd/etc/collectd.d/

CMD [ "/opt/stackdriver/start-wait-stackdriver-agent.sh" ]
