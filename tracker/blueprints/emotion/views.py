from flask import (
    Blueprint,
    render_template)
from flask_login import login_required

emotion = Blueprint('emotion', __name__, template_folder='templates')


@emotion.route('/emotions', defaults={'page': 1})
@emotion.route('/emotions/page/<int:page>')
@login_required
def emotions(page):

    return render_template('emotion/emotions.html',
                           senses=[])