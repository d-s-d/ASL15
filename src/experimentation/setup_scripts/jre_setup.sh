#!/bin/sh -e

export DEBIAN_FRONTEND=noninteractive

sudo apt-get -qq update
sudo apt-get -q upgrade -y
sudo apt-get -q install -y openjdk-7-jre-headless
sudo apt-get -q install -y ant
