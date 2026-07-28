"""
app/extensions.py
Centralized extension instantiation to prevent circular imports.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

# ==========================================
# CORE EXTENSIONS
# ==========================================
mail = Mail()
# 1. Database ORM
db = SQLAlchemy()

# 2. Database Migrations
migrate = Migrate()

# 3. Authentication & Session Management
login_manager = LoginManager()
# Security settings for production
login_manager.login_view = 'auth.login'  # Blueprint.route to redirect unauthorized users
login_manager.login_message_category = 'warning'
login_manager.session_protection = 'strong'

 Cross-Site Request Forgery Protection
csrf = CSRFProtect()

# ==========================================
# OPTIONAL EXTENSIONS (Uncomment if used)
# ==========================================

from flask_mail import Mail
mail = Mail()

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
limiter = Limiter(key_func=get_remote_address)
