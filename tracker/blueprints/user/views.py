from flask import (
    Blueprint,
    redirect,
    request,
    flash,
    url_for,
    render_template)

from flask_login import (
    login_user,
    logout_user, login_required)

from sqlalchemy import text
from lib.safe_next_url import safe_next_url
from tracker.blueprints.user.decorator import anonymous_required
from tracker.blueprints.user.forms import LoginForm, SearchForm
from tracker.blueprints.user.models import User

user = Blueprint('user', __name__, template_folder='templates')


@user.route('/login', methods=['GET', 'POST'])
@anonymous_required()
def login():
    form = LoginForm(next=request.args.get('next'))

    if form.validate_on_submit():
        u = User.find_by_email(request.form.get('identity'))

        if u and u.authenticated(password=request.form.get('password')):
            # As you can see remember me is always enabled, this was a design
            # decision I made because more often than not users want this
            # enabled. This allows for a less complicated login form.
            #
            # If however you want them to be able to select whether or not they
            # should remain logged in then perform the following 3 steps:
            # 1) Replace 'True' below with: request.form.get('remember', False)
            # 2) Uncomment the 'remember' field in user/forms.py#LoginForm
            # 3) Add a checkbox to the login form with the id/name 'remember'
            if login_user(u, remember=True) and u.is_active():
                # Handle optionally redirecting to the next URL safely.
                next_url = request.form.get('next')
                if next_url:
                    return redirect(safe_next_url(next_url))

                return redirect(url_for('page.home'))
            else:
                flash('This account has been disabled.', 'error')
        else:
            flash('Identity or password is incorrect.', 'error')

    return render_template('user/login.html', form=form)


@user.route('/profile')
@login_required
def profile():
    return render_template('user/profile.html')


@user.route('/users', defaults={'page': 1})
@user.route('/users/page/<int:page>')
@login_required
def users(page):
    search_form = SearchForm()

    sort_by = User.sort_by(request.args.get('sort', 'id'),
                           request.args.get('direction', 'desc'))

    order_values = '{0} {1}'.format(sort_by[0], sort_by[1])

    paginated_users = User.query \
        .filter(User.search(request.args.get('q', ''))) \
        .order_by(User.role.asc(), text(order_values)) \
        .paginate(page, 50, True)

    return render_template('user/users.html',
                           form=search_form,
                           users=paginated_users)


@user.route("/logout")
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('user.login'))
