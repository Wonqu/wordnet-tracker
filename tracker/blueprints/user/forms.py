from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, PasswordField
from wtforms.validators import DataRequired, Length, Optional


class SearchForm(FlaskForm):
    q = StringField('Search terms', [Optional(), Length(1, 256)])


class LoginForm(FlaskForm):
    next = HiddenField()
    identity = StringField('Username',
                           [DataRequired(), Length(3, 254)])
    password = PasswordField('Password', [DataRequired(), Length(3, 128)])
    # remember = BooleanField('Stay signed in')
