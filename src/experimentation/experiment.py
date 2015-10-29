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

experiments = dict()


def process_arg(arg, tags):
    if isinstance(arg, types.LambdaType) or isinstance(arg, types.FunctionType):
        return str(arg(tags))
    else:
        return str(arg).format(**tags)


class ExperimentInserter(object):
    def __init__(self, name, tags=None):
        self.name = name
        if tags is None:
            tags = {}
        self.tags = tags

    def add_child(self, child):
        experiments[process_arg(self.name, self.tags)] = child
        child.tags = self.tags

    def get_root(self):
        return self


def add_experiment(x_name, structure, combinations=None):
    if combinations is not None:
        combis = product(*combinations.values())
        for combi in combis:
            tags = dict(zip(combinations.keys(), combi))
            structure(ExperimentInserter(x_name, tags), 0, 0, [])
    else:
        structure(ExperimentInserter(x_name), 0, 0, [])


def process_args(args, siblingno, childno, exptags):
    child_tags = {'siblingno': siblingno, 'childno': childno}
    child_tags.update(exptags)
    return map(lambda a: process_arg(a, child_tags), args)


def node(cls, nodeargs, *args):
    def node_constructor(parent, level, childno, max_siblings):
        arg_offset = 0
        if len(max_siblings) < level+1:
            max_siblings.append(0)

        siblingno = max_siblings[level]
        _args = process_args(nodeargs, siblingno, childno, parent.get_root().tags)
        _kwargs = {}
        if len(args) > 0 and isinstance(args[0], dict):
            nodekwargs = args[0]
            _kwargs = dict(zip(nodekwargs.keys(),
                process_args(nodekwargs.values(), siblingno, childno,
                parent.get_root().tags)))
            arg_offset += 1

        new_child = cls(*_args, **_kwargs)
        new_child.siblingno = siblingno
        new_child.childno = childno
        parent.add_child(new_child) 
        max_siblings[level] += 1

        if len(args) > arg_offset and isinstance(args[arg_offset], list):
            children = args[arg_offset]
            _childno = 0
            for i in xrange(len(children)):
                _childno = children[i](new_child, level+1, _childno, max_siblings)
        return childno + 1

    return node_constructor


def xnode(reps, cls, nodeargs, *args):
    def node_constructor(parent, level, childno, max_siblings):
        constructor = node(cls, nodeargs, *args)
        _reps = reps
        if isinstance(_reps, str):
            _reps = int(process_arg([_reps], parent.get_root().tags)) 
        for i in xrange(_reps):
            childno = constructor(parent, level, childno, max_siblings)
        return childno
    return node_constructor
