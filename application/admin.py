from flask import Blueprint, flash, redirect, render_template, request, url_for
from application.models import Application, Company, Placement, Student, Users, db
from flask_login import current_user

api = Blueprint("admin_api", __name__)

@api.before_request
def require_admin():
    if not current_user.is_authenticated:
        return redirect(url_for("auth_api.login"))
    if current_user.role != "admin":
        flash("Unauthorized access", "warning")
        if current_user.role == "company":
            return redirect(url_for("company_api.company_dashboard"))
        if current_user.role == "student":
            return redirect(url_for("student_api.student_dashboard"))
        return redirect(url_for("auth_api.login"))

@api.route("/admin/admin_dashboard", methods=["GET"])
def admin_dashboard():
    all_companies = Company.query.all()
    all_students = Student.query.all()
    all_placements = Placement.query.all()
    all_applications = Application.query.all()
    total_companies = len(all_companies)
    total_students = len(all_students)
    total_placements = len(all_placements)
    total_applications = len(all_applications)
    approved_companies = [c for c in all_companies if (c.status or "").lower() == "approved"]
    pending_companies = [c for c in all_companies if (c.status or "").lower() == "pending"]
    active_students = [s for s in all_students if (s.status or "").lower() == "active"]

    placement_count = Application.query.filter(Application.status.ilike("selected")).count()

    admin_chart_data = {
        "labels": ["Placements", "Applications"],
        "values": [total_placements, total_applications],
    }

    return render_template(
        "admin/dashboard.html",
        all_companies=all_companies,
        approved_companies=approved_companies,
        pending_companies=pending_companies,
        all_students=all_students,
        active_students=active_students,
        all_placements=all_placements,
        all_applications=all_applications,
        total_companies=total_companies,
        total_students=total_students,
        total_placements=total_placements,
        total_applications=total_applications,
        admin_chart_data=admin_chart_data,
    )

@api.route("/admin/search", methods=["GET", "POST"])
def search():
    query = request.args.get("query", "").strip()
    companies = []
    students = []
    if query:
        companies = Company.query.filter(
            (Company.name.ilike(f"%{query}%"))
        ).all()
        students = Student.query.filter(
            (Student.name.ilike(f"%{query}%"))
        ).all()
    return render_template("admin/search.html", companies=companies, students=students)

@api.route("/admin/approve_company/<int:company_id>", methods=["POST"])
def approve_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.status = "approved"
    db.session.commit()
    flash("company approved successfully", category="alert-success")
    return redirect(url_for("admin_api.admin_dashboard"))

@api.route("/admin/reject_company/<int:company_id>", methods=["POST"])
def reject_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.status = "rejected"
    db.session.commit()
    flash("company rejected successfully", category="alert-success")
    return redirect(url_for("admin_api.admin_dashboard"))

@api.route("/admin/blacklist_company/<int:company_id>", methods=["POST"])
def blacklist_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.status = "blacklisted"
    db.session.commit()
    return redirect(url_for("admin_api.admin_dashboard"))

@api.route("/admin/approve_drive/<int:drive_id>", methods=["POST"])
def approve_drive(drive_id):
    drive = Placement.query.get_or_404(drive_id)
    if (drive.status or "").lower() not in ("pending", "open"):
        flash("Only pending drives can be reviewed.", "warning")
        return redirect(url_for("admin_api.admin_dashboard"))
    drive.status = "approved"
    db.session.commit()
    flash("Drive approved successfully", category="alert-success")
    return redirect(url_for("admin_api.admin_dashboard"))

@api.route("/admin/reject_drive/<int:drive_id>", methods=["POST"])
def reject_drive(drive_id):
    drive = Placement.query.get_or_404(drive_id)
    if (drive.status or "").lower() not in ("pending", "open"):
        flash("Only pending drives can be reviewed.", "warning")
        return redirect(url_for("admin_api.admin_dashboard"))
    drive.status = "rejected"
    db.session.commit()
    flash("Drive rejected successfully", category="alert-success")
    return redirect(url_for("admin_api.admin_dashboard"))

@api.route("/admin/blacklist_student/<int:student_id>", methods=["POST"])
def blacklist_student(student_id):
    student = Student.query.get_or_404(student_id)
    student.status = "blacklisted"
    db.session.commit()
    return redirect(url_for("admin_api.admin_dashboard"))

@api.route("/admin/active_student/<int:student_id>", methods=["POST"])
def active_student(student_id):
    student = Student.query.get_or_404(student_id)
    student.status = "active"
    db.session.commit()
    return redirect(url_for("admin_api.admin_dashboard"))

@api.route("/admin/delete_student/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    user = Users.query.get(student.user_id)

    db.session.delete(student)
    if user:
        db.session.delete(user)
    db.session.commit()
    flash("student deleted successfully", category="alert-success")
    return redirect(url_for("admin_api.admin_dashboard"))

@api.route("/admin/delete_company/<int:company_id>", methods=["POST"])
def delete_company(company_id):
    company = Company.query.get_or_404(company_id)
    user = Users.query.get(company.user_id)

    drives = Placement.query.filter_by(company_id=company.company_id).all()
    drive_ids = [d.drive_id for d in drives]

    if drive_ids:
        Application.query.filter(Application.drive_id.in_(drive_ids)).delete(synchronize_session=False)

    for drive in drives:
        db.session.delete(drive)

    db.session.delete(company)
    if user:
        db.session.delete(user)

    db.session.commit()
    flash("Company deleted successfully", "success")
    return redirect(url_for("admin_api.admin_dashboard"))
