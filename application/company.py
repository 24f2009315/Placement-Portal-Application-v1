from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from application.models import Application, Company, Placement, Users, db
from flask_login import current_user
from datetime import datetime

api = Blueprint("company_api",__name__)

@api.before_request
def require_company():
    if not current_user.is_authenticated:
        return redirect(url_for("auth_api.login"))
    if current_user.role != "company":
        flash("Unauthorized access", "warning")
        if current_user.role == "admin":
            return redirect(url_for("admin_api.admin_dashboard"))
        if current_user.role == "student":
            return redirect(url_for("student_api.student_dashboard"))
        return redirect(url_for("auth_api.login"))

@api.route("/company/company_dashboard",methods=["GET"])
def company_dashboard():
    company = Company.query.filter_by(user_id=current_user.user_id).first()
    approved_drives = Placement.query.filter(
        Placement.company_id == company.company_id,
        Placement.status.ilike("approved"),
    ).all()
    closed_drives = Placement.query.filter(
        Placement.company_id == company.company_id,
        Placement.status.ilike("closed"),
    ).all()
    pending_drives = Placement.query.filter(
        Placement.company_id == company.company_id,
        Placement.status.in_(["pending", "open"]),
    ).all()
    rejected_drives = Placement.query.filter(
        Placement.company_id == company.company_id,
        Placement.status.ilike("rejected"),
    ).all()

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
                           approved_drives=approved_drives,
                           closed_drives=closed_drives,
                           pending_drives=pending_drives,
                           rejected_drives=rejected_drives,
                           company_chart_data = company_chart_data)

@api.route("/company/shortlisted_candidates", methods=["GET"])
def shortlisted_candidates():
    company = Company.query.filter_by(user_id=current_user.user_id).first()
    shortlisted_applications = (
        Application.query.join(Placement, Application.drive_id == Placement.drive_id)
        .filter(
            Placement.company_id == company.company_id,
            Application.status.ilike("shortlisted"),
        )
        .all()
    )
    return render_template(
        "company/shortlisted_candidates.html",
        shortlisted_applications=shortlisted_applications,
    )

@api.route("/company/create_drive",methods=["GET","POST"])
def create_drive():
    if request.method == "GET":
        return render_template("company/create_drive.html")
    
    name = request.form.get("name")
    title = request.form.get("title")
    description = request.form.get("description")
    eligibility = request.form.get("eligibility")
    deadline_str = request.form.get("deadline","").strip()
    try:
        deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date()
    except ValueError:
        flash("Invalid deadline. Use YYYY-MM-DD.", "warning")
        return redirect(url_for("company_api.create_drive"))

    company = Company.query.filter_by(user_id=current_user.user_id).first()

    new_placement = Placement(name=name,title=title,description=description,eligibility=eligibility,deadline=deadline,company_id=company.company_id,status="pending")
    db.session.add(new_placement)
    db.session.commit()

    return redirect(url_for("company_api.company_dashboard"))
    
@api.route("/company/mark_complete/<int:drive_id>",methods=["POST"])
def mark_complete(drive_id):
    company = Company.query.filter_by(user_id=current_user.user_id).first()
    drive = Placement.query.filter_by(drive_id=drive_id, company_id=company.company_id).first()
    if not drive:
        flash("Drive not found.", "warning")
        return redirect(url_for("company_api.company_dashboard"))

    if (drive.status or "").lower() != "approved":
        flash("Only approved drives can be closed.", "warning")
        return redirect(url_for("company_api.company_dashboard"))

    drive.status = "closed"
    db.session.commit()
    return redirect(url_for("company_api.company_dashboard"))

@api.route("/company/stu_apply/<int:drive_id>",methods=["GET"])
def stu_apply(drive_id):
    applications = Application.query.filter_by(drive_id=drive_id).all()
    return render_template("company/stu_apply.html",applications=applications,drive_id=drive_id)

@api.route("/company/update_status/<int:application_id>", methods=["POST"])
def update_status(application_id):
    application = Application.query.get(application_id)
    if not application:
        flash("Application not found.", "warning")
        return redirect(url_for("company_api.company_dashboard"))
    new_status = request.form.get("status", "").strip()
    if not new_status:
        flash("Status is required.", "warning")
        return redirect(url_for("company_api.stu_apply", drive_id=application.drive_id))
    application.status = new_status
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
