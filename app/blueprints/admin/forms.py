from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from app.models.academic import Department, Course, Unit

class DepartmentForm(FlaskForm):
    name = StringField('Department Name', validators=[DataRequired(), Length(max=150)])
    code = StringField('Department Code (e.g., COMP)', validators=[DataRequired(), Length(max=20)])
    description = TextAreaField('Description')
    submit = SubmitField('Save Department')

class CourseForm(FlaskForm):
    name = StringField('Course Name', validators=[DataRequired(), Length(max=150)])
    code = StringField('Course Code (e.g., ICT-6)', validators=[DataRequired(), Length(max=30)])
    level = SelectField('TVET Level / Category', choices=[
        ('Level 3 - Artisan', 'Level 3 (Artisan)'),
        ('Level 4 - Craft Certificate', 'Level 4 (Craft Certificate)'),
        ('Level 5 - Diploma', 'Level 5 (Diploma)'),
        ('Level 6 - Higher Diploma', 'Level 6 (Higher Diploma / Technologist)')
    ], validators=[DataRequired()])
    department_id = SelectField('Parent Department', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save Course')

class UnitForm(FlaskForm):
    name = StringField('Unit Name', validators=[DataRequired(), Length(max=150)])
    code = StringField('Unit Code (e.g., CIT 2101)', validators=[DataRequired(), Length(max=30)])
    course_id = SelectField('Associated Course', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save Unit')
