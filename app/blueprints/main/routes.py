from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.utils import admin_required, student_required, lecturer_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('main/index.html')

# Base Dashboard route (Fallback)
@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('main/dashboard.html')

# Role-specific dashboard scaffolding (To be expanded in Phase 2)
@main_bp.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    return render_template('main/dashboard.html', title="Super Administrator Dashboard")

@main_bp.route('/student/dashboard')
@login_required
@student_required
def student_dashboard():
    return render_template('main/dashboard.html', title="Student Dashboard")

@main_bp.route('/lecturer/dashboard')
@login_required
@lecturer_required
def lecturer_dashboard():
    return render_template('main/dashboard.html', title="Lecturer Dashboard")

@main_bp.route('/principal/dashboard')
@login_required
def principal_dashboard():
    return render_template('main/dashboard.html', title="Principal Dashboard")

@main_bp.route('/deputy/dashboard')
@login_required
def deputy_dashboard():
    return render_template('main/dashboard.html', title="Deputy Principal Dashboard")

@main_bp.route('/registrar/dashboard')
@login_required
def registrar_dashboard():
    return render_template('main/dashboard.html', title="Registrar Dashboard")

@main_bp.route('/finance/dashboard')
@login_required
def finance_dashboard():
    return render_template('main/dashboard.html', title="Finance Dashboard")

@main_bp.route('/library/dashboard')
@login_required
def library_dashboard():
    return render_template('main/dashboard.html', title="Library Dashboard")
