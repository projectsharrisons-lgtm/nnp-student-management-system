from functools import wraps
from flask import abort, current_app
from flask_login import current_user
from flask_mail import Message
from app.extensions import mail
from threading import Thread

# --- Email Helpers ---
def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            app.logger.error(f"System Error: Failed to send email to {msg.recipients}. Error: {str(e)}")

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()


# --- Role-Based Access Control (RBAC) Decorators ---
def role_required(*roles):
    """Generic decorator to check multiple roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return current_app.login_manager.unauthorized()
            if current_user.role not in roles and current_user.role != 'Super Administrator':
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    return role_required('Super Administrator')(f)

def principal_required(f):
    return role_required('Principal')(f)

def registrar_required(f):
    return role_required('Registrar')(f)

def lecturer_required(f):
    return role_required('Lecturer')(f)

def finance_required(f):
    return role_required('Finance Officer')(f)

def librarian_required(f):
    return role_required('Librarian')(f)

def student_required(f):
    return role_required('Student')(f)
import os
from io import BytesIO
from datetime import datetime
from flask import current_app
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def _get_pdf_header_flowables():
    """Builds standard Nyeri National Polytechnic letterhead."""
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'PolyTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        alignment=1, # Center
        textColor=colors.HexColor('#1E3A8A')
    )
    
    subtitle_style = ParagraphStyle(
        'PolySubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        alignment=1,
        textColor=colors.HexColor('#4B5563')
    )
    
    return [
        Paragraph("THE NYERI NATIONAL POLYTECHNIC", title_style),
        Paragraph("P.O. Box 865-10100, Nyeri, Kenya | Tel: +254 700 000 000 | Email: info@nyerinationalpoly.ac.ke", subtitle_style),
        Paragraph("Website: www.nyerinationalpoly.ac.ke | Office of the Academic Registrar", subtitle_style),
        Spacer(1, 0.1 * inch),
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1E3A8A'), spaceAfter=15)
    ]

def generate_student_profile_pdf(student):
    """Generates a complete PDF document of a student's profile."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    heading_style = ParagraphStyle('SectionHeading', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#1E3A8A'), spaceAfter=6)
    cell_label = ParagraphStyle('CellLabel', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor('#374151'))
    cell_val = ParagraphStyle('CellVal', parent=styles['Normal'], fontName='Helvetica', fontSize=9, textColor=colors.HexColor('#111827'))
    
    story = _get_pdf_header_flowables()
    
    doc_title = ParagraphStyle('DocTitle', parent=styles['Heading2'], alignment=1, fontSize=13, fontName='Helvetica-Bold', textColor=colors.HexColor('#1F2937'), spaceAfter=12)
    story.append(Paragraph("OFFICIAL STUDENT PROFILE RECORD", doc_title))
    
    photo_path = os.path.join(current_app.root_path, 'static/uploads/students', student.passport_photo or 'default_avatar.png')
    if not os.path.exists(photo_path):
        photo_path = os.path.join(current_app.root_path, 'static/uploads/students/default_avatar.png')
        
    try:
        img = Image(photo_path, width=1.1 * inch, height=1.3 * inch)
    except Exception:
        img = Paragraph("<b>[Photo]</b>", cell_val)
        
    summary_text = f"""
    <b>Name:</b> {student.first_name} {student.middle_name or ''} {student.last_name}<br/>
    <b>Admission No:</b> {student.admission_number}<br/>
    <b>Department:</b> {student.department.name if student.department else 'N/A'}<br/>
    <b>Course:</b> {student.course.name if student.course else 'N/A'}<br/>
    <b>Status:</b> {student.status} | <b>Academic Year:</b> {student.academic_year}
    """
    
    header_table = Table([[img, Paragraph(summary_text, cell_val)]], colWidths=[1.3 * inch, 5.5 * inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F9FAFB')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB'))
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.15 * inch))
    
    story.append(Paragraph("1. Personal Particulars", heading_style))
    personal_data = [
        [Paragraph("Gender", cell_label), Paragraph(student.gender, cell_val), Paragraph("Date of Birth", cell_label), Paragraph(student.date_of_birth.strftime('%Y-%m-%d') if student.date_of_birth else 'N/A', cell_val)],
        [Paragraph("National ID / Cert", cell_label), Paragraph(student.national_id or 'N/A', cell_val), Paragraph("County", cell_label), Paragraph(student.county, cell_val)],
        [Paragraph("Email Address", cell_label), Paragraph(student.email, cell_val), Paragraph("Phone Number", cell_label), Paragraph(student.phone_number, cell_val)],
        [Paragraph("Residential Address", cell_label), Paragraph(student.address or 'N/A', cell_val), Paragraph("Enrollment Date", cell_label), Paragraph(student.enrollment_date.strftime('%Y-%m-%d') if student.enrollment_date else 'N/A', cell_val)]
    ]
    t1 = Table(personal_data, colWidths=[1.5*inch, 2.0*inch, 1.5*inch, 1.8*inch])
    t1.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#F3F4F6')),
        ('BACKGROUND', (2,0), (2,-1), colors.HexColor('#F3F4F6')),
        ('PADDING', (0,0), (-1,-1), 5)
    ]))
    story.append(t1)
    story.append(Spacer(1, 0.15 * inch))
    
    story.append(Paragraph("2. Guardian & Emergency Contacts", heading_style))
    guardian_data = [
        [Paragraph("Guardian Name", cell_label), Paragraph(student.guardian_name, cell_val), Paragraph("Guardian Phone", cell_label), Paragraph(student.guardian_phone, cell_val)],
        [Paragraph("Guardian Email", cell_label), Paragraph(student.guardian_email or 'N/A', cell_val), Paragraph("Emergency Contact", cell_label), Paragraph(student.emergency_contact, cell_val)]
    ]
    t2 = Table(guardian_data, colWidths=[1.5*inch, 2.0*inch, 1.5*inch, 1.8*inch])
    t2.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#F3F4F6')),
        ('BACKGROUND', (2,0), (2,-1), colors.HexColor('#F3F4F6')),
        ('PADDING', (0,0), (-1,-1), 5)
    ]))
    story.append(t2)
    
    story.append(Spacer(1, 0.3 * inch))
    footer_text = Paragraph(f"<i>Generated on {datetime.now().strftime('%d %B %Y at %H:%M')} | NNPSMS Official Academic Record System</i>", ParagraphStyle('Footer', parent=styles['Italic'], fontSize=8, alignment=1, textColor=colors.gray))
    story.append(footer_text)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_admission_letter_pdf(student):
    """Generates an official Nyeri National Polytechnic Admission Letter."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    normal = ParagraphStyle('Norm', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor('#1F2937'))
    bold_style = ParagraphStyle('BoldN', parent=normal, fontName='Helvetica-Bold')
    
    story = _get_pdf_header_flowables()
    
    ref_data = [
        [Paragraph(f"<b>REF NO:</b> NNP/ADM/{student.academic_year.replace('/', '-')}/{student.id:04d}", normal), Paragraph(f"<b>DATE:</b> {datetime.now().strftime('%d %B %Y')}", ParagraphStyle('Right', parent=normal, alignment=2))]
    ]
    story.append(Table(ref_data, colWidths=[3.5*inch, 3.5*inch]))
    story.append(Spacer(1, 0.15 * inch))
    
    recipient = f"""
    <b>TO:</b> {student.first_name} {student.middle_name or ''} {student.last_name}<br/>
    P.O. Box {student.address or 'N/A'}<br/>
    County: {student.county}<br/>
    Mobile: {student.phone_number} | Email: {student.email}
    """
    story.append(Paragraph(recipient, normal))
    story.append(Spacer(1, 0.2 * inch))
    
    subj_style = ParagraphStyle('Subj', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=11, alignment=1, textColor=colors.HexColor('#1E3A8A'))
    story.append(Paragraph(f"<u>RE: OFFER OF ADMISSION FOR ACADEMIC YEAR {student.academic_year}</u>", subj_style))
    story.append(Spacer(1, 0.15 * inch))
    
    body_p1 = f"""
    Following your application for admission to The Nyeri National Polytechnic, I am pleased to inform you that you have been offered a place in the Department of <b>{student.department.name if student.department else 'Academic Studies'}</b> to pursue a course leading to:
    """
    story.append(Paragraph(body_p1, normal))
    story.append(Spacer(1, 0.1 * inch))
    
    course_box = [
        [Paragraph("<b>COURSE OFFERED:</b>", bold_style), Paragraph(student.course.name if student.course else 'N/A', normal)],
        [Paragraph("<b>ADMISSION NUMBER:</b>", bold_style), Paragraph(f"<b>{student.admission_number}</b>", bold_style)],
        [Paragraph("<b>CURRENT MODULE/SEMESTER:</b>", bold_style), Paragraph(student.semester_module, normal)],
        [Paragraph("<b>REPORTING DATE:</b>", bold_style), Paragraph(student.enrollment_date.strftime('%d %B %Y') if student.enrollment_date else 'As Scheduled', normal)]
    ]
    cb_table = Table(course_box, colWidths=[2.2*inch, 4.8*inch])
    cb_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 6)
    ]))
    story.append(cb_table)
    story.append(Spacer(1, 0.15 * inch))
    
    body_p2 = """
    This offer is subject to satisfactory verification of your academic credentials, national identity documentation, and compliance with the rules and regulations governing student conduct at The Nyeri National Polytechnic.
    <br/><br/>
    Please ensure you download the institution's fee structure and medical clearance forms prior to reporting.
    """
    story.append(Paragraph(body_p2, normal))
    story.append(Spacer(1, 0.3 * inch))
    
    sign_off = """
    Yours Sincerely,<br/><br/><br/>
    <b>___________________________________</b><br/>
    <b>OFFICE OF THE ACADEMIC REGISTRAR</b><br/>
    The Nyeri National Polytechnic
    """
    story.append(Paragraph(sign_off, normal))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_student_list_pdf(students, filter_summary="All Enrolled Students"):
    """Generates a PDF directory report for a filtered list of students."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    
    story = _get_pdf_header_flowables()
    
    title_style = ParagraphStyle('ReportTitle', parent=styles['Heading2'], alignment=1, fontSize=12, fontName='Helvetica-Bold', textColor=colors.HexColor('#1E3A8A'))
    sub_style = ParagraphStyle('SubTitle', parent=styles['Normal'], alignment=1, fontSize=9, textColor=colors.HexColor('#6B7280'), spaceAfter=10)
    
    story.append(Paragraph("REGISTERED STUDENT DIRECTORY REPORT", title_style))
    story.append(Paragraph(f"Filter Criteria: {filter_summary} | Total Records: {len(students)}", sub_style))
    
    header_style = ParagraphStyle('HeaderStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)
    headers = [
        Paragraph("<b>#</b>", header_style),
        Paragraph("<b>Adm No</b>", header_style),
        Paragraph("<b>Student Name</b>", header_style),
        Paragraph("<b>Course</b>", header_style),
        Paragraph("<b>Phone</b>", header_style),
        Paragraph("<b>Status</b>", header_style)
    ]
    
    data = [headers]
    for idx, s in enumerate(students, start=1):
        data.append([
            Paragraph(str(idx), styles['Normal']),
            Paragraph(s.admission_number, styles['Normal']),
            Paragraph(f"{s.first_name} {s.last_name}", styles['Normal']),
            Paragraph(s.course.code if s.course else 'N/A', styles['Normal']),
            Paragraph(s.phone_number, styles['Normal']),
            Paragraph(s.status, styles['Normal'])
        ])
        
    t = Table(data, colWidths=[0.3*inch, 1.4*inch, 2.2*inch, 1.3*inch, 1.3*inch, 0.9*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F9FAFB')]),
        ('PADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    
    story.append(t)
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(f"<i>Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}</i>", ParagraphStyle('Foot', parent=styles['Italic'], fontSize=8, alignment=2)))
    
    doc.build(story)
    buffer.seek(0)
    return buffer
