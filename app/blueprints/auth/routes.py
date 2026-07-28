from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from app.blueprints.auth.forms import LoginForm, RegistrationForm, ForgotPasswordForm, ResetPasswordForm
from app.models.user import User
from app.extensions import db
from app.utils import send_email

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user:
            # Check Account Lockout
            if user.locked_until and user.locked_until > datetime.utcnow():
                flash(f'Account locked. Try again after {user.locked_until.strftime("%H:%M:%S UTC")}', 'error')
                return redirect(url_for('auth.login'))
            
            if not user.is_active:
                flash('Your account is deactivated. Contact administration.', 'error')
                return redirect(url_for('auth.login'))

            if not user.is_verified:
                flash('Please verify your email address before logging in.', 'error')
                return redirect(url_for('auth.login'))

            if user.check_password(form.password.data):
                # Success
                user.failed_login_attempts = 0
                user.locked_until = None
                user.last_login = datetime.utcnow()
                db.session.commit()
                login_user(user, remember=form.remember_me.data)
                
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
            else:
                # Failed attempt
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= 5:
                    user.locked_until = datetime.utcnow() + timedelta(minutes=15)
                    flash('Account locked for 15 minutes due to multiple failed login attempts.', 'error')
                else:
                    flash('Invalid email or password.', 'error')
                db.session.commit()
        else:
            flash('Invalid email or password.', 'error')
            
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, role=form.role.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        # Send Verification Email
        token = user.get_token('verify-email')
        verify_url = url_for('auth.verify_email', token=token, _external=True)
        send_email('Verify Your NNPSMS Account', 
                   current_app.config['MAIL_DEFAULT_SENDER'], 
                   [user.email], 
                   f'Click the link to verify your account: {verify_url}',
                   f'<p>Click the link to verify your account: <a href="{verify_url}">Verify Here</a></p>')

        flash('Registration successful! Please check your email to verify your account.', 'info')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html', form=form)

@auth_bp.route('/verify/<token>')
def verify_email(token):
    user = User.verify_token(token, 'verify-email')
    if user:
        user.is_verified = True
        db.session.commit()
        flash('Email verified successfully! You can now log in.', 'success')
    else:
        flash('The verification link is invalid or has expired.', 'error')
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.get_token('reset-password')
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            send_email('Password Reset Request - NNPSMS',
                       current_app.config['MAIL_DEFAULT_SENDER'],
                       [user.email],
                       f'To reset your password, visit: {reset_url}',
                       f'<p>To reset your password, click the following link: <a href="{reset_url}">Reset Password</a></p>')
        flash('If an account exists with that email, a password reset link has been sent.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/forgot_password.html', form=form)

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    user = User.verify_token(token, 'reset-password')
    if not user:
        flash('The reset link is invalid or has expired.', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been updated! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been successfully logged out.', 'info')
    return redirect(url_for('main.index'))
