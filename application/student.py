from flask import Flask,Blueprint,render_template,request,flash,redirect,url_for
from application.models import Users,Company,db,Student,Placement,Application
from flask_login import login_user,logout_user,login_required,current_user
from werkzeug.security import generate_password_hash, check_password_hash

api = Blueprint("student_api",__name__)

@api.route("/student_dashboard",methods=["GET","POST","PUT","PATCH","DELETE"])
@login_required
def student_dashboard():
    if current_user.role != "student":
        return redirect(url_for("auth_api.login"))

    registered_companies = Company.query.filter_by(status="approved").all()
    student = Student.query.filter_by(user_id = current_user.user_id).first()
    applied_drives = Application.query.filter_by(student_id = student.student_id).all()
    return render_template("student/dashboard.html",registered_companies=registered_companies,applied_drives=applied_drives)

@api.route("/view_drives/<int:company_id>",methods=["GET"])
def view_drives(company_id):
    company = Company.query.filter_by(company_id=company_id).first()
    drives = Placement.query.filter_by(company_id=company_id,status="open").all()
    return render_template("student/view_drives.html",company=company,drives=drives)

@api.route("/view_drive/<int:drive_id>", methods=["GET"])
def view_drive(drive_id):

    drive = Placement.query.filter_by(drive_id=drive_id).first()
    company = Company.query.get(drive.company_id)

    return render_template("student/drive.html",drive=drive,company=company)

@api.route("/apply_drive/<int:drive_id>",methods=["POST"])
@login_required
def apply_drive(drive_id):
    if current_user.role != "student":
        flash("only students can apply","danger")
        return redirect(url_for('auth_api.login'))
    
    student = Student.query.filter_by(user_id=current_user.user_id).first()

    existing_application = Application.query.filter_by(student_id=student.student_id,drive_id=drive_id).first()

    if existing_application:
        flash("You have already applied to this drive", "warning")
        return redirect(url_for("student_api.student_dashboard"))

    application = Application(student_id=student.student_id,drive_id=drive_id,status="applied")
    db.session.add(application)
    db.session.commit()

    flash("applied successfully",category="alert-success")
    return redirect(url_for('student_api.student_dashboard'))