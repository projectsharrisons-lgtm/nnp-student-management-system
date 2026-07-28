from datetime import datetime
from app.extensions import db

class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Relationships
    courses = db.relationship('Course', backref='department', lazy=True, cascade='all, delete-orphan')
    lecturers = db.relationship('LecturerProfile', backref='department', lazy=True)

    def __repr__(self):
        return f'<Department {self.code}: {self.name}>'


class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    code = db.Column(db.String(30), unique=True, nullable=False)
    level = db.Column(db.String(50), nullable=False)  # e.g., Level 3 (Artisan), Level 5 (Diploma), Level 6 (Higher Diploma)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    
    # Relationships
    units = db.relationship('Unit', backref='course', lazy=True, cascade='all, delete-orphan')
    students = db.relationship('StudentProfile', backref='course', lazy=True)

    def __repr__(self):
        return f'<Course {self.code} - {self.name}>'


class Unit(db.Model):
    __tablename__ = 'units'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    code = db.Column(db.String(30), unique=True, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)

    def __repr__(self):
        return f'<Unit {self.code}: {self.name}>'


class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    adm_number = db.Column(db.String(50), unique=True, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=True)
    academic_year = db.Column(db.String(20), nullable=False, default='2026/2027')
    module_term = db.Column(db.String(50), nullable=False, default='Module I')
    
    # Relationship back to base User model
    user = db.relationship('User', backref=db.backref('student_profile', uselist=False, cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<StudentProfile {self.adm_number}>'


class LecturerProfile(db.Model):
    __tablename__ = 'lecturer_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    staff_number = db.Column(db.String(50), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    specialization = db.Column(db.String(150), nullable=True)
    
    # Relationship back to base User model
    user = db.relationship('User', backref=db.backref('lecturer_profile', uselist=False, cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<LecturerProfile {self.staff_number}>'
