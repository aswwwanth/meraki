from app import app, db
from flask import render_template, flash, redirect, url_for, request, flash, jsonify
from flask_login import current_user, login_user, login_required, logout_user
from app.forms import RegistrationForm, LoginForm, CreateTeam, JoinTeam
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
 
@app.route('/register/', methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data.lower()).first()
            if user is not None:
                return jsonify(data={'username', 'Username already exists.'})
            user = User( 
                email=form.email.data.lower(), 
                fname=form.fname.data,
                username=form.username.data.lower(),
                lname=form.lname.data,
                verify=generateCode()
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            return render_template('display_message.html')
        return jsonify(data=form.errors)

    return render_template('register.html', title="Register", form=form)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data.lower()).first()
            if user is None or not user.check_password(form.password.data):
                return jsonify(data={'error': 'Invalid username or Password'})
            login_user(user)
            return jsonify(data={'status': 200})
        return jsonify(data={'error': 'Both username and password is required.'})
    
    return render_template('login.html', title="Login", form=form)
 
@app.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard/')
@app.route('/dashboard/teams/')
@login_required
def dashboard():
    teams = db.session.query(Team, TeamMember).filter(Team.id == TeamMember.tid, TeamMember.mid == current_user.id).all()
    return render_template('dashboard-teams.html', title="Teams", user=current_user, teams=teams)

@app.route('/dashboard/chat/')
@login_required
def dashboard_chat():
    return render_template('dashboard-chat.html', title="Chat");

@app.route('/dashboard/tasks/')
@login_required
def dashboard_tasks():
    return render_template('dashboard-tasks.html', title="Tasks");

@app.route('/team/create/', methods=['GET', 'POST'])
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

            return render_template('success_team.html', tcode=team_code)
        return jsonify(data=form.errors)

    return render_template('create_team.html', title="Create team", user=current_user, form=form)

@app.route('/team/join/', methods=['GET', 'POST'])
@login_required
def join_team():
    form = JoinTeam()
    if request.method == 'POST':
        if form.validate_on_submit():
            team = Team.query.filter_by(tcode=form.tcode.data).first()
            if team is None:
                return jsonify(data={'tcode': 'Team doesnt exist.'})
            
            team = team.query.filter_by(tcode=form.tcode.data).first()

            member = TeamMember(
                tid = team.id,
                mid = current_user.id
            )
            db.session.add(member)
            db.session.commit()
            flash("You have successfully joined the team " + team.tname)
            print(team)
            return jsonify(data={'status': 200}) 
        return jsonify(data=form.errors) 
    
    return render_template('join_team.html', title="Join team", user=current_user, form=form)

@app.route('/team/add/<tcode>/', methods=['GET', 'POST'])
@login_required
def add_team_member(tcode):
    team = Team.query.filter_by(tcode=tcode).first()
    if current_user.id == team.tadmin:
        if request.method == 'POST':
            user_list = request.form.getlist('users[]')
            for uid in user_list:
                check_user = TeamMember.query.filter_by(mid=uid,tid=team.id).first()
                if check_user is None:
                    # print(request.form.get('team'))
                    member = TeamMember(
                        tid = request.form.get('team'),
                        mid = uid
                    )
                    db.session.add(member)
                    db.session.commit()
            return jsonify(data={'status': 200})
        return render_template('add_member.html', team=team)
    else:
        return "Access denied."

@app.route('/team/delete/<tcode>/', methods=['GET', 'POST'])
@login_required
def delete_team(tcode):
    team = Team.query.filter_by(tcode=tcode).first()
    if current_user.id == team.tadmin:
        if request.method == 'POST':
            team = Team.query.filter_by(tcode=tcode).first()
            TeamMember.query.filter_by(tid=team.id).delete()
            Team.query.filter_by(id=team.id).delete()
            db.session.commit()
            message = "Team " + team.tname + " is successfully deleted and all the data associated with it was removed from our system."
            flash(message)
            return redirect(url_for('dashboard'))
        return render_template('delete_team.html', team=team)
    else:
        return "Access denied."

@app.route('/team/<tcode>/')
@app.route('/team/<tcode>/chat/')
@login_required
def team_chat(tcode):
    team = Team.query.filter_by(tcode=tcode).first()
    boolAdmin = False;
    if current_user.id == team.tadmin:
        boolAdmin = True;
    return render_template('tabs/chat-tab.html', checkAdmin=boolAdmin, team=team)

@app.route('/team/<tcode>/')
@app.route('/team/<tcode>/tasks/')
@login_required
def team_tasks(tcode):
    team = Team.query.filter_by(tcode=tcode).first()
    boolAdmin = False;
    if current_user.id == team.tadmin:
        boolAdmin = True;
    return render_template('tabs/tasks-tab.html', checkAdmin=boolAdmin, team=team)

@app.route('/team/<tcode>/')
@app.route('/team/<tcode>/members/')
@login_required
def team_members(tcode):
    
    team = Team.query.filter_by(tcode=tcode).first()
    boolAdmin = False;
    if current_user.id == team.tadmin:
        boolAdmin = True;

    get_ids = TeamMember.query.filter_by(tid=team.id).all()
    user_list = []
    for u in get_ids:
        user_list.append(u.mid)

    get_details = User.query.filter(User.id.in_(user_list)).all()
    
    return render_template('tabs/members-tab.html',checkAdmin=boolAdmin, team=team, members=get_details)


@app.route('/users/search', methods=['GET'])
@login_required
def search_user():
    responseObject = []
    user = request.args.get('user')
    team = request.args.get('team')
    # print(user, team)
    search = "%" + user + "%"
    user = User.query.filter(User.username.like(search)).all()
    if team is None:
        for u in user:
            responseObject.append({
                'uid': u.id,
                'username': u.username,
                'fname': u.fname,
                'lname': u.lname,
                'email': u.email
            })
    else:
        for u in user:
            check_team = TeamMember.query.filter_by(tid=team, mid=u.id).first()
            if check_team is None:
                responseObject.append({
                    'uid': u.id,
                    'username': u.username,
                    'fname': u.fname,
                    'lname': u.lname,
                    'email': u.email
                })

    return jsonify(responseObject)

@app.route('/members', methods=['GET'])
@login_required
def get_members():
    
    responseObject = []
    team = request.args.get('team')
    team = Team.query.filter_by(tcode=team).first()
    if team is None:
        return jsonify(data={'message' : 'Team not found'})

    get_ids = TeamMember.query.filter_by(tid=team.id).all()
    user_list = []
    for u in get_ids:
        user_list.append(u.mid)

    get_details = User.query.filter(User.id.in_(user_list)).all()
    
    for e in get_details:
        responseObject.append({
            'uid': e.id,
            'username': e.username,
            'fname': e.fname,
            'lname': e.lname,
            'email': e.email
        })

    return jsonify(responseObject)

