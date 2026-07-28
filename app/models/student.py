from app.extensions import db
from datetime import datetime

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    admission_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=False)
    passport_photo = db.Column(db.String(255), nullable=True, default='default_avatar.png')
    national_id = db.Column(db.String(30), unique=True, nullable=True)
    gender = db.Column(db.String(20), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    address = db.Column(db.Text, nullable=True)
    county = db.Column(db.String(50), nullable=False)
    
    # Guardian Details
    guardian_name = db.Column(db.String(100), nullable=False)
    guardian_phone = db.Column(db.String(20), nullable=False)
    guardian_email = db.Column(db.String(120), nullable=True)
    emergency_contact = db.Column(db.String(20), nullable=False)
    
    # Academic Relations
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='RESTRICT'), nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='RESTRICT'), nullable=False, index=True)
    academic_year = db.Column(db.String(20), nullable=False)
    semester_module = db.Column(db.String(30), nullable=False)
    enrollment_date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    
    # Status Management
    status = db.Column(db.String(30), default='Active', nullable=False, index=True) # Active, Deferred, Suspended, Graduated, Alumni, Archived
    is_archived = db.Column(db.Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships mapping
    department = db.relationship('Department', backref='students', lazy='select')
    course = db.relationship('Course', backref='enrolled_students', lazy='select')

    def __repr__(self):
        return f"<Student {self.admission_number}: {self.first_name} {self.last_name}>"
