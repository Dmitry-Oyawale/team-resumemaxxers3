from app import db
from flask import render_template, flash, redirect, url_for, request, jsonify
import sqlalchemy as sqla

from app.main.models import Viewer
from flask_login import current_user, login_required
from sqlalchemy import text

from app.main import main_blueprint as main

@main.route('/', methods=['GET'])
@main.route('/index', methods=['GET'])
def index():
    #courses = db.session.scalars(sqla.select(Course))
    Viewers = db.session.scalars(sqla.select(Viewer))
    return render_template('base.html', title="Course List", viewers = Viewers)