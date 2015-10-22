import re
import os

import boto3

from config import config


class VM_Pool(object):
    def __init__(self):
        self.hosts = dict()
        self.instances = list()
   
    def assign_groups(self):
        for vm_type in config['VM_TYPES']:
            vm_type_instances = filter(
                lambda i: {'Key': 'asltype', 'Value': vm_type} in i.tags,
                boto3.resource('ec2').instances.all())
            self.hosts[vm_type] = vm_type_instances

    def _instances(self):
        instances = list()
        for vm_type in config['VM_TYPES']:
            vm_type_instances = filter(
                lambda i: {'Key': 'asltype', 'Value': vm_type} in i.tags,
                boto3.resource('ec2').instances.all())
            instances.extend(vm_type_instances)
        return instances


    def get_vm(self, vm_type, idx=0):
        self.assign_groups()
        return self.hosts[vm_type][idx % len(self.hosts[vm_type])]

    def start(self):
        for inst in self._instances():
            inst.start()

    def are_all_running(self):
        for inst in self._instances():
            if inst.state['Name'] != 'running':
                return False
        return True

    def stop(self):
        for inst in self._instances():
            inst.stop()
