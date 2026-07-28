import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template
from werkzeug.exceptions import HTTPException
from config import config_dict
from app.extensions import db, migrate, login_manager, csrf, mail, limiter
from app.extensions import db
from app.models.user import User
from app.models.academic import Department, Course, Unit, StudentProfile, LecturerProfile
from app.blueprints.main.routes import main_bp
from app.blueprints.auth.routes import auth_bp
from app.blueprints.admin.routes import admin_bp
from app.blueprints.students.routes import students_bp
    
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp)
app.register_blueprint(students_bp)
def seed_database():
    print("🌱 Starting Nyeri National Polytechnic Seed Process...")

    # 1. Clear or check existing records to prevent duplication errors
    if Department.query.first():
        print("⚠️ Database already contains academic data. Skipping seeding.")
        return

    # 2. Create Default Users (Admin, Lecturer, Student)
    admin_user = User(username='superadmin', email='admin@thenyeripoly.ac.ke', role='Super Administrator', is_verified=True)
    admin_user.set_password('Admin@2026!')
    
    lecturer_user = User(username='jkamau', email='jkamau@thenyeripoly.ac.ke', role='Lecturer', is_verified=True)
    lecturer_user.set_password('Lecturer@2026!')

    student_user = User(username='wanjiku_s', email='student@thenyeripoly.ac.ke', role='Student', is_verified=True)
    student_user.set_password('Student@2026!')

    db.session.add_all([admin_user, lecturer_user, student_user])
    db.session.commit()

    # 3. Create NNP Departments (Real institutional data mapping)
    dept_ict = Department(name="Computing and Informatics", code="COMP", description="Department specializing in ICT, Software Engineering, and Network Administration.")
    dept_bus = Department(name="Business Studies and Entrepreneurship", code="BUS", description="Offering accounting, banking, human resource, and business administration.")
    dept_eng = Department(name="Electrical and Electronics Engineering", code="EE", description="Focuses on power systems, telecommunications, and industrial automation.")
    dept_agr = Department(name="Agriculture and Environmental Studies", code="AGR", description="Training in agricultural extension, horticulture, and animal health.")

    db.session.add_all([dept_ict, dept_bus, dept_eng, dept_agr])
    db.session.commit()

    # 4. Create Courses
    c_ict_dip = Course(name="Diploma in Information Communication Technology", code="ICT-D-06", level="Level 5 - Diploma", department_id=dept_ict.id)
    c_sw_dip = Course(name="Diploma in Software Development", code="SD-D-06", level="Level 5 - Diploma", department_id=dept_ict.id)
    c_bus_dip = Course(name="Diploma in Business Management", code="BM-D-05", level="Level 5 - Diploma", department_id=dept_bus.id)
    c_elec = Course(name="Electrical Engineering Technology (Power Option)", code="EE-T-06", level="Level 6 - Higher Diploma", department_id=dept_eng.id)

    db.session.add_all([c_ict_dip, c_sw_dip, c_bus_dip, c_elec])
    db.session.commit()

    # 5. Create Units
    u1 = Unit(name="Object Oriented Programming", code="CIT 2201", course_id=c_ict_dip.id)
    u2 = Unit(name="Database Management Systems", code="CIT 2202", course_id=c_ict_dip.id)
    u3 = Unit(name="Web Application Development", code="SWE 3101", course_id=c_sw_dip.id)
    u4 = Unit(name="Financial Accounting I", code="BUS 1101", course_id=c_bus_dip.id)

    db.session.add_all([u1, u2, u3, u4])
    db.session.commit()

    # 6. Create Associated Profiles
    student_profile = StudentProfile(user_id=student_user.id, adm_number="NNP/2026/09482", course_id=c_ict_dip.id)
    lecturer_profile = LecturerProfile(user_id=lecturer_user.id, staff_number="STF/COMP/041", department_id=dept_ict.id, specialization="Software Architecture")

    db.session.add_all([student_profile, lecturer_profile])
    db.session.commit()

    print("✅ Nyeri National Polytechnic database seeded successfully!")
def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_dict[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)

    from app.blueprints.main.routes import main_bp
    from app.blueprints.auth.routes import auth_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # FIX: Safe directory creation for logs
    os.makedirs('logs', exist_ok=True)
    
    audit_handler = RotatingFileHandler('logs/nnpsms_audit.log', maxBytes=10485760, backupCount=10)
    audit_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - AUDIT: %(message)s [in %(pathname)s:%(lineno)d]'))
    audit_handler.setLevel(logging.INFO)
    
    app.logger.addHandler(audit_handler)
    app.logger.setLevel(logging.INFO)
    
    if not app.debug and not app.testing:
        app.logger.info('NNPSMS System Startup')

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
        # FIX: Do not intercept normal routing errors (404, 405)
        if isinstance(e, HTTPException):
            return e
            
        db.session.rollback()
        app.logger.error(f"Unhandled Exception: {str(e)}", exc_info=True)
        return render_template('errors/500.html'), 500

    return app
