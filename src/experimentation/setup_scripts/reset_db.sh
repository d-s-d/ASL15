. ./db_config.sh

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
sudo -u postgres PGPASSWORD="$DBPASS" psql -h localhost $DBNAME $DBUSER -f schema.sql
