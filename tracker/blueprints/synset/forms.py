from flask_wtf import FlaskForm
from wtforms import HiddenField, DateField, IntegerField


class SynsetHistoryForm(FlaskForm):
    next = HiddenField()
    date_from = DateField('Changes from')
    date_to = DateField('Changes to')
    synset_id = IntegerField('Synset ID')
