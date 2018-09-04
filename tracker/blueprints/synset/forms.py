from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, TextField


class SynsetHistoryForm(FlaskForm):
    date_from = DateField("date from", format="%Y-%m-%d")
    date_to = DateField("date to", format="%Y-%m-%d")
    synset_id = IntegerField()
    user = TextField("user")


class SynsetRelationsHistoryForm(FlaskForm):
    date_from = DateField("date from", format="%Y-%m-%d")
    date_to = DateField("date to", format="%Y-%m-%d")
    synset_id = IntegerField()
    user = TextField("user")
    relation_type = TextField("relation_type")
