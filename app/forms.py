from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import User, Team

class RegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired()], render_kw={"placeholder": "Full Name"})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "Email"})
    username = StringField('Username', validators=[DataRequired()], render_kw={"placeholder": "Username"})
    password = PasswordField('Password', validators=[DataRequired()],render_kw={"placeholder": "Password"})
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email already registered')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username not available')

    def validate_password(self,password):
        if len(password.data) < 8:
            raise ValidationError('Password should be atleast 8 characters long')
        elif len(password.data) > 16:
            raise ValidationError('Password should not be more than 16 characters long')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={"placeholder": "Username"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})
    submit = SubmitField('Sign In')

class CreateTeam(FlaskForm):
    tname = StringField('Team Name', validators=[DataRequired()], render_kw={"placeholder": "Team Name"})
    tdesc = TextAreaField('Description', render_kw={"placeholder": "Description"})
    submit = SubmitField('Create team')

class JoinTeam(FlaskForm):
    tcode = StringField('Team Code', validators=[DataRequired()], render_kw={"placeholder": "Team Code"})
    submit = SubmitField('Join team')