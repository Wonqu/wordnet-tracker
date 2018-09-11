from flask_wtf import FlaskForm
from wtforms import TextField, IntegerField


class EmotionDisagreementForm(FlaskForm):
    sense_id = IntegerField("sense_id")
    user = TextField("user")
