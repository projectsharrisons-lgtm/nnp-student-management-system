from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required
from app.extensions import db
from app.utils import admin_required
from app.models.academic import Department, Course, Unit
from app.blueprints.admin.forms import DepartmentForm, CourseForm, UnitForm
from sqlalchemy.exc import IntegrityError

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
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    query = Department.query
    if search:
        query = query.filter(
            (Department.name.ilike(f'%{search}%')) | 
            (Department.code.ilike(f'%{search}%'))
        )
    
    pagination = query.paginate(page=page, per_page=10, error_out=False)
    departments = pagination.items
    return render_template('admin/departments.html', departments=departments, pagination=pagination, search=search)

@admin_bp.route('/departments/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_department():
    form = DepartmentForm()
    if form.validate_on_submit():
        existing = Department.query.filter((Department.code == form.code.data.upper()) | (Department.name == form.name.data)).first()
        if existing:
            flash('A department with this name or code already exists.', 'error')
            return render_template('admin/department_form.html', form=form, title="Add Department")
        
        try:
            dept = Department(name=form.name.data, code=form.code.data.upper(), description=form.description.data)
            db.session.add(dept)
            db.session.commit()
            current_app.logger.info(f"Admin added new Department: {dept.code}")
            flash('Department created successfully!', 'success')
            return redirect(url_for('admin.list_departments'))
        except IntegrityError:
            db.session.rollback()
            flash('Database error: Duplicate department code or name encountered.', 'error')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding department: {str(e)}")
            flash('An unexpected error occurred while saving. Please try again.', 'error')
            
    return render_template('admin/department_form.html', form=form, title="Add Department")

@admin_bp.route('/departments/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_department(id):
    dept = Department.query.get_or_404(id)
    form = DepartmentForm(obj=dept)
    if form.validate_on_submit():
        # Check duplicates excluding current ID
        existing = Department.query.filter(
            ((Department.code == form.code.data.upper()) | (Department.name == form.name.data)) & 
            (Department.id != id)
        ).first()
        if existing:
            flash('Another department with this name or code already exists.', 'error')
            return render_template('admin/department_form.html', form=form, title="Edit Department")
        
        try:
            dept.name = form.name.data
            dept.code = form.code.data.upper()
            dept.description = form.description.data
            db.session.commit()
            current_app.logger.info(f"Admin updated Department ID: {id}")
            flash('Department updated successfully!', 'success')
            return redirect(url_for('admin.list_departments'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during update. Please try again.', 'error')
            
    return render_template('admin/department_form.html', form=form, title="Edit Department")

@admin_bp.route('/departments/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_department(id):
    dept = Department.query.get_or_404(id)
    try:
        db.session.delete(dept)
        db.session.commit()
        current_app.logger.info(f"Admin deleted Department ID: {id}")
        flash('Department deleted safely along with associated child entities.', 'info')
    except Exception as e:
        db.session.rollback()
        flash('Cannot delete department due to active relational dependencies.', 'error')
    return redirect(url_for('admin.list_departments'))

# --- Course Management ---
@admin_bp.route('/courses')
@login_required
@admin_required
def list_courses():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    query = Course.query
    if search:
        query = query.filter(
            (Course.name.ilike(f'%{search}%')) | 
            (Course.code.ilike(f'%{search}%'))
        )
    
    pagination = query.paginate(page=page, per_page=10, error_out=False)
    courses = pagination.items
    return render_template('admin/courses.html', courses=courses, pagination=pagination, search=search)

@admin_bp.route('/courses/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_course():
    form = CourseForm()
    form.department_id.choices = [(d.id, d.name) for d in Department.query.all()]
    if form.validate_on_submit():
        existing = Course.query.filter_by(code=form.code.data.upper()).first()
        if existing:
            flash('A course with this code already exists.', 'error')
            return render_template('admin/course_form.html', form=form, title="Add Course")
        
        try:
            course = Course(name=form.name.data, code=form.code.data.upper(), level=form.level.data, department_id=form.department_id.data)
            db.session.add(course)
            db.session.commit()
            current_app.logger.info(f"Admin added new Course: {course.code}")
            flash('Course created successfully!', 'success')
            return redirect(url_for('admin.list_courses'))
        except Exception as e:
            db.session.rollback()
            flash('Failed to save course. Please check inputs.', 'error')
            
    return render_template('admin/course_form.html', form=form, title="Add Course")

@admin_bp.route('/courses/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_course(id):
    course = Course.query.get_or_404(id)
    form = CourseForm(obj=course)
    form.department_id.choices = [(d.id, d.name) for d in Department.query.all()]
    
    if form.validate_on_submit():
        existing = Course.query.filter((Course.code == form.code.data.upper()) & (Course.id != id)).first()
        if existing:
            flash('Another course with this code already exists.', 'error')
            return render_template('admin/course_form.html', form=form, title="Edit Course")
        
        try:
            course.name = form.name.data
            course.code = form.code.data.upper()
            course.level = form.level.data
            course.department_id = form.department_id.data
            db.session.commit()
            flash('Course updated successfully!', 'success')
            return redirect(url_for('admin.list_courses'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating course database record.', 'error')
            
    return render_template('admin/course_form.html', form=form, title="Edit Course")

@admin_bp.route('/courses/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_course(id):
    course = Course.query.get_or_404(id)
    try:
        db.session.delete(course)
        db.session.commit()
        flash('Course deleted successfully.', 'info')
    except Exception as e:
        db.session.rollback()
        flash('Cannot delete course due to linked student records or units.', 'error')
    return redirect(url_for('admin.list_courses'))

# --- Unit Management ---
@admin_bp.route('/units')
@login_required
@admin_required
def list_units():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    query = Unit.query
    if search:
        query = query.filter(
            (Unit.name.ilike(f'%{search}%')) | 
            (Unit.code.ilike(f'%{search}%'))
        )
    
    pagination = query.paginate(page=page, per_page=10, error_out=False)
    units = pagination.items
    return render_template('admin/units.html', units=units, pagination=pagination, search=search)

@admin_bp.route('/units/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_unit():
    form = UnitForm()
    form.course_id.choices = [(c.id, f"{c.code} - {c.name}") for c in Course.query.all()]
    if form.validate_on_submit():
        existing = Unit.query.filter_by(code=form.code.data.upper()).first()
        if existing:
            flash('A unit with this code already exists.', 'error')
            return render_template('admin/unit_form.html', form=form, title="Add Unit")
        
        try:
            unit = Unit(name=form.name.data, code=form.code.data.upper(), course_id=form.course_id.data)
            db.session.add(unit)
            db.session.commit()
            flash('Unit created successfully!', 'success')
            return redirect(url_for('admin.list_units'))
        except Exception as e:
            db.session.rollback()
            flash('Failed to save unit record.', 'error')
            
    return render_template('admin/unit_form.html', form=form, title="Add Unit")

@admin_bp.route('/units/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_unit(id):
    unit = Unit.query.get_or_404(id)
    form = UnitForm(obj=unit)
    form.course_id.choices = [(c.id, f"{c.code} - {c.name}") for c in Course.query.all()]
    
    if form.validate_on_submit():
        existing = Unit.query.filter((Unit.code == form.code.data.upper()) & (Unit.id != id)).first()
        if existing:
            flash('Another unit with this code already exists.', 'error')
            return render_template('admin/unit_form.html', form=form, title="Edit Unit")
        
        try:
            unit.name = form.name.data
            unit.code = form.code.data.upper()
            unit.course_id = form.course_id.data
            db.session.commit()
            flash('Unit updated successfully!', 'success')
            return redirect(url_for('admin.list_units'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating unit record.', 'error')
            
    return render_template('admin/unit_form.html', form=form, title="Edit Unit")

@admin_bp.route('/units/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_unit(id):
    unit = Unit.query.get_or_404(id)
    try:
        db.session.delete(unit)
        db.session.commit()
        flash('Unit removed successfully.', 'info')
    except Exception as e:
        db.session.rollback()
        flash('Error occurred while deleting unit.', 'error')
    return redirect(url_for('admin.list_units'))
