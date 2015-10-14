import sys
import argparse
import os
import hashlib

from experiment import Experiment
from vm_pool import assign_vms, VM_Pool

from config import config

def phase(title=""):
    print("\n############ PHASE: {0} ############".format(title))


def subphase(title=""):
    print("\n# {0}".format(title))

if __name__=="__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('experiment_name', type=str, help='name of the experiment')
    # argparser.add_argument('db_password', type=str, help='name of the experiment')
    argparser.add_argument('-f', '--experiments-file', help='experiments file',
        default='experiments.txt')
    argparser.add_argument('-p', '--vm-pool-file', help='file specifying vm hostnames',
        default='pool.txt')
    args = argparser.parse_args()

    m = hashlib.md5()
    m.update(os.urandom(16))
    config['DBPASS'] = m.hexdigest()

    xps = Experiment.parse_experiments_file(open(args.experiments_file))
    x = xps[args.experiment_name]
    vmpool = VM_Pool(open(args.vm_pool_file))
    assign_vms(x, vmpool)

    phase("SETUP")

    tasks = x.collect_command('setup')
    for l in tasks:
        for t in l:
            subphase("SCHEDULING TASK {0}".format(t.__repr__()))
            t.execute()
        for t in l:
            t.join()

    phase("RUN")
    #x.run()

    #x.collectlogs()
    #x.reset()
    #x.shutdown()
