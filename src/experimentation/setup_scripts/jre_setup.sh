#!/bin/sh -e

export DEBIAN_FRONTEND=noninteractive

sudo apt-get -qq update
sudo apt-get -q upgrade -y
sudo apt-get -q install -y openjdk-7-jre-headless
sudo apt-get -q install -y fastjar

LOG4J_CORE_JAR=log4j-core-2.4.1.jar
JDBC_PSQL_JAR=postgresql-9.4-1204.jdbc4.jar

mkdir lib
cd lib
if ! [ -e $LOG4J_CORE_JAR ]; then
    LOG4J_FILE=apache-log4j-2.4.1-bin.tar.gz
    wget http://www.us.apache.org/dist/logging/log4j/2.4.1/$LOG4J_FILE
    tar zxvf $LOG4J_FILE
    cp apache-log4j-2.4.1-bin/log4j-core-2.4.1.jar .
    cp apache-log4j-2.4.1-bin/log4j-api-2.4.1.jar .
fi

if ! [ -e $JDBC_PSQL_JAR ]; then
    wget https://jdbc.postgresql.org/download/$JDBC_PSQL_JAR
fi

cd 

fastjar xf ASL15.jar
