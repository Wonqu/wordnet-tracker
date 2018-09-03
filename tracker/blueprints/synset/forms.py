from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField


class SynsetHistoryForm(FlaskForm):
    date_from = DateField("date from", format="%Y-%m-%d")
    date_to = DateField("date to", format="%Y-%m-%d")
    synset_id = IntegerField()
