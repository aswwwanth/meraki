from app import app, db
from flask import render_template, redirect, url_for, request, flash, jsonify
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
    return "TESTING"

@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', title="Login", form=form)

@app.route('/register', methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if request.method == 'GET':
        return render_template('register.html', title="Register", form=form)
    elif request.method == "POST":
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

    return "403"
