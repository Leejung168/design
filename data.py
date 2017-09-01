from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import CustomerGroup, ServerGroup, Base

import random,string
from random import choice

def generate_passwd(length):
    passwd_format = string.digits + string.ascii_letters
    passwd = []
    while (len(passwd) < length):
        passwd.append(choice(passwd_format))
    return ''.join(passwd)

#Setup DB session
engine = create_engine('mysql://root:lambert@127.0.0.1:3306/customergroup')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

for i in ["ChinaNetCloud","Lambert","SixthTone","YiJieDai","King","DayDayCook"]:
    customer=CustomerGroup(name=i)
    session.add(customer)
    session.commit()

    server = ServerGroup(sname="srv-{0}-web1".format(i.lower()), spassword=generate_passwd(12), sip="202.248.35.58", sport="40022", owner=customer)
    session.add(server)
    session.commit()

    server1 = ServerGroup(sname="srv-{0}-db1".format(i.lower()), spassword=generate_passwd(12), sip="103.8.25.33", sport="40022", owner=customer)
    session.add(server1)
    session.commit()

    server2 = ServerGroup(sname="srv-{0}-lb1".format(i.lower()), spassword=generate_passwd(12), sip="54.28.35.58", sport="40022", owner=customer)
    session.add(server2)
    session.commit()

    server3 = ServerGroup(sname="srv-{0}-app1".format(i.lower()), spassword=generate_passwd(12), sip="47.8.35.58", sport="40022", owner=customer)
    session.add(server3)
    session.commit()

