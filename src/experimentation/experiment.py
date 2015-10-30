import re
import os
import sys
import types
import inspect
from itertools import product
from remote_task import RemoteTask
from config import config

EXP_DEF_REGEXP = re.compile("^[a-zA-Z_][a-zA-Z0-9_]*:\n")
NOD_DEF_REGEXP = re.compile(
    "^(\*+)\s*([1-9][0-9]*)?\s*([a-zA-Z_][0-9a-zA-Z_-]*) ?(.*)\n")

def get_script_path(script_name):
    return os.path.join(config['SCRIPT_DIR'], script_name)


def setup_jre_task(hostname):
    t = RemoteTask('setup jre and jar', hostname=hostname, once=True)
    t.run_sh_script(get_script_path(config['JRE_SETUP_SCRIPT']))
    return t


def deploy_task(hostname):
    t = RemoteTask('deploy', hostname=hostname, once=True)
    t.copy_file(config['LOCAL_JAR_FILE'])
    return t


class ExperimentNode(object):
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.args = args
        self.instance = None
        self.children = []
        self.parent = None

    def _hostname(self):
        return self.instance.public_dns_name

    def collect_command(self, command, *args, **kwargs):
        def collect_rec(collections, level, node):
            collections.append([])
            if hasattr(node, command):
                task = getattr(node, command)(*args, **kwargs)
                if task is not None:
                    collections[level].append(task)
            if hasattr(node, 'children'):
                for c in node.children:
                    collect_rec(collections, level+1, c)
        collections = []
        collect_rec(collections, 0, self)
        return collections

    def get_root(self):
        node = self
        while node.parent is not None:
            node = self.parent
        return node

    def add_child(self, child):
        self.children.append(child)
        child.parent = self

    def assign_vm(self, vm_pool):
        self.instance = vm_pool.get_vm(self.__class__.VM_TYPE,
            self.siblingno)

    def __repr__(self):
        return "{cls}:{host}:{name} ({cs})".format(cls=self.__class__.__name__,
            host=self._hostname(), name=self.name, cs='\n  '.join(map(repr, (self.children))) )


class ClientNode(ExperimentNode):
    VM_TYPE='client'
    def __init__(self, name, client_type, *args, **kwargs):
        super(ClientNode, self).__init__(name, client_type, *args, **kwargs) 
        self.client_type = client_type
        self.args = args

    def setup(self):
        return setup_jre_task(self._hostname())

    def run(self):
        t = RemoteTask('run client', self._hostname())
        t.run_sh_script(get_script_path(config['CLIENT_LOG_CONFIG_SCRIPT']),
            [self.name])
        t.command(config['JAVA_CLIENT_COMMAND'],
            [self.client_type, self.name, self.parent._hostname(), config['MWPORT']] + list(self.args))
        return t

    def deploy(self):
        t = deploy_task(self._hostname())
        t.copy_file(config['CLIENT_LOG4J2_XML'])
        return t

    def collect_logs(self, target_dir):
        host_target_dir = os.path.join(target_dir, self._hostname())
        try:
            os.makedirs(host_target_dir)
        except OSError as e:
            if e.errno != 17:
                print e
        t = RemoteTask('collect middleware log', self._hostname(), once=True)
        t.command('gzip', [config['CLIENT_LOG_REGEX']])
        t.download_file(config['CLIENT_LOG_REGEX']+'.gz', host_target_dir)
        return t

    def cleanup(self):
        t = RemoteTask('cleanup client', self._hostname(), once=True)
        t.command('rm -rf', ['{0}*'.format(config['CLIENT_LOG_REGEX'])])
        t.command('rm -rf', ['log4j2*.xml'])
        return t

    def reset(self):
        return self.cleanup()


class DelayedClientNode(ClientNode):
    VM_TYPE='client'

    def __init__(self, *args, **kwargs):
        super(DelayedClientNode, self).__init__(*args, **kwargs)
        assert 'delay' in kwargs
        self.delay = kwargs['delay']

    def run(self):
        task = super(DelayedClientNode, self).run()
        task.prepend_command("sleep", [self.delay]) # ;-)
        return task

    def __repr__(self):
        return super(DelayedClientNode, self).__repr__() + " delayed by: " + str(self.delay)


