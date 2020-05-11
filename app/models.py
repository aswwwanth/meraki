from app import db
from app import login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import datetime, math, random

class User(db.Model, UserMixin):
	
	username = db.Column(db.String(256), primary_key=True)
	email = db.Column(db.String(256),index=True, unique=True)
	name = db.Column(db.String(75), nullable=False)
	password_hash = db.Column(db.String(256))
	verify = db.Column(db.String(512))
	isVerified = db.Column(db.Boolean, default=False)
	chatroom = db.Column(db.String(512), unique=True, index=True)
	
	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	def get_id(self):
           return (self.username)

@login.user_loader
def load_user(id):
	return User.query.get(id)

class Team(db.Model):

	tcode = db.Column(db.String(256), primary_key=True)
	tname = db.Column(db.String(256))
	tdesc = db.Column(db.Text)
	tadmin = db.Column(db.String(256), db.ForeignKey(User.username))
	chatroom = db.Column(db.String(256), unique=True)
	
class TeamMember(db.Model):

	team_code = db.Column(db.String(256), db.ForeignKey(Team.tcode, ondelete='CASCADE'), primary_key=True)
	musername = db.Column(db.String(256), db.ForeignKey(User.username), primary_key=True)

class PrivateChat(db.Model):

	id = db.Column(db.Integer, primary_key=True, autoincrement=True, index=True)
	sender_username = db.Column(db.String(256), db.ForeignKey(User.username), index=True)
	recipient_username = db.Column(db.String(256), db.ForeignKey(User.username), index=True)
	message = db.Column(db.Text)
	time = db.Column(db.DateTime)

class TeamChat(db.Model):

	id = db.Column(db.Integer, primary_key=True, autoincrement=True, index=True)
	sender_username = db.Column(db.String(256), db.ForeignKey(User.username), index=True)
	team_code = db.Column(db.String(256), db.ForeignKey(Team.tcode, ondelete='CASCADE'))
	message = db.Column(db.Text)
	time = db.Column(db.DateTime)

# class SeenPrivate(db.Model):

# 	from_id = db.Column(db.String(256), db.ForeignKey(User.username), primary_key=True)
# 	recipient_username = db.Column(db.String(256), db.ForeignKey(User.username), primary_key=True, index=True)
# 	last_read = db.Column(db.Integer, db.ForeignKey(PrivateChat.id))

# class SeenTeam(db.Model):

# 	team_code = db.Column(db.String(256), db.ForeignKey(Team.tcode), primary_key=True)
# 	recipient_username = db.Column(db.String(256), db.ForeignKey(User.username), primary_key=True, index=True)
# 	last_read = db.Column(db.Integer, db.ForeignKey(TeamChat.id))

class Tasks(db.Model):
	task_code = db.Column(db.String(256), primary_key=True)
	task_admin = db.Column(db.String(256), db.ForeignKey(User.username))
	team_code = db.Column(db.String(256), db.ForeignKey(Team.tcode, ondelete='CASCADE'))
	title = db.Column(db.String(256))
	tag = db.Column(db.String(256))
	desc = db.Column(db.Text)
	created_on = db.Column(db.DateTime)
	deadline = db.Column(db.DateTime)
	completed_on = db.Column(db.DateTime)
	completed_by = db.Column(db.String(256), db.ForeignKey(User.username))
	status = db.Column(db.Boolean, default=False)

class Milestones(db.Model):
	id = db.Column(db.Integer, primary_key=True, autoincrement=True, index=True)
	task_code = db.Column(db.String(256), db.ForeignKey(Tasks.task_code, ondelete='CASCADE'))
	title = db.Column(db.String(256))
	status = db.Column(db.Boolean, default=False)

class TasksAssigned(db.Model):
	user = db.Column(db.String(256), db.ForeignKey(User.username), primary_key=True)
	task_code = db.Column(db.String(256), db.ForeignKey(Tasks.task_code, ondelete='CASCADE'), primary_key=True)

class TaskProgressLog(db.Model):
	id = db.Column(db.Integer, primary_key=True, autoincrement=True, index=True)
	task_code = db.Column(db.String(256), db.ForeignKey(Tasks.task_code, ondelete='CASCADE'))
	log_by = db.Column(db.String(256), db.ForeignKey(User.username))
	time = db.Column(db.DateTime)
	log = db.Column(db.Text)