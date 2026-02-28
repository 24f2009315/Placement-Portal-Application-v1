from flask import Flask,Blueprint,render_template,request,flash,redirect,url_for
from application.authz import role_required
from application.models import Users,Company,db,Student,Application,Placement
from flask_login import login_user,logout_user,login_required,current_user
from werkzeug.security import generate_password_hash, check_password_hash

api = Blueprint("admin_api",__name__)

@api.route("/admin/admin_dashboard",methods=["GET"])
@login_required
@role_required("admin")
def admin_dashboard():
    all_companies=Company.query.all()
    all_students=Student.query.all()
    all_placements=Placement.query.all()
    all_applications = Application.query.all()

    placement_count = Application.query.filter(Application.status.ilike("selected")).count()

    admin_chart_data = {
        "labels": ["Job Postings", "Applications", "Placements"],
        "values": [len(all_placements), len(all_applications), placement_count]
    }

    return render_template("admin/dashboard.html",
                               all_companies=all_companies,
                               all_students=all_students,
                               all_placements=all_placements,
                               all_applications=all_applications,
                               admin_chart_data = admin_chart_data)

@api.route("/admin/search",methods=["GET","POST"])
@role_required("admin")
def search():
    query=request.args.get("query","").strip()
    companies=[]
    students=[]
    if query:
        companies = Company.query.filter(
            (Company.name.ilike(f'%{query}%'))
        ).all()
        students = Student.query.filter(
            (Student.name.ilike(f'%{query}%'))
        ).all()
    return render_template("admin/search.html",companies=companies,students=students)

@api.route("/admin/approve_company/<int:company_id>",methods=["POST"])
@login_required
@role_required("admin")
def approve_company(company_id):
    company=Company.query.get_or_404(company_id)
    company.status = "approved"
    db.session.commit()
    flash("company approved successfully",category="alert-success")
    return redirect(url_for('admin_api.admin_dashboard'))

@api.route("/admin/reject_company/<int:company_id>",methods=["POST"])
@login_required
@role_required("admin")
def reject_company(company_id):
    company=Company.query.get_or_404(company_id)
    company.status = "rejected"
    db.session.commit()
    flash("company approved successfully",category="alert-success")
    return redirect(url_for('admin_api.admin_dashboard'))

@api.route("/admin/blacklist_company/<int:company_id>",methods=["POST"])
@login_required
@role_required("admin")
def blacklist_company(company_id):
    company=Company.query.get_or_404(company_id)
    company.status = "blacklisted"
    db.session.commit()
    return redirect(url_for('admin_api.admin_dashboard'))

@api.route("/admin/blacklist_student/<int:student_id>",methods=["POST"])
@login_required
@role_required("admin")
def blacklist_student(student_id):
    student=Student.query.get_or_404(student_id)
    student.status = "blacklisted"
    db.session.commit()
    return redirect(url_for('admin_api.admin_dashboard'))

@api.route("/admin/active_student/<int:student_id>",methods=["POST"])
@login_required
@role_required("admin")
def active_student(student_id):
    student=Student.query.get_or_404(student_id)
    student.status = "active"
    db.session.commit()
    return redirect(url_for('admin_api.admin_dashboard'))

@api.route("/admin/delete_student/<int:student_id>",methods=["POST"])
@login_required
@role_required("admin")
def delete_student(student_id):
    student=Student.query.get_or_404(student_id)
    user=Users.query.get(student.user_id)

    db.session.delete(student)
    if user:
        db.session.delete(user)
    db.session.commit()
    flash("student deleted successfully",category="alert-success")
    return redirect(url_for('admin_api.admin_dashboard'))

@api.route("/admin/delete_company/<int:company_id>", methods=["POST"])
@login_required
@role_required("admin")
def delete_company(company_id):
    company = Company.query.filter_by(company_id=company_id).first_or_404()
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