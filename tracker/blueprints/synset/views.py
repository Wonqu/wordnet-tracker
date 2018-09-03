from flask import (
    Blueprint,
    render_template, request)
from flask_login import login_required
from flask_sqlalchemy import Pagination

from tracker.blueprints.synset.forms import SynsetHistoryForm
from tracker.blueprints.synset.models import TrackerSynsetsHistory

synset = Blueprint('synset', __name__, template_folder='templates')


@synset.route('/synsets/relations/history', defaults={'page': 1})
@synset.route('/synsets/relations/history/page/<int:page>')
@login_required
def synsets_relations_history(page):
    return render_template('synset/synset-relations-history.html',
                           synsets=[])


@synset.route('/synsets/history', defaults={'page': 1})
@synset.route('/synsets/history/page/<int:page>')
@login_required
def synsets_history(page):

    filter_form = SynsetHistoryForm()

    paginated_synsets = TrackerSynsetsHistory.query \
        .filter(TrackerSynsetsHistory.search_by_form_filter(request.args.get('date_from', ''),
                                                            request.args.get('date_to', ''),
                                                            request.args.get('synset_id', '')))

    pagination = optimised_pagination(paginated_synsets, 50, page)

    return render_template('synset/synset-history.html',
                           form=filter_form,
                           synsets=pagination)


def optimised_pagination(query, per_page, page):
    ''' A more efficient pagination for SQLAlchemy
    Fetch one item before offset (to know if there's a previous page)
    Fetch one item after limit (to know if there's a next page)
    The trade-off is that the total items are not available, but if you don't need them
    there's no need for an extra COUNT query
    '''
    offset_start = (page - 1) * per_page

    query_offset = max(offset_start - 1, 0)
    optimistic_items = query.limit(per_page + 1).offset(query_offset).all()
    if page == 1:
        if len(optimistic_items) == per_page + 1:
            # On first page, there's no optimistic item for previous page
            items = optimistic_items[:-1]
        else:
            # The number of items on the first page is fewer than per_page
            items = optimistic_items
    elif len(optimistic_items) == per_page + 2:
        # We fetched an extra item on both ends
        items = optimistic_items[1:-1]
    else:
        # An extra item only on the head
        # This is the last page
        items = optimistic_items[1:]
    # This total is at least the number of items for the query, could be more
    total = offset_start + len(optimistic_items)
    return Pagination(query, page, per_page, total, items)
