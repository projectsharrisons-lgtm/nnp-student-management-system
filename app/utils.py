from functools import wraps
from flask import abort, current_app
from flask_login import current_user
from flask_mail import Message
from app.extensions import mail
from threading import Thread

# --- Email Helpers ---
def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            app.logger.error(f"System Error: Failed to send email to {msg.recipients}. Error: {str(e)}")

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()


# --- Role-Based Access Control (RBAC) Decorators ---
def role_required(*roles):
    """Generic decorator to check multiple roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return current_app.login_manager.unauthorized()
            if current_user.role not in roles and current_user.role != 'Super Administrator':
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    return role_required('Super Administrator')(f)

def principal_required(f):
    return role_required('Principal')(f)

def registrar_required(f):
    return role_required('Registrar')(f)

def lecturer_required(f):
    return role_required('Lecturer')(f)

def finance_required(f):
    return role_required('Finance Officer')(f)

def librarian_required(f):
    return role_required('Librarian')(f)

def student_required(f):
    return role_required('Student')(f)
