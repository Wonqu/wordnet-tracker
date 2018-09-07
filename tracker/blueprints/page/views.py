import datetime
from datetime import timedelta, datetime

from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from flask_sqlalchemy import xrange

from tracker.blueprints.page.model import find_created_items_today, find_user_activity_now
from tracker.extensions import cache

page = Blueprint('page', __name__, template_folder='templates')


@page.route('/')
@login_required
def home():

    results = cache.get("dashboard_today_items")
    if results is None:
        items = find_created_items_today()
        result = []
        for i in items:
            result.append(i)
        cache.set("dashboard_today_items", result, timeout=10 * 60)

    return render_template('page/dashboard.html', stats=results)


@page.route('/api/users/activity')
def users_activity_now():

    active = find_user_activity_now(datetime(2018, 7, 1, 0, 0, 0))

    start_date = datetime(2018, 1, 1, 0, 0, 0)
    d = []
    v = []
    users = set()

    for x in active:
        v.append(x)
        users.add(x[0])

    for td in (start_date + timedelta(hours=1 * it) for it in xrange(24)):
        row = dict()
        row['y'] = td.strftime("%H:%M")
        for u in users:
            row[u] = 0
        d.append(row)

    for r in v:
        for x in d:
            if x['y'] == r[1] and x[r[0]] == r[0]:
                x[r[0]] = r[2]

    print(d)

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
        'stacked': bool('true')
    }
    return jsonify(response), 200
