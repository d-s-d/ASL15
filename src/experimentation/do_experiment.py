import sys
import argparse
import os
import hashlib
import time
from datetime import datetime
from Queue import Queue

from experiment import experiments
from vm_pool import VM_Pool

from remote_task import RemoteTask, AlreadyScheduledException
from config import config

import experiments_local

def phase(title=""):
    print("\n############ PHASE: {0} ############".format(title))


def subphase(title=""):
    print("\n# {0}".format(title))

def execute_at_once(tasks):
    for l in tasks:
        for t in l:
            subphase("SCHEDULING TASK {0}".format(t.__repr__()))
            t.register_pipe_event(pipe='stdout')
            try:
                t.execute()
            except AlreadyScheduledException:
                pass
    for l in tasks:
        for t in l:
            t.join()

if __name__=="__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('experiment_name', type=str, help='name of the experiment')
    args = argparser.parse_args()

    m = hashlib.md5()
    m.update(os.urandom(16))

    vmpool = VM_Pool()
    x = experiments[args.experiment_name]
    
    phase("START VMS")

    if not vmpool.are_all_running():
        vmpool.start()
    while not vmpool.are_all_running():
        time.sleep(6)
        print("Waiting for vms to start.")


    phase("SETUP")
    
    x.collect_command('assign_vm', vmpool)
    execute_at_once(x.collect_command('setup'))

    phase("RUN")
    subphase("RUN MIDDLEWARE")

    tasks = x.collect_command('run')
    mw_queues = dict(map(lambda t: (t, t.register_filtered_queue(
        lambda l: 'Middleware started' in l, Queue())), tasks[1]))
    for mw_t in tasks[1]:
        try:
            mw_t.execute()
        except:
            del mw_queues[mw_t]

    for q in mw_queues.values():
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

    phase("COLLECT LOGS")
    targetdir = os.path.join("logs", 
        args.experiment_name,
        datetime.now().isoformat().replace(':','_'))
    execute_at_once(x.collect_command("collect_logs", targetdir))

    phase("STOP VMs")
    #vmpool.stop()
