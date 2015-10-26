#!/usr/bin/sh -e

CLIENT_NAME=$1

sed "s/%clientname/$CLIENT_NAME/" log4j2-client.xml > "log4j2-"$CLIENT_NAME".xml"
