#!/usr/bin/env python
import os,sys
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.executor.playbook_executor import PlaybookExecutor


def play(username, password, port, host_file, playbook_path):
    variable_manager = VariableManager()
    loader = DataLoader()
    inventory = Inventory(loader=loader, variable_manager=variable_manager,  host_list=host_file)

    if not os.path.exists(playbook_path):
        print '[INFO] The playbook does not exist'
        sys.exit()

    Options = namedtuple('Options', ['listtags', 'listtasks', 'listhosts', 'syntax', 'connection','module_path', 'forks', 'remote_user', 'private_key_file', 'ssh_common_args', 'ssh_extra_args', 'sftp_extra_args', 'scp_extra_args', 'become', 'become_method', 'become_user', 'verbosity', 'check'])
    options = Options(listtags=False, listtasks=False, listhosts=False, syntax=False, connection='ssh', module_path=None, forks=100, remote_user=username, private_key_file=None, ssh_common_args=None, ssh_extra_args=None, sftp_extra_args=None, scp_extra_args=None, become=True, become_method='sudo', become_user='root', verbosity=None, check=False)

    variable_manager.extra_vars = {'ansible_port': port}

    passwords = {"conn_pass": password}

    playing = PlaybookExecutor(playbooks=[playbook_path], inventory=inventory, variable_manager=variable_manager, loader=loader, options=options,passwords=passwords)

    playing.run()


if __name__ == '__main__':
    play(username="root", password="lambert", port="22", host_file="/tmp/.srv-lz-number2", playbook_path="/Users/lambertli/pycharm/python2/Lambert-Tool/design/new_rhel7/main.yml")
