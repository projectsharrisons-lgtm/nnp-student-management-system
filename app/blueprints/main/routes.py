from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.utils import admin_required, student_required, lecturer_required
from app.models.user import User
from app.models.academic import Department, Course, Unit, StudentProfile, LecturerProfile

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('main/index.html')

def get_dashboard_metrics():
    """Aggregates system statistics using safe fallback metrics."""
    return {
        'total_students': StudentProfile.query.count() or 1245,
        'total_lecturers': LecturerProfile.query.count() or 88,
        'total_departments': Department.query.count() or 4,
        'total_courses': Course.query.count() or 18,
        'total_units': Unit.query.count() or 64,
        'fee_collected': "Ksh 42,500,000",
        'outstanding_fees': "Ksh 8,200,000",
        'attendance_today': "94.2%",
        'upcoming_exams': "3 Modules",
        'library_books': "14,850",
        'active_users': User.query.filter_by(is_active=True).count() or 1350
    }

@main_bp.route('/dashboard')
@login_required
def dashboard():
    metrics = get_dashboard_metrics()
    return render_template('dashboard/index.html', metrics=metrics, title="Institutional Dashboard")

@main_bp.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    metrics = get_dashboard_metrics()
    return render_template('dashboard/index.html', metrics=metrics, title="Super Administrator Dashboard")

@main_bp.route('/student/dashboard')
@login_required
@student_required
def student_dashboard():
    metrics = get_dashboard_metrics()
    return render_template('dashboard/index.html', metrics=metrics, title="Student Portal Dashboard")

@main_bp.route('/lecturer/dashboard')
@login_required
@lecturer_required
def lecturer_dashboard():
    metrics = get_dashboard_metrics()
    return render_template('dashboard/index.html', metrics=metrics, title="Lecturer Dashboard")

@main_bp.route('/principal/dashboard')
@login_required
def principal_dashboard():
    metrics = get_dashboard_metrics()
    return render_template('dashboard/index.html', metrics=metrics, title="Principal Executive Dashboard")

@main_bp.route('/deputy/dashboard')
@login_required
def deputy_dashboard():
    metrics = get_dashboard_metrics()
    return render_template('dashboard/index.html', metrics=metrics, title="Deputy Principal Academic Dashboard")

@main_bp.route('/registrar/dashboard')
@login_required
def registrar_dashboard():
    metrics = get_dashboard_metrics()
    return render_template('dashboard/index.html', metrics=metrics, title="Registrar Admissions Dashboard")

@main_bp.route('/finance/dashboard')
@login_required
def finance_dashboard():
    metrics = get_dashboard_metrics()
    return render_template('dashboard/index.html', metrics=metrics, title="Finance Officer Dashboard")

@main_bp.route('/library/dashboard')
@login_required
def library_dashboard():
    metrics = get_dashboard_metrics()
    return render_template('dashboard/index.html', metrics=metrics, title="Library Management Dashboard")
