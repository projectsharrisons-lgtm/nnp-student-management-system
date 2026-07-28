from datetime import datetime, timedelta
from urllib.parse import urlparse, urljoin
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from app.blueprints.auth.forms import LoginForm, RegistrationForm, ForgotPasswordForm, ResetPasswordForm
from app.models.user import User
from app.extensions import db
from app.utils import send_email

auth_bp = Blueprint('auth', __name__)

def get_dashboard_redirect(role):
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

# SECURITY FIX: Prevent Open Redirect Vulnerabilities
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(get_dashboard_redirect(current_user.role))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user:
            if user.locked_until and user.locked_until > datetime.utcnow():
                current_app.logger.warning(f"Failed login attempt on locked account: {user.email}")
                flash(f'Account locked. Try again after {user.locked_until.strftime("%H:%M UTC")}', 'error')
                return redirect(url_for('auth.login'))
            
            if not user.is_active:
                flash('Your account is deactivated. Contact administration.', 'error')
                return redirect(url_for('auth.login'))

            if not user.is_verified:
                current_app.logger.warning(f"Login attempt on unverified account: {user.email}")
                flash('Please verify your email address before logging in.', 'error')
                return redirect(url_for('auth.login'))

            if user.check_password(form.password.data):
                user.failed_login_attempts = 0
                user.locked_until = None
                user.last_login = datetime.utcnow()
                db.session.commit()
                login_user(user, remember=form.remember_me.data)
                
                current_app.logger.info(f"User login successful: {user.email} (Role: {user.role})")
                
                # SECURITY FIX: Validate the 'next' parameter
                next_page = request.args.get('next')
                if not next_page or not is_safe_url(next_page):
                    next_page = get_dashboard_redirect(user.role)
                    
                return redirect(next_page)
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

# ... (rest of auth_bp routes remain unchanged) ...
