from flask import Flask
#For reading cookies
from flask import request
#For storing cookies
from flask import make_response
import functools
from flask import (
    current_app, flash, g, redirect, render_template, request, session, url_for
)
#for authentication
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config.from_mapping(SECRET_KEY='dev')
app.add_url_rule('/', endpoint='index')
credDictionary = dict();
    
def credentialsVerification(passedUsername, passedPassword):
    return true

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        if username in credDictionary:
            userpass = credDictionary.get('username')
            print("user is" + username + " " + userpass)
            if check_password_hash(userpass, password):
                print("password good")
            else:
                error = 'Incorrect password.'
        if error is None:
            session.clear()
            #session['user_id'] = username['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('login.html')

@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            credDictionary['username'] = generate_password_hash('password', "sha256")
            print("hashed.")
        else:
            return redirect(url_for("login"))
        flash(error)
    return render_template('register.html')
