FROM debian:stable
MAINTAINER Kousha Najafi <kousha@lazyhack.com>

ENV SCALA_VERSION 2.10
ENV KAFKA_VERSION 0.8.2.1

RUN apt-get update && apt-get install -y openjdk-7-jre-headless wget

RUN wget -q -O - http://mirrors.ibiblio.org/apache/kafka/$KAFKA_VERSION/kafka_$SCALA_VERSION-$KAFKA_VERSION.tgz | tar -xzf - -C /opt

ENV JAVA_HOME /usr/lib/jvm/java-7-openjdk-amd64
ENV KAFKA_HOME /opt/kafka_$SCALA_VERSION-$KAFKA_VERSION

WORKDIR $KAFKA_HOME

COPY kafka-config-start.sh $KAFKA_HOME/bin/

RUN sed -i 's/zookeeper.connect=localhost:2181/zookeeper.connect=zookeeper:2181/' $KAFKA_HOME/config/server.properties

VOLUME /tmp/kafka-logs

EXPOSE 9092

ENV JMX_PORT 9090
EXPOSE $JMX_PORT

ENTRYPOINT [ "bin/kafka-config-start.sh" ]
CMD [ "bin/kafka-server-start.sh", "config/server.properties" ]
