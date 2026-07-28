from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SelectField, DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional, ValidationError
from app.models.student import Student

class StudentForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    middle_name = StringField('Middle Name', validators=[Optional(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    
    national_id = StringField('National ID / Birth Certificate', validators=[Optional(), Length(max=30)])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[DataRequired()])
    date_of_birth = DateField('Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])
    
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    email = StringField('Email Address', validators=[DataRequired(), Email(), Length(max=120)])
    address = TextAreaField('Residential Address', validators=[Optional()])
    county = StringField('County', validators=[DataRequired(), Length(max=50)])
    
    guardian_name = StringField('Guardian / Parent Name', validators=[DataRequired(), Length(max=100)])
    guardian_phone = StringField('Guardian Phone Number', validators=[DataRequired(), Length(max=20)])
    guardian_email = StringField('Guardian Email', validators=[Optional(), Email(), Length(max=120)])
    emergency_contact = StringField('Emergency Contact', validators=[DataRequired(), Length(max=20)])
    
    department_id = SelectField('Department', coerce=int, validators=[DataRequired()])
    course_id = SelectField('Course', coerce=int, validators=[DataRequired()])
    academic_year = StringField('Academic Year (e.g. 2025/2026)', validators=[DataRequired(), Length(max=20)])
    semester_module = SelectField('Semester / Module', choices=[
        ('Term I', 'Term I'), ('Term II', 'Term II'), ('Term III', 'Term III'),
        ('Module I', 'Module I'), ('Module II', 'Module II'), ('Module III', 'Module III')
    ], validators=[DataRequired()])
    
    status = SelectField('Student Status', choices=[
        ('Active', 'Active'), ('Deferred', 'Deferred'), ('Suspended', 'Suspended'),
        ('Graduated', 'Graduated'), ('Alumni', 'Alumni')
    ], validators=[DataRequired()])
    
    passport_photo = FileField('Passport Photo', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    submit = SubmitField('Save Student Record')
