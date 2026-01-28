from flask import Flask,Blueprint,render_template,request,flash,redirect,url_for
from application.models import Users,Company,db,Student,Application,Placement,JobPosition
from flask_login import login_user,logout_user,login_required,current_user
from werkzeug.security import generate_password_hash, check_password_hash

api = Blueprint("admin_api",__name__)

@api.route("/admin_dashboard",methods=["GET"])
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        return redirect(url_for("auth_api.login"))
    
    all_companies=Company.query.all()
    all_students=Student.query.all()
    all_placements=Placement.query.all()
    all_jobs=JobPosition.query.all()
    return render_template("admin/dashboard.html",
                               all_companies=all_companies,
                               all_students=all_students,
                               all_placements=all_placements,
                               all_jobs=all_jobs)

@api.route("/search",methods=["GET","POST"])
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

@api.route("/approve_company/<int:company_id>",methods=["POST"])
def approve_company(company_id):
    company=Company.query.get_or_404(company_id)
    company.status = "approved"
    db.session.commit()
    flash("company approved successfully",category="alert-success")
    return redirect(url_for('admin_api.admin_dashboard'))

@api.route("/reject_company/<int:company_id>",methods=["POST"])
def reject_company(company_id):
    company=Company.query.get_or_404(company_id)
    company.status = "rejected"
    db.session.commit()
    flash("company approved successfully",category="alert-success")
    return redirect(url_for('admin_api.admin_dashboard'))

@api.route("/delete_company/<int:company_id>",methods=["POST"])
@login_required
def delete_company(company_id):
    company=Company.query.get_or_404(company_id)
    user=Users.query.get(company.user_id)

    db.session.delete(company)
    if user:
        db.session.delete(user)
    db.session.commit()
    flash("company deleted successfully",category="alert-success")
    return redirect(url_for('admin_api.admin_dashboard'))

@api.route("/blacklist_company/<int:company_id>",methods=["POST"])
def blacklist_company(company_id):
    company=Company.query.get_or_404(company_id)
    company.status = "blacklisted"
    db.session.commit()
    return redirect(url_for('admin_api.admin_dashboard'))

@api.route("/blacklist_student/<int:student_id>",methods=["POST"])
def blacklist_student(student_id):
    student=Student.query.get_or_404(student_id)
    student.status = "blacklisted"
    db.session.commit()
    return redirect(url_for('admin_api.admin_dashboard'))

@api.route("/active_student/<int:student_id>",methods=["POST"])
def active_student(student_id):
    student=Student.query.get_or_404(student_id)
    student.status = "active"
    db.session.commit()
    return redirect(url_for('admin_api.admin_dashboard'))

@api.route("/delete_student/<int:student_id>",methods=["POST"])
@login_required
def delete_student(student_id):
    student=Student.query.get_or_404(student_id)
    user=Users.query.get(student.user_id)

    db.session.delete(student)
    if user:
        db.session.delete(user)
    db.session.commit()
    flash("student deleted successfully",category="alert-success")
    return redirect(url_for('admin_api.admin_dashboard'))