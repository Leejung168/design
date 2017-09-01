from flask import Flask, render_template, request, redirect, jsonify, url_for, g, flash,abort

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from models import Base, CustomerGroup, ServerGroup

app = Flask(__name__)

#Create Database session
engine = create_engine('mysql://root:lambert@127.0.0.1:3306/customergroup')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


#Index Page
@app.route('/')
def index():
    return render_template("index.html")

#Get Customer List
@app.route('/get_cu_list/', methods=['POST'])
def get_cu_list():
    customers=[]
    id = request.args.get('id')
    if id==1:
        try:
            customer_group=session.query(CustomerGroup).all()
            for c in customer_group:
                customers.append(c.name)
        except:
            customers.append("Error")
    else:
       customers.append("Error")
    return jsonify(customers)

#Customer--->Servers Page
@app.route('/server')
def server():
    return render_template("server.html")

#Keepass Page
@app.route('/keepass')
def keepass():
    return render_template("keepass.html")



if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)