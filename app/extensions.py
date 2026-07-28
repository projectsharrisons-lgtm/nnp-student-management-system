"""
app/extensions.py
Centralized extension instantiation to prevent circular imports.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Database
db = SQLAlchemy()

# Database Migrations
migrate = Migrate()

# Login Manager
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"
login_manager.session_protection = "strong"

# CSRF Protection
csrf = CSRFProtect()

# Mail
mail = Mail()

# Rate Limiter
limiter = Limiter(
    key_func=get_remote_address
)
