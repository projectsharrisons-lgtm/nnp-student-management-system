from functools import wraps
from flask import abort, current_app, url_for, render_template
from flask_login import current_user
from flask_mail import Message
from app.extensions import mail
from threading import Thread

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return current_app.login_manager.unauthorized()
            if current_user.role not in roles and 'Super Administrator' not in current_user.role:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            app.logger.error(f"Failed to send email: {str(e)}")

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()
