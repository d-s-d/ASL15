import re
import os
from urllib import quote_plus

from config import config
from remote_task import RemoteTask

POOL_REGEXP = re.compile("^(\*+)(\s+(.*))?\n$");

def get_script_path(script_name):
    return os.path.join(config['SCRIPT_DIR'], script_name)

class VM(object):
    def __init__(self, hostname="localhost"):
        self.hostname = hostname

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

    def __repr__(self):
        return "{0}@{1}".format(self.__class__.__name__, self.hostname)

def setup_jre_task(hostname):
    t = RemoteTask('setup jre and jar', hostname=hostname, once=True)
    t.copy_file(config['JAR_FILE'])
    t.run_sh_script(get_script_path(config['JRE_SETUP_SCRIPT']))
    return t
    

class Client_VM(VM):
    def __init__(self, hostname="localhost"):
        super(Client_VM, self).__init__(hostname)
        pass

    def setup(self):
        return setup_jre_task(self.hostname)

    def run(self):
        pass


class Middleware_VM(VM):
    def setup(self):
        return setup_jre_task(self.hostname)

    def __init__(self, hostname="localhost"):
        super(Middleware_VM, self).__init__(hostname)
        pass

class Database_VM(VM):
    def __init__(self, hostname="localhost"):
        super(Database_VM, self).__init__(hostname)

    def setup(self):
        t = RemoteTask('setup postgres', hostname=self.hostname, once=True)
        t.copy_file('../sql/schema.sql')
        t.run_sh_script(get_script_path(config['DB_SETUP_SCRIPT']),
            [config['DBNAME'], config['DBUSER'], config['DBPASS']])
        return t

    def reset(self):
        pass
        # self._run('sudo -u postgres psql -f schema.sql')

level_to_vm_type = [Database_VM, Middleware_VM, Client_VM]

def assign_vms(experiment, vm_pool):
    instantiated_vms = {}
    def assign_vms_rec(cur_node, level):
        cur_node.instance = vm_pool.get_next_vm(level)
        if hasattr(cur_node, 'children'):
            for child in cur_node.children:
                assign_vms_rec(child, level+1)
        
    assign_vms_rec(experiment, 0)


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
            self.hosts[level] = map(lambda h: level_to_vm_type[level](h), hosts)
        self.modulus = map(lambda l: len(l), self.hosts)
    
    def get_next_vm(self, level=0):
        cur_idx = self.vm_pointer[level]
        host = self.hosts[level][cur_idx]
        self.vm_pointer[level] = (cur_idx + 1) % self.modulus[level]
        return host

