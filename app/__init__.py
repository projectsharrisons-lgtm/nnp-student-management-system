import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template
from config import config_dict
from app.extensions import db, migrate, login_manager, csrf, mail, limiter

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_dict[config_name])

    # Initialize Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)

    # Register Blueprints
    from app.blueprints.main.routes import main_bp
    from app.blueprints.auth.routes import auth_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Configure Audit Logging
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    audit_handler = RotatingFileHandler('logs/nnpsms_audit.log', maxBytes=10485760, backupCount=10) # 10MB per file
    audit_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - AUDIT: %(message)s [in %(pathname)s:%(lineno)d]'))
    audit_handler.setLevel(logging.INFO)
    
    app.logger.addHandler(audit_handler)
    app.logger.setLevel(logging.INFO)
    
    if not app.debug and not app.testing:
        app.logger.info('NNPSMS System Startup')

    # Global Error Handlers & Production Safeguards
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    @app.errorhandler(Exception)
    def handle_unhandled_exception(e):
        """Catch-all for unexpected production errors to ensure graceful failure and DB rollback."""
        db.session.rollback()
        app.logger.error(f"Unhandled Exception: {str(e)}")
        return render_template('errors/500.html'), 500

    return app
