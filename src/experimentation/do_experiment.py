import sys
import argparse
import os
import hashlib
from Queue import Queue

from experiment import ExperimentFile
from vm_pool import VM_Pool

from remote_task import RemoteTask

from config import config

def phase(title=""):
    print("\n############ PHASE: {0} ############".format(title))


def subphase(title=""):
    print("\n# {0}".format(title))

def execute_at_once(tasks):
    for l in tasks:
        for t in l:
            subphase("SCHEDULING TASK {0}".format(t.__repr__()))
            t.execute()
    for l in tasks:
        for t in l:
            t.join()

if __name__=="__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('experiment_name', type=str, help='name of the experiment')
    # argparser.add_argument('db_password', type=str, help='name of the experiment')
    argparser.add_argument('-f', '--experiments-file', help='experiments file',
        default='experiments.txt')
    args = argparser.parse_args()

    m = hashlib.md5()
    m.update(os.urandom(16))

    vmpool = VM_Pool()
    xfile = ExperimentFile(open(args.experiments_file), vmpool)
    x = xfile.children[args.experiment_name]

    phase("SETUP")
    execute_at_once(x.collect_command('setup'))

    phase("RUN")
    subphase("RUN MIDDLEWARE")

    tasks = x.collect_command('run')
    mw_queues = map(lambda t: t.register_filtered_queue(lambda l: 'Middleware started' in l, Queue()),
        tasks[1])
    for mw_t in tasks[1]:
        mw_t.execute()
    for q in mw_queues:
        print(q.get())
    
    subphase("RUN CLIENTS")
    for client_task in tasks[2]:
        client_task.register_pipe_event(lambda x: True, RemoteTask._print_command)
        client_task.execute()

    for client_task in tasks[2]:
        client_task.join()

    subphase("SHUTDOWN MIDDLEWARE")
    kill_tasks = x.collect_command('terminate')
    for kill_task in kill_tasks[1]:
        kill_task.execute()

#x.collectlogs()
    #x.reset()
    #x.shutdown()
