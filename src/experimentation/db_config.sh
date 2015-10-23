DBNAME=$1
DBUSER=$2
DBPASS=$3
PG_VERSION=9.3
PG_ETC=/etc/postgresql/$PG_VERSION/main/
PG_CONF="$PG_ETC/postgresql.conf"
PG_HBA="$PG_ETC/pg_hba.conf"

echo "`date`: executed with arguments $DBNAME $DBUSER $DBPASS" >> db_setup.log
export DEBIAN_FRONTEND=noninteractive
