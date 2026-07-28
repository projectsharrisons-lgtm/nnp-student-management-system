"""
app/models/academic.py
Contains academic structure models (Department, Course, Unit) 
and academic profiles (StudentProfile, LecturerProfile).
"""

from app.extensions import db


class Department(db.Model):
    __tablename__ = 'department'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    code = db.Column(db.String(20), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=db.func.now())

    # Relationships
    courses = db.relationship('Course', backref='department', lazy=True, cascade="all, delete-orphan")
    units = db.relationship('Unit', backref='department', lazy=True, cascade="all, delete-orphan")
    lecturers = db.relationship('LecturerProfile', backref='department', lazy=True)

    def __repr__(self):
        return f"<Department {self.code}>"


class Course(db.Model):
    __tablename__ = 'course'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    code = db.Column(db.String(50), nullable=False, unique=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id', ondelete='RESTRICT'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

    # Relationships
    units = db.relationship('Unit', backref='course', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Course {self.code}>"


class Unit(db.Model):
    __tablename__ = 'unit'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    code = db.Column(db.String(50), nullable=False, unique=True)
    credits = db.Column(db.Integer, default=3)
    
    # Foreign Keys
    department_id = db.Column(db.Integer, db.ForeignKey('department.id', ondelete='RESTRICT'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id', ondelete='RESTRICT'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f"<Unit {self.code}>"


class StudentProfile(db.Model):
    __tablename__ = 'student_profile'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete='CASCADE'), nullable=False, unique=True)
    bio = db.Column(db.Text, nullable=True)
    hobbies = db.Column(db.String(255), nullable=True)
    extracurricular_activities = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    # Relationships
    student = db.relationship('Student', backref=db.backref('profile', uselist=False, lazy=True))

    def __repr__(self):
        return f"<StudentProfile for Student ID {self.student_id}>"


class LecturerProfile(db.Model):
    __tablename__ = 'lecturer_profile'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, unique=True)
    employee_number = db.Column(db.String(50), nullable=False, unique=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id', ondelete='RESTRICT'), nullable=True)
    
    title = db.Column(db.String(20), nullable=True)
    qualifications = db.Column(db.Text, nullable=True)
    bio = db.Column(db.Text, nullable=True)
    date_joined = db.Column(db.Date, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    # Relationships
    user = db.relationship('User', backref=db.backref('lecturer_profile', uselist=False, lazy=True))

    def __repr__(self):
        return f"<LecturerProfile {self.employee_number}>"
