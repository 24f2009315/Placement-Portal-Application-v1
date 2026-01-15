from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db=SQLAlchemy()

class Users(db.Model, UserMixin):
    __tablename__ = "users"

    user_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20),nullable=False)
    is_active = db.Column(db.Boolean(), default=True)

    def get_id(self):
        return str(self.user_id)

class Student(db.Model):
    __tablename__ = "student"

    student_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer(),db.ForeignKey("users.user_id"),nullable=False,unique=True)
    roll_no = db.Column(db.String(20), unique=True, nullable=False)
    phone = db.Column(db.String(15))
    department = db.Column(db.String(50))
    degree = db.Column(db.String(50))
    batch_year = db.Column(db.Integer())
    cgpa = db.Column(db.Float())
    resume_url = db.Column(db.String(255))
    is_placed = db.Column(db.Boolean(), default=False)
    status = db.Column(db.String(20), default="active")  # active / blocked

class JobPosition(db.Model):
    __tablename__ = "job_position"

    position_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    drive_id = db.Column(db.Integer(),db.ForeignKey("placement.drive_id"),nullable=False)
    title = db.Column(db.String(100), nullable=False)  # Software Engineer, Data Analyst, ML Intern, etc.
    job_type = db.Column(db.String(20),nullable=False)  # Internship / Full-time / PPO
    location = db.Column(db.String(100))
    vacancies = db.Column(db.Integer())
    stipend = db.Column(db.Integer())      # for internships
    ctc = db.Column(db.Float())            # for full-time roles
    min_cgpa = db.Column(db.Float())
    eligible_departments = db.Column(db.String(255))
    eligible_batches = db.Column(db.String(50))
    description = db.Column(db.Text())
    status = db.Column(db.String(20),default="Open")  # Open / Closed / Filled

class Placement(db.Model):
    __tablename__ = "placement"

    drive_id = db.Column(db.Integer(),primary_key=True,autoincrement=True)
    company_id = db.Column(db.Integer(),db.ForeignKey("company.company_id"),nullable=False)
    title=db.Column(db.String(50))
    description=db.Column(db.Text())
    eligibility=db.Column(db.String(200))
    deadline=db.Column(db.Date())
    status=db.Column(db.String(30)) #open/closed

class Application(db.Model):
    __tablename__ = "application"

    application_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer(), db.ForeignKey("student.student_id"), nullable=False)
    drive_id = db.Column(db.Integer(), db.ForeignKey("placement.drive_id"), nullable=False)
    application_date = db.Column(db.DateTime(), server_default=db.func.now())
    status = db.Column(db.String(30),default="Applied")  # Applied / Shortlisted / Rejected / Selected
    remarks = db.Column(db.String(255))  # optional admin/HR notes

class  Company(db.Model):
    __tablename__ = "company"

    company_id = db.Column(db.Integer(),primary_key=True,autoincrement=True)
    user_id = db.Column(db.Integer(),db.ForeignKey("users.user_id"),nullable=False,unique=True)
    HR_contact=db.Column(db.String(15),unique=True)
    website=db.Column(db.String(200)) #url
    status=db.Column(db.String(30)) #approved or pending or rejected