from flask import Flask, render_template, request, redirect, jsonify, url_for, g, flash,abort

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from models import Base, CustomerGroup, ServerGroup

app = Flask(__name__)

# Create Database session
engine = create_engine('mysql://root:lambert@127.0.0.1:3306/customergroup')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


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


@app.route('/keepass')
def keepass():
    return render_template("keepass.html")



if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
