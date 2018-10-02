import datetime

from flask import request
from flask_sqlalchemy import Pagination
from sqlalchemy import DateTime
from sqlalchemy.types import TypeDecorator
from werkzeug.exceptions import abort

from lib.util_datetime import tzware_datetime
from tracker.extensions import db, cache


class AwareDateTime(TypeDecorator):
    """
    A DateTime type which can only store tz-aware DateTimes.

    Source:
      https://gist.github.com/inklesspen/90b554c864b99340747e
    """
    impl = DateTime(timezone=True)

    def process_bind_param(self, value, dialect):
        if isinstance(value, datetime.datetime) and value.tzinfo is None:
            raise ValueError('{!r} must be TZ-aware'.format(value))
        return value

    def __repr__(self):
        return 'AwareDateTime()'


class ResourceMixin(object):
    # Keep track when records are created and updated.
    created_on = db.Column(AwareDateTime(),
                           default=tzware_datetime)
    updated_on = db.Column(AwareDateTime(),
                           default=tzware_datetime,
                           onupdate=tzware_datetime)

    @classmethod
    def sort_by(cls, field, direction):
        """
        Validate the sort field and direction.

        :param field: Field name
        :type field: str
        :param direction: Direction
        :type direction: str
        :return: tuple
        """
        if field not in cls.__table__.columns:
            field = 'created_on'

        if direction not in ('asc', 'desc'):
            direction = 'asc'

        return field, direction

    @classmethod
    def get_bulk_action_ids(cls, scope, ids, omit_ids=[], query=''):
        """
        Determine which IDs are to be modified.

        :param scope: Affect all or only a subset of items
        :type scope: str
        :param ids: List of ids to be modified
        :type ids: list
        :param omit_ids: Remove 1 or more IDs from the list
        :type omit_ids: list
        :param query: Search query (if applicable)
        :type query: str
        :return: list
        """
        omit_ids = map(str, omit_ids)

        if scope == 'all_search_results':
            # Change the scope to go from selected ids to all search results.
            ids = cls.query.with_entities(cls.id).filter(cls.search(query))

            # SQLAlchemy returns back a list of tuples, we want a list of strs.
            ids = [str(item[0]) for item in ids]

        # Remove 1 or more items from the list, this could be useful in spots
        # where you may want to protect the current user from deleting themself
        # when bulk deleting user accounts.
        if omit_ids:
            ids = [id for id in ids if id not in omit_ids]

        return ids

    @classmethod
    def bulk_delete(cls, ids):
        """
        Delete 1 or more model instances.

        :param ids: List of ids to be deleted
        :type ids: list
        :return: Number of deleted instances
        """
        delete_count = cls.query.filter(cls.id.in_(ids)).delete(
            synchronize_session=False)
        db.session.commit()

        return delete_count

    def save(self):
        """
        Save a model instance.

        :return: Model instance
        """
        db.session.add(self)
        db.session.commit()

        return self

    def delete(self):
        """
        Delete a model instance.

        :return: db.session.commit()'s result
        """
        db.session.delete(self)
        return db.session.commit()

    def __str__(self):
        """
        Create a human readable version of a class instance.

        :return: self
        """
        obj_id = hex(id(self))
        columns = self.__table__.c.keys()

        values = ', '.join("%s=%r" % (n, getattr(self, n)) for n in columns)
        return '<%s %s(%s)>' % (obj_id, self.__class__.__name__, values)


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


