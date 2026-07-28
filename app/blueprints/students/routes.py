@students_bp.route('/')
@login_required
@admin_required
def list_students():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    status_filter = request.args.get('status', '', type=str)
    
    query = Student.query.filter_by(is_archived=False)
    if search:
        query = query.filter(
            (Student.first_name.ilike(f'%{search}%')) |
            (Student.last_name.ilike(f'%{search}%')) |
            (Student.admission_number.ilike(f'%{search}%')) |
            (Student.email.ilike(f'%{search}%')) |
            (Student.phone_number.ilike(f'%{search}%'))
        )
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    pagination = query.paginate(page=page, per_page=10, error_out=False)
    students = pagination.items
    return render_template('students/list.html', students=students, pagination=pagination, search=search, status_filter=status_filter)

@students_bp.route('/profile/<int:id>')
@login_required
@admin_required
def view_student(id):
    student = Student.query.get_or_404(id)
    current_app.logger.info(f"User {current_user.username} viewed student profile {student.admission_number}")
    return render_template('students/profile.html', student=student)
