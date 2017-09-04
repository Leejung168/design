from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import CustomerGroup, ServerGroup, Base, PasswordGroup

from Crypto.Cipher import XOR
import base64


import random,string
from random import choice

secret_key = '*XaDt(sfGd{6Qy+4q|.%0j;Fdm5?n!*~'


def encrypt(plaintext, key=secret_key):
  cipher = XOR.new(key)
  return base64.b64encode(cipher.encrypt(plaintext))

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


servers = session.query(ServerGroup).all()

for i in servers:
    pw = PasswordGroup(root=encrypt(generate_passwd(12)), ncadmin=encrypt(generate_passwd(12)), nccheckdb=encrypt(generate_passwd(12)), ncbackupdb=encrypt(generate_passwd(12)),ncdba=encrypt(generate_passwd(12)), gpg_key=encrypt(generate_passwd(32)), owner=i)

    session.add(pw)
    session.commit()
