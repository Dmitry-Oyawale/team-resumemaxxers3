from app import db
from flask import render_template, flash, redirect, url_for
import sqlalchemy as sqla

from app.main.models import Student, CourseEnrollment
from app.auth.auth_forms import RegistrationForm, LoginForm
from flask_login import login_user, current_user, logout_user, login_required
from app.auth import auth_blueprint as auth

@auth.route('/student/register', methods = ['GET', 'POST'])
def register():
    rform = RegistrationForm()
    if rform.validate_on_submit():
        student = Student( username = rform.username.data,
                           firstname = rform.firstname.data,
                           lastname = rform.lastname.data,
                           email = rform.email.data,
                           majors = rform.majors.data,
                           gpa = rform.gpa.data,
                           research_topics = rform.research_topics.data,
                           languages = rform.languages.data
                         )
        print(student)

        student.set_password(rform.password.data)
        db.session.add(student)
        db.session.commit()

        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('main.index'))
    return render_template('register.html', form = rform)

'''
@auth.route('/faculty/register', methods = ['GET', 'POST'])
def register():
    rform = RegistrationForm()
    if rform.validate_on_submit():
        student = Student( username = rform.username.data,
                           firstname = rform.firstname.data,
                           lastname = rform.lastname.data,
                           email = rform.email.data,
                           address = rform.address.data)
        student.set_password(rform.password.data)
        db.session.add(student)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('main.index'))
    return render_template('register.html', form = rform)
'''

@auth.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    lform = LoginForm()

    if lform.validate_on_submit():

        query = sqla.select(Student).where(Student.username == lform.username.data)
        student = db.session.scalars(query).first()

        if (student is None) or (student.check_password(lform.password.data) == False):
            return redirect(url_for('auth.login'))
        
        login_user(student, remember = lform.remember_me.data)
        flash('The user {} has successfully logged in!'.format(current_user.username))
        return redirect(url_for('main.index'))
    return render_template('login.html', form = lform)

@auth.route('/logout', methods = ['GET'])
@login_required 
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

#@auth.route('/faculty/verify/<token>', methods = ['GET'])
#@auth.route('/faculty/login/sso', methods = ['GET'])

from flask import request, jsonify
from flask_login import login_user
from werkzeug.security import check_password_hash
import sqlalchemy as sqla
from app import db
from app.main.models import Student
from app.main.models import Faculty


@auth.route("/api/auth/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"ok": False, "error": "Email and password required"}), 400

    student = db.session.scalar(
        sqla.select(Student).where(Student.email == email)
    )
    faculty = db.session.scalar(
        sqla.select(Faculty).where(Faculty.email == email)
    )

    user = student or faculty

    if user is None or not check_password_hash(user.password_hash, password):
        return jsonify({"ok": False, "error": "Invalid credentials"}), 401

    login_user(user)
    return jsonify({"ok": True})


@auth.route("/api/auth/me", methods=["GET"])
def api_me():
    if not current_user.is_authenticated:
        return jsonify({"authenticated": False}), 200

    return jsonify({
        "authenticated": True,
        "id": current_user.id,
        "role": getattr(current_user, "role", None),
        "email": getattr(current_user, "email", None),
        "name": getattr(current_user, "name", None),
    })
