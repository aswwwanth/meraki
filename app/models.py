from app import db
from app import login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import datetime, math, random

class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True, autoincrement= True)
	email = db.Column(db.String(256),index=True)
	fname = db.Column(db.String(75), nullable=False)
	lname = db.Column(db.String(75))
	username = db.Column(db.String(256), unique=True)
	password_hash = db.Column(db.String(256))
	verify = db.Column(db.String(256))
	isVerified = db.Column(db.Boolean, default=False)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	def super(self):
		return self.email=='aswanth366@gmail.com'

@login.user_loader
def load_user(id):
	return User.query.get(id)

class Team(db.Model):
	
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	tcode = db.Column(db.String(256))
	tname = db.Column(db.String(256))
	tdesc = db.Column(db.Text)
	tadmin = db.Column(db.Integer, db.ForeignKey(User.id))

class TeamMember(db.Model):

	tid = db.Column(db.Integer, db.ForeignKey(Team.id), primary_key=True)
	mid = db.Column(db.Integer, db.ForeignKey(User.id), primary_key=True)
