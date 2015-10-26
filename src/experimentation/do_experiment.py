import sys
import argparse
import os
import hashlib
import time
from re import compile
from datetime import datetime
from Queue import Queue

from experiment import experiments
from vm_pool import VM_Pool

from remote_task import RemoteTask, AlreadyScheduledException
from config import config

import experiments_local

executed_phases = set()

def remote_phase(f):
    f.is_remote_phase = True
    return f

def phase(title=""):
    print("\n############ PHASE: {0} ############".format(title))


def subphase(title=""):
    print("\n# {0}".format(title))

def execute_at_once(tasks, delay=0.5):
    for l in tasks:
        for t in l:
            subphase("SCHEDULING TASK {0}".format(t.__repr__()))
            t.register_pipe_event(pipe='stdout')
            try:
                t.execute()
                time.sleep(delay)
            except AlreadyScheduledException:
                pass
    for l in tasks:
        for t in l:
            t.join()

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('experiment_name', type=str, help='name of the experiment')
    argparser.add_argument('-x', '--exclude-phases', type=str,
        help='comma separated list of phases to exclude')
    argparser.add_argument('-i', '--include-phases', type=str,
        help='comma separated list of phases to exclude')
    argparser.add_argument('-s', '--select', type=int,
        help=
"""if this option is provided, the experiment name is treated as a regular expression
and the n'th experiment matching the regular expression is chosen for execution.""")
    
    args = argparser.parse_args()
   
    if args.include_phases:
        included_phases = args.include_phases.split(',')
    else:
        included_phases = list()

    if args.exclude_phases:
        excluded_phases = args.exclude_phases.split(',')
    else:
        excluded_phases = list()

    if args.experiment_name == 'list':
        for exp_name in sorted(experiments.keys()):
            print(exp_name)
        sys.exit(0)

    if args.select is not None:
        r = compile(args.experiment_name)
        xs = filter(lambda n: r.match(n) is not None, sorted(experiments.keys()))
        x_name = xs[args.select]
    else:
        x_name = args.experiment_name
   
    print("Running experiment {0}".format(x_name))

    try:
        x = experiments[x_name]
    except KeyError:
        print("ERROR: experiment {0} not found.".format(x_name))
        sys.exit(1)
    
    vmpool = VM_Pool()

    def _assign_vm():
        if hasattr(_assign_vm, 'executed'):
            return
        x.collect_command('assign_vm', vmpool)
        _assign_vm.executed = True

    def phase_boot():
        sys.stdout.write("Waiting for vms to start.")
        sys.stdout.flush()
        if not vmpool.are_all_running():
            vmpool.start()
        while not vmpool.are_all_running():
            time.sleep(6)
            sys.stdout.write('.')
            sys.stdout.flush()

        print ""

    def phase_warmup():
        for i in xrange(16):
            time.sleep(1)
            sys.stdout.write('.')
            sys.stdout.flush()

        print ""

    @remote_phase
    def phase_setup():
        execute_at_once(x.collect_command('setup'))

    @remote_phase
    def phase_deploy():
        execute_at_once(x.collect_command('deploy'))

    @remote_phase
    def phase_run():
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


    @remote_phase
    def phase_collect_logs():
        targetdir = os.path.join("logs", 
            x_name,
            datetime.now().isoformat().replace(':','_'))
        execute_at_once(x.collect_command("collect_logs", targetdir))

    @remote_phase
    def phase_reset():
        execute_at_once(x.collect_command("reset"))

    def phase_stop():
        vmpool.stop()

    that_locals = locals()

    available_phases = map(lambda pname: that_locals[pname],
        filter(lambda s: s.startswith('phase_'), main.__code__.co_varnames))
    if len(included_phases) > 0:
        inc_run_phases = filter(lambda p: p.__name__[len('phase_'):] in included_phases,
            available_phases)
    else:
        inc_run_phases = available_phases
    run_phases = filter(lambda p: p.__name__[len('phase_'):] not in excluded_phases,
        inc_run_phases)

    for phas in run_phases:
        phase(phas.__name__)
        if hasattr(phas, 'is_remote_phase'):
            _assign_vm()
        phas()

    
if __name__=="__main__":
    main()

