# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, jsonify

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, CustomerGroup, ServerGroup, PasswordGroup

from Crypto.Cipher import XOR
import base64, json

from sender import publish
from translate import encode, services_check

from get_info import server_info

import redis
redis_session0 = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
redis_session1 = redis.StrictRedis(host='127.0.0.1', port=6379, db=1)


# Store server's dynamic data
redis_session2 = redis.StrictRedis(host='127.0.0.1', port=6379, db=2)
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


# App index page
@app.route('/')
def index():
    return render_template("index.html")


# List all customers
@app.route('/customer', methods=['GET', 'POST'])
def customer():
    customers = []
    idd = request.form.get('iid')
    if idd == "1":
        try:
            customer_group = session.query(CustomerGroup).all()
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
            checkstatus = redis_session1.get(s.sservername)
            if checkstatus == "OKay" or checkstatus == "InProgress":
                status = 1
            else:
                status = 0

            single = {
                "sservername": s.sservername,
                "sip": s.sip,
                "sport": s.sport,
                "sfunction": s.sfunction,
                "ssystem": s.ssystem,
                "splatform": s.splatform,
                "status": status,
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
            "status": 0,
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
        services = json.loads(info.sservices)
        install = services_check(services)

        dynamic = json.loads(redis_session2.get(server))

        print dynamic

        backup_dirs = []
        for i in [1, 2, 3, 4]:
            backup_dir = "backup_folder"+str(i)
            if encode(services[backup_dir]) != "-":
                backup_dirs.append(encode(services[backup_dir]))

        single = {
            "sname": info.sservername,
            "sip": info.sip,
            "sport": info.sport,
            "slvm": info.slvm,
            "sdisk": info.sdisk,
            "sbackup_dest": services["backup_destination"],
            "szabbix_proxy": services["zabbix_proxy"],
            "sbackup_dirs": backup_dirs,
            "sservices": install,
            "scpu": dynamic["cpu"],
            "smem": dynamic["mem"],
            "spri_ip": dynamic["spri_ip"],
        }
    except:
        single = {
            "sname": "query-database-error",
            "sip": "0.0.0.0",
            "sport": "0",
            "slvm": "0",
            "sdisk": "0",
            "sbackup_dest": "0",
            "szabbix_proxy": "0",
            "sbackup_dirs": "-",
            "sservices": "-",
            "scpu": "-",
            "smem": "-",
            "spri_ip": "-"
        }
    print single
    return render_template("detailed_info.html", info=single)


# Obtain the password info per server name from the request header.
@app.route('/pw')
def pw():
    engine = create_engine('mysql://root:lambert@127.0.0.1:3306/cg')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session1 = DBSession()
    sname = request.args.get("sname")
    try:

        sid = session.query(ServerGroup).filter_by(sservername=sname).one().id
        passwd = session1.query(PasswordGroup).filter_by(sid=sid).one()

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
            "ncadmin": "query-database-error or No entry",
            "root": "query-database-error or No entry",
            "gpg_key": "query-database-error or No entry",
            "nccheckdb": "query-database-error or No entry",
            "ncbackupdb": "query-database-error or No entry",
            "ncdba": "query-database-error or No entry"
        }
    session1.close()
    return render_template("pw_info.html", pw=info)


# Obtain Plus info
@app.route('/plus_server', methods=["POST"])
def plus_server():
    data = request.form.to_dict()
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
            session.close()
            return redirect("http://localhost:5000", code=302)
        except:
            errors = {"Status": "500", "info": "Failed to add server {0}".format(sservername), "Reason": "Internal Error"}
            return render_template("error.html", messages=errors), 500


# Obtain Plus info via Ajax, but via post is not safe, so I gave up.
@app.route('/s_plus', methods=["POST"])
def s_plus():
    data = request.args.to_dict()

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
            return jsonify(sgroup)
        except:
            errors = {"Status": "500", "info": "Failed to add server {0}".format(sservername),
                      "Reason": "Internal Error"}
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
            session.close()
            return redirect("http://localhost:5000", code=302)
        except:
            errors = {"Status": "500", "info": "Failed to add Customer {0}".format(customer_name), "Reason": "Internal Error"}
            return render_template("error.html", messages=errors), 500


@app.route('/s_delete', methods=['POST'])
def s_delete():
    servername = request.form.get('server_delete')
    server_delete = session.query(ServerGroup).filter_by(sservername=servername).one()
    server_password_delete = session.query(PasswordGroup).filter_by(sid=server_delete.id).one()
    try:
        try:
            session.delete(server_password_delete)
            session.commit()
        except:
            pass

        session.delete(server_delete)
        session.commit()
        # session.close()
    except Exception, e:
        errors = {"Status": "500", "info": "Failed to delete server {0}".format(servername), "Reason": "Internal Error->Database"}
        return render_template("error.html", messages=errors), 500

    return jsonify(server_delete.sgroup)

@app.route('/s_launch', methods=['POST'])
def s_launch():
    session = DBSession()

    server_name = request.form.get('server_name')

    # Obtain some server informations and store to database
    server = session.query(ServerGroup).filter_by(sservername=server_name).one()
    try:
        dynamic_info = server_info(server.sip, int(server.sport), server.susername, server.spassword)
        server.sdynamicinfo = dynamic_info
        redis_session2.set(server_name, dynamic_info)
    except:
        print "Can't connect to {0}".format(server_name)

    # Check the server if exist in redis
    CheckExist = redis_session1.get(server_name)
    if CheckExist is not None:
        if CheckExist == "FAILED" or CheckExist == "FAILED_DIRECTLY":
            redis_session1.set(server_name, "InProgress")
        if CheckExist == "OKay":
            # TODO, Debug, so didn't return directly when it was successful.
            redis_session1.set(server_name, "InProgress")

            # return jsonify("Already run, and it was successful!!!")
    else:
        redis_session1.set(server_name, "InProgress")

    publish(server_name)
    return jsonify(server.sgroup)


# Show task status
@app.route('/show_tasks')
def show_tasks():
    status = []
    try:
        keys = redis_session1.keys()
        for k in keys:
            s = {k: redis_session1.get(k)}
            status.append(s)
            s = {}

    except Exception as e:
        print e
        s = {"error": e}
        status.append(s)

    return render_template("show_tasks.html", status=status)


# Show task status
@app.route('/logs')
def logs():
    name = request.args.get("name")
    try:
        log = redis_session0.get(name)
    except Exception as e:
        log = e

    return render_template("error.html", messages=log)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000, threaded=True)
