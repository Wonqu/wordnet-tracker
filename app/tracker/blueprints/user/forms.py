from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, PasswordField, DateField
from wtforms.validators import DataRequired, Length, Optional


class SearchForm(FlaskForm):
    q = StringField('Search terms', [Optional(), Length(1, 256)])


class LoginForm(FlaskForm):
    next = HiddenField()
    identity = StringField('Username',
                           [DataRequired(), Length(3, 254)])
    password = PasswordField('Password', [DataRequired(), Length(3, 128)])
    # remember = BooleanField('Stay signed in')


class UserActivityForm(FlaskForm):
    date_from = DateField("date from", format="%Y-%m-%d")
    date_to = DateField("date to", format="%Y-%m-%d")
