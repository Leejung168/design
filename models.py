import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

#CustomerGroup
class CustomerGroup(Base):
    __tablename__ = 'customer_group'

    id = Column(Integer, primary_key=True)
    name = Column(String(16), nullable=False)

#Server asset information
class ServerGroup(Base):
    __tablename__ = 'server_group'

    id = Column(Integer, primary_key=True)
    sname = Column(String(32), nullable=False)
    spassword = Column(String(64), nullable=False)
    sip = Column(String(32), nullable=False)
    sport = Column(String(16), nullable=False)
    ownerid = Column(Integer, ForeignKey('customer_group.id'))
    owner = relationship(CustomerGroup)

#Password info per server.
class PasswordGroup(Base):
    __tablename__ = 'password_group'

    id = Column(Integer, primary_key=True)
    root = Column(String(64), nullable=False)
    ncadmin = Column(String(64), nullable=False)
    gpg_key = Column(String(64), nullable=False)
    ncdba = Column(String(64), nullable=False)
    nccheckdb = Column(String(64))
    ncbackupdb = Column(String(64))
    ncdba = Column(String(64))
    sid = Column(Integer, ForeignKey('server_group.id'))
    owner = relationship(ServerGroup)



engine = create_engine('mysql://root:lambert@127.0.0.1:3306/customergroup')

Base.metadata.create_all(engine)
