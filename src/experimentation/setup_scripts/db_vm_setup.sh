#!/bin/sh -e

. ./db_config.sh

# Setup PostgreSQL
sudo apt-get -qq update
sudo apt-get -qq -y upgrade
sudo apt-get -qq -y install "postgresql-$PG_VERSION" "postgresql-contrib-$PG_VERSION"

sudo cp postgresql.conf $PG_CONF

# Edit postgresql.conf to change listen address to '*'.
#sudo sh -c "sed -i \"s/#listen_addresses = 'localhost'/listen_addresses = '*'/\" \"$PG_CONF\""
#sudo sh -c "sed -i \"s/#default_transaction_isolation = 'read committed'/default_transaction_isolation = 'repeatable read'/\" \"$PG_CONF\""

# Append to pg_hba.conf to add password auth.
sudo sh -c "echo \"host    all             all             all       md5\" >> \"$PG_HBA\""

# restart pgsql
sudo service postgresql restart

. ./reset_db.sh

sudo /sbin/sysctl -w net.ipv4.tcp_tw_reuse=1
