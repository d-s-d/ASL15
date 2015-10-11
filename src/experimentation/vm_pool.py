import re

from fabric.api import run
from fabric.state import env

env.use_ssh_config = True

POOL_REGEXP = re.compile("(\*+)(\s+(.*))?\n");

class VM(object):
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
  def __init__(self, hostname="localhost"):
    super(Middleware_VM, self).__init__(hostname)
    pass


class Database_VM(VM):
  def __init__(self, hostname="localhost"):
    super(Database_VM, self).__init__(hostname)
    pass


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

