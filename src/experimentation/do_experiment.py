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

from remote_task import RemoteTask, AlreadyScheduledException, reset_scheduled_tasks
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


def print_experiment(x_id):
    print(" {0}: {1} {2}".format(x_id, *experiments[x_id][:2]))

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
    argparser.add_argument('experiments', type=str,
        help=
"""comma separated list of numbers of experiments to run. For example,
1-3  : run experiment 1,2, and 3
1,5-7: run experiments 1,5,6, and 7.""")
    argparser.add_argument('-x', '--exclude-phases', type=str,
        help='comma separated list of phases to exclude')
    argparser.add_argument('-i', '--include-phases', type=str,
        help='comma separated list of phases to exclude')
    
    args = argparser.parse_args()
   
    if args.include_phases:
        included_phases = args.include_phases.split(',')
    else:
        included_phases = list()

    if args.exclude_phases:
        excluded_phases = args.exclude_phases.split(',')
    else:
        excluded_phases = list()

    if args.experiments == 'list':
        for x_id in xrange(len(experiments)):
            print_experiment(x_id)
        sys.exit(0)

    x_idcs = set()
    for exp_arg in args.experiments.split(','):
        r = map(lambda s: int(s), exp_arg.split('-'))
        x_idcs.update( range(r[0], r[len(r)-1]+1) )

    x_idcs = sorted(list(x_idcs))
  
    xname = ''
    xparams = {}
    x = None

    print("Running experiments: ")
    try:
        for x_id in x_idcs:
            print(" {0}: {1} {2}".format(x_id, *experiments[x_id][:2]))
    except IndexError as e:
        print(e)
        sys.exit(1)
   
    #xs = [x[x_id][2] for x_id in x_list]

    vmpool = VM_Pool()

    def _assign_vm(x):
        if hasattr(_assign_vm, 'executed') and _assign_vm.executed:
            return
        x.collect_command('assign_vm', vmpool)
        print x
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
            kill_task.join()


    @remote_phase
    def phase_collect_logs():
        targetdir = os.path.join("logs", 
            '{0}__{1}'.format(xname,
                datetime.now().isoformat().replace(':','_')))
        os.makedirs(targetdir)
        if xparams is not None:
            fparams = open(os.path.join(targetdir, 'params.txt'), 'w')
            for item in xparams.items():
                fparams.write("{0}:{1}\n".format(*item))
            fparams.close()
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

    for x_id in x_idcs:
        _assign_vm.executed = False
        reset_scheduled_tasks()
        print("Current Experiment:")
        print_experiment(x_id)
        (xname, xparams, x) = experiments[x_id]
        for phas in run_phases:
            phase(phas.__name__)
            if hasattr(phas, 'is_remote_phase'):
                _assign_vm(x)
            phas()

    
if __name__=="__main__":
    main()

