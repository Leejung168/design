# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, jsonify, url_for, g, flash,abort

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from models import Base, CustomerGroup, ServerGroup, PasswordGroup

from Crypto.Cipher import XOR
import base64

app = Flask(__name__)


# Create Database session
engine = create_engine('mysql://root:lambert@127.0.0.1:3306/customergroup')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Encrypt/Decrypt Password

secret_key = '*XaDt(sfGd{6Qy+4q|.%0j;Fdm5?n!*~'
def encrypt(plaintext, key=secret_key):
  cipher = XOR.new(key)
  return base64.b64encode(cipher.encrypt(plaintext))


def decrypt(ciphertext, key=secret_key):
  cipher = XOR.new(key)
  return cipher.decrypt(base64.b64decode(ciphertext))


# App
@app.route('/')
def index():
    return render_template("index.html")


@app.route('/customer', methods=['GET', 'POST'])
def customer():
    customers = []
    idd = request.form.get('iid')
    if idd == "1":
        try:
            customer_group=session.query(CustomerGroup).all()
            for c in customer_group:
                customers.append(c.name)
        except:
            customers.append("Error")
    else:
        customers.append("Error")
    return jsonify(customers)


@app.route('/home')
def home():
    return render_template("index.html")


# Customer--->Servers Page
@app.route('/servers')
def servers():
    well = []
    # Obtain customer name from request header.
    name = request.args.get("name")
    try:
        ownerid = session.query(CustomerGroup).filter_by(name=name).one().id
        servers = session.query(ServerGroup).filter_by(ownerid=ownerid).all()
        for s in servers:
            single = {
                "sname": s.sname,
                "sip": s.sip,
                "sport": s.sport
            }
            well.append(single)
            single = {}
    except:
        single = {
            "sname": "query-database-error",
            "sip": "0.0.0.0",
            "sip": "0"
        }
        well.append(single)
    return render_template("server.html", servers=well)


# Customer--->Servers--->Server Info Detailed Page
@app.route('/s_detailed')
def s_detailed():
    # Obtain server name from the request header;
    server = request.args.get("server")
    try:
        info = session.query(ServerGroup).filter_by(sname=server).one()
        single = {
            "sname": info.sname,
            "sip": info.sip,
            "sport": info.sport
        }
    except:
        single = {
            "sname": "query-database-error",
            "sip": "0.0.0.0",
            "sip": "0"
        }

    return render_template("detailed_info.html", info=single)


# Obtain the password info per server name from the request header.
@app.route('/pw')
def pw():
    sname = request.args.get("sname")
    try:
        sid = session.query(ServerGroup).filter_by(sname=sname).one().id
        passwd = session.query(PasswordGroup).filter_by(sid=sid).one()
        info = {
            "ncadmin": decrypt(passwd.ncadmin),
            "root": decrypt(passwd.root),
            "gpg_key": decrypt(passwd.gpg_key),
            "nccheckdb": decrypt(passwd.nccheckdb),
            "ncbackupdb": decrypt(passwd.ncbackupdb),
            "ncdba": decrypt(passwd.ncdba)
        }

        print info
    except Exception as e:
        print e
        info = {
            "ncadmin": "query-database-error",
            "root": "query-database-error",
            "gpg_key": "query-database-error",
            "nccheckdb": "query-database-error",
            "ncbackupdb": "query-database-error",
            "ncdba": "query-database-error"
        }

    return render_template("pw_info.html", pw=info)



if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
