from experiment import Experiment
from vm_pool import assign_hosts, VM_Pool

xps = Experiment.parse_experiments_file(open("experiments.txt"))
x = xps['SomeExperiment']
vmpool = VM_Pool(open("pools.txt"))
assign_hosts(x, vmpool)
print(x)
