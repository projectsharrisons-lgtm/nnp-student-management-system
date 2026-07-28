from app.extensions import db
from datetime import datetime

class Department(db.Model):
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False, index=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    courses = db.relationship('Course', backref='department', lazy='select', cascade='save-update, merge')

    def __repr__(self):
        return f"<Department {self.code}: {self.name}>"

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False, index=True)
    code = db.Column(db.String(30), unique=True, nullable=False, index=True)
    level = db.Column(db.String(50), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='RESTRICT'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    units = db.relationship('Unit', backref='course', lazy='select', cascade='all, delete-orphan')
    students = db.relationship('StudentProfile', backref='course', lazy='select', cascade='save-update, merge')

    def __repr__(self):
        return f"<Course {self.code}: {self.name}>"

class Unit(db.Model):
    __tablename__ = 'units'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    code = db.Column(db.String(30), unique=True, nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Unit {self.code}: {self.name}>"
class StudentProfile(db.Model):
    __tablename__ = "student_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    adm_number = db.Column(db.String(50), unique=True, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    academic_year = db.Column(db.String(20), default="2026/2027")
    module_term = db.Column(db.String(50), default="Module I")

    user = db.relationship(
        "User",
        backref=db.backref("student_profile", uselist=False)
    )

    def __repr__(self):
        return f"<StudentProfile {self.adm_number}>"
        class LecturerProfile(db.Model):
    __tablename__ = "lecturer_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    staff_number = db.Column(db.String(50), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"))
    specialization = db.Column(db.String(150))

    department = db.relationship(
        "Department",
        backref=db.backref("lecturers", lazy=True)
    )

    user = db.relationship(
        "User",
        backref=db.backref("lecturer_profile", uselist=False)
    )

    def __repr__(self):
        return f"<LecturerProfile {self.staff_number}>"
