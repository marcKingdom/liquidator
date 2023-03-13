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
# create the sql extension
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
with app.app_context():
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
            print(jsonData['account'])
            user = g.user
            user.walletConnect = True
            user.walletAddress = int(jsonData['account'], 16)
            db.session.commit()
            return {
                'response' : 'user account accepted'
            }
        else:
            print("data sent" + g.user.walletAddress)
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
            #return redirect(url_for("index", id=user.id))
        flash(error)
    return render_template('register.html')
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))
