from flask import Blueprint, render_template
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('main/index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Render different dashboard metrics based on role
    # Core system generates standard view, data fetching will expand in next phases
    return render_template('main/dashboard.html')
