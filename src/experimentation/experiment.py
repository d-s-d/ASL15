import re
import os
import sys
import inspect
from remote_task import RemoteTask
from config import config

EXP_DEF_REGEXP = re.compile("^[a-zA-Z_][a-zA-Z0-9_]*:\n")
NOD_DEF_REGEXP = re.compile(
    "^(\*+)\s*([1-9][0-9]*)?\s*([a-zA-Z_][0-9a-zA-Z_-]*) ?(.*)\n")

def get_script_path(script_name):
    return os.path.join(config['SCRIPT_DIR'], script_name)


def setup_jre_task(hostname):
    t = RemoteTask('setup jre and jar', hostname=hostname, once=True)
    t.copy_file(config['JAR_FILE'])
    t.run_sh_script(get_script_path(config['JRE_SETUP_SCRIPT']))
    return t


class ExperimentNode(object):
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.args = args
        self.instance = None
        self.children = []

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

    def add_child(self, child):
        self.children.append(child)

    def assign_vm(self, vm_pool):
        self.instance = vm_pool.get_vm(self.__class__.VM_TYPE)

    def __repr__(self):
        return "{cls}:{host}:{name} ({cs})".format(cls=self.__class__.__name__,
            host=self._hostname(), name=self.name, cs='\n  '.join(map(repr, (self.children))) )

class ClientNode(ExperimentNode):
    VM_TYPE='client'
    def __init__(self, name, client_type, *args, **kwargs):
        super(ClientNode, self).__init__(name, client_type, *args, **kwargs) 
        self.client_type = client_type

    def run(self):
        t = RemoteTask('run client', self._hostname())
        t.command(config['JAVA_CLIENT_COMMAND'],
            [self.client_type, self.name, self.parent._hostname(), config['MWPORT']] + self.args)
        return t


class MiddlewareNode(ExperimentNode):
    VM_TYPE='middleware'
    def setup(self):
        return setup_jre_task(self._hostname())

    def run(self):
        t = RemoteTask('run middleware', self._hostname())
        t.command(config['JAVA_MW_COMMAND'],
            [self.name, self.parent._hostname(), config['DBNAME'],
            config['DBUSER'], config['DBPASS'], config['MWPORT']])
        return t
   
    def terminate(self):
        t = RemoteTask('stop middleware', self._hostname(), once=True)
        t.command('killall java')
        return t


class DatabaseNode(ExperimentNode):
    VM_TYPE='database'
    def setup(self):
        t = RemoteTask('setup postgres', hostname=self._hostname(), once=True)
        t.copy_file('../sql/schema.sql')
        t.run_sh_script(get_script_path(config['DB_SETUP_SCRIPT']),
            [config['DBNAME'], config['DBUSER'], config['DBPASS']])
        return t

experiments = dict()

class ExperimentFile(object):
    def __init__(self, name):
        self.name = name

    def add_child(self, child):
        experiments[self.name] = child

def add_experiment(x_name, structure, combinations=None):
    structure(ExperimentFile(x_name), 0, 0, [])

def node(cls, nodeargs, *args):
    def node_constructor(parent, level, childno, max_siblings):
        if len(max_siblings) < level+1:
            max_siblings.append(0)
        child_tags = {'siblingno': max_siblings[level], 'childno': childno}
        _args = map(lambda a: a.format(**child_tags), nodeargs)
        new_child = cls(*_args)
        parent.add_child(new_child) 

        max_siblings[level] += 1

        if len(args) > 0:
            children = args[0]
            _childno = 0
            for i in xrange(len(children)):
                _childno = children[i](new_child, level+1, _childno, max_siblings)
        return childno + 1

    return node_constructor

def xnode(reps, cls, nodeargs, *args):
    def node_constructor(parent, level, childno, max_siblings):
        constructor = node(cls, nodeargs, *args)
        for i in xrange(reps):
            childno = constructor(parent, level, childno, max_siblings)
        return childno
    return node_constructor
