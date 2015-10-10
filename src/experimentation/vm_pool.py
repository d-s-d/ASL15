from fabric.api import run
from fabric.statis import env

env.use_ssh_config = True

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

  def __init__(self):
    pass

class Client_VM(VM):
  
  def __init__(self):
    pass

class Middleware_VM(VM):
  def __init__(self):
    pass

class Database_VM(object):
  def __init__(self):
    pass

class VM_Pool():
  def __init__(self, f=None)
    pass
