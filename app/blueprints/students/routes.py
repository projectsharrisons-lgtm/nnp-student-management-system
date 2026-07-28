from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.utils import admin_required
from app.models.student import Student
from app.models.academic import Department, Course
from app.blueprints.students.forms import StudentForm
from datetime import datetime
import os
import uuid

students_bp = Blueprint('students', __name__, url_prefix='/students')

def generate_admission_number():
    """Generates a unique NNP admission number: NNP/YYYY/XXXX"""
    year = datetime.utcnow().year
    random_digits = str(uuid.uuid4().int)[:4]
    adm = f"NNP/{year}/{random_digits}"
    while Student.query.filter_by(admission_number=adm).first():
        random_digits = str(uuid.uuid4().int)[:4]
        adm = f"NNP/{year}/{random_digits}"
    return adm

@students_bp.route('/')
@login_required
@admin_required
def list_students():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str).strip()
    status_filter = request.args.get('status', '', type=str).strip()
    
    query = Student.query.filter_by(is_archived=False)
    
    if search:
        query = query.filter(
            (Student.first_name.ilike(f'%{search}%')) |
            (Student.middle_name.ilike(f'%{search}%')) |
            (Student.last_name.ilike(f'%{search}%')) |
            (Student.admission_number.ilike(f'%{search}%')) |
            (Student.email.ilike(f'%{search}%')) |
            (Student.phone_number.ilike(f'%{search}%'))
        )
        
    if status_filter:
        query = query.filter_by(status=status_filter)
        
    pagination = query.order_by(Student.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    students = pagination.items
    
    return render_template('students/list.html', students=students, pagination=pagination, search=search, status_filter=status_filter)

@students_bp.route('/profile/<int:id>')
@login_required
@admin_required
def view_student(id):
    student = Student.query.get_or_404(id)
    current_app.logger.info(f"User {current_user.username} viewed student profile {student.admission_number}")
    return render_template('students/profile.html', student=student)

@students_bp.route('/register', methods=['GET', 'POST'])
@login_required
@admin_required
def register_student():
    form = StudentForm()
    form.department_id.choices = [(d.id, d.name) for d in Department.query.order_by(Department.name).all()]
    form.course_id.choices = [(c.id, f"{c.code} - {c.name}") for c in Course.query.order_by(Course.code).all()]
    
    if form.validate_on_submit():
        if Student.query.filter_by(email=form.email.data).first():
            flash('A student with this email address already exists.', 'error')
            return render_template('students/register.html', form=form)
            
        try:
            filename = 'default_avatar.png'
            if form.passport_photo.data:
                file = form.passport_photo.data
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"{uuid.uuid4().hex}.{ext}"
                upload_folder = os.path.join(current_app.root_path, 'static/uploads/students')
                os.makedirs(upload_folder, exist_ok=True)
                file.save(os.path.join(upload_folder, filename))
            
            adm_no = generate_admission_number()
            
            student = Student(
                admission_number=adm_no,
                first_name=form.first_name.data,
                middle_name=form.middle_name.data,
                last_name=form.last_name.data,
                national_id=form.national_id.data,
                gender=form.gender.data,
                date_of_birth=form.date_of_birth.data,
                phone_number=form.phone_number.data,
                email=form.email.data,
                address=form.address.data,
                county=form.county.data,
                guardian_name=form.guardian_name.data,
                guardian_phone=form.guardian_phone.data,
                guardian_email=form.guardian_email.data,
                emergency_contact=form.emergency_contact.data,
                department_id=form.department_id.data,
                course_id=form.course_id.data,
                academic_year=form.academic_year.data,
                semester_module=form.semester_module.data,
                status=form.status.data,
                passport_photo=filename
            )
            
            db.session.add(student)
            db.session.commit()
            current_app.logger.info(f"User {current_user.username} registered student {adm_no}")
            flash(f'Student registered successfully with Admission No: {adm_no}', 'success')
            return redirect(url_for('students.list_students'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Student registration error: {str(e)}")
            flash('An error occurred while saving student record.', 'error')
            
    return render_template('students/register.html', form=form)

@students_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_student(id):
    student = Student.query.get_or_404(id)
    form = StudentForm(obj=student)
    form.department_id.choices = [(d.id, d.name) for d in Department.query.order_by(Department.name).all()]
    form.course_id.choices = [(c.id, f"{c.code} - {c.name}") for c in Course.query.order_by(Course.code).all()]
    
    if form.validate_on_submit():
        existing = Student.query.filter((Student.email == form.email.data) & (Student.id != id)).first()
        if existing:
            flash('Another student with this email address already exists.', 'error')
            return render_template('students/edit.html', form=form, student=student)
            
        try:
            if form.passport_photo.data:
                file = form.passport_photo.data
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"{uuid.uuid4().hex}.{ext}"
                upload_folder = os.path.join(current_app.root_path, 'static/uploads/students')
                os.makedirs(upload_folder, exist_ok=True)
                
                # Unlink previous photo if not default avatar
                if student.passport_photo and student.passport_photo != 'default_avatar.png':
                    old_file_path = os.path.join(upload_folder, student.passport_photo)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                        
                file.save(os.path.join(upload_folder, filename))
                student.passport_photo = filename
                
            student.first_name = form.first_name.data
            student.middle_name = form.middle_name.data
            student.last_name = form.last_name.data
            student.national_id = form.national_id.data
            student.gender = form.gender.data
            student.date_of_birth = form.date_of_birth.data
            student.phone_number = form.phone_number.data
            student.email = form.email.data
            student.address = form.address.data
            student.county = form.county.data
            student.guardian_name = form.guardian_name.data
            student.guardian_phone = form.guardian_phone.data
            student.guardian_email = form.guardian_email.data
            student.emergency_contact = form.emergency_contact.data
            student.department_id = form.department_id.data
            student.course_id = form.course_id.data
            student.academic_year = form.academic_year.data
            student.semester_module = form.semester_module.data
            student.status = form.status.data
            
            db.session.commit()
            current_app.logger.info(f"User {current_user.username} updated student {student.admission_number}")
            flash('Student record updated successfully!', 'success')
            return redirect(url_for('students.view_student', id=student.id))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Student update error: {str(e)}")
            flash('Failed to update student record.', 'error')
            
    return render_template('students/edit.html', form=form, student=student)

@students_bp.route('/archive/<int:id>', methods=['POST'])
@login_required
@admin_required
def archive_student(id):
    student = Student.query.get_or_404(id)
    try:
        student.is_archived = True
        student.status = 'Archived'
        db.session.commit()
        current_app.logger.info(f"User {current_user.username} archived student {student.admission_number}")
        flash('Student archived successfully.', 'info')
    except Exception as e:
        db.session.rollback()
        flash('Error archiving student record.', 'error')
    return redirect(url_for('students.list_students'))

@students_bp.route('/restore/<int:id>', methods=['POST'])
@login_required
@admin_required
def restore_student(id):
    student = Student.query.get_or_404(id)
    try:
        student.is_archived = False
        student.status = 'Active'
        db.session.commit()
        current_app.logger.info(f"User {current_user.username} restored student {student.admission_number}")
        flash('Student restored successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error restoring student record.', 'error')
    return redirect(url_for('students.list_students'))

@students_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_student(id):
    student = Student.query.get_or_404(id)
    try:
        if student.passport_photo and student.passport_photo != 'default_avatar.png':
            upload_folder = os.path.join(current_app.root_path, 'static/uploads/students')
            old_file_path = os.path.join(upload_folder, student.passport_photo)
            if os.path.exists(old_file_path):
                os.remove(old_file_path)
                
        db.session.delete(student)
        db.session.commit()
        current_app.logger.info(f"User {current_user.username} permanently deleted student {student.admission_number}")
        flash('Student record permanently deleted.', 'info')
    except Exception as e:
        db.session.rollback()
        flash('Cannot delete student due to active system relations.', 'error')
    return redirect(url_for('students.list_students'))
