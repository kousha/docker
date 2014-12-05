FROM debian:stable
MAINTAINER Kousha Najafi <kousha@lazyhack.com>

ENV SCALA_VERSION 2.10
ENV KAFKA_VERSION 0.8.2-beta
RUN apt-get update && apt-get install -y openjdk-7-jre-headless wget
RUN wget -q -O - http://apache.mirrors.lucidnetworks.net/kafka/$KAFKA_VERSION/kafka_$SCALA_VERSION-$KAFKA_VERSION.tgz | tar -xzf - -C /opt

ENV JAVA_HOME /usr/lib/jvm/java-7-openjdk-amd64
ENV KAFKA_HOME /opt/kafka_$SCALA_VERSION-$KAFKA_VERSION

WORKDIR $KAFKA_HOME

VOLUME /tmp/kafka-logs
VOLUME $KAFKA_HOME

EXPOSE 9092

ENTRYPOINT ["bin/kafka-server-start.sh"]
CMD ["config/server.properties"]
