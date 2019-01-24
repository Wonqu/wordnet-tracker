import flask_admin
from flask import url_for, request, current_app, render_template, abort, make_response, Blueprint
from flask_admin.contrib import sqla
from flask_login import login_required, current_user
from sqlalchemy import select
from werkzeug.utils import redirect

from tracker.blueprints.tracker_admin import models
from tracker.extensions import db

tracker_admin = Blueprint('tracker_admin', __name__, template_folder='templates')


class AdminIndexView(flask_admin.AdminIndexView):

    def is_accessible(self):
        return hasattr(current_user, 'role') and current_user.role == "ADMIN"

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('page.home', next=request.url))


class AdminQueryView(sqla.ModelView):

    def is_accessible(self):
        return hasattr(current_user, 'role') and current_user.role == "ADMIN"

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('page.home', next=request.url))


@tracker_admin.route('/admin_query/<int:pk>/')
@login_required
def admin_query(pk):
    keys, result, query_name = models.AdminQuery.results(pk)
    context = {
        'name': query_name,
        'pk': pk,
        'data': result,
        'keys': keys,
    }
    return render_template('tracker_admin/admin-query.html', **context)


@tracker_admin.route('/admin_query/<int:pk>/csv')
@login_required
def admin_query_csv(pk):
    headings, rows, query_name = models.AdminQuery.results(pk)
    csv_content = ",".join(headings)
    rows = [[str(value) for (key, value) in o.items()] for o in rows]
    rows = [','.join(row) for row in rows]
    csv_content += "\n" + "\n".join(rows)
    response = make_response(csv_content)
    response.headers['Content-Disposition'] = f'attachment; filename={query_name}-dump.csv'
    response.mimetype = 'text/csv'
    return response


@tracker_admin.route('/statistics/')
@login_required
def admin_query_list_statistic():
    engine = db.get_engine(current_app, models.AdminQuery.__bind_key__)
    connection = engine.connect()
    aqs = connection.execute(
        select([models.AdminQuery]).where(
            models.AdminQuery.type == models.AdminQueryTypeEnum.statistic
        )
    )
    if aqs.returns_rows:
        aqs = [{key: value for (key, value) in o.items()} for o in aqs]
    else:
        aqs = []
    context = {
        'data': aqs,
        'title': 'Statistics'
    }
    return render_template('tracker_admin/admin-query-list.html', **context)


@tracker_admin.route('/diagnostics/')
@login_required
def admin_query_list_diagnostic():
    engine = db.get_engine(current_app, models.AdminQuery.__bind_key__)
    connection = engine.connect()
    aqs = connection.execute(
        select([models.AdminQuery]).where(
            models.AdminQuery.type == models.AdminQueryTypeEnum.diagnostic
        )
    )
    if aqs.returns_rows:
        aqs = [{key: value for (key, value) in o.items()} for o in aqs]
    else:
        aqs = []
    context = {
        'data': aqs,
        'title': 'Diagnostics'
    }
    return render_template('tracker_admin/admin-query-list.html', **context)
