import re

from fabric.api import run, put
from fabric.state import env

from config import config

env.use_ssh_config = True


POOL_REGEXP = re.compile("(\*+)(\s+(.*))?\n");

def once_per_instance(f):
    def wrapper(self, *args, **kwargs):
        ret = None
        if not hasattr(self, '__has_run'):
            self.__has_run = set()
        if f not in self.__has_run:
            ret = f(self, *args, **kwargs)
            self.__has_run.add(f)
        return ret
    return wrapper


class VM(object):
    def _put(self, *args, **kwargs):
        env.host_string = self.hostname
        put(*args, **kwargs)

    def _run(self, *args, **kwargs):
        env.host_string = self.hostname
        run(*args, **kwargs)
        
    def setup():
        pass
    
    def reset():
        pass

    def run():
        pass

    def collectlogs():
        pass

    def shutdown():
        pass

    def __init__(self, hostname="localhost"):
        self.hostname = hostname

    def __repr__(self):
        return "{0}@{1}".format(self.__class__.__name__, self.hostname)


class Client_VM(VM):
    def __init__(self, hostname="localhost"):
        super(Client_VM, self).__init__(hostname)
        pass


class Middleware_VM(VM):
    @once_per_instance
    def setup(self):
        self._put('setup_scripts/mw_vm_setup.sh', 'mw_vm_setup.sh')
        self._run('sh mw_vm_setup.sh')

    def __init__(self, hostname="localhost"):
        super(Middleware_VM, self).__init__(hostname)
        pass


class Database_VM(VM):
    def __init__(self, hostname="localhost"):
        super(Database_VM, self).__init__(hostname)

    @once_per_instance
    def setup(self):
        self._put('../sql/schema.sql', 'schema.sql')
        self._put('setup_scripts/db_vm_setup.sh', 'db_vm_setup.sh')
        self._run('sh db_vm_setup.sh {DBNAME} {DBUSER} {DBPASS}'.format(**config))

    @once_per_instance
    def run(self):
        pass # nothing to do here

    @once_per_instance
    def reset(self):
        self._run('sudo -u postgres psql -f schema.sql')


level_to_vm_type = [Database_VM, Middleware_VM, Client_VM]

def assign_hosts(experiment, vm_pool):
    def assign_hosts_rec(cur_node, level):
        cur_node.instance = level_to_vm_type[level](vm_pool.get_next_vm(level))
        if hasattr(cur_node, 'children'):
            for child in cur_node.children:
                assign_hosts_rec(child, level+1)
        
    assign_hosts_rec(experiment, 0)

class VM_Pool(object):
    def __init__(self, f=None):
        ms = filter(lambda m: m is not None, map(lambda l: POOL_REGEXP.match(l), f))
        self.hosts = [None, None, None]
        self.vm_pointer = [0,0,0]

        for m in ms:
            level = len(m.groups()[0])-1
            hosts_string = m.groups()[2]
            if hosts_string is not None:
                hosts = hosts_string.split()
            else:
                hosts = ['localhost']
            self.hosts[level] = hosts
        self.modulus = map(lambda l: len(l), self.hosts)
    
    def get_next_vm(self, level=0):
        cur_idx = self.vm_pointer[level]
        host = self.hosts[level][cur_idx]
        self.vm_pointer[level] = (cur_idx + 1) % self.modulus[level]
        return host

