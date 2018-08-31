from flask import Blueprint, render_template
from flask_login import login_required

page = Blueprint('page', __name__, template_folder='templates')


@page.route('/')
@login_required
def home():
    return render_template('page/dashboard.html')
