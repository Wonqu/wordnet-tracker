from flask import (
    Blueprint,
    render_template, request)
from flask_login import login_required

from lib.util_sqlalchemy import paginate
from tracker.blueprints.emotion.forms import EmotionDisagreementForm
from tracker.blueprints.emotion.models import EmotionDisagreement
from tracker.blueprints.synset.models import get_user_emotion_list

emotion = Blueprint('emotion', __name__, template_folder='templates')


@emotion.route('/annotator-disagreement', defaults={'page': 1})
@emotion.route('/annotator-disagreement/page/<int:page>')
@login_required
def annotator_disagreement(page):
    filter_form = EmotionDisagreementForm()

    users = get_user_emotion_list()

    cache_key = 'emo_dis-count-' + \
                request.args.get('sense_id', '') + "_" + \
                request.args.get('user', '')

    paginated_emotions = EmotionDisagreement.query.filter(
        EmotionDisagreement.search_by_form_filter(
            request.args.get('sense_id', ''),
            request.args.get('user', '')
        )
    )

    pagination = paginate(paginated_emotions, page, 50, cache_key)

    return render_template(
        '/emotion/annotator-disagreement.html',
        form=filter_form,
        users=users,
        emotions=pagination
    )
