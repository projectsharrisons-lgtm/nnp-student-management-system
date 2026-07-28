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
