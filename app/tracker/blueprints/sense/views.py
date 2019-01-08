from flask import (
    Blueprint,
    render_template, request)
from flask_login import login_required

from lib.util_sqlalchemy import paginate, status, parts_of_speech, domain, aspect
from tracker.blueprints.emotion.models import Emotion
from tracker.blueprints.sense.forms import SenseRelationsHistoryForm, SenseHistoryForm
from tracker.blueprints.sense.models import get_sense_relation_list, TrackerSenseRelationsHistory, Sense, \
    find_sense_history, find_sense_incoming_relations, find_sense_outgoing_relations, TrackerSenseHistory
from tracker.blueprints.synset.models import get_user_name_list

sense = Blueprint('sense', __name__, template_folder='templates')


class SenseistoryForm(object):
    pass


@sense.route('/senses/history', defaults={'page': 1})
@sense.route('/senses/history/page/<int:page>')
@login_required
def senses_history(page):

    filter_form = SenseHistoryForm()
    users = get_user_name_list()

    paginated_senses = TrackerSenseHistory.query \
        .filter(TrackerSenseHistory.search_by_form_filter(request.args.get('date_from', ''),
                                                                   request.args.get('date_to', ''),
                                                                   request.args.get('sense_id', ''),
                                                                   request.args.get('user', ''),
                                                                   request.args.get('pos', ''),
                                                                   request.args.get('status', '')))
    cache_key = 'luh-count-' + \
                request.args.get('date_from', '') + "_" + \
                request.args.get('date_to', '') + "_" + \
                request.args.get('sense_id', '') + "_" + \
                request.args.get('pos', '') + "_" + \
                request.args.get('status', '') + "_" + \
                request.args.get('user', '')

    pagination = paginate(paginated_senses, page, 50, cache_key)

    return render_template('sense/sense-history.html',
                           form=filter_form,
                           users=users,
                           sense_history=pagination,
                           status=status(),
                           pos=parts_of_speech(),
                           domain=domain())


@sense.route('/senses/relations/history', defaults={'page': 1})
@sense.route('/senses/relations/history/page/<int:page>')
@login_required
def senses_relations_history(page):
    filter_form = SenseRelationsHistoryForm()

    users = get_user_name_list()
    relations = get_sense_relation_list()

    cache_key = 'lurh-count-' + \
                request.args.get('date_from', '') + "_" + \
                request.args.get('date_to', '') + "_" + \
                request.args.get('sense_id', '') + "_" + \
                request.args.get('user', '') + "_" + \
                request.args.get('relation_type', '')

    paginated_senses = TrackerSenseRelationsHistory.query \
        .filter(TrackerSenseRelationsHistory.search_by_form_filter(request.args.get('date_from', ''),
                                                                   request.args.get('date_to', ''),
                                                                   request.args.get('sense_id', ''),
                                                                   request.args.get('user', ''),
                                                                   request.args.get('relation_type', '')
                                                                   ))

    pagination = paginate(paginated_senses, page, 50, cache_key)

    return render_template('sense/sense-relations-history.html',
                           form=filter_form,
                           users=users,
                           relations=relations,
                           history=pagination)


@sense.route('/sense/<int:id>')
@login_required
def sense_by_id(id):

    sense = Sense.query.get(id)
    sense_hist = find_sense_history(id)

    incoming_rel = find_sense_incoming_relations(id)
    incoming_history = TrackerSenseRelationsHistory.query.filter(TrackerSenseRelationsHistory.target_id == id).all()

    outgoing_rel = find_sense_outgoing_relations(id)
    outgoing_history = TrackerSenseRelationsHistory.query.filter(TrackerSenseRelationsHistory.source_id == id).all()

    emotions = Emotion.query.filter(Emotion.sense_id == id).all()

    return render_template('sense/sense.html',
                           sense=sense,
                           pos=parts_of_speech(),
                           domain=domain(),
                           status=status(),
                           aspect=aspect(),
                           sense_history=sense_hist,
                           incoming_rel=incoming_rel,
                           outgoing_rel=outgoing_rel,
                           outgoing_history=outgoing_history,
                           incoming_history=incoming_history,
                           emotions=emotions)
