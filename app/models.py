from app import db
# from app import login
# from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True, autoincrement= True)
	email = db.Column(db.String(256),index=True)
	fname = db.Column(db.String(75), nullable=False)
	lname = db.Column(db.String(75))
	password_hash = db.Column(db.String(256))
	verify = db.Column(db.String(256))
	isVerified = db.Column(db.Boolean, default=False)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	def super(self):
		return self.email=='aswanth366@gmail.com'
