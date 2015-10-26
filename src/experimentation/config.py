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
config['JAR_FILE'] = 'ASL15.jar'
config['JAR_OUT_DIR'] = '../../'
config['LOCAL_JAR_FILE'] = config['JAR_OUT_DIR'] + config['JAR_FILE']

config['JAVA_LIBS'] = ['log4j-core-2.4.1.jar', 'log4j-api-2.4.1.jar', 'postgresql-9.4-1204.jdbc4.jar']
config['JAVA_CP'] = '"{0}:{1}"'.format(config['JAR_FILE'], ':'.join(map(
    lambda x: 'lib/' + x, config['JAVA_LIBS'])))
config['JAVA_CLIENT_COMMAND'] = 'java -cp ' + config['JAVA_CP'] + ' ch.ethz.inf.stefand.ClientMain'
config['JAVA_MW_COMMAND'] = 'java -cp "' + config['JAVA_CP'] + ':." ch.ethz.inf.stefand.MiddlewareMain'

config['CLIENT_LOG_REGEX'] = '/tmp/ASLClient*.log'
config['MW_LOG_REGEX'] = '/tmp/ASLMW*.log'

config['CLIENT_LOG4J2_XML'] = '../../res/log4j2-client.xml'
config['CLIENT_LOG_CONFIG_SCRIPT'] = 'client_config_log.sh'

