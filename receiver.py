#!/usr/bin/env python
import redis
from run import play
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, sessionmaker
from models import Base, ServerGroup
import yaml

# Create Database session
engine = create_engine('mysql://root:lambert@127.0.0.1:3306/cg')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# db=0 will save the running logs.
redis_session0 = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)

# db=1 will save the last status.
redis_session1 = redis.StrictRedis(host='127.0.0.1', port=6379, db=1)
ps = redis_session1.pubsub()
ps.subscribe(['servername'])

for item in ps.listen():
    if item['type'] == 'message':
        server_name = item['data']

        server = session.query(ServerGroup).filter_by(sservername=server_name).one()
        username = server.susername
        password = server.spassword
        port = server.sport

        #Write Inventory to file
        inventory = "/tmp/." + server_name
        with open(inventory, 'w') as f:
            f.write(server_name + " ansible_ssh_host=" + server.sip)


        #To check LVM if needed, then write to host var.
        lvm_check = server.slvm
        if lvm_check == 'No':
            host_var = "server_enable_lvm: false"
        else:
            disk_name = server.sdisk
            host_var = {'vgs': [{'device': disk_name, 'name': 'domuvg'}]}

        with open("/Users/lambertli/pycharm/python2/post_install/host_vars/{0}".format(server_name), 'w') as f:
            if host_var is dict:
                yaml.dump(host_var, f)
            else:
                f.write(host_var)

        try:
            play(username=username, password=password, port=port, host_file=inventory)
            last_log = redis_session0.get(server_name)
            last_status = last_log.split("-")[1].strip()
            redis_session1.set(server_name, last_status)
        except:
            redis_session1.set(server_name, "Failed")