def paginate(query, page=None, per_page=None, total_cache_key=''):
    """Returns ``per_page`` items from page ``page``.

    If ``page`` or ``per_page`` are ``None``, they will be retrieved from
    the request query. If ``max_per_page`` is specified, ``per_page`` will
    be limited to that value. If there is no request or they aren't in the
    query, they default to 1 and 20 respectively.

    When ``error_out`` is ``True`` (default), the following rules will
    cause a 404 response:

    * No items are found and ``page`` is not 1.
    * ``page`` is less than 1, or ``per_page`` is negative.
    * ``page`` or ``per_page`` are not ints.

    When ``error_out`` is ``False``, ``page`` and ``per_page`` default to
    1 and 20 respectively.

    Returns a :class:`Pagination` object.
    """

    error_out = True
    max_per_page = None

    if request:
        if page is None:
            try:
                page = int(request.args.get('page', 1))
            except (TypeError, ValueError):
                if error_out:
                    abort(404)

                page = 1

        if per_page is None:
            try:
                per_page = int(request.args.get('per_page', 20))
            except (TypeError, ValueError):
                if error_out:
                    abort(404)

                per_page = 20
    else:
        if page is None:
            page = 1

        if per_page is None:
            per_page = 20

    if max_per_page is not None:
        per_page = min(per_page, max_per_page)

    if page < 1:
        if error_out:
            abort(404)
        else:
            page = 1

    if per_page < 0:
        if error_out:
            abort(404)
        else:
            per_page = 20

    items = query.limit(per_page).offset((page - 1) * per_page).all()

    if not items and page != 1 and error_out:
        abort(404)

    # No need to count if we're on the first page and there are fewer
    # items than we expected.
    if page == 1 and len(items) < per_page:
        total = len(items)
    else:
        if total_cache_key != '':
            total = cache.get(total_cache_key)
            if total is None:
                total = query.order_by(None).count()
                cache.set(total_cache_key, total, timeout=7200)
        else:
            total = query.order_by(None).count()

    return Pagination(query, page, per_page, total, items)


def parts_of_speech():
    return {
        'None': '',
        '1': 'Verb',
        '2': 'Noun',
        '3': 'Adverb',
        '4': 'Adjective',
        '5': 'Verb Princeton',
        '6': 'Noun Princeton',
        '7': 'Adverb Princeton',
        '8': 'Adjective Princeton'
    }


def status():
    return {
        'None': {'value': '', 'tag': ''},
        '0': {'value': 'Unprocessed', 'tag': 'label-default'},
        '1': {'value': 'New', 'tag': 'label-primary'},
        '2': {'value': 'Error', 'tag': 'label-danger'},
        '3': {'value': 'Checked', 'tag': 'label-success'},
        '4': {'value': 'Meaning', 'tag': 'label-info'},
        '5': {'value': 'Partially Checked', 'tag': 'label-warning'}
}


def domain():
    return {
        'None': '',
        '1': 'bhp',
        '2': 'czy',
        '3': 'wytw',
        '4': 'cech',
        '5': 'czc',
        '6': 'umy',
        '7': 'por',
        '8': 'zdarz',
        '9': 'czuj',
        '10': 'jedz',
        '11': 'grp',
        '12': 'msc',
        '13': 'cel',
        '14': 'rz',
        '15': 'os',
        '16': 'zj',
        '17': 'rsl',
        '18': 'pos',
        '19': 'prc',
        '20': 'il',
        '21': 'zw',
        '22': 'ksz',
        '23': 'st',
        '24': 'sbst',
        '25': 'czas',
        '26': 'zwz',
        '27': 'hig',
        '28': 'zmn',
        '29': 'cumy',
        '30': 'cpor',
        '31': 'wal',
        '32': 'cjedz',
        '33': 'dtk',
        '34': 'cwyt',
        '35': 'cczuj',
        '36': 'ruch',
        '37': 'pst',
        '38': 'cpos',
        '39': 'sp',
        '40': 'cst',
        '41': 'pog',
        '42': 'jak',
        '43': 'rel',
        '44': 'odcz',
        '46': 'sys',
        '47': 'adj',
        '48': 'adv',
        '49': 'mat',
        '45': 'grad',
        '50': 'cdystr',
        '51': 'caku',
        '52': 'cper',
        '53': 'cdel'
    }


def aspect():
    return {
        'None': '',
        '0': 'Not a verb',
        '1': 'Perfective',
        '2': 'Imperfective',
        '3': 'Predicative',
        '4': 'Two aspect verb'
    }
