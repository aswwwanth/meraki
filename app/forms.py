from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import User, Team

class RegistrationForm(FlaskForm):
    fname = StringField('First Name', validators=[DataRequired()], render_kw={"placeholder": "First Name"})
    lname = StringField('Last Name', validators=[DataRequired()], render_kw={"placeholder": "Last Name"})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[DataRequired()],render_kw={"placeholder": "Password"})
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email already registered')

    def validate_password(self,password):
    	if len(password.data) < 8 and len(password.data) >16:
    		raise ValidationError('Please keep a password with length between 8 and 16 characters')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()], render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})
    submit = SubmitField('Sign In')

class CreateTeam(FlaskForm):
    tname = StringField('Team Name', validators=[DataRequired()], render_kw={"placeholder": "Team Name"})
    tdesc = TextAreaField('Description', render_kw={"placeholder": "Description"})
    submit = SubmitField('Create team')