from flask import (
    Blueprint,
    render_template, request)
from flask_login import login_required


from lib.util_sqlalchemy import paginate, status, parts_of_speech
from tracker.blueprints.synset.forms import SynsetHistoryForm, SynsetRelationsHistoryForm
from tracker.blueprints.synset.models import TrackerSynsetsHistory, get_user_name_list, \
    TrackerSynsetsRelationsHistory, get_synset_relation_list, Synset, find_synset_incoming_relations, \
    find_synset_outgoing_relations, find_synset_senses, find_synset_sense_history, find_synset_history


synset = Blueprint('synset', __name__, template_folder='templates')


@synset.route('/synsets', defaults={'page': 1})
@synset.route('/synsets/page/<int:page>')
@login_required
def synsets(page):
    paginated_users = Synset.query \
        .filter(Synset.search(request.args.get('gq', ''))) \
        .paginate(page, 50, True)

    return render_template('synset/synsets.html',
                           synsets=paginated_users)


@synset.route('/synsets/relations/history', defaults={'page': 1})
@synset.route('/synsets/relations/history/page/<int:page>')
@login_required
def synsets_relations_history(page):
    filter_form = SynsetRelationsHistoryForm()

    users = get_user_name_list()
    relations = get_synset_relation_list()

    cache_key = 'srh-count-{}_{}_{}_{}_{}'.format(
        request.args.get('date_from', ''),
        request.args.get('date_to', ''),
        request.args.get('synset_id', ''),
        request.args.get('user', ''),
        request.args.get('relation_type', '')
    )

    paginated_synsets = TrackerSynsetsRelationsHistory.query.filter(
        TrackerSynsetsRelationsHistory.search_by_form_filter(
            request.args.get('date_from', ''),
            request.args.get('date_to', ''),
            request.args.get('synset_id', ''),
            request.args.get('user', ''),
            request.args.get('relation_type', '')
        )
    )

    pagination = paginate(paginated_synsets, page, 50, cache_key)

    return render_template(
        'synset/synset-relations-history.html',
        form=filter_form,
        users=users,
        relations=relations,
        history=pagination
    )


@synset.route('/synsets/history', defaults={'page': 1})
@synset.route('/synsets/history/page/<int:page>')
@login_required
def synsets_history(page):
    filter_form = SynsetHistoryForm()

    users = get_user_name_list()

    paginated_synsets = TrackerSynsetsHistory.query.filter(
        TrackerSynsetsHistory.search_by_form_filter(
            request.args.get('date_from', ''),
            request.args.get('date_to', ''),
            request.args.get('synset_id', ''),
            request.args.get('user', '')
        )
    )
    cache_key = "sh-count-{}_{}_{}_{}".format(
        request.args.get('date_from', ''),
        request.args.get('date_to', ''),
        request.args.get('synset_id', ''),
        request.args.get('user', ''),
    )

    pagination = paginate(paginated_synsets, page, 50, cache_key)

    return render_template(
        'synset/synset-history.html',
        form=filter_form,
        users=users,
        synsets=pagination
    )


@synset.route('/synsets/<int:id>')
@login_required
def synset_by_id(id):

    synset = Synset.query.get(id)
    synset_history = find_synset_history(id)

    incoming_rel = find_synset_incoming_relations(id)
    incoming_history = TrackerSynsetsRelationsHistory.query.filter(TrackerSynsetsRelationsHistory.target_id == id).all()

    outgoing_rel = find_synset_outgoing_relations(id)
    outgoing_history = TrackerSynsetsRelationsHistory.query.filter(TrackerSynsetsRelationsHistory.source_id == id).all()

    senses = find_synset_senses(id)
    senses_history = find_synset_sense_history(id)

    return render_template(
        'synset/synset.html',
        status=status(),
        pos=parts_of_speech(),
        incoming_rel=incoming_rel,
        outgoing_rel=outgoing_rel,
        outgoing_history=outgoing_history,
        incoming_history=incoming_history,
        senses_history=senses_history,
        senses=senses,
        synset=synset,
        synset_history=synset_history
    )
