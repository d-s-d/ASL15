import os
from select import poll, POLLIN, POLLHUP
from threading import Thread
from Queue import Queue
from subprocess import Popen, PIPE
import types

SHELL_COMMAND = 'sh'

scheduled_tasks = set()

def escape_string(s):
    return s.replace('\\', '\\\\').replace('"', '\\"')

def get_args_string(args):
    return ' '.join(map(lambda a: '"{0}"'.format(escape_string(str(a))), args))

def get_ssh_command(hostname, remote_command):
    return "ssh {0} \"{1}\"".format(hostname, escape_string(remote_command))

def get_scp_command(hostname, local_list, remote=''):
    return "scp {0} {1}:{2}".format(get_args_string(local_list), hostname, remote)


class RemoteTask(object):
    def __init__(self, unique_task_name, hostname='localhost', once=False, silence_stderr=False):
        self.commands = list()
        self.files = list()
        self.scripts = list()
        self.once = once
        self.hostname = hostname
        self.supported_pipes = ('stdout', 'stderr')
        self.filtered_queues = dict([(name, list()) for name in self.supported_pipes])
        self.pipe_event_handlers = dict([(name, list()) for name in self.supported_pipes])

        self.repr_string = "{0}: {1}".format(hostname, unique_task_name)
        self.t = None

        if not silence_stderr:
            def print_err(task, line):
                print("ERR: [{0}] {1}".format(task.__repr__(), line))
            self.pipe_event_handlers['stderr'].append((lambda x: True, print_err))

    def register_filtered_queue(self, filt, q, pipe='stdout'):
        assert pipe in ('stdout', 'stderr')
        assert isinstance(filt, types.FunctionType)
        assert isinstance(q, Queue)
        self.filtered_queues[pipe].append((filt, q))
        return q

    def register_pipe_event(self, filt, handler, pipe='stdout'):
        print(pipe)
        assert pipe in ('stdout', 'stderr')
        assert isinstance(filt, types.FunctionType)
        assert isinstance(handler, types.FunctionType) or isinstance(handler, types.MethodType)
        self.pipe_event_handlers[pipe].append((filt, handler))

    def command(self, cmd, args=None):
        if args is None:
            args = []
        self.commands.append("{0} {1}".format(cmd, get_args_string(args)))

    def copy_file(self, src, target=None):
        self.files.append( (src, target) )

    def run_sh_script(self, script, args=None):
        if args is None:
            args = []
        self.copy_file( script )
        self.commands.append("{0} {1} {2}".format(
            SHELL_COMMAND, os.path.split(script)[1], get_args_string(args)))

    def _print_command(self, cmd):
        print("[{rep}] {command}".format(rep=self.__repr__(), command=cmd))

    def _run_command(self, cmd):
        self._print_command(cmd)
        new_proc = Popen([cmd], shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        return new_proc

    def filter_output(self, ps):
        fd_map = dict([(getattr(ps, name).fileno(), (name, getattr(ps, name)))
            for name in self.supported_pipes])
        p = poll()
        for fd in fd_map.keys():
            p.register(fd, POLLIN)

        hup = False
        while not hup:
            for (ready_fd, mask) in p.poll():
                (fd_name, f) = fd_map[ready_fd]
                line = f.readline()
                if len(line) > 0:
                    for (filt, handler) in self.pipe_event_handlers[fd_name]:
                        if filt(line):
                            handler(self, line)
                    for (filt, q) in self.filtered_queues[fd_name]:
                        line = f.readline()
                        if filt(line):
                            q.put(line)
                if mask & POLLHUP != 0:
                    hup = True

        # read remaining lines
        for fd_name in self.supported_pipes:
            line = getattr(ps, fd_name).readline()
            while len(line) > 0:
                for (filt, q) in self.filtered_queues[fd_name]:
                    if filt(line):
                        q.put(line)
                line = ps.stdout.readline()

        for fd in fd_map.keys():
            p.unregister(fd)

    def execute(self):
        def execute_deploy_task():
            # copy files without target
            files_wo_trgt = map(lambda i: i[0], filter(lambda i: i[1] is None, self.files))
            if len(files_wo_trgt) > 0:
                p_wo_trgt = self._run_command(get_scp_command(self.hostname, files_wo_trgt))
                self.filter_output(p_wo_trgt)
            # copy files with target
            files_w_trgt = filter(lambda i: i[1] is not None, self.files)
            if len(files_w_trgt) > 0:
                for f in files_w_trgt:
                    self.filter_output(self._run_command(
                        get_scp_command(self.hostname, f[0], f[1])))

            # run scripts
            if len(self.commands) > 0:
                for c in self.commands:
                    self.filter_output(self._run_command(
                        get_ssh_command(self.hostname, c)))
       
        if self.once:
            if self.__repr__() in scheduled_tasks:
                return
            else:
                scheduled_tasks.add(self.__repr__())
        
        self.t = Thread(target=execute_deploy_task)
        self.t.start()

    def join(self):
        if self.t is not None:
            self.t.join()

    def __repr__(self):
        return self.repr_string
