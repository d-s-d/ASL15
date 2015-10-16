import re
import os

import boto3

from config import config


class VM_Pool(object):
    def __init__(self):
        self.hosts = dict()
        instances = boto3.resource('ec2').instances.all()

        for vm_type in config['VM_TYPES']:
            self.hosts[vm_type] = filter(
                lambda i: {'Key': 'asltype', 'Value': vm_type} in i.tags,
                instances)
    
    def get_vm(self, vm_type, idx=0):
        return self.hosts[vm_type][idx % len(self.hosts[vm_type])]

    def start():
        pass #TODO

    def stop():
        pass #TODO
