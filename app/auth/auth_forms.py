from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, BooleanField
from wtforms.validators import  Length, DataRequired, Email, EqualTo, ValidationError
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms_sqlalchemy.fields import QuerySelectMultipleField

from app import db
from app.main.models import *
import sqlalchemy as sqla


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])

    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Password', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Post')

    def validate_username(self, username):
        query = sqla.select(Viewer).where(Viewer.username == username.data)
        viewer = db.session.scalars(query).first()
        query1 = sqla.select(Author).where(Author.username == username.data)
        author = db.session.scalars(query1).first()
        if viewer is not None: 
            raise ValidationError('The username already exists! Please use a different username.')
        if author is not None:
            raise ValidationError('The username already exists! Please use a different username.')
     
    def validate_email(self, email):
        query = sqla.select(Viewer).where(Viewer.email == email.data)
        viewer = db.session.scalars(query).first()
        query1 = sqla.select(Author).where(Author.email == email.data)
        author = db.session.scalars(query1).first()
        if viewer is not None: 
            raise ValidationError('The username already exists! Please use a different email.')
        if author is not None:
            raise ValidationError('The username already exists! Please use a different username.')
                                  
class LoginForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class VerificationForm(FlaskForm):
    code = StringField('Verification Code', validators=[DataRequired()])
    submit = SubmitField('Verify')
