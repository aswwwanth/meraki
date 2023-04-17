from app import app, db
from flask import render_template, flash, redirect, url_for, request, flash, jsonify
from functools import wraps
from sqlalchemy import func
from flask_login import current_user, login_user, login_required, logout_user
from app.forms import *
from app.models import *
import math, random, uuid

def generateCode():
	return uuid.uuid4().hex

def is_member():
    def is_member_wrap(func):    
        @wraps(func)
        def d_view(tcode, *args, **kwargs):
            isMember = TeamMember.query.filter_by(team_code=tcode,musername=current_user.username).first()
            if isMember is not None:
                return func(tcode, *args, **kwargs)
            flash('You are not a part of the team.')
            return redirect(url_for('dashboard'))
        return d_view
    return is_member_wrap

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

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
            user = User( 
                username=form.username.data.lower(),
                email=form.email.data.lower(), 
                name=form.name.data,
                verify=generateCode(),
                chatroom=generateCode()
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
                return jsonify(data={'error': 'Invalid username or password'})
            login_user(user)
            return jsonify(data={'status': 200})
        return jsonify(data={'error': 'Both username and password are required'})
    
    return render_template('login.html', title="Login", form=form)
 
@app.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard/')
@app.route('/dashboard/teams/')
@login_required
def dashboard():
    teams = db.session.query(Team, TeamMember).filter(Team.tcode==TeamMember.team_code, TeamMember.musername==current_user.username).all()
    return render_template('dashboard-teams.html', title="Teams", user=current_user, teams=teams)

@app.route('/dashboard/chat/')
@login_required
def dashboard_chat():
    return render_template('dashboard-chat.html', title="Chat");

@app.route('/dashboard/tasks/')
@login_required
def dashboard_tasks():
    
    tasks = db.session.query(Tasks, TasksAssigned, Team).filter(Team.tcode==Tasks.team_code, TasksAssigned.user==current_user.username, Tasks.task_code==TasksAssigned.task_code).order_by(Tasks.deadline).all()
    
    tasks_data = {}
    tasks_completed = 0
    tasks_pending = 0
    tasks_created = 0
    
    for task in tasks:
        if task.Tasks.deadline not in tasks_data:
            tasks_data[task.Tasks.deadline] = []
        tasks_data[task.Tasks.deadline].append((task.Tasks, task.Team.tname))
        if task.Tasks.task_admin == current_user.username:
            tasks_created += 1
        if task.Tasks.status == False:
            tasks_pending += 1
        else:
            tasks_completed += 1

    return render_template(
        'dashboard-tasks.html', 
        title="Tasks", 
        tasks=tasks_data, 
        datetimenow=datetime.datetime.now(),
        tasks_pending=tasks_pending,
        tasks_completed=tasks_completed,
        tasks_created=tasks_created
    );

@app.route('/team/create/', methods=['GET', 'POST'])
@login_required
def create_team():
    form = CreateTeam()
    if request.method == 'POST':
        if form.validate_on_submit():
            
            team_code = generateCode()

            team = Team( 
                tcode=team_code,
                tname=form.tname.data, 
                tdesc=form.tdesc.data,
                tadmin=current_user.username,
                chatroom=generateCode()
            )
            
            db.session.add(team)
            db.session.commit()
            
            member = TeamMember(
                team_code = team.tcode,
                musername = current_user.username
            )

            db.session.add(member)
            db.session.commit()
            
            flash("Team " + form.tname.data + " successfully created ")
            
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

            member = TeamMember(
                team_code = form.tcode.data,
                musername = current_user.username
            )
            
            db.session.add(member)
            db.session.commit()

            flash("You have successfully joined the team " + team.tname)
            
            return jsonify(data={'status': 200}) 
        return jsonify(data=form.errors) 
    
    return render_template('join_team.html', title="Join team", user=current_user, form=form)

@app.route('/team/leave/<tcode>/', methods=['GET', 'POST'])
@login_required
@is_member()
def leave_team(tcode):
    
    team = Team.query.filter_by(tcode=tcode).first()
    if current_user.username == team.tadmin:
        return jsonify(data={'message': 'You cant leave the team, you are the admin!!!'})

    TeamMember.query.filter_by(musername=current_user.username, team_code=team.tcode).delete()
    db.session.commit()
    flash("Successfully left team " + team.tname)

    return redirect(url_for('dashboard'))

@app.route('/team/add/<tcode>/', methods=['GET', 'POST'])
@login_required
def add_team_member(tcode):
    team = Team.query.filter_by(tcode=tcode).first()
    if current_user.username == team.tadmin:
        if request.method == 'POST':
            user_list = request.form.getlist('users[]')
            for uname in user_list:
                check_user = TeamMember.query.filter_by(musername=uname,team_code=team.tcode).first()
                if check_user is None:
                    member = TeamMember(
                        team_code = team.tcode,
                        musername = uname
                    )
                    db.session.add(member)
                    db.session.commit()

            flash("Successfully added")
            return jsonify(data={'status': 200})
        return render_template('add_member.html', team=team)
    else:
        return jsonify(data={'message': 'Access denied.'})

@app.route('/team/remove', methods=['POST'])
@login_required
def remove_team_member():
    team = request.args.get('team')
    user = request.args.get('user')
    team = Team.query.filter_by(tcode=team).first()
    if current_user.username == team.tadmin:
        print("user = ", user)
        print("Team code = ", team.tcode)
        member = TeamMember.query.filter_by(musername=user, team_code=team.tcode).first()
        if member is not None:
            print("HERE ", member)
            TeamMember.query.filter_by(musername=user, team_code=team.tcode).delete()
            db.session.commit()
            flash("User successfully removed.")
        return redirect('/team/' + team.tcode + '/members/')
    else:
        return jsonify(data={'message': 'Access denied.'})

@app.route('/team/delete/<tcode>/', methods=['GET', 'POST'])
@login_required
def delete_team(tcode):
    team = Team.query.filter_by(tcode=tcode).first()
    if current_user.username == team.tadmin:
        if request.method == 'POST':
            Team.query.filter_by(tcode=team.tcode).delete()
            db.session.commit()
            message = "Team " + team.tname + " is successfully deleted and all the data associated with it was removed from our system."
            flash(message)
            return redirect(url_for('dashboard'))
        return render_template('delete_team.html', team=team)
    else:
        return jsonify(data={'message': 'Access denied.'})

@app.route('/team/<tcode>/')
@app.route('/team/<tcode>/chat/')
@login_required
@is_member()
def team_chat(tcode):
    team = Team.query.filter_by(tcode=tcode).first()
    return render_template('tabs/chat-tab.html', team=team)

@app.route('/team/<tcode>/')
@app.route('/team/<tcode>/tasks/')
@login_required
@is_member()
def team_tasks(tcode):
    team = Team.query.filter_by(tcode=tcode).first()
    tasks = Tasks.query.filter_by(team_code=tcode).order_by(Tasks.deadline).all()
    return render_template('tabs/tasks-tab.html', team=team, tasks=tasks, datetimenow=datetime.datetime.now())

@app.route('/team/<tcode>/tasks/<task_code>/')
@login_required
@is_member()
def team_tasks_details(tcode, task_code):
    team = Team.query.filter_by(tcode=tcode).first()
    task = Tasks.query.filter_by(task_code=task_code).first()
    milestones = Milestones.query.filter_by(task_code=task_code).order_by(Milestones.id).all()
    assigneesData = TasksAssigned.query.filter_by(task_code=task_code).all()
    task_progress = TaskProgressLog.query.filter_by(task_code=task_code).order_by(TaskProgressLog.time).all()
    assignees = []
    for assignee in assigneesData:
        assignees.append(assignee.user)
    return render_template(
        'tabs/tasks-tab-details.html',
        team=team, 
        task=task, 
        milestones=milestones, 
        assignees =assignees, 
        datetimenow=datetime.datetime.now(),
        task_progress=task_progress
    )

@app.route('/team/<tcode>/task/<task_code>/update/milestone/<mid>/', methods=['POST'])
@login_required
@is_member()
def update_milestone(tcode,task_code, mid):
    
    milestone = Milestones.query.filter_by(id=mid).first()
    log = "Nothing"
    
    if(request.form['state'] == '1'):
        milestone.status = True
        log = " marked as complete"
    else:
        milestone.status = False
        log = " was reopened"

    progress = TaskProgressLog(
        task_code=task_code,
        log="<b>\"" + milestone.title + "\"</b> " + log,
        log_by=current_user.username,
        time=datetime.datetime.now()
    )
    db.session.add(progress)
    db.session.commit()

    return jsonify({'status': 200})

@app.route('/team/<tcode>/task/<task_code>/update/', methods=['POST'])
@login_required
@is_member()
def update_task_progress(tcode,task_code):
    
    datetimenow = datetime.datetime.now()
    task = Tasks.query.filter_by(task_code=task_code).first()
    task.status = True
    task.completed_on = datetimenow
    task.completed_by = current_user.username
    progress = TaskProgressLog(
        task_code=task_code,
        log="Task completed ",
        log_by=current_user.username,
        time=datetimenow
    )
    db.session.add(progress)
    db.session.commit()

    return jsonify({'status': 200, 'message': 'Task completed by ' + current_user.username})

@app.route('/team/<tcode>/task/add/', methods=['GET', 'POST'])
@login_required
def add_task(tcode):
    team = Team.query.filter_by(tcode=tcode).first()
    if current_user.username == team.tadmin:
        if request.method == 'POST':
            code = generateCode()
            milestones = request.form.getlist('milestones[]')
            assigned = request.form.getlist('assigned[]')
            deadline = request.form['deadline']
            datetimenow = datetime.datetime.now()
            task = Tasks(
                task_code=code,
                task_admin=current_user.username,
                title=request.form['task-title'],
                desc=request.form['task-desc'],
                deadline=deadline,
                team_code=tcode,
                tag=request.form['task-tag'],
                created_on=datetimenow
            )
            db.session.add(task)
            db.session.commit()
            progress = TaskProgressLog(
                task_code=code,
                log="Task created ",
                log_by=current_user.username,
                time=datetimenow
            )
            db.session.add(progress)
            for m in milestones:
                milestone = Milestones(
                    task_code=code,
                    title=m
                )
                milestone_progress = TaskProgressLog(
                    task_code=code,
                    log="Milestone <b>\"" + m + "\"</b> added ",
                    log_by=current_user.username,
                    time=datetimenow
                )
                db.session.add(milestone_progress)
                db.session.add(milestone)
                
            for a in assigned:
                task_assign = TasksAssigned(
                    user=a,
                    task_code=code
                )
                assign_progress = TaskProgressLog(
                    task_code=code,
                    log="Task assigned to <b>@" + a + "</b> ",
                    log_by=current_user.username,
                    time=datetimenow
                )
                db.session.add(assign_progress)
                db.session.add(task_assign)
            db.session.commit()
            message = "Task " + request.form['task-title'] + " is successfully added"
            flash(message)
            return jsonify(data={'status': 200})
        return render_template('add_tasks.html', team=team)
    else:
        return jsonify(data={'message': 'Access denied.'})

@app.route('/team/<tcode>/tasks/<task_code>/delete/', methods=['GET', 'POST'])
@login_required
def delete_task(tcode, task_code):
    task = Tasks.query.filter_by(task_code=task_code).first()
    if current_user.username == task.task_admin:
        if request.method == 'POST':
            Tasks.query.filter_by(task_code=task_code).delete()
            db.session.commit()
            message = "Task " + task.title + " is successfully deleted and all the data associated with it was removed from our system."
            flash(message)
            return redirect(url_for('team_tasks', tcode=tcode))
        return render_template('delete_task.html', task=task, tcode=tcode)
    else:
        return jsonify(data={'message': 'Access denied.'})

@app.route('/team/<tcode>/')
@app.route('/team/<tcode>/members/')
@login_required
@is_member()
def team_members(tcode):

    team = Team.query.filter_by(tcode=tcode).first()
    get_details = db.session.query(User,TeamMember).filter(TeamMember.team_code==tcode,User.username==TeamMember.musername).all()
    
    return render_template('tabs/members-tab.html', team=team, members=get_details)

@app.route('/users/search/', methods=['GET'])
@login_required
def search_user():
    responseObject = []
    user = request.args.get('user')
    team = request.args.get('team')
    search = "%" + user + "%"
    user = User.query.filter(User.username.like(search)).all()
    if team is None:
        for u in user:
            if u.username != current_user.username:
                responseObject.append({
                    'username': u.username,
                    'name': u.name,
                    'email': u.email
                })
    else:
        for u in user:
            check_team = TeamMember.query.filter_by(team_code=team, musername=u.username).first()
            if check_team is None:
                responseObject.append({
                    'username': u.username,
                    'name': u.name,
                    'email': u.email
                })

    return jsonify(responseObject)

@app.route('/users/members/', methods=['GET'])
@login_required
def search_member():
    responseObject = []
    user = request.args.get('user')
    team = request.args.get('team')
    search = "%" + user + "%"
    user = User.query.filter(User.username.like(search)).all()
    for u in user:
        check_team = TeamMember.query.filter_by(team_code=team, musername=u.username).first()
        if check_team is not None:
            responseObject.append({
                'username': u.username,
                'name': u.name,
                'email': u.email
            })

    return jsonify(responseObject)

@app.route('/user/<username>/', methods=['GET'])
@login_required
def get_user_info(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return jsonify('Not found')
    return jsonify(data={'username': user.username, 'name': user.name})

def convert_time(time):
    db_time = time
    if(db_time.date() == datetime.datetime.today().date()):
        db_time = db_time.strftime("%I:%M %p")
    elif(db_time.year == datetime.datetime.today().year):
        db_time = db_time.strftime("%d %b %I:%M %p")
    else:
        db_time = db_time.strftime("%d %b %Y %I:%M %p")
    return db_time

# Messages
@app.route('/messages/team/<tcode>/', methods=['GET'])
@login_required
@is_member()
def get_team_messages(tcode):
    
    messages = TeamChat.query.filter_by(team_code=tcode).order_by(TeamChat.time.asc()).all()
    
    payLoad = []
    for m in messages:
        db_time = convert_time(m.time)
        payLoad.append({
            'username': m.sender_username,
            'message': m.message,
            'time': db_time
        })

    return jsonify(payLoad)

@app.route('/messages/private/<username>/', methods=['GET'])
@login_required
def get_private_messages(username):

    messages = db.session.query(PrivateChat).filter(((PrivateChat.sender_username==current_user.username) & (PrivateChat.recipient_username==username)) | ((PrivateChat.sender_username==username) & (PrivateChat.recipient_username==current_user.username))).order_by(PrivateChat.time.asc()).all()
    
    payLoad = []
    for m in messages:
        db_time = convert_time(m.time)        
        payLoad.append({
            'username': m.sender_username,
            'message': m.message,
            'time': db_time
        })

    return jsonify(payLoad)

@app.route('/messages/private/recent/', methods=['GET'])
@login_required
def get_private_recent():

    messages = db.session.execute("select * from private_chat a where id = (select max(id) from private_chat where (sender_username = a.sender_username and recipient_username = a.recipient_username) or (sender_username = a.recipient_username and recipient_username = a.sender_username)) and (sender_username = '"+ current_user.username +"' or recipient_username = '"+ current_user.username +"') order by time desc;")
    
    payLoad = []
    for m in messages:
        db_time = m[4]
        
        if(db_time.date() == datetime.datetime.today().date()):
            db_time = db_time.strftime("%I:%M %p")
        elif(db_time.year == datetime.datetime.today().year):
            db_time = db_time.strftime("%d %b")
        else:
            db_time = db_time.strftime("%b %Y")
        
        username = m[1]
        message = m[3]

        if username == current_user.username:
            username = m[2]
            message = 'You: ' + message

        payLoad.append({
            'username': username,
            'message': message,
            'time': db_time
        })

    return jsonify(payLoad)

@app.route('/video-demo/')
def video():
    return redirect('https://youtu.be/Qd0j6bbjSTE')