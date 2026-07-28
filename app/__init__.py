import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template

# Top-level extension imports
from app.extensions import db, migrate, login_manager, csrf
from config import Config

def create_app(config_class=Config):
    """
    Construct the core application.
    Uses the Flask Application Factory pattern.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 1. Initialize Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # 2. Configure Logging (Compatible with Render & Local File System)
    if not app.debug and not app.testing:
        # File Logging
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/nnpsms.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        # Stream Logging (Required for Render to capture logs in dashboard)
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('NNPSMS Startup Application Factory Initialized')

    # 3. Import Blueprints (Placed inside create_app to avoid circular imports)
    from app.blueprints.main.routes import main_bp
    from app.blueprints.auth.routes import auth_bp
    from app.blueprints.admin.routes import admin_bp
    from app.blueprints.students.routes import students_bp

    # 4. Register Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(students_bp)

    # 5. Register Error Handlers
    register_error_handlers(app)

    return app


def register_error_handlers(app):
    """
    Helper function to register application-wide error handlers.
    """
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Server Error: {error}')
        return render_template('500.html'), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('403.html'), 403
