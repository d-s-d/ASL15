#!/bin/sh -e

DBNAME=$1
DBUSER=$2
DBPASS=$3
PG_VERSION=9.3
PG_ETC=/etc/postgresql/$PG_VERSION/main/

echo "`date`: ecuted with arguments $DBNAME $DBUSER $DBPASS" >> db_setup.log
export DEBIAN_FRONTEND=noninteractive

# Setup PostgreSQL
sudo apt-get -qq update
sudo apt-get -q -y upgrade
sudo apt-get -q -y install "postgresql-$PG_VERSION" "postgresql-contrib-$PG_VERSION"

PG_CONF="$PG_ETC/postgresql.conf"
PG_HBA="$PG_ETC/pg_hba.conf"

# Edit postgresql.conf to change listen address to '*'.
sudo sh -c "sed -i \"s/#listen_addresses = 'localhost'/listen_addresses = '*'/\" \"$PG_CONF\""
sudo sh -c "sed -i \"s/#default_transaction_isolation = 'read committed'/default_transaction_isolation = 'serializable'/\" \"$PG_CONF\""

# Append to pg_hba.conf to add password auth.
sudo sh -c "echo \"host    all             all             all       md5\" >> \"$PG_HBA\""

# restart pgsql
sudo service postgresql restart

cat << EOF | sudo -u postgres psql
-- drop database
DROP DATABASE IF EXISTS $DBNAME;
-- drop user
DROP USER IF EXISTS $DBUSER;
-- register db user
CREATE USER $DBUSER WITH PASSWORD '$DBPASS';
-- create database
CREATE DATABASE $DBNAME WITH OWNER $DBUSER;
EOF

# load schema
sudo -u postgres psql -f schema.sql
