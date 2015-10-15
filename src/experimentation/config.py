import config_local

config = dict()

# DB configuration
config['DBNAME'] = 'asl15'
config['DBUSER'] = 'asl15_mw'
config['DBPASS'] = config_local.config['DBPASS']

config['VM_TYPES'] = ['database', 'middleware', 'client']

config['MWPORT'] = '9999'
config['SCRIPT_DIR'] = 'setup_scripts'
config['JRE_SETUP_SCRIPT'] = 'jre_setup.sh'
config['DB_SETUP_SCRIPT'] = 'db_vm_setup.sh'
config['JAR_FILE'] = '../../ASL15.jar'

config['JAVA_LIBS'] = 'lib/log4j-core-2.4.1.jar:lib/log4j-api-2.4.1.jar:lib/postgresql-9.4-1204.jdbc4.jar'
config['JAVA_CLIENT_COMMAND'] = 'java -cp "' + config['JAVA_LIBS'] + ':." ch.ethz.inf.stefand.ClientMain'
config['JAVA_MW_COMMAND'] = 'java -cp "' + config['JAVA_LIBS'] + ':." ch.ethz.inf.stefand.MiddlewareMain'
