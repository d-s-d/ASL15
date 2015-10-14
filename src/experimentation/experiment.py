import re
from remote_task import RemoteTask
from config import config

EXP_DEF_REGEXP = re.compile("(\*+)\s*([1-9][0-9]*)?\s*([a-zA-Z_][0-9a-zA-Z_-]*) ?(.*)\n")

class ExperimentNode(object):
    def setup(self):
        return self.instance.setup()

    def collect_command(self, command):
        def collect_rec(collections, level, node):
            if hasattr(node, command):
                task = getattr(node, command)()
                if task is not None:
                    collections[level].append(task)
            if hasattr(node, 'children'):
                for c in node.children:
                    collect_rec(collections, level+1, c)
        collections = [[], [], []]
        collect_rec(collections, 0, self)
        return collections
    

class Client(ExperimentNode):
    def __init__(self, client_type, arg_str):
        self.client_type = client_type
        self.args = arg_str.split()
        # TODO: move this into the parser
        if len(self.args) < 1:
            raise Exception("too few arguments for client")
        self.name = self.args[0]
        self.args = self.args[1:]

    def run(self):
        t = RemoteTask('run client', self.instance.hostname)
        t.command(config['JAVA_CLIENT_COMMAND'],
            [self.client_type, self.name, self.parent.instance.hostname, config['MWPORT']] + self.args)
        return t

    def __repr__(self):
        hostname = ""
        if hasattr(self, 'instance'):
            hostname = self.instance.hostname
        return "ClientType ({2}) {0} with Arguments: {1} ".format(self.client_type, str(self.args), hostname)


class Middleware(ExperimentNode):
    def __init__(self, identifier):
        self.identifier = identifier
        self.children = []

    def run(self):
        t = RemoteTask('run middleware', self.instance.hostname)
        t.command(config['JAVA_MW_COMMAND'],
            [self.identifier, self.parent.instance.hostname, config['DBNAME'],
            config['DBUSER'], config['DBPASS'], config['MWPORT']])
        return t
   
    def terminate(self):
        t = RemoteTask('stop middleware', self.instance.hostname, once=True)
        t.command('killall java')
        return t

    def __repr__(self):
        hostname = ""
        if hasattr(self, 'instance'):
            hostname = self.instance.hostname
        return "Middleware: ({2}) {0} \n    {1} ".format(
            self.identifier, '\n    '.join(map(lambda c: c.__repr__(), self.children)), hostname)


class Experiment(ExperimentNode):
    def __init__(self, identifier):
        self.identifier = identifier
        self.children = []

    def __repr__(self):
        hostname = ""
        if hasattr(self, 'instance'):
            hostname = self.instance.hostname
        return "Experiment: ({2}) {0} \n {1} ".format(
            self.identifier, '\n '.join(map(lambda c: c.__repr__(), self.children)), hostname)

    def reset(self):
        self.instance.reset()

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
                    cur_exp.parent = None
                if level == 2:
                    if cur_exp is None:
                        raise Exception("Middleware without experiment, line: {0}".format(line_count))
                    cur_mw = Middleware(m.groups()[2])
                    cur_exp.children.append(cur_mw)
                    cur_mw.parent = cur_exp
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
                        cur_client = Client(m.groups()[2],
                            arg_str.replace('%i', '{0:03d}'.format(i)))
                        cur_mw.children.append(cur_client)
                        cur_client.parent = cur_mw

        return experiments
