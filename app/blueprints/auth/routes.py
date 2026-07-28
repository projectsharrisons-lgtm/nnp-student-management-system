from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from app.blueprints.auth.forms import LoginForm, RegistrationForm, ForgotPasswordForm, ResetPasswordForm
from app.models.user import User
from app.extensions import db
from app.utils import send_email

auth_bp = Blueprint('auth', __name__)

def get_dashboard_redirect(role):
    """Helper to route users to their specific dashboards."""
    dashboards = {
        'Super Administrator': 'main.admin_dashboard',
        'Principal': 'main.principal_dashboard',
        'Deputy Principal': 'main.deputy_dashboard',
        'Registrar': 'main.registrar_dashboard',
        'Lecturer': 'main.lecturer_dashboard',
        'Finance Officer': 'main.finance_dashboard',
        'Librarian': 'main.library_dashboard',
        'Student': 'main.student_dashboard',
    }
    return url_for(dashboards.get(role, 'main.dashboard'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(get_dashboard_redirect(current_user.role))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user:
            # 1. Check Lockout
            if user.locked_until and user.locked_until > datetime.utcnow():
                current_app.logger.warning(f"Failed login attempt on locked account: {user.email}")
                flash(f'Account locked. Try again after {user.locked_until.strftime("%H:%M UTC")}', 'error')
                return redirect(url_for('auth.login'))
            
            # 2. Check Activation & Verification
            if not user.is_active:
                flash('Your account is deactivated. Contact administration.', 'error')
                return redirect(url_for('auth.login'))

            if not user.is_verified:
                current_app.logger.warning(f"Login attempt on unverified account: {user.email}")
                flash('Please verify your email address before logging in.', 'error')
                return redirect(url_for('auth.login'))

            # 3. Validate Password
            if user.check_password(form.password.data):
                user.failed_login_attempts = 0
                user.locked_until = None
                user.last_login = datetime.utcnow()
                db.session.commit()
                login_user(user, remember=form.remember_me.data)
                
                current_app.logger.info(f"User login successful: {user.email} (Role: {user.role})")
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(get_dashboard_redirect(user.role))
            else:
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= 5:
                    user.locked_until = datetime.utcnow() + timedelta(minutes=15)
                    current_app.logger.warning(f"Account locked due to failed logins: {user.email}")
                    flash('Account locked for 15 minutes due to multiple failed login attempts.', 'error')
                else:
                    current_app.logger.warning(f"Failed login attempt: {user.email}")
                    flash('Invalid email or password.', 'error')
                db.session.commit()
        else:
            current_app.logger.warning(f"Failed login attempt for non-existent email: {form.email.data}")
            flash('Invalid email or password.', 'error')
            
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(get_dashboard_redirect(current_user.role))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, role=form.role.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        current_app.logger.info(f"New user registered: {user.email} (Role: {user.role})")

        # Generate Token and Send Verification Email
        token = user.get_token('verify-email')
        verify_url = url_for('auth.verify_email', token=token, _external=True)
        send_email('Verify Your NNPSMS Account', 
                   current_app.config['MAIL_DEFAULT_SENDER'], 
                   [user.email], 
                   f'Click the link to verify your account: {verify_url}',
                   f'<p>Welcome to NNPSMS. Please verify your account by clicking here: <a href="{verify_url}">Verify Email</a></p>')

        flash('Registration successful! Check your email to verify your account before logging in.', 'info')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html', form=form)

@auth_bp.route('/verify/<token>')
def verify_email(token):
    user = User.verify_token(token, 'verify-email')
    if user:
        if not user.is_verified:
            user.is_verified = True
            db.session.commit()
            current_app.logger.info(f"Email verified successfully: {user.email}")
            flash('Email verified successfully! You can now log in.', 'success')
        else:
            flash('Account is already verified.', 'info')
    else:
        current_app.logger.warning("Invalid or expired email verification token used.")
        flash('The verification link is invalid or has expired.', 'error')
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(get_dashboard_redirect(current_user.role))
        
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
                       f'<p>You requested a password reset. Click here to reset it: <a href="{reset_url}">Reset Password</a></p>')
            current_app.logger.info(f"Password reset requested for: {user.email}")
            
        # Generic message to prevent email enumeration
        flash('If an account exists with that email, a password reset link has been sent.', 'info')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/forgot_password.html', form=form)

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(get_dashboard_redirect(current_user.role))
        
    user = User.verify_token(token, 'reset-password')
    if not user:
        current_app.logger.warning("Invalid or expired password reset token used.")
        flash('The reset link is invalid or has expired.', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        
        # Unlock account if it was locked due to failures
        user.failed_login_attempts = 0
        user.locked_until = None
        
        db.session.commit()
        current_app.logger.info(f"Password reset successfully for: {user.email}")
        flash('Your password has been updated! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/reset_password.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    current_app.logger.info(f"User logged out: {current_user.email}")
    logout_user()
    flash('You have been successfully logged out.', 'info')
    return redirect(url_for('main.index'))
