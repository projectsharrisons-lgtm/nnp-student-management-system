from app.extensions import db
from app.models.user import User
from app.models.academic import Department, Course, Unit, StudentProfile, LecturerProfile

def seed_database():
    print("🌱 Starting Nyeri National Polytechnic Seed Process...")

    # 1. Clear or check existing records to prevent duplication errors
    if Department.query.first():
        print("⚠️ Database already contains academic data. Skipping seeding.")
        return

    # 2. Create Default Users (Admin, Lecturer, Student)
    admin_user = User(username='superadmin', email='admin@thenyeripoly.ac.ke', role='Super Administrator', is_verified=True)
    admin_user.set_password('Admin@2026!')
    
    lecturer_user = User(username='jkamau', email='jkamau@thenyeripoly.ac.ke', role='Lecturer', is_verified=True)
    lecturer_user.set_password('Lecturer@2026!')

    student_user = User(username='wanjiku_s', email='student@thenyeripoly.ac.ke', role='Student', is_verified=True)
    student_user.set_password('Student@2026!')

    db.session.add_all([admin_user, lecturer_user, student_user])
    db.session.commit()

    # 3. Create NNP Departments (Real institutional data mapping)
    dept_ict = Department(name="Computing and Informatics", code="COMP", description="Department specializing in ICT, Software Engineering, and Network Administration.")
    dept_bus = Department(name="Business Studies and Entrepreneurship", code="BUS", description="Offering accounting, banking, human resource, and business administration.")
    dept_eng = Department(name="Electrical and Electronics Engineering", code="EE", description="Focuses on power systems, telecommunications, and industrial automation.")
    dept_agr = Department(name="Agriculture and Environmental Studies", code="AGR", description="Training in agricultural extension, horticulture, and animal health.")

    db.session.add_all([dept_ict, dept_bus, dept_eng, dept_agr])
    db.session.commit()

    # 4. Create Courses
    c_ict_dip = Course(name="Diploma in Information Communication Technology", code="ICT-D-06", level="Level 5 - Diploma", department_id=dept_ict.id)
    c_sw_dip = Course(name="Diploma in Software Development", code="SD-D-06", level="Level 5 - Diploma", department_id=dept_ict.id)
    c_bus_dip = Course(name="Diploma in Business Management", code="BM-D-05", level="Level 5 - Diploma", department_id=dept_bus.id)
    c_elec = Course(name="Electrical Engineering Technology (Power Option)", code="EE-T-06", level="Level 6 - Higher Diploma", department_id=dept_eng.id)

    db.session.add_all([c_ict_dip, c_sw_dip, c_bus_dip, c_elec])
    db.session.commit()

    # 5. Create Units
    u1 = Unit(name="Object Oriented Programming", code="CIT 2201", course_id=c_ict_dip.id)
    u2 = Unit(name="Database Management Systems", code="CIT 2202", course_id=c_ict_dip.id)
    u3 = Unit(name="Web Application Development", code="SWE 3101", course_id=c_sw_dip.id)
    u4 = Unit(name="Financial Accounting I", code="BUS 1101", course_id=c_bus_dip.id)

    db.session.add_all([u1, u2, u3, u4])
    db.session.commit()

    # 6. Create Associated Profiles
    student_profile = StudentProfile(user_id=student_user.id, adm_number="NNP/2026/09482", course_id=c_ict_dip.id)
    lecturer_profile = LecturerProfile(user_id=lecturer_user.id, staff_number="STF/COMP/041", department_id=dept_ict.id, specialization="Software Architecture")

    db.session.add_all([student_profile, lecturer_profile])
    db.session.commit()

    print("✅ Nyeri National Polytechnic database seeded successfully!")
