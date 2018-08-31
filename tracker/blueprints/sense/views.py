from flask import (
    Blueprint,
    render_template)
from flask_login import login_required

sense = Blueprint('sense', __name__, template_folder='templates')


@sense.route('/senses/history', defaults={'page': 1})
@sense.route('/senses/history/page/<int:page>')
@login_required
def senses_history(page):

    return render_template('sense/sense-history.html',
                           senses=[])


@sense.route('/senses/relations/history', defaults={'page': 1})
@sense.route('/senses/relations/history/page/<int:page>')
@login_required
def senses_relations_history(page):

    return render_template('sense/sense-relations-history.html',
                           senses=[])
