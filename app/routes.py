from app import app, db
from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import current_user, login_user, login_required, logout_user
from app.forms import RegistrationForm, LoginForm, CreateTeam
from app.models import User, Team, TeamMember
import math, random

def generateCode():
	string = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
	OTP = "" 
	length = len(string)
	for i in range(6):
		OTP += string[math.floor(random.random() * length)] 
	return OTP  

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template("index.html")
 
@app.route('/register', methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User( 
                email=form.email.data.lower(), 
                fname=form.fname.data,
                lname=form.lname.data,
                verify=generateCode()
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
        return redirect(url_for('dashboard'))
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
@login_required
def dashboard():
    return render_template('dashboard.html', title="Dashboard", user=current_user)

@app.route('/create_team', methods=['GET', 'POST'])
@login_required
def create_team():
    form = CreateTeam()
    if request.method == 'POST':
        if form.validate_on_submit():
            
            team_code = generateCode()
            team = Team( 
                tname=form.tname.data, 
                tdesc=form.tdesc.data,
                tadmin=current_user.id,
                tcode=team_code
            )
            db.session.add(team)
            db.session.commit()
            
            team = team.query.filter_by(tcode=team_code).first()
            
            member = TeamMember(
                tid = team.id,
                mid = current_user.id
            )
            db.session.add(member)
            db.session.commit()

            return render_template('success_team.html')
        return jsonify(data=form.errors)
    return render_template('create_team.html', title="Create team", user=current_user, form=form)
