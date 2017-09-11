# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, jsonify, url_for, g, flash,abort

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from models import Base, CustomerGroup, ServerGroup, PasswordGroup

from Crypto.Cipher import XOR
import base64

import json

app = Flask(__name__)


# Create Database session
engine = create_engine('mysql://root:lambert@127.0.0.1:3306/cg')
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
    whole = {}
    well = []
    # Obtain customer name from request header.
    name = request.args.get("name")
    try:
        ownerid = session.query(CustomerGroup).filter_by(name=name).one().id
        servers = session.query(ServerGroup).filter_by(ownerid=ownerid).all()
        for s in servers:
            single = {
                "sservername": s.sservername,
                "sip": s.sip,
                "sport": s.sport,
                "sfunction": s.sfunction,
                "ssystem": s.ssystem,
                "splatform": s.splatform,
            }
            well.append(single)
            single = {}
    except:
        single = {
            "sservername": "query-database-error",
            "sip": "0.0.0.0",
            "sport": "0",
            "sgroup": "-",
            "ssystem": "-",
            "splatform": "-",
        }
        well.append(single)

    whole = {
        "customer_name": name,
        "servers": well,
    }

    return render_template("server.html", whole=whole)


# Customer--->Servers--->Server Info Detailed Page
@app.route('/s_detailed')
def s_detailed():
    # Obtain server name from the request header;
    server = request.args.get("server")
    try:
        info = session.query(ServerGroup).filter_by(sservername=server).one()
        single = {
            "sname": info.sservername,
            "sip": info.sip,
            "sport": info.sport
        }
    except:
        single = {
            "sname": "query-database-error",
            "sip": "0.0.0.0",
            "sport": "0"
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


# Obtain Plus info
@app.route('/plus_server', methods=["POST"])
def plus_server():
    data = request.form.to_dict()
    print data

    sservername = data.pop("server_name").encode("utf-8")
    susername = data.pop("server_username").encode("utf-8")
    spassword = data.pop("server_password").encode("utf-8")
    sip = data.pop("server_ip").encode("utf-8")
    sport = data.pop("server_port").encode("utf-8")
    sfunction = data.pop("server_function").encode("utf-8")
    slvm = data.pop("server_lvm").encode("utf-8")
    sgroup = data.pop("server_group").encode("utf-8")
    sdisk = data.pop("server_disk").encode("utf-8")
    ssystem = data.pop("server_system").encode("utf-8")
    splatform = data.pop("server_platform").encode("utf-8")
    sservices = json.dumps(data)

    try:
        session.query(ServerGroup).filter_by(sservername=sservername).one()
        existed = {"Status": "Error", "Reason": "Server {0} Already Existed".format(sservername)}
        return render_template("error.html", messages=existed), 499
    except:
        try:
            customer_entry = session.query(CustomerGroup).filter_by(name=sgroup).one()
            server = ServerGroup(
                sservername=sservername,
                susername=susername,
                spassword=spassword,
                sip=sip,
                sport=sport,
                sfunction=sfunction,
                slvm=slvm,
                sgroup=sgroup,
                sdisk=sdisk,
                ssystem=ssystem,
                splatform=splatform,
                sservices=sservices,
                owner=customer_entry
            )
            session.add(server)
            session.commit()
            return redirect("http://localhost:5000", code=302)
        except:
            errors = {"Status": "500", "info": "Failed to add server {0}".format(sservername), "Reason": "Internal Error"}
            return render_template("error.html", messages=errors), 500



@app.route('/plus_customer', methods=["POST"])
def plus_customer():
    customer_name = request.form.get("customer_name")
    contact1 = request.form.get("customer_first_contact")
    phone1 = request.form.get("first_phone")
    contact2 = request.form.get("customer_second_contact")
    phone2 = request.form.get("second_phone")
    # Check if exist
    try:
        session.query(CustomerGroup).filter_by(name=customer_name).one()
        existed = {"Status": "Error", "Reason": "{0} Already Existed".format(customer_name)}
        return render_template("error.html", messages=existed), 499
    except:
        try:
            customer = CustomerGroup(name=customer_name, contact1=contact1, phone1=phone1, contact2=contact2, phone2=phone2)
            session.add(customer)
            session.commit()
            return redirect("http://localhost:5000", code=302)
        except:
            errors = {"Status": "500", "info": "Failed to add Customer {0}".format(customer_name), "Reason": "Internal Error"}
            return render_template("error.html", messages=errors), 500


@app.route('/s_delete', methods=['POST'])
def delete():
    servername = request.form.get('server_delete')
    ServerToDelete = session.query(ServerGroup).filter_by(sservername=servername).one()
    # try:
    #     session.delete(ServerToDelete)
    #     session.commit()
    # except Exception, e:
    #     errors = {"Status": "500", "info": "Failed to delete server {0}".format(servername), "Reason": "Internal Error->Database"}
    #     return render_template("error.html", messages=errors), 500

    # return jsonify(ServerToDelete.sgroup)
    return jsonify("CNC")

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
