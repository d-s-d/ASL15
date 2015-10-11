import re

EXP_DEF_REGEXP = re.compile("(\*+)\s*([1-9][0-9]*)?\s*([a-zA-Z_][0-9a-zA-Z_-]*) ?(.*)\n")

class Client(object):
  def __init__(self, client_type, arg_str):
    self.client_type = client_type
    self.arg_str = arg_str

  def __repr__(self):
    hostname = ""
    if hasattr(self, 'instance'):
      hostname = self.instance.hostname
    return "ClientType ({2}) {0} with Arguments: {1} ".format(self.client_type, self.arg_str, hostname)

class Middleware(object):
  def __init__(self, identifier):
    self.identifier = identifier
    self.children = []
  
  def __repr__(self):
    hostname = ""
    if hasattr(self, 'instance'):
      hostname = self.instance.hostname
    return "Middleware: ({2}) {0} \n  {1} ".format(
      self.identifier, '\n  '.join(map(lambda c: c.__repr__(), self.children)), hostname)

class Experiment(object):
  def __init__(self, identifier):
    self.identifier = identifier
    self.children = []

  def __repr__(self):
    hostname = ""
    if hasattr(self, 'instance'):
      hostname = self.instance.hostname
    return "Experiment: ({2}) {0} \n {1} ".format(
      self.identifier, '\n '.join(map(lambda c: c.__repr__(), self.children)), hostname)

  def run():
    pass

  @staticmethod
  def parse_experiments_file(f):
    cur_exp = None
    cur_mw = None
    experiments = {}
    line_count = 0
    for line in f:
      line_count += 1
      m = EXP_DEF_REGEXP.match(line)
      if m is not None:
        level = len(m.groups()[0])
        if level == 1:
          exp_name = m.groups()[2]
          cur_exp = Experiment(m.groups()[2])
          experiments[exp_name] = cur_exp
        if level == 2:
          if cur_exp is None:
            raise Exception("Middleware without experiment, line: {0}".format(line_count))
          cur_mw = Middleware(m.groups()[2])
          cur_exp.children.append(cur_mw)
        if level == 3:
          if cur_mw is None:
            raise Exception("Client without middleware, line: {0}".format(line_count))
          if m.groups()[1] is not None:
            repetitions = int(m.groups()[1])
          else:
            repetitions = 1
          for i in xrange(0, repetitions):
            if m.groups()[3] is not None:
              arg_str = m.groups()[3]
            else:
              arg_str = ''
            cur_mw.children.append(Client(m.groups()[2], arg_str.replace('%i', str(i))))
    return experiments
