from flask import Flask
#database
from flask_sqlalchemy import SQLAlchemy
#For reading cookies
from flask import request
#For storing cookies
from flask import make_response
import functools
from flask import (
    current_app, flash, g, redirect, render_template, request, jsonify, session, url_for
)
#for authentication
from werkzeug.security import check_password_hash, generate_password_hash
#for turning ansynchronous request data back into an object
import json
#for sending tokens
#from https://paohuee.medium.com/interact-binance-smart-chain-using-python-4f8d745fe7b7
from web3 import Web3
import time
import requests
from PriceMachine import calculateWalletValue
#for binance smart chain network
bsc = "https://bsc-dataseed.binance.org/"
url_eth = "https://api.bscscan.com/api"
web3 = Web3(Web3.HTTPProvider(bsc))

if web3.is_connected():
    print("connected to binance network")
else:
    print("unable to connect to binance network!")
# create the sql connection
db = SQLAlchemy()
app = Flask(__name__)
app.config.from_mapping(SECRET_KEY='dev')
app.add_url_rule('/', endpoint='index')
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://postgres:password@localhost:5432/liquidbase"
db.init_app(app)
#user data class
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String)
    walletAddress = db.Column(db.String)
    walletConnected = db.Column(db.Boolean)
    walletValue = db.Column(db.Float)
    #adress, key, token, sellPrice, latency
    accounts = db.relationship('Account', backref='user')
#in future new bank accounts will be opened on binance smart chain when an account is opened
#accounts will hold funds that will be liquidated if certain price conditions are mt
class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.Integer, db.ForeignKey('user.id'))
    address = db.Column(db.String)
    key = db.Column(db.String)
    token = db.Column(db.String)
    latency = db.Column(db.Integer)
    sellPrice = db.Column(db.String)
with app.app_context():
    #uncomment following line to clean database on startup
    #db.drop_all()
    db.create_all()
#before every request the database and g object (instance object) must be synced
@app.before_request
def load_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = db.session.execute(db.select(User).filter_by(id=user_id)).scalar_one()

@app.route("/", methods=["GET", "POST"])
@app.route('/index', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        jsonData = request.get_json()
        if 'account' in jsonData:
            #print(jsonData['account'])
            user = g.user
            user.walletConnect = True
            user.walletAddress = int(jsonData['account'], 16)
            user.walletValue = float(calculateWalletValue(user.walletAddress))
            #print("wallet value")
            #print(user.walletValue)
            db.session.commit()
            #this is a temporary measure, in future a message will be shown to the user
            return {
                'response' : 'user account accepted'
            }
        if 'getWalletValues' in jsonData:
            print("getting wallet values")
            calculateWalletValue(g.user.walletAddress)
            return render_template('index.html')          
        else:
            print("data sent" + g.user.walletAddress)
            #this is a temporary measure, in future a message will be shown to the user
            return {
                'response' : 'user data accepted'
            }
    if 'user_id' in session:
        print("logged in")
    return render_template('index.html')

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = db.session.execute(db.select(User).filter_by(username=username)).scalar_one()
        if username == user.username:
            if not check_password_hash(user.password, 'password'):
                error = 'Incorrect password.'
        else:
            error = "no user"
        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('index'))
        flash(error)
    return render_template('login.html')

@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        name = request.form['username']
        passW = request.form['password']
        error = None
        if not name:
            error = 'Username is required.'
        elif not passW:
            error = 'Password is required.'
        if error is None:
            user = User(
                username=request.form["username"],
                password = generate_password_hash('password', "sha256"),
                walletConnected = False,
                walletAddress = -1
            )
            db.session.add(user)
            db.session.commit()
            error = "Account created."
            print("account created")
            return redirect(url_for("index"))
        flash(error)
    return render_template('register.html')
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/openAccount', methods=('GET', 'POST'))
def openAccount():
    if request.method == 'POST':
        user = g.user
        newAccount = 0
        newKey = 0
        coin = request.form['token']
        latency = request.form['latency']
        error = None
        if not coin:
            error = 'coin is required.'
        elif not latency:
            error = 'latency is required.'
        if error is None:
            account = Account(
                owner = user.id,
                address = newAccount,
                key = newKey,
                token = request.form["token"],
                latency = request.form["latency"],
            )
            db.session.add(account)
            db.session.commit()
            return redirect(url_for("index"))
        flash(error)
    return render_template('openAccount.html')

