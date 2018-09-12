from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, TextField


class SenseRelationsHistoryForm(FlaskForm):
    date_from = DateField("date from", format="%Y-%m-%d")
    date_to = DateField("date to", format="%Y-%m-%d")
    sense_id = IntegerField("sense_id")
    user = TextField("user")
    relation_type = TextField("relation_type")


class SenseHistoryForm(FlaskForm):
    date_from = DateField("date from", format="%Y-%m-%d")
    date_to = DateField("date to", format="%Y-%m-%d")
    sense_id = IntegerField("sense_id")
    user = TextField("user")
    pos = IntegerField("pos")
    status = IntegerField("status")

