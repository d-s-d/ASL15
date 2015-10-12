import sys
import argparse

from experiment import Experiment
from vm_pool import assign_hosts, VM_Pool

def section(title=""):
    print("\n############ {0} ############".format(title))

if __name__=="__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('experiment_name', type=str, help='name of the experiment')
    argparser.add_argument('-f', '--experiments-file', help='experiments file',
        default='experiments.txt')
    argparser.add_argument('-p', '--vm-pool-file', help='file specifying vm hostnames',
        default='pool.txt')
    args = argparser.parse_args()

    xps = Experiment.parse_experiments_file(open(args.experiments_file))
    x = xps[args.experiment_name]
    vmpool = VM_Pool(open(args.vm_pool_file))
    assign_hosts(x, vmpool)

    section("SETUP PHASE")
    x.setup()

    section("RUN PHASE")
    #x.run()

    #x.collectlogs()
    #x.reset()
    #x.shutdown()