class MiddlewareNode(ExperimentNode):
    VM_TYPE='middleware'
    def setup(self):
        return setup_jre_task(self._hostname())

    def run(self):
        t = RemoteTask('run middleware', self._hostname(), once=True)
        t.command(config['JAVA_MW_COMMAND'],
            [self.name, self.parent._hostname(), config['DBNAME'],
            config['DBUSER'], config['DBPASS'], config['MWPORT']])
        return t

    def deploy(self):
        return deploy_task(self._hostname())

    def terminate(self):
        t = RemoteTask('stop middleware', self._hostname(), once=True)
        t.command('killall java')
        return t

    def collect_logs(self, target_dir):
        host_target_dir = os.path.join(target_dir, self._hostname())
        try:
            os.makedirs(host_target_dir)
        except OSError as e:
            if e.errno != 17:
                print e
        t = RemoteTask('collect middleware log', self._hostname(), once=True)
        t.command('gzip', [config['MW_LOG_REGEX']])
        t.download_file(config['MW_LOG_REGEX']+'.gz', host_target_dir)
        return t

    def cleanup(self):
        t = RemoteTask('cleanup middleware', self._hostname(), once=True)
        t.command('rm -rf', ['{0}*'.format(config['MW_LOG_REGEX'])])
        return t

    def reset(self):
        return self.cleanup()

class DatabaseNode(ExperimentNode):
    VM_TYPE='database'
    def setup(self):
        t = RemoteTask('setup postgres', hostname=self._hostname(), once=True)
        t.copy_file('../sql/schema.sql')
        t.copy_file('setup_scripts/postgresql.conf')
        t.copy_file('setup_scripts/db_config.sh')
        t.copy_file('setup_scripts/reset_db.sh')
        t.run_sh_script(get_script_path(config['DB_SETUP_SCRIPT']),
            [config['DBNAME'], config['DBUSER'], config['DBPASS']])
        return t

    def reset(self):
        t = RemoteTask('reset postgres', hostname=self._hostname())
        t.run_sh_script(get_script_path('reset_db.sh'),
            [config['DBNAME'], config['DBUSER'], config['DBPASS']])
        return t

experiments = list()
    
def gen_experiment(name, middleware_nodes, clients, tags=None):
    assert not callable(middleware_nodes) or isinstance(tags, dict)
    assert not callable(clients) or isinstance(tags, dict)
    
    if callable(middleware_nodes):
        middleware_nodes = middleware_nodes(tags)
    if callable(clients):
        clients = clients(tags)

    # create middleware and client nodes
    mw_nodes = map(lambda args: MiddlewareNode(*args), middleware_nodes)
    client_nodes = map(lambda args: DelayedClientNode(*args[1:], delay=args[0]),
        clients)

    # assign sibling numbers
    for nodes in [mw_nodes, client_nodes]:
        for node in zip(nodes, xrange(len(nodes))):
            node[0].siblingno = node[1]
    
    # add clients to middlewares in round robin fashion
    mw_count = len(mw_nodes)
    for cli_i in xrange(len(client_nodes)):
        mw_nodes[cli_i % mw_count].add_child(client_nodes[cli_i])

    db_node = DatabaseNode('db')
    db_node.siblingno = 0

    # add all middlewares to the database node
    for mw_node in mw_nodes:
        db_node.add_child(mw_node)

    # add the experiment
    experiments.append((name, tags, db_node))


def new_experiment(name, middleware_nodes, clients, parameters=None):
    assert middleware_nodes is not None
    assert clients is not None

    if parameters is not None:
        combis = product(*parameters.values())
        for combi in combis:
            tags = dict(zip(parameters.keys(), combi))
            gen_experiment(name, middleware_nodes, clients, tags)
    else:
        gen_experiment(name, middleware_nodes, clients)


def prod_cons_pair(delay, duration, queue_name):
    return [(delay, 'p_{0}'.format(queue_name), 'OneQueueProducerClient', queue_name, duration),
        (delay, 'c_{0}'.format(queue_name), 'OneQueueConsumerClient', queue_name, duration*2)]

