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
    def __init__(self, *args, **kwargs):
        assert isinstance(kwargs['tags'], dict)
        assert 'instance' in kwargs
        self.tags = kwargs['tags']
        self.args = args
        self.instance = kwargs['instance']
        self.children = []

    def _hostname(self):
        return self.instance.public_dns_name

    def collect_command(self, command):
        def collect_rec(collections, level, node):
            collections.append([])
            if hasattr(node, command):
                task = getattr(node, command)()
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

    def __repr__(self):
        return "{cls}:{host} ({args})".format(cls=self.__class__.__name__,
            host=self._hostname(), args=repr(self.args))

class ClientNode(ExperimentNode):
    VM_TYPE='client'
    def __init__(self, client_type, client_name, *args, **kwargs):
        super(ClientNode, self).__init__(*args, **kwargs) 
        self.client_type = client_type
        self.client_name = client_name

    def run(self):
        t = RemoteTask('run client', self._hostname())
        t.command(config['JAVA_CLIENT_COMMAND'],
            [self.client_type, self.name, self.parent._hostname(), config['MWPORT']] + self.args)
        return t


class MiddlewareNode(ExperimentNode):
    VM_TYPE='middleware'
    def __init__(self, name, *args, **kwargs):
        super(MiddlewareNode, self).__init__(*args, **kwargs)
        self.name = name

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
    def __init__(self, name, *args, **kwargs):
        super(DatabaseNode, self).__init__(*args, **kwargs)
        self.name = name

    def setup(self):
        t = RemoteTask('setup postgres', hostname=self._hostname(), once=True)
        t.copy_file('../sql/schema.sql')
        t.run_sh_script(get_script_path(config['DB_SETUP_SCRIPT']),
            [config['DBNAME'], config['DBUSER'], config['DBPASS']])
        return t

    def reset(self):
        self.instance.reset()

NODE_CLASSES = dict(filter(lambda cls: cls[0].endswith('Node'),
    inspect.getmembers(sys.modules[__name__], inspect.isclass)))

class ExperimentFile(object):
    def __init__(self, f, instance_pool):
        path = dict()
        self.children = dict()
        path[0] = self
        line_count = 0
        for line in f:
            line_count += 1
            m = NOD_DEF_REGEXP.match(line)
            if m is None:
                continue
            (_depth, repetitions, cls_name, arg_string) = m.groups()
            if repetitions is None:
                repetitions = 1
            _depth = len(_depth)
            for i in xrange(int(repetitions)):
                try:
                    cousinno = path[_depth].tags['cousinno']
                except KeyError:
                    cousinno = 0
                siblingno = len(path[_depth-1].children)
                child_tags = {'siblingno': siblingno, 'cousinno': cousinno}
                args = arg_string.format(**child_tags).split()
                cls = NODE_CLASSES[cls_name+'Node']
                new_child = cls(*args, tags=child_tags,
                    instance=instance_pool.get_vm(cls.VM_TYPE, cousinno))
                path[_depth-1].add_child(new_child)
                new_child.parent = path[_depth-1]
                path[_depth] = new_child

    def add_child(self, new_child):
        self.children[new_child.name] = new_child

