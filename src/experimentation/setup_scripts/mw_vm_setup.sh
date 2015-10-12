#!/bin/sh -e

export DEBIAN_FRONTEND=noninteractive

sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y openjdk-7-jre-headless
sudo apt-get install -y ant
