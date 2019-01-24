import datetime
from calendar import monthrange
from time import strftime, gmtime

from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required

from tracker.blueprints.page.models import find_created_items_today, find_user_activity_month, \
    user_activity_cached
from tracker.extensions import cache

page = Blueprint('page', __name__, template_folder='templates')


@page.route('/')
@login_required
def home():
    result = cache.get("dashboard_today_items")
    if result is None:
        items = find_created_items_today()
        result = []
        for i in items:
            result.append(i)
        cache.set("dashboard_today_items", result, timeout=10 * 60)

    return render_template('page/dashboard.html', stats=result)


@page.route('/api/users/activity/now')
def users_activity_now():

    q = request.args.get('q', '')
    today = strftime("%Y-%m-%d", gmtime())

    d, users = user_activity_cached(today, q)

    response = {
        'data': d,
        'xkey': 'y',
        'ykeys': list(users),
        'labels': list(users),
        'fillOpacity': 0.6,
        'hideHover': 'auto',
        'behaveLikeLine': bool('true'),
        'resize': bool('true'),
        'pointFillColors': ['#ffffff'],
        'pointStrokeColors': ['black'],
        'element': 'user-activity-today',
        'parseTime': bool('false'),
        'stacked': bool('true')
    }

    return jsonify(response), 200


@page.route('/api/users/activity/monthly')
def users_activity_monthly():

    q = request.args.get('q', '')
    active = []

    if q != '':
        active = find_user_activity_month(strftime("%Y", gmtime()), strftime("%m", gmtime()), q)

    d = []
    v = []
    users = set()

    for x in active:
        v.append(x)
        users.add(x[0])

    _max = monthrange(int(strftime("%Y", gmtime())),  int(strftime("%m", gmtime())))[1] + 1

    for m in range(1, _max):
        row = dict()
        row['y'] = str(m).zfill(2)
        for u in users:
            row[u] = 0
        d.append(row)

    for r in v:
        for item in range(0, len(d)):
            if str(d[item]['y']) == str(r[1]):
                d[item][r[0]] = r[2]

    response = {
        'data': d,
        'xkey': 'y',
        'ykeys': list(users),
        'labels': list(users),
        'fillOpacity': 0.6,
        'hideHover': 'auto',
        'behaveLikeLine': bool('true'),
        'resize': bool('true'),
        'pointFillColors': ['#ffffff'],
        'pointStrokeColors': ['black'],
        'element': 'user-activity-monthly',
        'parseTime': bool('false'),
        'stacked': bool('true')
    }

    return jsonify(response), 200


@page.route('/api/users/activity/date/<string:_date>')
def users_activity_by_day(_date):

    d, users = user_activity_cached(_date, '')

    response = {
        'data': d,
        'xkey': 'y',
        'ykeys': list(users),
        'labels': list(users),
        'fillOpacity': 0.6,
        'hideHover': 'auto',
        'behaveLikeLine': bool('true'),
        'resize': bool('true'),
        'pointFillColors': ['#ffffff'],
        'pointStrokeColors': ['black'],
        'element': 'user-activity-today',
        'parseTime': bool('false'),
        'stacked': bool('true')
    }

    return jsonify(response), 200
