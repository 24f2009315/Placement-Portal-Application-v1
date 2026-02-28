from flask import Flask,Blueprint,render_template,request,flash,redirect,url_for,jsonify
from application.authz import role_required
from application.models import Users,Company,db,Student,Placement,Application
from flask_login import login_user,logout_user,login_required,current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

api = Blueprint("company_api",__name__)

@api.route("/company/company_dashboard",methods=["GET"])
@login_required
@role_required("company")
def company_dashboard():
    company = Company.query.filter_by(user_id=current_user.user_id).first()
    upcoming_drives = Placement.query.filter_by(status="open").all()
    past_drives = Placement.query.filter_by(status="closed").all()
    all_company_drives = Placement.query.filter_by(company_id=company.company_id).all()
    trend_labels = []
    trend_values = []

    for drive in all_company_drives:
        trend_labels.append(drive.name or f"Drive {drive.drive_id}")
        trend_values.append(Application.query.filter_by(drive_id=drive.drive_id).count())

    company_chart_data = {
        "labels": trend_labels,
        "values": trend_values
    }
    return render_template("company/dashboard.html",
                           upcoming_drives=upcoming_drives,
                           past_drives=past_drives,
                           company_chart_data = company_chart_data)

@api.route("/company/create_drive",methods=["GET","POST"])
@login_required
@role_required("company")
def create_drive():
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
    
@api.route("/company/mark_complete/<int:drive_id>",methods=["POST"])
@login_required
@role_required("company")
def mark_complete(drive_id):
    drive = Placement.query.filter_by(drive_id=drive_id).first()

    drive.status = "closed"
    db.session.commit()
    return redirect(url_for("company_api.company_dashboard"))

@api.route("/company/stu_apply/<int:drive_id>",methods=["GET"])
@login_required
@role_required("company")
def stu_apply(drive_id):
    applications = Application.query.filter_by(drive_id=drive_id).all()
    return render_template("company/stu_apply.html",applications=applications,drive_id=drive_id)

@api.route("/company/update_status/<int:application_id>", methods=["POST"])
@login_required
@role_required("company")
def update_status(application_id):
    application = Application.query.get(application_id)
    application.status = request.form.get("status")
    db.session.commit()
    return redirect(url_for('company_api.stu_apply',drive_id=application.drive_id))

@api.route('/api/companies', methods=['GET'])
def get_companies_api():
    companies = Company.query.all()
    result = []
    for _ in companies:
        result.append({
            "company_id":_.company_id,
            "name":_.name
        })
    return jsonify(result)

@api.route('/api/companies', methods=['POST'])
def create_company_api():
    data = request.get_json()

    if not data or not data.get("name") or not data.get("username") or not data.get("password"):
        return jsonify({"error": "invalid input"}), 400

    new_user = Users(
        name=data.get("name"),
        username=data.get("username"),
        password=data.get("password"),
        role="company",
        is_active=True
    )
    db.session.add(new_user)
    db.session.commit()

    new_company = Company(
        name=data.get("name"),
        user_id=new_user.user_id,
        website = data.get("website")
    )
    db.session.add(new_company)
    db.session.commit()

    return jsonify({
        "message": "company created",
        "company_id": new_company.company_id,
        "user_id": new_user.user_id
    }), 201

@api.route('/api/companies/<int:company_id>', methods=['PUT'])
def update_company_api(company_id):
    data = request.get_json()

    company = Company.query.get(company_id)

    if not company:
        return jsonify({"error": "Company not found"}), 404

    if data.get("name"):
        company.user.name = data.get("name")

    if data.get("hr_contact"):
        company.hr_contact = data.get("hr_contact")

    if data.get("website"):
        company.website = data.get("website")

    db.session.commit()

    return jsonify({"message": "Company updated successfully"})

@api.route('/api/companies/<int:company_id>', methods=['DELETE'])
def delete_company_api(company_id):

    company = Company.query.get(company_id)

    if not company:
        return jsonify({"error": "Company not found"}), 404

    user = company.user

    db.session.delete(company)
    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "Company deleted successfully"})