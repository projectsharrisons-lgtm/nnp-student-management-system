from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required
from app.extensions import db
from app.utils import admin_required
from app.models.academic import Department, Course, Unit
from app.blueprints.admin.forms import DepartmentForm, CourseForm, UnitForm

admin_bp = Blueprint('admin', __name__, url_prefix='/admin-panel')

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    dept_count = Department.query.count()
    course_count = Course.query.count()
    unit_count = Unit.query.count()
    return render_template('admin/dashboard.html', dept_count=dept_count, course_count=course_count, unit_count=unit_count)

# --- Department Management ---
@admin_bp.route('/departments')
@login_required
@admin_required
def list_departments():
    departments = Department.query.all()
    return render_template('admin/departments.html', departments=departments)

@admin_bp.route('/departments/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_department():
    form = DepartmentForm()
    if form.validate_on_submit():
        dept = Department(name=form.name.data, code=form.code.data.upper(), description=form.description.data)
        db.session.add(dept)
        db.session.commit()
        current_app.logger.info(f"Admin added new Department: {dept.code}")
        flash('Department created successfully!', 'success')
        return redirect(url_for('admin.list_departments'))
    return render_template('admin/department_form.html', form=form, title="Add Department")

@admin_bp.route('/departments/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_department(id):
    dept = Department.query.get_or_404(id)
    form = DepartmentForm(obj=dept)
    if form.validate_on_submit():
        dept.name = form.name.data
        dept.code = form.code.data.upper()
        dept.description = form.description.data
        db.session.commit()
        current_app.logger.info(f"Admin updated Department ID: {id}")
        flash('Department updated successfully!', 'success')
        return redirect(url_for('admin.list_departments'))
    return render_template('admin/department_form.html', form=form, title="Edit Department")

@admin_bp.route('/departments/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_department(id):
    dept = Department.query.get_or_404(id)
    db.session.delete(dept)
    db.session.commit()
    current_app.logger.info(f"Admin deleted Department ID: {id}")
    flash('Department deleted safely along with associated child entities.', 'info')
    return redirect(url_for('admin.list_departments'))

# --- Course Management ---
@admin_bp.route('/courses')
@login_required
@admin_required
def list_courses():
    courses = Course.query.all()
    return render_template('admin/courses.html', courses=courses)

@admin_bp.route('/courses/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_course():
    form = CourseForm()
    form.department_id.choices = [(d.id, d.name) for d in Department.query.all()]
    if form.validate_on_submit():
        course = Course(name=form.name.data, code=form.code.data.upper(), level=form.level.data, department_id=form.department_id.data)
        db.session.add(course)
        db.session.commit()
        current_app.logger.info(f"Admin added new Course: {course.code}")
        flash('Course created successfully!', 'success')
        return redirect(url_for('admin.list_courses'))
    return render_template('admin/course_form.html', form=form, title="Add Course")

@admin_bp.route('/courses/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_course(id):
    course = Course.query.get_or_404(id)
    db.session.delete(course)
    db.session.commit()
    flash('Course deleted successfully.', 'info')
    return redirect(url_for('admin.list_courses'))

# --- Unit Management ---
@admin_bp.route('/units')
@login_required
@admin_required
def list_units():
    units = Unit.query.all()
    return render_template('admin/units.html', units=units)

@admin_bp.route('/units/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_unit():
    form = UnitForm()
    form.course_id.choices = [(c.id, f"{c.code} - {c.name}") for c in Course.query.all()]
    if form.validate_on_submit():
        unit = Unit(name=form.name.data, code=form.code.data.upper(), course_id=form.course_id.data)
        db.session.add(unit)
        db.session.commit()
        flash('Unit created successfully!', 'success')
        return redirect(url_for('admin.list_units'))
    return render_template('admin/unit_form.html', form=form, title="Add Unit")

@admin_bp.route('/units/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_unit(id):
    unit = Unit.query.get_or_404(id)
    db.session.delete(unit)
    db.session.commit()
    flash('Unit removed successfully.', 'info')
    return redirect(url_for('admin.list_units'))
