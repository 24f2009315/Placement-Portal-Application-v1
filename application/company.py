from flask import Flask,Blueprint,render_template,request,flash,redirect,url_for
from application.models import Users,Company,db,Student,Placement,Application
from flask_login import login_user,logout_user,login_required,current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

api = Blueprint("company_api",__name__)

@api.route("/company_dashboard",methods=["GET"])
def company_dashboard():
    upcoming_drives = Placement.query.filter_by(status="open").all()
    past_drives = Placement.query.filter_by(status="closed").all()
    return render_template("company/dashboard.html",upcoming_drives=upcoming_drives,past_drives=past_drives)

@api.route("/create_drive",methods=["GET","POST"])
def create_drive():

    if current_user.role != "company":
        flash("Only companies can create placement drives", "danger")
        return redirect(url_for("auth_api.login"))
    
    if request.method == "GET":
        return render_template("company/create_drive.html")
    
    name = request.form.get("name")
    title = request.form.get("title")
    description = request.form.get("description")
    eligibility = request.form.get("eligibility")
    deadline_str = request.form.get("deadline")   # "2026-02-07"
    deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date()

    company = Company.query.filter_by(user_id=current_user.user_id).first()

    new_placement = Placement(name=name,title=title,description=description,eligibility=eligibility,deadline=deadline,company_id=company.company_id,status="open")
    db.session.add(new_placement)
    db.session.commit()

    return redirect(url_for("company_api.company_dashboard"))
    
@api.route("/mark_complete/<int:drive_id>",methods=["POST"])
def mark_complete(drive_id):
    drive = Placement.query.filter_by(drive_id=drive_id).first()

    drive.status = "closed"
    db.session.commit()
    return redirect(url_for("company_api.company_dashboard"))

@api.route("/stu_apply/<int:drive_id>",methods=["GET"])
def stu_apply(drive_id):
    applications = Application.query.filter_by(drive_id=drive_id).all()
    return render_template("company/stu_apply.html",applications=applications,drive_id=drive_id)

@api.route("/update_status/<int:application_id>", methods=["POST"])
def update_status(application_id):
    application = Application.query.get(application_id)
    application.status = request.form.get("status")
    db.session.commit()
    return redirect(url_for('company_api.stu_apply',drive_id=application.drive_id))