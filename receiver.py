#!/usr/bin/env python
import redis
from run import play
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, sessionmaker
from models import Base, ServerGroup

# Create Database session
engine = create_engine('mysql://root:lambert@127.0.0.1:3306/cg')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

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
        inventory = "/tmp/." + server.sip
        with open(inventory, 'w') as f:
            f.write(server_name + " ansible_ssh_host=" + server.sip)

        try:
            play(username=username, password=password, port=port, host_file=inventory)
            redis_session1.set(server_name, "Succeed")
        except:
            redis_session1.set(server_name, "Failed")
