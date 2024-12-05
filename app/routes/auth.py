from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.exc import IntegrityError
from app.models import User
from app.forms import LoginForm, RegisterForm, UpdateProfileForm, ChangePasswordForm
from app.extensions import db
from app.routes import auth
from werkzeug.security import generate_password_hash
from flask_mail import Message, Mail
from itsdangerous import URLSafeTimedSerializer, SignatureExpired


@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = URLSafeTimedSerializer(current_app.config['SECRET_KEY']).loads(token, salt='password-reset-salt', max_age=3600)
    except SignatureExpired:
        flash('The password reset link has expired.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    user = User.query.filter_by(email=email).first_or_404()

    if request.method == 'POST':
        new_password = request.form.get('new_password')
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        flash('Password has been reset successfully.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html')


@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            token = URLSafeTimedSerializer(current_app.config['SECRET_KEY']).dumps(email, salt='password-reset-salt')
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            msg = Message(
                'Password Reset Request',
                sender='no-reply@example.com',
                recipients=[email]
            )
            msg.body = f'Click the link to reset your password: {reset_url}'
            mail = Mail(current_app)
            mail.send(msg)
            flash('Check your email for password reset instructions.', 'info')
        else:
            flash('Email not found.', 'danger')
    return render_template('forgot_password.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('main.index'))
        flash('Invalid email or password', 'danger')
    return render_template('user/login.html', form=form)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data.strip(),
            email=form.email.data.strip()
        )
        user.set_password(form.password.data)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('Email is already registered. Please log in.', 'danger')
            return redirect(url_for('auth.login'))
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('user/register.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@auth.route('/account', methods=['GET', 'POST'])
@login_required
def view_account():
    profile_form = UpdateProfileForm(obj=current_user)
    password_form = ChangePasswordForm()

    if profile_form.validate_on_submit():
        current_user.username = profile_form.username.data
        current_user.email = profile_form.email.data
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('auth.view_account'))

    if password_form.validate_on_submit():
        if current_user.check_password(password_form.current_password.data):
            # Обновление хэша пароля
            current_user.password_hash = generate_password_hash(password_form.new_password.data)
            db.session.commit()
            flash('Password updated successfully.', 'success')
        else:
            flash('Incorrect current password.', 'danger')
        return redirect(url_for('auth.view_account'))

    return render_template('account.html', profile_form=profile_form, password_form=password_form)


@auth.route('/account/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        # Проверка текущего пароля
        if not current_user.check_password(form.current_password.data):
            flash('Incorrect current password.', 'danger')
            return redirect(url_for('auth.change_password'))

        # Установка нового пароля
        current_user.password_hash = generate_password_hash(form.new_password.data)
        db.session.commit()
        flash('Your password has been updated successfully.', 'success')
        return redirect(url_for('auth.view_account'))

    return render_template('change_password.html', form=form)
