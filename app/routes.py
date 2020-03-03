from app import app, db
from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import current_user, login_user, login_required, logout_user
from app.forms import RegistrationForm, LoginForm
from app.models import User
import math, random

def generateOTP():
	string = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
	OTP = "" 
	length = len(string)
	for i in range(6):
		OTP += string[math.floor(random.random() * length)] 
	return OTP 

@app.route('/')
def home():
    if current_user.is_authenticated:
        return current_user.fname
    return "TESTING"
 
@app.route('/register', methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User( 
                email=form.email.data.lower(), 
                fname=form.fname.data,
                lname=form.lname.data,
                verify=generateOTP()
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            return render_template('display_message.html')
        return jsonify(data=form.errors)

    return render_template('register.html', title="Register", form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is None or not user.check_password(form.password.data):
            return jsonify(data={'error': 'Invalid username or Password'})
        login_user(user)
        return jsonify(data={'status': 200})
    return render_template('login.html', title="Login", form=form)
 
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    return ("Welcome " + current_user.fname + "!")
    