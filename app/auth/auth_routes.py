from app import db
from flask import render_template, flash, redirect, url_for
import sqlalchemy as sqla

from app.main.models import Viewer, Author
from app.auth.auth_forms import RegistrationForm, LoginForm, VerificationForm
from flask_login import login_user, current_user, logout_user, login_required
from app.auth import auth_blueprint as auth
from app.auth.email import send_email

import hashlib

@auth.route('/viewer/register', methods = ['GET', 'POST'])
def register():
    rform = RegistrationForm()
    if rform.validate_on_submit():
        viewer = Viewer( username = rform.username.data,
                           email = rform.email.data)

        vercode_unhashed = viewer.email + "SALT!!!"
        subject = "Your Verification Code"
        message = f"""
        Greetings, {rform.username.data}!

        Please find your verification code below:

        **{hashlib.sha256(vercode_unhashed.encode('utf-8')).hexdigest()}**

        Best wishes,
        Dmitry-Oyawale
        """

        send_email(rform.email.data, subject, message)

        viewer.set_password(rform.password.data)
        db.session.add(viewer)
        db.session.commit()

        flash('Congratulations, you are now a registered user! Please check for a verification code')
        return redirect(url_for('auth.verify'))
    return render_template('register.html', form = rform)


@auth.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    lform = LoginForm()

    if lform.validate_on_submit():

        query = sqla.select(Viewer).where(Viewer.username == lform.username.data)
        user = db.session.scalars(query).first()

        if (user is None):
            query = sqla.select(Author).where(Author.username == lform.username.data)
            user = db.session.scalars(query).first()

        if (user is None) or (user.check_password(lform.password.data) == False):
            return redirect(url_for('auth.login'))
        
        login_user(user, remember = lform.remember_me.data)
        flash('The user {} has successfully logged in!'.format(current_user.username))
        return redirect(url_for('main.index'))
    
    return render_template('login.html', form = lform)

@auth.route('/logout', methods = ['GET'])
@login_required 
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/auth/new_verification', methods=['GET', 'POST'])
@login_required
def resend_verification():
    vercode_unhashed = current_user.email + "SALT!!!"
    subject = "Your Verification Code"
    message = f"""
            Greetings, {current_user.username}!

            Please find your verification code below:

            **{hashlib.sha256(vercode_unhashed.encode('utf-8')).hexdigest()}**

            Best wishes,
            Dmitry-Oyawale
            """

    send_email(current_user.email, subject, message)

    flash(
        'Please check your email for a verification code.')
    return redirect(url_for('auth.verify'))

@auth.route('/auth/email_verifications/', methods=['GET', 'POST'])
@login_required
def verify():
    form = VerificationForm()
    if form.validate_on_submit():
        vercode_unhashed = current_user.email + "SALT!!!"
        verification_code = hashlib.sha256(vercode_unhashed.encode('utf-8')).hexdigest()
        print(verification_code)
        if form.code.data == verification_code:
            current_user.verified = True
            db.session.commit()
            flash('Your account has been verified!')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid verification code.')
    return render_template('verify.html', form=form)