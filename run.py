#!/usr/bin/env python
import string
from random import choice
from Crypto.Cipher import XOR
import base64

import os, sys
from passlib.hash import md5_crypt
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.executor.playbook_executor import PlaybookExecutor

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, PasswordGroup, ServerGroup

engine = create_engine('mysql://root:lambert@127.0.0.1:3306/cg')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

secret_key = '*XaDt(sfGd{6Qy+4q|.%0j;Fdm5?n!*~'

def encrypt(plaintext, key=secret_key):
  cipher = XOR.new(key)
  return base64.b64encode(cipher.encrypt(plaintext))

def decrypt(ciphertext, key=secret_key):
  cipher = XOR.new(key)
  return cipher.decrypt(base64.b64decode(ciphertext))

def generate_passwd(length):
    passwd_format = string.digits + string.ascii_letters
    passwd = []
    while (len(passwd) < length):
        passwd.append(choice(passwd_format))
    return ''.join(passwd)

def generate_passwd(length):
    passwd_format = string.digits + string.ascii_letters
    passwd = []
    while (len(passwd) < length):
        passwd.append(choice(passwd_format))
    return ''.join(passwd)


def play(username="root", password="lambert", port="22", host_file="/tmp/.srv-lz-node1", servername="srv-lz-node1"):

    ncadmin = generate_passwd(12)
    i = session.query(ServerGroup).filter_by(sservername=servername).one()

    try:
        CheckExist = session.query(PasswordGroup).filter_by(sid=i.id).one()
        ncadmin = decrypt(CheckExist.ncadmin)
    except:
        pw = PasswordGroup(root=encrypt(password), ncadmin=encrypt(ncadmin),
                           nccheckdb="-", ncbackupdb="-",
                           ncdba="-", gpg_key="-", owner=i)
        session.add(pw)
        session.commit()

    env = os.environ
    env['NCADMIN_PASSWORD'] = md5_crypt.hash(ncadmin)

    variable_manager = VariableManager()
    loader = DataLoader()

    inventory = Inventory(loader=loader, variable_manager=variable_manager,  host_list=host_file)
    playbook_path = '/Users/lambertli/pycharm/python2/post_install/postinstall_step2.yml'

    if not os.path.exists(playbook_path):
        print '[INFO] The playbook does not exist'
        sys.exit()

    Options = namedtuple('Options', ['listtags', 'listtasks', 'listhosts', 'syntax', 'connection','module_path', 'forks', 'remote_user', 'private_key_file', 'ssh_common_args', 'ssh_extra_args', 'sftp_extra_args', 'scp_extra_args', 'become', 'become_method', 'become_user', 'verbosity', 'check'])
    options = Options(listtags=False, listtasks=False, listhosts=False, syntax=False, connection='ssh', module_path=None, forks=100, remote_user=username, private_key_file=None, ssh_common_args=None, ssh_extra_args=None, sftp_extra_args=None, scp_extra_args=None, become=True, become_method='sudo', become_user='root', verbosity=None, check=False)

    variable_manager.extra_vars = {'ansible_port': port}

    passwords = {"conn_pass": password}

    play = PlaybookExecutor(playbooks=[playbook_path], inventory=inventory, variable_manager=variable_manager, loader=loader, options=options,passwords=passwords)

    results = play.run()


if __name__ == '__main__':
    play(username="root", password="lambert", port="22", host_file="/tmp/.srv-lz-client1")
